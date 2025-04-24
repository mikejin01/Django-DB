
import os
import django
import datetime
import pandas as pd
from django.contrib.auth.hashers import make_password

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from db.models import User, Client, Service, Lot, ServiceOnLot, ValidationRecord

# Load Excel file
df_user = pd.read_excel('seed.xlsx', sheet_name='User')
df_client = pd.read_excel('seed.xlsx', sheet_name='Client')
df_service = pd.read_excel('seed.xlsx', sheet_name='Service')
df_lot = pd.read_excel('seed.xlsx', sheet_name='Lot')
df_service_on_lot = pd.read_excel('seed.xlsx', sheet_name='ServiceOnLot')
df_validation = pd.read_excel('seed.xlsx', sheet_name='ValidationRecord')

# Seed Users
user_map = {}
for _, row in df_user.iterrows():
    user = User.objects.create(
        username=row['username'],
        email=row.get('email', ''),
        is_staff=bool(row.get('is_staff', False)),
        is_active=bool(row.get('is_active', True)),
        is_superuser=bool(row.get('is_superuser', False)),
        password=make_password(row.get('password', 'default123'))
    )
    user_map[row['username']] = user

# Seed Clients
for _, row in df_client.iterrows():
    user = User.objects.filter(id=row['user']).first()
    contacts = row.get('contacts', '')
    contacts_list = []
    if isinstance(contacts, str):
        for email in contacts.split('; '):
            if email.strip():
                contacts_list.append({'name': '', 'phone': '', 'email': email.strip()})
    Client.objects.create(
        user=user,
        primary_email=contacts_list[0]['email'] if contacts_list else '',
        outlook_folder_link=row.get('outlook_folder_link'),
        contacts=contacts_list
    )

# Seed Services
for _, row in df_service.iterrows():
    Service.objects.create(
        name=row['name'],
        price=str(row['price']),
    )

# Seed Lots
for _, row in df_lot.iterrows():
    client_user = User.objects.filter(username=row['client'].split()[0]).first()
    client = Client.objects.filter(user=client_user).first()
    Lot.objects.create(
        bbl=str(row['bbl']),
        zipcode=str(row['zipcode']),
        primary_address=row['primary_address'],
        client=client,
        owner_name=row['owner_name'],
        owner_email=row['owner_email'],
        espm_email=row['espm_email']
    )

# Seed ServiceOnLot
for _, row in df_service_on_lot.iterrows():
    ServiceOnLot.objects.create(
        lot_id=row['lot'],
        service_id=row['service'],
        status=row['status'],
        year=row['year'],
        deadline=None if pd.isna(row['deadline']) else bool(row['deadline'])
    )

# Seed ValidationRecords
for _, row in df_validation.iterrows():
    user = user_map.get(row['user'], None)
    ValidationRecord.objects.create(
        user=user,
        datetime=row['datetime'],
        table=row['table'],
        record=str(row['record']),
        field=row['field'],
        old=str(row['old']) if not pd.isna(row['old']) else '',
        new=str(row['new']) if not pd.isna(row['new']) else '',
        action=row['action'],
        status=row['status'],
        comment=row.get('comment', '')
    )
print("Seeding completed.")
