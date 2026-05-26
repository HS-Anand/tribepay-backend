from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid


class User(AbstractUser):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    phone_number = models.CharField(max_length=15, unique=True)