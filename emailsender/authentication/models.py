from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        return self.create_user(email, password, **extra_fields)

class Users(AbstractBaseUser, PermissionsMixin):
    email       = models.EmailField(unique=True,blank=True, null=True)
    username    = models.CharField(max_length=150, null=True, blank=True)
    first_name  = models.CharField(max_length=30,blank=True, null=True)
    last_name   = models.CharField(max_length=30,blank=True, null=True)
    phone       = models.CharField(max_length=15, unique=True, null=True, blank=True)
    is_active   = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)
    is_staff    = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    objects     = CustomUserManager()

    USERNAME_FIELD = "email"  # Login via email
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email
