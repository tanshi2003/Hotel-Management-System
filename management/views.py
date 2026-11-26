import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count
from django.core.exceptions import ValidationError

from room_booking.models import Booking
from room_booking.lifecycle import allowed_targets, transition_booking


class ManagementAccessMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        user = self.request.user
        return any((
            getattr(user, 'is_admin', False),
            getattr(user, 'is_manager', False),
            getattr(user, 'is_receptionist', False),
        ))


class ManagementView(ManagementAccessMixin, View):
    template_name = 'pages/management.html'

    def get(self, request, *args, **kwargs):
        bookings = Booking.objects.select_related('person').prefetch_related(
            'rooms', 'bookinghistory_set__room'
        ).order_by('-pk')
        counts = {status: 0 for status, _ in Booking.BOOKING_STATUS}
        for status, count in Booking.objects.values('booking_status').annotate(total=Count('pk')).values_list('booking_status', 'total'):
            counts[status] = count
        role = 'admin' if request.user.is_admin else 'manager' if request.user.is_manager else 'receptionist'
        transition_options = {status: sorted(allowed_targets(status, role)) for status, _ in Booking.BOOKING_STATUS}
        context = {
            'title': 'Management',
            'active_nav_item': 'nav-management',
            'bookings': bookings,
            'status_counts': counts,
            'in_house_count': counts.get('checked-in', 0),
            'total_bookings': bookings.count(),
            'is_privileged': request.user.is_admin or request.user.is_manager,
            'status_labels': dict(Booking.BOOKING_STATUS),
            'transition_options': transition_options,
        }
        return render(request=request, template_name=self.template_name, context=context)


class BookingStatusTransitionView(ManagementAccessMixin, View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body or '{}')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        if not isinstance(data, dict):
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        target = data.get('status')
        if not isinstance(target, str):
            return JsonResponse({'error': 'A target status is required.'}, status=400)

        role = 'admin' if request.user.is_admin else 'manager' if request.user.is_manager else 'receptionist'
        with transaction.atomic():
            booking = get_object_or_404(
                Booking.objects.select_for_update(),
                reservation_number=kwargs['reservation_number'],
            )
            current = booking.booking_status
            try:
                transition_booking(booking, target, role)
            except ValidationError as error:
                return JsonResponse({'error': str(error), 'current_status': current, 'target_status': target}, status=409)
        return JsonResponse({'reservationNumber': booking.reservation_number, 'status': booking.booking_status})
