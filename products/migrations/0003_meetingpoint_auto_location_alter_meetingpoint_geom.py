# Generated by Django 5.0.1 on 2024-01-28 08:56

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_meetingpoint_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingpoint',
            name='auto_location',
            field=models.BooleanField(default=False, help_text='After saving coordinates will be auto-defined by entered address'),
        ),
        migrations.AlterField(
            model_name='meetingpoint',
            name='geom',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, help_text='If the cursor was moved, then the coordinates (longitude, latitude) will be changed automatically after saving. Auto Location must be off.', null=True, srid=4326),
        ),
    ]
