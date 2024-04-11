# Generated by Django 5.0.1 on 2024-04-11 11:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0011_alter_destination_be_interested_destinations_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destination',
            name='slug',
            field=models.SlugField(blank=True, help_text='max 255 characters, exactly url tail that is unique', max_length=255, unique=True),
        ),
    ]
