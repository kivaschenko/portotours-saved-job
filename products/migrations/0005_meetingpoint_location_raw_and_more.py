# Generated by Django 5.0.1 on 2024-01-28 12:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_meetingpoint_update_coords_by_geom_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingpoint',
            name='location_raw',
            field=models.JSONField(blank=True, help_text='Raw describe from openstreetmaps coordinates.', null=True),
        ),
        migrations.AlterField(
            model_name='meetingpoint',
            name='update_coords_by_geom',
            field=models.BooleanField(default=False, help_text='Automatically update longitude and latitude from map marker place. Turn off Auto location for this.'),
        ),
    ]
