from datetime import date, timezone
import datetime
from django.db import models
from django.contrib.auth import get_user_model

from user_profile.models import Person
from hotel_room.models import Room

# Create your models here.
class Booking(models.Model):
    BOOKING_STATUS = (
        ("requested", "Requested"),
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("checked-in", "Checked-in"),
        ("checked-out", "Checked-out"),
        ("canceled", "Canceled"),
        ("abandoned", "Abandoned"),
    )
    reservation_number = models.CharField(max_length=20, unique=True)
    rooms = models.ManyToManyField(Room, related_name='rooms')
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    booking_status = models.CharField(max_length=50, choices=BOOKING_STATUS)


    def __str__(self) -> str:
        return self.reservation_number

class BookingHistory(models.Model):
    reservation_number = models.ForeignKey(Booking, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True)
    check_in = models.DateField(default=datetime.date.today(), blank=True, null=True)
    check_out = models.DateField(default=datetime.date.today(), blank=True, null=True)
    room_cleaning = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    breakfast = models.BooleanField(default=False)
    total_price = models.FloatField(default=0)
    new_field = models.CharField(max_length=140, default='SOME STRING')

    def __str__(self):
        return f"{self.reservation_number}-{self.room.room_number}"


class WishList(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='person')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='room')
    check_in = models.DateField(default=datetime.date.today(), blank=True, null=True)
    check_out = models.DateField(default=datetime.date.today(), blank=True, null=True)
    room_cleaning = models.BooleanField(default=False)
    laundry = models.BooleanField(default=False)
    breakfast = models.BooleanField(default=False)
    total_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.room.room_number} {self.room.style}"



