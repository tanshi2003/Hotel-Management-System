from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms

from user_profile.models import Account, Person, Address


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = Account
        fields = ('email',)


class CustomUserChangeForm(UserChangeForm):

    class Meta:
        model = Account
        fields = ('email',)


class PersonForm(forms.ModelForm):
    # password = forms.CharField(max_length=12, widget=forms.PasswordInput())
    class Meta:
        model = Person
        fields = ['name', 'email']

class PersonForm2(forms.ModelForm):
    # password = forms.CharField(max_length=12, widget=forms.PasswordInput())
    class Meta:
        model = Person
        fields = "__all__"


class AccountForm(forms.ModelForm):
    # email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    class Meta:
        model = Account
        fields = ['password']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['person']
        

class ProfileForm(forms.Form):
    name = forms.CharField(max_length=64)
    email = forms.EmailField()
    phone = forms.CharField(max_length=16)
    account_type = forms.CharField(max_length=20, disabled=True)
    city = forms.CharField(max_length=50)
    country = forms.CharField(max_length=50)
    zip_code = forms.IntegerField()