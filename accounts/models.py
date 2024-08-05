from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class CustomUser(AbstractUser):
    convoyName = models.CharField(max_length=50, blank=False)  # name caravan
    phoneNumber = models.CharField(max_length=11, blank=False)
    profilePicture = models.ImageField(upload_to='profiles/', null=True, blank=True)
    email = models.EmailField(unique=True)

    USERNAME_FIELDS = ['email', 'username']
    REQUIRED_FIELDS = ['convoyName', 'phoneNumber']

