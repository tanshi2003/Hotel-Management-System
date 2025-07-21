from django.db import models


# Create your models here.
class Hotel(models.Model):
    name: models.CharField = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.name


class Room(models.Model):
    ROOM_STYLE = (
        ('standard', 'Standard'),
        ("delux", "Delux"),
        ("family", "Family Suite"),
        ("business", "Business Suite")
    )

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, unique=True)
    style = models.CharField(max_length=20, choices=ROOM_STYLE)
    booking_price = models.IntegerField()
    is_smoking = models.BooleanField(default=False)
    is_wifi = models.BooleanField(default=False)
    is_ac = models.BooleanField(default=False)
    is_balcony = models.BooleanField(default=False)
    is_tv = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f"{self.room_number} {self.style}"
    




    