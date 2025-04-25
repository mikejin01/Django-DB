from django.db import models
import datetime


class Client(models.Model):
    name = models.CharField(max_length=100, default='Unknown')
    phone = models.CharField(max_length=20, default='', blank=True)  # Optional
    email = models.EmailField(max_length=100, default='', blank=True)  # Optional
    contact_info = models.CharField(max_length=100, default='', blank=True)  # Optional
    
    def __str__(self):
        return self.name


class Service(models.Model):
    name = models.CharField(max_length=20, unique=True)  # Unique service names
    
    def __str__(self):
        return self.name


class Building(models.Model):
    address = models.CharField(max_length=100, default='Unknown')
    borough = models.CharField(max_length=20, default='Unknown')
    BBL = models.CharField(max_length=30, default='', blank=True)
    BIN = models.CharField(max_length=30, default='', blank=True)
    number_of_bins = models.IntegerField(default=0)
    services = models.ManyToManyField(Service, related_name='buildings')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)  # Allow null
    
    def __str__(self):
        return self.address


class BuildingTracking(models.Model):
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='trackings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='trackings')
    tracking_info = models.CharField(max_length=500, default='Unknown')
    last_updated = models.DateTimeField(auto_now=True)  # Track updates

    # LL84 Fields
    LL84_Price = models.CharField(max_length=100, default='Unknown')
    LL84_2020_Filed = models.BooleanField(default=False)
    LL84_2021PMT = models.CharField(max_length=100, default='Unknown')
    LL84_2022_Score_to_customer = models.BooleanField(default=False)
    LL84_2023_Invoice_sent = models.BooleanField(default=False)
    LL84_2023_PMT = models.BooleanField(default=False)
    LL84_Submission = models.BooleanField(default=False)
    LL84_23_Grading = models.BooleanField(default=False)
    LL84_24_Outreach = models.BooleanField(default=False)
    LL84_2024_PMT = models.BooleanField(default=False)
    LL84_24_Submission = models.BooleanField(default=False)
    LL84_2024_Score = models.CharField(max_length=100, default='Unknown')
    LL84_water_benchmark = models.BooleanField(default=False)
    LL84_2025_Paid = models.BooleanField(default=False)
    LL84_2025_submission = models.CharField(max_length=100, default='Unknown')
    LL84_Confirmation_Email = models.CharField(max_length=100, default='Unknown')
    LL84_Show_data_in_BEAM = models.CharField(max_length=100, default='Unknown')

    class Meta:
        unique_together = ('building', 'service')  # One tracking record per building-service pair
        indexes = [
            models.Index(fields=['building']),
            models.Index(fields=['service']),
        ]
    
    def __str__(self):
        return f"{self.service.name} tracking for {self.building.address}"

