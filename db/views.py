from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from django.http import JsonResponse
from .models import Client, Service, Building, BuildingTracking
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import logging
import openpyxl
import tempfile
from openpyxl.utils import get_column_letter
import os

# Helper function to convert Excel dates to Python dates
def to_date(value):
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

# Check if the user is the admin (username == 'admin')
def is_admin_user(user):
    return user.is_authenticated and user.username == 'admin'

@login_required
def building_detail(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    context = {
        'building': building,
        'services': building.services.all(),
        'client': building.client,
        'trackings': building.trackings.all()
    }
    return render(request, 'building_detail.html', context)

@login_required
def home(request):
    query = request.GET.get('q')
    tab = request.GET.get('tab', 'buildings')

    buildings = Building.objects.prefetch_related('services', 'client').all()
    clients = Client.objects.all()

    if query:
        buildings = buildings.filter(
            Q(address__icontains=query) |
            Q(BBL__icontains=query) |
            Q(BIN__icontains=query) |
            Q(client__name__icontains=query)
        )

        if tab == 'clients':
            clients = clients.filter(
                Q(name__icontains=query) |
                Q(phone__icontains=query) |
                Q(email__icontains=query)
            )

    return render(request, 'home.html', {
        'tab': tab,
        'query': query,
        'buildings': buildings,
        'clients': clients
    })

# Configure logger for this module
logger = logging.getLogger(__name__)

def reformat_excel_merged_cells(input_file_stream, output_file_path, sheet_name="LL84- Benchmarking"):
    wb = openpyxl.load_workbook(input_file_stream)
    if sheet_name not in wb.sheetnames:
        raise ValueError(f"Sheet '{sheet_name}' not found in the workbook")
    ws = wb[sheet_name]
    merged_ranges = list(ws.merged_cells.ranges)
    for merged_range in merged_ranges:
        top_left_cell = ws.cell(row=merged_range.min_row, column=merged_range.min_col)
        value = top_left_cell.value
        ws.unmerge_cells(start_row=merged_range.min_row,
                         start_column=merged_range.min_col,
                         end_row=merged_range.max_row,
                         end_column=merged_range.max_col)
        for row in range(merged_range.min_row, merged_range.max_row + 1):
            for col in range(merged_range.min_col, merged_range.max_col + 1):
                ws.cell(row=row, column=col).value = value
    wb.save(output_file_path)
    print(f"Reformatted Excel file saved as '{output_file_path}'")

def process_ll84_benchmarking(excel_data):
    if not isinstance(excel_data, pd.ExcelFile):
        raise ValueError("Expected a pandas ExcelFile object")
    if 'LL84- Benchmarking' not in excel_data.sheet_names:
        raise ValueError("Excel file does not contain 'LL84- Benchmarking' tab")
    df = pd.read_excel(excel_data, sheet_name='LL84- Benchmarking')
    df.columns = df.columns.str.strip()
    ll84_service, _ = Service.objects.get_or_create(name='LL84')
    for index, row in df.iterrows():
        building_address = row['Building'] if not pd.isna(row['Building']) else 'Unknown'
        if building_address.lower() == 'archive buildings below:':
            print("Stopping processing: 'Archive Buildings Below:' found")
            break
        customer = row['Customer'] if not pd.isna(row['Customer']) else 'Unknown'
        contact = row['Contact'] if not pd.isna(row['Contact']) else ''
        client, _ = Client.objects.get_or_create(
            name=customer,
            defaults={
                'contact_info': contact,
                'phone': '',
                'email': ''
            }
        )
        block = str(row['Block']) if not pd.isna(row['Block']) else ''
        building_obj = Building.objects.create(
            address=building_address,
            borough='Unknown',
            BBL=block,
            BIN='',
            number_of_bins=0,
            client=client
        )
        building_obj.services.add(ll84_service)
        tracking_data = {}
        for col in df.columns:
            if col not in ['Building Address', '2024 File', 'Contact']:
                value = row[col]
                tracking_data[col] = str(value) if not pd.isna(value) else 'Unknown'
        BuildingTracking.objects.get_or_create(
            building=building_obj,
            service=ll84_service,
            defaults={
                'tracking_info': json.dumps(tracking_data, ensure_ascii=False),
            }
        )

def import_excel(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')
        sheet_type = request.POST.get('sheet_type')
        if not excel_file:
            messages.error(request, 'No file uploaded.')
            return redirect('home')
        if not sheet_type:
            messages.error(request, 'Please select a sheet type.')
            return redirect('home')
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                for chunk in excel_file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            if sheet_type == 'LL84-Benchmarking':
                reformatted_file_path = temp_file_path.replace('.xlsx', '_reformatted.xlsx')
                reformat_excel_merged_cells(temp_file_path, reformatted_file_path)
                excel_data = pd.ExcelFile(reformatted_file_path)
            else:
                excel_data = pd.ExcelFile(temp_file_path)
            if sheet_type == 'LL84-Benchmarking':
                process_ll84_benchmarking(excel_data)
            elif sheet_type == 'LL97':
                df = pd.read_excel(excel_data, sheet_name='LL97')
                df.columns = df.columns.str.strip()
                service_name = 'LL97'
                service_field = 'LL97-321'
                client_name_field = '2024 File'
                address_field = 'Building Address'
                contact_field = 'Contact'
                service, _ = Service.objects.get_or_create(name=service_name)
                for index, row in df.iterrows():
                    client_name = row[client_name_field] if not pd.isna(row[client_name_field]) else 'Unknown'
                    email = row.get(contact_field, '').split(';')[0] if not pd.isna(row.get(contact_field, '')) else ''
                    client, _ = Client.objects.get_or_create(
                        name=client_name,
                        defaults={'email': email}
                    )
                    building = Building.objects.create(
                        address=row[address_field] if not pd.isna(row[address_field]) else 'Unknown',
                        borough='Unknown',
                        BBL=str(row['BBL']) if 'BBL' in row and not pd.isna(row['BBL']) else '',
                        BIN=str(row['BIN']) if 'BIN' in row and not pd.isna(row['BIN']) else '',
                        number_of_bins=int(row['# BINs']) if '# BINs' in row and not pd.isna(row['# BINs']) else 0,
                        client=client
                    )
                    if not pd.isna(row.get(service_field)):
                        building.services.add(service)
            else:
                messages.error(request, 'Invalid sheet type selected.')
                return redirect('home')
            messages.success(request, f'Imported data from {sheet_type} successfully!')
        except Exception as e:
            messages.error(request, f'Error importing file: {str(e)}')
        finally:
            if 'temp_file_path' in locals():
                try:
                    os.remove(temp_file_path)
                except:
                    pass
            if 'reformatted_file_path' in locals():
                try:
                    os.remove(reformatted_file_path)
                except:
                    pass
        return redirect('home')
    return render(request, 'home.html')

@login_required
def preview_gsheet(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sheet_id = data.get('sheet_id')
        if not sheet_id:
            return JsonResponse({'error': 'Please provide a valid Google Sheet ID.'}, status=400)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/sfe-import-credentials.json', scope)
        client = gspread.authorize(creds)
        try:
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            return JsonResponse({'sheet_id': sheet_id, 'preview': data}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def import_gsheet(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        sheet_id = data.get('sheet_id')
        if not sheet_id:
            return JsonResponse({'error': 'Please provide a valid Google Sheet ID.'}, status=400)
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('credentials/sfe-import-credentials.json', scope)
        client = gspread.authorize(creds)
        try:
            sheet = client.open_by_key(sheet_id).sheet1
            data = sheet.get_all_records()
            ll97_service, _ = Service.objects.get_or_create(name='LL97')
            ll88_service, _ = Service.objects.get_or_create(name='LL88')
            for row in data:
                client_name = row.get('2024 File', 'Unknown')
                email = row.get('Contact Email', '').split(';')[0]
                client, _ = Client.objects.get_or_create(
                    name=client_name,
                    defaults={'email': email}
                )
                building = Building.objects.create(
                    address=row.get('Building Address', 'Unknown'),
                    borough='Unknown',
                    BBL=str(row.get('BBL', '')),
                    BIN=str(row.get('BIN', '')),
                    number_of_bins=int(row.get('# BINs', 0)),
                    client=client
                )
                if row.get('LL97 Schedule'):
                    building.services.add(ll97_service)
                if row.get('LL88 Needed') == 'Y':
                    building.services.add(ll88_service)
            return JsonResponse({'message': 'Data imported successfully.'}, status=200)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=405)

@login_required
def delete_all_data(request):
    if request.method == 'POST':
        try:
            Building.objects.all().delete()
            Client.objects.all().delete()
            Service.objects.all().delete()
            messages.success(request, "All buildings, clients, and services have been deleted successfully.")
        except Exception as e:
            messages.error(request, f"An error occurred while deleting data: {str(e)}")
        return redirect(reverse('home') + '?tab=buildings')
    return redirect('home')

@login_required
def building_compliance_detail(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    return render(request, 'building_detail.html', {'building': building})

@login_required
def client_detail(request, client_id):
    client = get_object_or_404(Client, id=client_id)
    buildings = Building.objects.filter(client=client)
    return render(request, 'client_detail.html', {'client': client, 'buildings': buildings})

# New admin view restricted to username 'admin'
def is_admin_user(user):
    return user.is_authenticated and user.username == 'admin'

# ... (other views remain unchanged)

@login_required
@user_passes_test(is_admin_user)
def admin_view(request):
    buildings = Building.objects.prefetch_related('services', 'client').all()
    building_count = Building.objects.count()
    client_count = Client.objects.count()
    service_count = Service.objects.count()
    tracking_count = BuildingTracking.objects.count()

    context = {
        'buildings': buildings,
        'building_count': building_count,
        'client_count': client_count,
        'service_count': service_count,
        'tracking_count': tracking_count,
    }
    return render(request, 'admin_view.html', context)

@login_required
@user_passes_test(is_admin_user)
def update_tracking(request):
    if request.method == 'POST':
        tracking_id = request.POST.get('tracking_id')
        tracking = get_object_or_404(BuildingTracking, id=tracking_id)

        # Update fields
        tracking.LL84_Price = request.POST.get('LL84_Price', tracking.LL84_Price)
        tracking.LL84_2020_Filed = request.POST.get('LL84_2020_Filed') == 'Yes'
        tracking.LL84_2021PMT = request.POST.get('LL84_2021PMT', tracking.LL84_2021PMT)
        tracking.LL84_2022_Score_to_customer = request.POST.get('LL84_2022_Score_to_customer') == 'Yes'
        tracking.LL84_2023_Invoice_sent = request.POST.get('LL84_2023_Invoice_sent') == 'Yes'
        tracking.LL84_2023_PMT = request.POST.get('LL84_2023_PMT') == 'Yes'
        tracking.LL84_Submission = request.POST.get('LL84_Submission') == 'Yes'
        tracking.LL84_23_Grading = request.POST.get('LL84_23_Grading') == 'Yes'
        tracking.LL84_24_Outreach = request.POST.get('LL84_24_Outreach') == 'Yes'
        tracking.LL84_2024_PMT = request.POST.get('LL84_2024_PMT') == 'Yes'
        tracking.LL84_24_Submission = request.POST.get('LL84_24_Submission') == 'Yes'
        tracking.LL84_2024_Score = request.POST.get('LL84_2024_Score', tracking.LL84_2024_Score)
        tracking.LL84_water_benchmark = request.POST.get('LL84_water_benchmark') == 'Yes'
        tracking.LL84_2025_Paid = request.POST.get('LL84_2025_Paid') == 'Yes'
        tracking.LL84_2025_submission = request.POST.get('LL84_2025_submission', tracking.LL84_2025_submission)
        tracking.LL84_Confirmation_Email = request.POST.get('LL84_Confirmation_Email', tracking.LL84_Confirmation_Email)
        tracking.LL84_Show_data_in_BEAM = request.POST.get('LL84_Show_data_in_BEAM', tracking.LL84_Show_data_in_BEAM)

        try:
            tracking.save()
            messages.success(request, f'LL84 tracking data for "{tracking.building.address}" updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating tracking data: {str(e)}')

        return redirect('building_detail', building_id=tracking.building.id)

    return redirect('home')

@login_required
@user_passes_test(is_admin_user)
def process_all_buildings(request):
    buildings = Building.objects.all()
    updated_count = 0
    error_count = 0

    # Same field mappings as in building_update_bins
    field_mappings = {
        'Price': ('LL84_Price', lambda x: str(x)),
        '2020 Filed': ('LL84_2020_Filed', lambda x: x.strip().lower() == 'y'),
        '2021PMT': ('LL84_2021PMT', lambda x: str(x)),
        '2022 Score to customer': ('LL84_2022_Score_to_customer', lambda x: x.strip().lower() == 'y'),
        '2023 Invoice sent': ('LL84_2023_Invoice_sent', lambda x: x.strip().lower() == 'y'),
        '2023 PMT': ('LL84_2023_PMT', lambda x: x.strip().lower() == 'y'),
        'Submission': ('LL84_Submission', lambda x: x.strip().lower() == 'y'),
        '23 Grading': ('LL84_23_Grading', lambda x: x.strip().lower() == 'y'),
        '24 Outreach': ('LL84_24_Outreach', lambda x: x.strip().lower() == 'y'),
        '2024 PMT': ('LL84_2024_PMT', lambda x: x.strip().lower() == 'y'),
        '24 Submission': ('LL84_24_Submission', lambda x: x.strip().lower() == 'y'),
        '2024 Score': ('LL84_2024_Score', lambda x: str(x)),
        'water benchmark': ('LL84_water_benchmark', lambda x: x.strip().lower() == 'y'),
        '2025 Paid': ('LL84_2025_Paid', lambda x: x.strip().lower() == 'y'),
        '2025 submission': ('LL84_2025_submission', lambda x: str(x)),
        'Confirmation Email': ('LL84_Confirmation_Email', lambda x: str(x)),
        'Show data in BEAM': ('LL84_Show_data_in_BEAM', lambda x: str(x)),
    }

    for building in buildings:
        try:
            tracking = BuildingTracking.objects.get(building=building, service__name='LL84')
            tracking_info = json.loads(tracking.tracking_info)

            for json_key, (field_name, transform) in field_mappings.items():
                if json_key in tracking_info:
                    setattr(tracking, field_name, transform(tracking_info[json_key]))

            tracking.save()
            updated_count += 1
        except BuildingTracking.DoesNotExist:
            logger.warning(f'No LL84 tracking data found for "{building.address}".')
            error_count += 1
        except json.JSONDecodeError:
            logger.error(f'Invalid tracking_info format for "{building.address}".')
            error_count += 1
        except Exception as e:
            logger.error(f'Error updating tracking data for "{building.address}": {str(e)}')
            error_count += 1

    if updated_count > 0:
        messages.success(request, f'Successfully updated LL84 tracking data for {updated_count} building(s).')
    if error_count > 0:
        messages.error(request, f'Failed to update {error_count} building(s) due to missing or invalid data.')

    return redirect('admin_view')


@login_required
@user_passes_test(is_admin_user)
def building_update_bins(request, building_id):
    building = get_object_or_404(Building, id=building_id)
    # Find the BuildingTracking record for the LL84 service
    try:
        tracking = BuildingTracking.objects.get(building=building, service__name='LL84')
    except BuildingTracking.DoesNotExist:
        messages.error(request, f'No LL84 tracking data found for "{building.address}".')
        return redirect('admin_view')

    try:
        # Parse tracking_info JSON
        tracking_info = json.loads(tracking.tracking_info)

        # Mapping of tracking_info keys to BuildingTracking fields
        field_mappings = {
            'Price': ('LL84_Price', lambda x: str(x)),
            '2020 Filed': ('LL84_2020_Filed', lambda x: x.strip().lower() == 'y'),
            '2021PMT': ('LL84_2021PMT', lambda x: str(x)),
            '2022 Score to customer': ('LL84_2022_Score_to_customer', lambda x: x.strip().lower() == 'y'),
            '2023 Invoice sent': ('LL84_2023_Invoice_sent', lambda x: x.strip().lower() == 'y'),
            '2023 PMT': ('LL84_2023_PMT', lambda x: x.strip().lower() == 'y'),
            'Submission': ('LL84_Submission', lambda x: x.strip().lower() == 'y'),
            '23 Grading': ('LL84_23_Grading', lambda x: x.strip().lower() == 'y'),
            '24 Outreach': ('LL84_24_Outreach', lambda x: x.strip().lower() == 'y'),
            '2024 PMT': ('LL84_2024_PMT', lambda x: x.strip().lower() == 'y'),
            '24 Submission': ('LL84_24_Submission', lambda x: x.strip().lower() == 'y'),
            '2024 Score': ('LL84_2024_Score', lambda x: str(x)),
            'water benchmark': ('LL84_water_benchmark', lambda x: x.strip().lower() == 'y'),
            '2025 Paid': ('LL84_2025_Paid', lambda x: x.strip().lower() == 'y'),
            '2025 submission': ('LL84_2025_submission', lambda x: str(x)),
            'Confirmation Email': ('LL84_Confirmation_Email', lambda x: str(x)),
            'Show data in BEAM': ('LL84_Show_data_in_BEAM', lambda x: str(x)),
        }

        # Update fields based on tracking_info
        for json_key, (field_name, transform) in field_mappings.items():
            if json_key in tracking_info:
                setattr(tracking, field_name, transform(tracking_info[json_key]))

        tracking.save()
        messages.success(request, f'LL84 tracking data for "{building.address}" updated successfully.')
    except json.JSONDecodeError:
        messages.error(request, f'Invalid tracking_info format for "{building.address}".')
    except Exception as e:
        messages.error(request, f'Error updating tracking data for "{building.address}": {str(e)}')

    return redirect('admin_view')