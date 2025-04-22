from django.db import models
import datetime


# Create your models here.

class Client(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=100)
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

class Service(models.Model):
    name = models.CharField(max_length=20)
    def __str__(self):
        return self.name


# Building model updated with additional fields from the Excel file
class Building(models.Model):
    address = models.CharField(max_length=100)
    BBL = models.CharField(max_length=30, default='', blank=True)  # Borough-Block-Lot number
    BIN = models.CharField(max_length=30, default='', blank=True)  # Building Identification Number
    number_of_bins = models.IntegerField(default=1, blank=True)  # Number of BINs associated with the BBL
    zola_link = models.URLField(blank=True, null=True)  # ZOLA link for zoning info
    bis_bbl_link = models.URLField(blank=True, null=True)  # BIS BBL link
    bis_link = models.URLField(blank=True, null=True)  # BIS BIN link
    zola_gfa = models.FloatField(null=True, blank=True)  # Gross Floor Area from ZOLA
    number_of_floors = models.IntegerField(null=True, blank=True)  # Number of floors
    basement_code = models.CharField(max_length=10, blank=True)  # Basement code
    uniformly_adjusted_gfa = models.FloatField(null=True, blank=True)  # Uniformly adjusted GFA
    adjusted_gfa = models.FloatField(null=True, blank=True)  # Adjusted GFA
    services = models.ManyToManyField(Service)  # Retained for potential other services
    client = models.ForeignKey(Client, on_delete=models.CASCADE)  # Corrected from Customer to Client
    
    def __str__(self):
        return self.address

# New model to store compliance-related data from the Excel file
class BuildingCompliance(models.Model):
    building = models.OneToOneField(Building, on_delete=models.CASCADE)  # One compliance record per building
    ll87_needed_2025 = models.CharField(max_length=10, blank=True)  # e.g., "-", "Y"
    ll87_filed = models.CharField(max_length=10, blank=True)  # e.g., "", "45547"
    ll97_schedule = models.CharField(max_length=50, blank=True)  # e.g., "Need Challenge", "321 Pass"
    cbl_ll97_path_2025 = models.CharField(max_length=50, blank=True)  # e.g., "321", "320"
    field_schedule = models.CharField(max_length=50, blank=True)  # e.g., "321", "320"
    ll88_lighting = models.CharField(max_length=10, blank=True)  # e.g., ""
    ll88_submeter = models.CharField(max_length=10, blank=True)  # e.g., ""
    ll88_needed = models.CharField(max_length=10, blank=True)  # e.g., "Y"
    proof_sent = models.CharField(max_length=10, blank=True)  # e.g., ""
    request_info_date = models.DateField(null=True, blank=True)  # Date requested info
    invoice_sent = models.DateField(null=True, blank=True)  # Date invoice sent
    request_share_espm = models.DateField(null=True, blank=True)  # Date ESPM share requested
    espm_email = models.EmailField(blank=True)  # ESPM contact email
    dob_now_email = models.EmailField(blank=True)  # DOB NOW contact email
    contact_email = models.EmailField(blank=True)  # General contact email
    dob_now_transaction_number = models.CharField(max_length=50, blank=True)  # e.g., "LL97000002894"
    dob_filing_fee_paid = models.DateField(null=True, blank=True)  # Date filing fee paid
    dob_pmt_confirmation = models.CharField(max_length=50, blank=True)  # e.g., "97320S000002894"
    attestation_received = models.DateField(null=True, blank=True)  # Date attestation received
    complete_attestation = models.BooleanField(default=False)  # e.g., "Y" or blank
    proof_of_correction = models.CharField(max_length=255, blank=True)  # e.g., "Y" or text
    payment_cleared = models.BooleanField(default=False)  # e.g., "Cleared" or blank
    espm_data_in_beam = models.BooleanField(default=False)  # e.g., "Y" or "N"
    attestation_file = models.FileField(upload_to='attestations/', null=True, blank=True)  # Path to attestation file
    proof_of_correction_file = models.FileField(upload_to='proofs/', null=True, blank=True)  # Path to proof file
    
    def __str__(self):
        return f"Compliance for {self.building.address}"






