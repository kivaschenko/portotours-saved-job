# Generated by Django 5.0.1 on 2024-04-29 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0062_alter_experienceimage_slider_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentexperience',
            name='drop_off_location',
            field=models.CharField(blank=True, help_text='location to drop off this experience, max 255 characters', max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='pick_up_location',
            field=models.CharField(blank=True, help_text='location to pick up this experience, max 255 characters', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='name',
            field=models.CharField(help_text='Short name for the experience, max 255 characters', max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='experienceschedule',
            name='description',
            field=models.TextField(blank=True, help_text='Description of stop max 600 characters.', max_length=600, null=True),
        ),
        migrations.AlterField(
            model_name='experienceschedule',
            name='name_stop',
            field=models.CharField(blank=True, help_text='Name of stop max 255 character length.', max_length=255, null=True),
        ),
    ]
