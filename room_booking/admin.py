from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError

from room_booking.models import Booking, WishList, BookingHistory
from room_booking.lifecycle import transitions_for_role, can_transition


# Keep Django admin edits aligned with the staff booking lifecycle endpoint.
ADMIN_TRANSITIONS = transitions_for_role('admin')


class BookingAdminForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = '__all__'

    def clean_booking_status(self):
        target = self.cleaned_data['booking_status']
        if not self.instance.pk:
            if target != 'requested':
                raise ValidationError('New bookings must start in requested status.')
            return target
        current = Booking.objects.get(pk=self.instance.pk).booking_status
        if target != current and not can_transition(current, target, 'admin'):
            raise ValidationError(f'Invalid booking status transition: {current} → {target}.')
        return target


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    form = BookingAdminForm
    list_display = ('reservation_number', 'person', 'booking_status')
    list_filter = ('booking_status',)
    search_fields = ('reservation_number', 'person__name', 'person__email')


admin.site.register(WishList)
admin.site.register(BookingHistory)
