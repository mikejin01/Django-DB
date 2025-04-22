from django.contrib import admin
from .models import Client, Service, Building

# Register your models here.
admin.site.register(Client)
admin.site.register(Service)
admin.site.register(Building)