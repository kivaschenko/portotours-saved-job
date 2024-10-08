# Generated by Django 5.0.1 on 2024-01-28 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_meetingpoint_auto_update_address_name_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='meetingpoint',
            name='auto_update_address_name',
            field=models.BooleanField(default=True, help_text='Automatically update address name form open street maps response by coordinates.'),
        ),
    ]
