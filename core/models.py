from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.


class User(AbstractUser):
    email = models.EmailField(unique=True)

    class Meta:
        permissions = [
            ("cancel_order", "Can cancel order")
        ]
