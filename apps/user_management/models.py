from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator
import random
import string


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password=password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=30, unique=True)
    profile = models.CharField(max_length=255, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/%Y/%m/%d/', null=True, blank=True)
    region = models.CharField(max_length=30, null=True, blank=True)
    region_detail = models.CharField(max_length=30, null=True, blank=True)
    username = models.CharField(max_length=30, unique=False, null=True, blank=True)
    fuel = models.FloatField(null=True, blank=True, default=0, validators=[MinValueValidator(0)],)
    new = models.BooleanField(default=True)
    coin = models.PositiveIntegerField(default=5000)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return self.is_superuser

    def get_group_permissions(self, obj=None):
        return set()

    def get_all_permissions(self, obj=None):
        return set()

    class Meta:
        db_table = "User"

    def save(self, *args, **kwargs):
        if not self.nickname:
            self.nickname = self.generate_random_nickname()
        super().save(*args, **kwargs)

    def generate_random_nickname(self):
        return ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
