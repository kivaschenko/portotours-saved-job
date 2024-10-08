# Generated by Django 5.0.1 on 2024-02-05 09:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='all_about_title',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='be_interested_subtitle',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='be_interested_title',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='faq_subtitle',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='faq_title',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='top_attractions_subtitle',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
        migrations.AddField(
            model_name='destination',
            name='top_attractions_title',
            field=models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True),
        ),
    ]
