from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import datetime

class User(AbstractUser):
    # Inherits all the following fields by default:

    # username = models.CharField(max_length=150, unique=True)
    # first_name = models.CharField(max_length=150, blank=True)
    # last_name = models.CharField(max_length=150, blank=True)
    # email = models.EmailField(blank=True)

    # is_staff = models.BooleanField(default=False)
    # is_active = models.BooleanField(default=True)
    # is_superuser = models.BooleanField(default=False)
    # groups = models.ManyToManyField(Group, related_name='user_set', blank=True)
    # user_permissions = models.ManyToManyField(Permission, related_name='user_set', blank=True)

    # last_login = models.DateTimeField(blank=True, null=True)
    # date_joined = models.DateTimeField(default=timezone.now)

    # password = models.CharField(max_length=128)
    pass

# Client model with default values
class Client(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='client')
    primary_email = models.CharField(max_length=255, default='', blank=True)  # One main email
    outlook_folder_link = models.URLField(blank=True, null=True)
    contacts = models.JSONField(default=list, blank=True)           # List of clients: name, phone, email, comment

    comment = models.TextField(blank=True, default='')                # Rich text comment
    additional_data = models.JSONField(blank=True, default=dict)     # Freeform structured data

    def __str__(self):
        return self.user.username

# Service model with default values
class Service(models.Model):
    name = models.CharField(max_length=20, default='')
    price = models.CharField(max_length=100, blank=True, null=True)

    comment = models.TextField(blank=True, default='')                # Rich text comment
    additional_data = models.JSONField(blank=True, default=dict)     # Freeform structured data
    def __str__(self):
        return self.name

# Building model with default values
class Lot(models.Model):
    bbl = models.CharField(max_length=20, default='', blank=True)  # e.g. 1012345678
    zipcode = models.CharField(max_length=10, default='', blank=True)  # Zipcode, stored as string
    primary_address = models.CharField(max_length=255, default='', blank=True)  # One main address
    buildings = models.JSONField(default=list, blank=True)        # List of buildings: address, BIN, comment.

    client = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, blank=True)

    open_violations = models.TextField(blank=True, default='')     # Optional text summary
    owner_name = models.CharField(max_length=100, default='', blank=True)
    owner_email = models.EmailField(blank=True, null=True)         # DOB Now email
    espm_email = models.EmailField(blank=True, null=True)

    comment = models.TextField(blank=True, default='')                # Rich text comment
    additional_data = models.JSONField(blank=True, default=dict)     # Freeform structured data

    def __str__(self):
        return self.primary_address.get("address", "(No Address)") if isinstance(self.primary_address, dict) else "(No Address)"

# BuildingCompliance model with default values
class ServiceOnLot(models.Model):
    lot = models.ForeignKey("Lot", on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey("Service", on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, blank=True, default='')
    year = models.CharField(max_length=10, blank=True, default='')  # Compliance year (optional)
    deadline = models.BooleanField(null=True, blank=True)     # Can be True, False, or unset

    comment = models.TextField(blank=True, default='')                # Rich text comment
    additional_data = models.JSONField(blank=True, default=dict)     # Freeform structured data

    def __str__(self):
        if self.lot and self.service:
            return f"{self.service.name} for {self.lot.primary_address}"
        return "(Incomplete record)"

class ValidationRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    datetime = models.DateTimeField(auto_now_add=True)

    table = models.CharField(max_length=100, blank=True, default='')      # e.g., "Client", "Lot"
    record = models.CharField(max_length=100, blank=True, default='')
    field = models.CharField(max_length=100, blank=True, default='')      # e.g., "email", "bbl"

    old = models.TextField(blank=True, default='')                   # Raw text or serialized JSON string
    new = models.TextField(blank=True, default='')

    action = models.CharField(max_length=20, blank=True, default='')
    status = models.CharField(max_length=20, blank=True, default='')

    comment = models.TextField(blank=True, default='')                    # Rich text comment
    additional_data = models.JSONField(blank=True, default=dict)          # Structured or raw data

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} on {self.field or 'unknown field'}"