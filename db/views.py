from django.shortcuts import render, redirect, get_object_or_404
from .models import Building, Client, BuildingCompliance, Service
from django.db.models import Q
import pandas as pd
from django.contrib import messages
import datetime

# Helper function to convert Excel dates to Python dates
def to_date(value):
    """
    Convert various date formats (including Excel serial dates) to Python date objects.
    Returns None for invalid or missing values.
    """
    if pd.isna(value):
        return None
    if isinstance(value, datetime.date):
        return value
    if isinstance(value, datetime.datetime):
        return value.date()
    try:
        return pd.to_datetime(value).date()
    except:
        return None

def import_excel(request):
    """
    Handle the import of Excel data into the Django database.
    Processes Client, Building, BuildingCompliance, and Service models.
    """
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        if not excel_file:
            messages.error(request, 'No file uploaded.')
            return redirect('home')

        try:
            # Read the Excel file into a pandas DataFrame
            df = pd.read_excel(excel_file)
            df.columns = df.columns.str.strip()  # Remove leading/trailing spaces from column names

            # Create or get Service instances
            ll97_service, _ = Service.objects.get_or_create(name='LL97')
            ll88_service, _ = Service.objects.get_or_create(name='LL88')

            # Process each row in the DataFrame
            for index, row in df.iterrows():
                # --- Client ---
                client_name = row['2024 File'] if not pd.isna(row['2024 File']) else 'Unknown'
                email = row['Contact Email'].split(';')[0] if not pd.isna(row['Contact Email']) else ''
                client, _ = Client.objects.get_or_create(
                    name=client_name,
                    defaults={'email': email}
                )

                # --- Building ---
                building = Building.objects.create(
                    address=row['Building Address'] if not pd.isna(row['Building Address']) else 'Unknown',
                    BBL=str(row['BBL']) if not pd.isna(row['BBL']) else '',
                    BIN=str(row['BIN']) if not pd.isna(row['BIN']) else '',
                    number_of_bins=int(row['# BINs']) if not pd.isna(row['# BINs']) else 0,
                    zola_link=row['ZOLA Link'] if not pd.isna(row['ZOLA Link']) else '',
                    bis_bbl_link=row['BIS BBL Link'] if not pd.isna(row['BIS BBL Link']) else '',
                    bis_link=row['BIS Link'] if not pd.isna(row['BIS Link']) else '',
                    zola_gfa=float(row['ZOLA GFA']) if not pd.isna(row['ZOLA GFA']) else 0.0,
                    number_of_floors=int(row['# Floor']) if not pd.isna(row['# Floor']) else 0,
                    basement_code=str(row['Basement Code']) if not pd.isna(row['Basement Code']) else '',
                    uniformly_adjusted_gfa=float(row['Uniformly Adjusted GFA']) if not pd.isna(row['Uniformly Adjusted GFA']) else 0.0,
                    adjusted_gfa=float(row['Adjusted GFA`']) if not pd.isna(row['Adjusted GFA`']) else 0.0,
                    client=client
                )

                # Associate services with the building
                if not pd.isna(row['LL97 Schedule']):
                    building.services.add(ll97_service)
                if row.get('LL88 Needed') == 'Y':
                    building.services.add(ll88_service)

                # --- BuildingCompliance ---
                BuildingCompliance.objects.create(
                    building=building,
                    ll87_needed_2025=row['LL87 Needed-2025'] if not pd.isna(row['LL87 Needed-2025']) else '',
                    ll87_filed=row['LL87 Filed'] if not pd.isna(row['LL87 Filed']) else '',
                    ll97_schedule=row['LL97 Schedule'] if not pd.isna(row['LL97 Schedule']) else '',
                    cbl_ll97_path_2025=row['CBL LL97 Path 2025'] if not pd.isna(row['CBL LL97 Path 2025']) else '',
                    field_schedule=row['Field Schedule (04/16/2025)'] if not pd.isna(row['Field Schedule (04/16/2025)']) else '',
                    ll88_lighting=row['LL88 Lighting'] if not pd.isna(row['LL88 Lighting']) else '',
                    ll88_submeter=row['LL88 Submeter'] if not pd.isna(row['LL88 Submeter']) else '',
                    ll88_needed=row['LL88 Needed'] if not pd.isna(row['LL88 Needed']) else '',
                    proof_sent=row['proof sent'] if not pd.isna(row['proof sent']) else '',
                    request_info_date=to_date(row['Request Info. Date']),
                    invoice_sent=to_date(row['Invoice sent']),
                    request_share_espm=to_date(row['Request Share ESPM']),
                    espm_email=row['ESPM Email'] if not pd.isna(row['ESPM Email']) else '',
                    dob_now_email=row['DOB NOW Email'] if not pd.isna(row['DOB NOW Email']) else '',
                    contact_email=row['Contact Email'] if not pd.isna(row['Contact Email']) else '',
                    dob_now_transaction_number=row['DOB NOW Transaction #'] if not pd.isna(row['DOB NOW Transaction #']) else '',
                    dob_filing_fee_paid=to_date(row['DOB Filing Fee Paid']),
                    dob_pmt_confirmation=row['DOB PMT Confirmation#'] if not pd.isna(row['DOB PMT Confirmation#']) else '',
                    attestation_received=to_date(row['Attestation Received']),
                    complete_attestation=True if row.get('Complete Attestation') == 'Y' else False,
                    proof_of_correction=row['Proof of Correction'] if not pd.isna(row['Proof of Correction']) else '',
                    payment_cleared=True if row.get('Payment cleared') == 'Cleared' else False,
                    espm_data_in_beam=True if row.get('ESPM Data in BEAM') == 'Y' else False,
                    # Note: File fields (attestation_file, proof_of_correction_file) are not handled here;
                    #       paths are stored as strings, handle file uploads separately if needed
                )

            messages.success(request, 'Import successful!')
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
        return redirect('home')
    return render(request, 'home.html')

def building_compliance_detail(request, building_id):
    # Fetch the building object with its related data
    building = get_object_or_404(Building, id=building_id)
    return render(request, 'building_detail.html', {'building': building})

def home(request):
    query = request.GET.get('q')
    tab = request.GET.get('tab', 'buildings')  # default to buildings

    buildings = Building.objects.prefetch_related('services', 'client').all()
    clients = Client.objects.all()

    if query:
        # Always filter buildings by BBL (no matter which tab is selected)
        buildings = buildings.filter(
            Q(address__icontains=query) |
            Q(BIN__icontains=query) |
            Q(BBL__icontains=query) |
            Q(client__name__icontains=query)  # Updated to use the 'name' field
        )

        # Only filter clients if the tab is 'clients'
        if tab == 'clients':
            clients = clients.filter(
                Q(name__icontains=query) |  # Use 'name' instead of 'first_name' or 'last_name'
                Q(phone__icontains=query) |
                Q(email__icontains=query)
            )

    return render(request, 'home.html', {
        'tab': tab,
        'query': query,
        'buildings': buildings,
        'clients': clients
    })