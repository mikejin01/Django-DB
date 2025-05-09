# Generated by Django 5.2 on 2025-04-22 18:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0003_remove_building_service_building_services'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Customer',
            new_name='Client',
        ),
        migrations.RenameField(
            model_name='building',
            old_name='customer',
            new_name='client',
        ),
        migrations.AddField(
            model_name='building',
            name='adjusted_gfa',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='building',
            name='basement_code',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AddField(
            model_name='building',
            name='bis_bbl_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='building',
            name='bis_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='building',
            name='number_of_bins',
            field=models.IntegerField(blank=True, default=1),
        ),
        migrations.AddField(
            model_name='building',
            name='number_of_floors',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='building',
            name='uniformly_adjusted_gfa',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='building',
            name='zola_gfa',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='building',
            name='zola_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='building',
            name='BBL',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.AlterField(
            model_name='building',
            name='BIN',
            field=models.CharField(blank=True, default='', max_length=30),
        ),
        migrations.CreateModel(
            name='BuildingCompliance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ll87_needed_2025', models.CharField(blank=True, max_length=10)),
                ('ll87_filed', models.CharField(blank=True, max_length=10)),
                ('ll97_schedule', models.CharField(blank=True, max_length=50)),
                ('cbl_ll97_path_2025', models.CharField(blank=True, max_length=50)),
                ('field_schedule', models.CharField(blank=True, max_length=50)),
                ('ll88_lighting', models.CharField(blank=True, max_length=10)),
                ('ll88_submeter', models.CharField(blank=True, max_length=10)),
                ('ll88_needed', models.CharField(blank=True, max_length=10)),
                ('proof_sent', models.CharField(blank=True, max_length=10)),
                ('request_info_date', models.DateField(blank=True, null=True)),
                ('invoice_sent', models.DateField(blank=True, null=True)),
                ('request_share_espm', models.DateField(blank=True, null=True)),
                ('espm_email', models.EmailField(blank=True, max_length=254)),
                ('dob_now_email', models.EmailField(blank=True, max_length=254)),
                ('contact_email', models.EmailField(blank=True, max_length=254)),
                ('dob_now_transaction_number', models.CharField(blank=True, max_length=50)),
                ('dob_filing_fee_paid', models.DateField(blank=True, null=True)),
                ('dob_pmt_confirmation', models.CharField(blank=True, max_length=50)),
                ('attestation_received', models.DateField(blank=True, null=True)),
                ('complete_attestation', models.BooleanField(default=False)),
                ('proof_of_correction', models.CharField(blank=True, max_length=255)),
                ('payment_cleared', models.BooleanField(default=False)),
                ('espm_data_in_beam', models.BooleanField(default=False)),
                ('attestation_file', models.FileField(blank=True, null=True, upload_to='attestations/')),
                ('proof_of_correction_file', models.FileField(blank=True, null=True, upload_to='proofs/')),
                ('building', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='db.building')),
            ],
        ),
    ]
