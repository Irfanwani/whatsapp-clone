from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, dp, name, contact, is_staff=False, is_active=True, is_superuser=False):
        user = self.model(contact=contact, name=name, dp=dp, is_staff=is_staff,
                          is_active=is_active, is_superuser=is_superuser)
        user.save(using=self._db)
        return user

    def create_superuser(self, dp, name, contact):
        user = self.create_user(
            dp=dp, name=name, contact=contact, is_superuser=True, is_staff=True)
        return user


class User(AbstractUser):
    username = None
    password = None
    dp = models.ImageField(upload_to='images/', blank=True)
    name = models.CharField(
        max_length=100, unique=False, null=False, blank=True)
    contact = models.CharField(
        max_length=20, unique=True, null=False, blank=False)

    USERNAME_FIELD = 'contact'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return f"{self.username} with contact {self.contact} added"


class Otp(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.IntegerField()

    def __str__(self):
        return f"{self.otp} "


class Room(models.Model):
    dp = models.ImageField(upload_to='images/', blank=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.CharField(max_length=100, null=False, blank=False)
    user = models.ManyToManyField(User, related_name='users')

    def __str__(self):
        return self.room


class Messages(models.Model):
    message = models.CharField(max_length=10000)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.message
