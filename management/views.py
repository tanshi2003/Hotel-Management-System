import json

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction

from room_booking.models import Booking


# Staff transitions are intentionally forward-only. Receptionists can operate
# the day-to-day lifecycle; only managers/admins can mark a booking abandoned.
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
        context = {
            'title': 'Management',
            'active_nav_item': 'nav-management',
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
        try:
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
        except Exception:
            raise
        return JsonResponse({'reservationNumber': booking.reservation_number, 'status': booking.booking_status})


