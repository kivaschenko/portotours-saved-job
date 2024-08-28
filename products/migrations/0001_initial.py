# Generated by Django 5.0.1 on 2024-01-27 18:25

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MeetingPoint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=60, unique=True)),
                ('slug', models.SlugField(blank=True, help_text='Slug generated from name', max_length=70, unique=True)),
                ('country', models.CharField(blank=True, help_text='Country name max 150 characters', max_length=150, null=True)),
                ('region', models.CharField(blank=True, help_text='Region name max 150 characters', max_length=150, null=True)),
                ('city', models.CharField(blank=True, help_text='City name max 150 characters', max_length=150, null=True)),
                ('latitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('longitude', models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True)),
                ('geom', django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
    ]
