from django import forms

from room_booking.models import WishList


class WishListForm(forms.ModelForm):
    class Meta:
        model = WishList
        exclude = ['']


