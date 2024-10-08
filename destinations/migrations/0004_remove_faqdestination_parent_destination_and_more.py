# Generated by Django 5.0.1 on 2024-02-28 11:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0003_destination_recommendations_slogan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='faqdestination',
            name='parent_destination',
        ),
        migrations.AddField(
            model_name='faqdestination',
            name='destination',
            field=models.ForeignKey(blank=True, help_text='The Parent destination brings together all destinations with multilingual content but same location and common FAQ.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='destinations.destination'),
        ),
    ]
