# Generated by Django 2.2.28 on 2024-08-22 21:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api_v2', '0031_credential_raw_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='credentialtype',
            name='visible_fields',
        ),
    ]
