from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = email.strip().lower()
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault("is_admin", True)
        other_fields.setdefault("is_manager", True)
        other_fields.setdefault("is_receptionist", True)
        other_fields.setdefault("is_guest", True)
        other_fields.setdefault("is_staff", True)
        other_fields.setdefault("is_active", True)
        other_fields.setdefault('is_superuser', True)
        for flag in ('is_admin', 'is_manager', 'is_receptionist', 'is_guest', 'is_staff'):
            if other_fields.get(flag) is not True:
                raise ValueError(_(f'Admin must have {flag}=True.'))
        return self.create_user(email, password, **other_fields)
