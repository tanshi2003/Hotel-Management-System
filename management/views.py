import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.db.models import Count\nfrom django.core.exceptions import ValidationError

from room_booking.models import Booking

RECEPTION_TRANSITIONS = {
    'requested': {'pending', 'confirmed', 'canceled'},
    'pending': {'confirmed', 'canceled'},
    'confirmed': {'checked-in', 'canceled'},
    'checked-in': {'checked-out'},
}
PRIVILEGED_TRANSITIONS = {
    **RECEPTION_TRANSITIONS,
    'requested': {'pending', 'confirmed', 'canceled', 'abandoned'},
    'pending': {'confirmed', 'canceled', 'abandoned'},
    'confirmed': {'checked-in', 'canceled', 'abandoned'},
}


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
        aggregated = Booking.objects.values('booking_status').annotate(total=Count('pk'))
        for status, count in aggregated.values_list('booking_status', 'total'):
            counts[status] = count
        context = {
            'title': 'Management',
            'active_nav_item': 'nav-management',
            'bookings': bookings,
            'status_counts': counts,
            'in_house_count': counts.get('checked-in', 0),
            'total_bookings': bookings.count(),
            'is_privileged': request.user.is_admin or request.user.is_manager,
            'status_labels': dict(Booking.BOOKING_STATUS),\n            'transition_options': transition_options,
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

        is_privileged = request.user.is_admin or request.user.is_manager
        allowed_map = PRIVILEGED_TRANSITIONS if is_privileged else RECEPTION_TRANSITIONS
        with transaction.atomic():
            booking = get_object_or_404(
                Booking.objects.select_for_update(),
                reservation_number=kwargs['reservation_number'],
            )
            current = booking.booking_status
            if target not in allowed_map.get(current, set()):
                return JsonResponse({
                    'error': 'This booking status transition is not allowed.',
                    'current_status': current,
                    'target_status': target,
                }, status=409)
            booking.booking_status = target
            booking.save(update_fields=['booking_status'])
        return JsonResponse({'reservationNumber': booking.reservation_number, 'status': booking.booking_status})
