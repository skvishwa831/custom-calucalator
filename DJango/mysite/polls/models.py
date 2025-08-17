from django.utils import timezone
from django.db import models
# accounts/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class Contact(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=10)
    matka_number = models.IntegerField()
    amount = models.FloatField()
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name



class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    current_token_jti = models.CharField(max_length=255, blank=True, null=True)


    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email
    
    
class CustomerNames(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
from django.db import models

class GamesTypes(models.Model):
    gameName = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.gameName

class GameRecords(models.Model):
    name = models.CharField(max_length=255)
    gameName = models.CharField(max_length=255)
    content = models.TextField()  # Suitable for large text

    def __str__(self):
        return f"{self.name} - {self.gameName}"

class GameDashBoard(models.Model):
    name = models.CharField(max_length=255)
    totalAmount = models.FloatField()
    date = models.DateField()  # Accepts only date (e.g., 17/08/2025)

    def __str__(self):
        return f"{self.name} - {self.date}"
