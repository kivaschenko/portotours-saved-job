# Generated by Django 5.0.3 on 2024-05-10 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('landing_pages', '0002_landingpage_related_landing_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='landingpage',
            name='title_related_landing_pages',
            field=models.CharField(blank=True, help_text='Title of the landing page, max 255 characters', max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='landingpage',
            name='banner',
            field=models.FileField(blank=True, help_text='Banner image, this image will be cropped and scaled max width: 1920 and max height: 460', null=True, upload_to='media/banners/'),
        ),
    ]
