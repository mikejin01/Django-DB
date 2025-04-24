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

'''
# Client model with default values
class Client(models.Model):
    name = models.CharField(max_length=100, default='Unknown')  # Default to 'Unknown'
    phone = models.CharField(max_length=20, default='')  # Default to empty string
    email = models.EmailField(max_length=100, default='')  # Default to empty string
    
    def __str__(self):
        return self.name

# Service model with default values
class Service(models.Model):
    name = models.CharField(max_length=20, default='Unknown')  # Default to 'Unknown'
    
    def __str__(self):
        return self.name

# Building model with default values
class Building(models.Model):
    address = models.CharField(max_length=100, default='Unknown')  # Default to 'Unknown'
    BBL = models.CharField(max_length=30, default='')  # Default to empty string
    BIN = models.CharField(max_length=30, default='')  # Default to empty string
    number_of_bins = models.IntegerField(default=0)  # Default to 0
    zola_link = models.URLField(blank=True, null=True, default='')  # Default to empty string
    bis_bbl_link = models.URLField(blank=True, null=True, default='')  # Default to empty string
    bis_link = models.URLField(blank=True, null=True, default='')  # Default to empty string
    zola_gfa = models.FloatField(null=True, blank=True, default=0.0)  # Default to 0.0
    number_of_floors = models.IntegerField(null=True, blank=True, default=0)  # Default to 0
    basement_code = models.CharField(max_length=10, default='')  # Default to empty string
    uniformly_adjusted_gfa = models.FloatField(null=True, blank=True, default=0.0)  # Default to 0.0
    adjusted_gfa = models.FloatField(null=True, blank=True, default=0.0)  # Default to 0.0
    services = models.ManyToManyField(Service)  # No default needed for ManyToMany
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=1)  # Default to client ID 1
    
    def __str__(self):
        return self.address

# BuildingCompliance model with default values
class BuildingCompliance(models.Model):
    building = models.OneToOneField(Building, on_delete=models.CASCADE, default=1)  # Default to building ID 1
    ll87_needed_2025 = models.CharField(max_length=10, default='')  # Default to empty string
    ll87_filed = models.CharField(max_length=10, default='')  # Default to empty string
    ll97_schedule = models.CharField(max_length=50, default='')  # Default to empty string
    cbl_ll97_path_2025 = models.CharField(max_length=50, default='')  # Default to empty string
    field_schedule = models.CharField(max_length=50, default='')  # Default to empty string
    ll88_lighting = models.CharField(max_length=10, default='')  # Default to empty string
    ll88_submeter = models.CharField(max_length=10, default='')  # Default to empty string
    ll88_needed = models.CharField(max_length=10, default='')  # Default to empty string
    proof_sent = models.CharField(max_length=10, default='')  # Default to empty string
    request_info_date = models.DateField(null=True, blank=True, default='2000-01-01')  # Default to a date
    invoice_sent = models.DateField(null=True, blank=True, default='2000-01-01')  # Default to a date
    request_share_espm = models.DateField(null=True, blank=True, default='2000-01-01')  # Default to a date
    espm_email = models.EmailField(blank=True, default='')  # Default to empty string
    dob_now_email = models.EmailField(blank=True, default='')  # Default to empty string
    contact_email = models.EmailField(blank=True, default='')  # Default to empty string
    dob_now_transaction_number = models.CharField(max_length=50, default='')  # Default to empty string
    dob_filing_fee_paid = models.DateField(null=True, blank=True, default='2000-01-01')  # Default to a date
    dob_pmt_confirmation = models.CharField(max_length=50, default='')  # Default to empty string
    attestation_received = models.DateField(null=True, blank=True, default='2000-01-01')  # Default to a date
    complete_attestation = models.BooleanField(default=False)  # Default to False
    proof_of_correction = models.CharField(max_length=255, default='')  # Default to empty string
    payment_cleared = models.BooleanField(default=False)  # Default to False
    espm_data_in_beam = models.BooleanField(default=False)  # Default to False
    attestation_file = models.FileField(upload_to='attestations/', null=True, blank=True, default='')  # Default to empty string
    proof_of_correction_file = models.FileField(upload_to='proofs/', null=True, blank=True, default='')  # Default to empty string
    
    def __str__(self):
        return f"Compliance for {self.building.address}"
'''