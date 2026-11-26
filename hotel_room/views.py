from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views import View
from django.views.decorators.http import require_GET, require_POST
from django.utils.dateparse import parse_date
import json

from .models import Room
from room_booking.models import BookingHistory


class RoomsView(View):
    template_name = 'pages/rooms.html'

    def get(self, req, *args, **kwargs):
        rooms = Room.objects.all()
        context = {
            'title': 'Hotel Rooms',
            'active_nav_item': 'nav-rooms',
            'rooms': rooms,
        }
        return render(req, self.template_name, context=context)


class RoomDetailsView(View):
    template_name = "pages/room_details.html"

    ROOM_STATUS = (
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("occupied", "Occupied"),
        ("not available", "Not Available"),
        ("being serviced", "Being Serviced"),
        ("other", "Other"),
    )

    def get(self, req, *args, **kwargs):
        room_number = req.GET.get('roomNumber')
        room_details = get_object_or_404(Room, room_number=room_number)
        context = {
            'title': 'Room Details',
            'active_nav_item': 'nav-rooms',
            "room_details": room_details,
        }
        return render(req, self.template_name, context=context)


@require_GET
def get_standard_rooms(req):
    filtered_rooms = Room.objects.filter(style='standard').values()
    return JsonResponse({'filtered_rooms': list(filtered_rooms)})


@require_GET
def get_delux_rooms(req):
    delux_rooms = Room.objects.filter(style='delux').values()
    return JsonResponse({'filtered_rooms': list(delux_rooms)})


@require_GET
def get_family_suit(req):
    filtered_rooms = Room.objects.filter(style='family').values()
    return JsonResponse({'filtered_rooms': list(filtered_rooms)})


@require_GET
def get_business_suit(req):
    filtered_rooms = Room.objects.filter(style='business').values()
    return JsonResponse({'filtered_rooms': list(filtered_rooms)})


@require_POST
def check_room_availability(req):
    try:
        data = json.loads(req.body or '{}')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON request.'}, status=400)

    checkin_date = parse_date(data.get('checkInDate', ''))
    checkout_date = parse_date(data.get('checkOutDate', ''))
    room_number = data.get('roomNumber')

    if not checkin_date or not checkout_date or checkout_date <= checkin_date or not room_number:
        return JsonResponse({'error': 'Provide a room number and valid check-in/check-out dates.'}, status=400)

    room = get_object_or_404(Room, room_number=room_number)
    active_statuses = ('requested', 'pending', 'confirmed', 'checked-in')

    # A booking conflicts when its stay overlaps the requested date range.
    # Checkout on the requested check-in date is allowed, and vice versa.
    conflict = BookingHistory.objects.filter(
        room=room,
        check_in__lt=checkout_date,
        check_out__gt=checkin_date,
        reservation_number__booking_status__in=active_statuses,
    ).exists()

    return JsonResponse({'is_available': not conflict})
