import importlib
from re import A
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Account, Address, Person
from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = Account
    list_display = ('email','is_admin', 'is_manager', 'is_receptionist', 'is_guest', 'is_staff', 'is_active',)
    list_filter = ('email','is_admin', 'is_manager', 'is_receptionist', 'is_guest', 'is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('is_admin', 'is_manager', 'is_receptionist', 'is_guest', 'is_staff', 'is_active', 'groups')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_admin', 'is_manager', 'is_receptionist', 'is_guest', 'is_staff', 'is_active')}
        ),
    )
    search_fields = ('email',)
    ordering = ('email',)


# Register your models here.
admin.site.register(Account, CustomUserAdmin)
admin.site.register(Address)
admin.site.register(Person)