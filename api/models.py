from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Create your models here.


class User(AbstractUser):
    tokens = models.IntegerField(default=5)
    bypass_token_limit = models.BooleanField(default=False)
    email = models.EmailField(max_length=254)
    whop_user_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    whop_username = models.CharField(max_length=150, null=True, blank=True)

class IcsFile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to="ical/")
    created_at = models.DateTimeField(auto_now_add=True)

class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_payment_id = models.CharField(max_length=64, null=True, blank=True)
    last_paid_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=False)