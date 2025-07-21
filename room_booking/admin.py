from django.contrib import admin

from room_booking.models import Booking, WishList, BookingHistory


# Register your models here.
admin.site.register(Booking)
admin.site.register(WishList)
admin.site.register(BookingHistory)