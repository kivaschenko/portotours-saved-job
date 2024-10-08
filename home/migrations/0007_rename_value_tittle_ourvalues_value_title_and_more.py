# Generated by Django 5.0.3 on 2024-05-30 10:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_aboutuspage_ourvalues_staff'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ourvalues',
            old_name='value_tittle',
            new_name='value_title',
        ),
        migrations.AddField(
            model_name='aboutuspage',
            name='main_image_desktop',
            field=models.ImageField(blank=True, null=True, upload_to='about_us/'),
        ),
        migrations.AddField(
            model_name='aboutuspage',
            name='main_image_mobile',
            field=models.ImageField(blank=True, null=True, upload_to='about_us/'),
        ),
        migrations.AlterField(
            model_name='aboutuspage',
            name='intro_text',
            field=models.TextField(blank=True, help_text='Under title text block markdown content of the page, max 1000 characters', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='aboutuspage',
            name='our_mission_text',
            field=models.TextField(blank=True, help_text='Under Our Mission title text block markdown content of the page, max 1000 characters', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='aboutuspage',
            name='our_team_text',
            field=models.TextField(blank=True, help_text='max 1000 characters', max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='ourvalues',
            name='icon_img',
            field=models.ImageField(blank=True, null=True, upload_to='about_us/icons/'),
        ),
        migrations.AlterField(
            model_name='ourvalues',
            name='value_text',
            field=models.TextField(help_text='max 1000 characters', max_length=1000),
        ),
        migrations.AlterField(
            model_name='staff',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='about_us/staff_photos/'),
        ),
    ]
