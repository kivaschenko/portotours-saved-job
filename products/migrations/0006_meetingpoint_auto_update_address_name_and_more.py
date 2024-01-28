# Generated by Django 5.0.1 on 2024-01-28 12:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_meetingpoint_location_raw_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingpoint',
            name='auto_update_address_name',
            field=models.BooleanField(default=True, help_text='Automatically update address name form open street maps response.'),
        ),
        migrations.AlterField(
            model_name='meetingpoint',
            name='location_raw',
            field=models.JSONField(blank=True, help_text='Raw describe from open street maps coordinates.', null=True),
        ),
    ]
