from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

# Your model definitions go here


from user_profile.managers import CustomUserManager


class Person(models.Model):
    ACCOUNT_TYPES = (
        ('admin','Admin'),
        ( 'manager', 'Manager'),
        ( 'receptionist' ,'Receptionist'),
        ( 'guest' ,'Guest'),
        ( 'staff','staff')
    )
    
    name = models.CharField(max_length=64)
    email = models.EmailField(unique=True, blank=True)
    phone = models.CharField(max_length=16)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)

    def __str__(self) -> str:
        return self.name


class Address(models.Model):
    city = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    zip_code = models.IntegerField()
    person = models.OneToOneField(Person, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.person.name}, {self.city}, {self.country}"


class Account(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_("email address"), unique=True, blank=True)
    is_admin = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_receptionist = models.BooleanField(default=False)
    is_guest = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    person = models.OneToOneField(Person, on_delete=models.CASCADE, null=True, blank=True)
    new_field = models.CharField(max_length=140, default='SOME STRING')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self) -> str:
        return self.email

