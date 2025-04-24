from django.contrib import admin
from .models import Client, Service, Building, BuildingTracking

# Register your models here.
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(BuildingTracking)
admin.site.register(Building)