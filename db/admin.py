from django.contrib import admin
from .models import Customer, Service, Building

# Register your models here.
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(Building)