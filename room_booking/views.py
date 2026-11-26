from uuid import uuid4
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils.dateparse import parse_date

from room_booking.models import WishList, Booking, BookingHistory
from user_profile.models import Person
from hotel_room.models import Room


def calculate_stay_price(room, checkin, checkout, cleaning=False, laundry=False, breakfast=False):
    nights = (checkout - checkin).days
    if nights < 1:
        raise ValueError('Stay must be at least one night.')
    # Room rates are charged per night; optional service fees are currently flat per stay.
    return (room.booking_price * nights) + (5 if cleaning else 0) + (5.5 if laundry else 0) + (5 if breakfast else 0)


class AddToWishListView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body or '{}')
            checkin = parse_date(data.get('checkInDate', ''))
            checkout = parse_date(data.get('checkOutDate', ''))
            room_number = data.get('roomNumber')
            cleaning = bool(data.get('isCleaning'))
            laundry = bool(data.get('isLaundry'))
            breakfast = bool(data.get('isBreakfast'))
            if not checkin or not checkout or checkout <= checkin:
                return JsonResponse({'msg': 'Please select valid check-in and check-out dates.'}, status=400)
            if not room_number:
                return JsonResponse({'msg': 'Room number is required.'}, status=400)
            person = get_object_or_404(Person, email=request.user.email)
            room = get_object_or_404(Room, room_number=room_number)
            active_statuses = ('requested', 'pending', 'confirmed', 'checked-in')
            conflict = BookingHistory.objects.filter(room=room, check_in__lt=checkout, check_out__gt=checkin, reservation_number__booking_status__in=active_statuses).exists()
            if conflict:
                return JsonResponse({'msg': 'This room is already booked for those dates.'}, status=409)
            total_price = calculate_stay_price(room, checkin, checkout, cleaning, laundry, breakfast)
            wishlist = WishList.objects.create(person=person, room=room, check_in=checkin, check_out=checkout, room_cleaning=cleaning, laundry=laundry, breakfast=breakfast, total_price=total_price)
            return JsonResponse({'msg': 'Added to wish list.', 'itemId': wishlist.pk, 'totalPrice': total_price})
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({'msg': 'Invalid request data.'}, status=400)

    def get(self, request, *args, **kwargs):
        return redirect('wishlist')


class WishListView(LoginRequiredMixin, View):
    __template_name = 'room_booking/wishlist.html'

    def get(self, request, *args, **kwargs):
        person = get_object_or_404(Person, email=request.user.email)
        items = WishList.objects.filter(person=person).select_related('room')
        total_amount = sum(item.total_price for item in items)
        return render(request=request, template_name=self.__template_name, context={'items': items, 'total_amount': total_amount})


class DeleteWishListItemView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        person = get_object_or_404(Person, email=request.user.email)
        WishList.objects.filter(pk=kwargs['id'], person=person).delete()
        return redirect('wishlist')


class BookingListView(LoginRequiredMixin, View):
    __template_name = 'room_booking/my_booking.html'

    def get(self, request, *args, **kwargs):
        person = get_object_or_404(Person, email=request.user.email)
        bookings = Booking.objects.filter(person=person).prefetch_related('rooms', 'bookinghistory_set__room')
        return render(request=request, template_name=self.__template_name, context={'title': 'My Bookings', 'bookings': bookings})


class AddBookingView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body or '{}')
            raw_ids = data.get('itemId', [])
            if not isinstance(raw_ids, list) or not raw_ids:
                return JsonResponse({'msg': 'Please select at least one wishlist item.'}, status=400)
            selected_ids = list(dict.fromkeys(int(item_id) for item_id in raw_ids))
        except (ValueError, TypeError, json.JSONDecodeError):
            return JsonResponse({'msg': 'Invalid wishlist selection.'}, status=400)
        person = get_object_or_404(Person, email=request.user.email)
        items = list(WishList.objects.filter(pk__in=selected_ids, person=person).select_related('room'))
        if len(items) != len(selected_ids):
            return JsonResponse({'msg': 'One or more selected wishlist items are invalid.'}, status=400)
        active_statuses = ('requested', 'pending', 'confirmed', 'checked-in')
        for index, item in enumerate(items):
            if not item.check_in or not item.check_out or item.check_out <= item.check_in:
                return JsonResponse({'msg': 'A selected item has invalid booking dates.'}, status=400)
            # Prevent overlapping duplicate room selections in the same checkout request.
            for other in items[index + 1:]:
                if item.room_id == other.room_id and item.check_in < other.check_out and item.check_out > other.check_in:
                    return JsonResponse({'msg': 'Selected wishlist items overlap for the same room.'}, status=400)
            conflict = BookingHistory.objects.filter(room=item.room, check_in__lt=item.check_out, check_out__gt=item.check_in, reservation_number__booking_status__in=active_statuses).exists()
            if conflict:
                return JsonResponse({'msg': f'Room {item.room.room_number} is no longer available for those dates.'}, status=409)
        # Ignore client-submitted prices and recompute all totals from database room rates.
        for item in items:
            item.total_price = calculate_stay_price(item.room, item.check_in, item.check_out, item.room_cleaning, item.laundry, item.breakfast)
        with transaction.atomic():
            booking = Booking.objects.create(person=person, booking_status='requested', reservation_number=f'R-{uuid4().hex[:16]}')
            for item in items:
                booking.rooms.add(item.room)
                BookingHistory.objects.create(reservation_number=booking, room=item.room, person=person, check_in=item.check_in, check_out=item.check_out, room_cleaning=item.room_cleaning, laundry=item.laundry, breakfast=item.breakfast, total_price=item.total_price)
            WishList.objects.filter(pk__in=selected_ids, person=person).delete()
        return JsonResponse({'msg': 'Your reservation request has been placed!', 'reservationNumber': booking.reservation_number}, status=201)

from room_booking.models import BookingHistory