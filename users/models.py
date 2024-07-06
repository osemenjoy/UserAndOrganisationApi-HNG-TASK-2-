from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class CustomUser(AbstractUser):
    userId = models.CharField(max_length=50, unique=True, null=False, default=uuid.uuid4 )
    firstName = models.CharField(max_length=50, null=False)
    lastName = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=50, unique=True, null=False)
    phone = models.CharField(max_length=20)

class Organisation(models.Model):
    orgId = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True)
    users = models.ManyToManyField(CustomUser, related_name='organisations')

    def __str__(self):
        return self.name