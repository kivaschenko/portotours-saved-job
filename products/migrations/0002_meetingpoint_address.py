# Generated by Django 5.0.1 on 2024-01-27 19:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meetingpoint',
            name='address',
            field=models.CharField(blank=True, help_text='Address name max 255 characters', max_length=255, null=True),
        ),
    ]
