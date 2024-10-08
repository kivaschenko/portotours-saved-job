# Generated by Django 5.0.1 on 2024-02-05 16:04

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('destinations', '0002_destination_all_about_title_and_more'),
        ('products', '0022_remove_faqdestination_language_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Experience',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('slug', models.SlugField(blank=True, help_text='max 60 characters, exactly url tail that is unique', max_length=60, unique=True)),
                ('page_title', models.CharField(blank=True, help_text='seo title for header in search list, max 120 characters', max_length=120, null=True)),
                ('page_description', models.TextField(blank=True, help_text='seo page description, max 500 characters', max_length=600, null=True)),
                ('keywords', models.TextField(blank=True, help_text='seo keywords', max_length=500, null=True)),
                ('name', models.CharField(help_text='Short name for the experience, max 60 characters', max_length=60, unique=True)),
                ('title_for_booking_form', models.CharField(blank=True, help_text='Title above book form, max 120 characters', max_length=120, null=True)),
                ('long_name', models.CharField(blank=True, help_text='Long name for the experience, max 255 characters', max_length=255, null=True)),
                ('short_description', models.CharField(blank=True, help_text='Short description for the Short Name, max 255 characters', max_length=255, null=True)),
                ('full_description', ckeditor.fields.RichTextField(blank=True, help_text='Full description for the Experience, max 6000 characters', max_length=6000, null=True)),
                ('languages', ckeditor.fields.RichTextField(blank=True, help_text='list of available languages during experience trip', null=True)),
                ('duration', ckeditor.fields.RichTextField(blank=True, help_text="duration of the experience, for example '5 hours'", max_length=60, null=True)),
                ('accessibility', ckeditor.fields.RichTextField(blank=True, help_text='max 255 characters', max_length=255, null=True)),
                ('possibility', ckeditor.fields.RichTextField(blank=True, help_text='max 255 characters', max_length=255, null=True)),
                ('recommendations_title', models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True)),
                ('recommendations_subtitle', models.CharField(blank=True, help_text='max 255 characters', max_length=255, null=True)),
                ('recommendations_slogan', models.CharField(blank=True, help_text='max 120 characters, belong SEE MORE button', max_length=120, null=True)),
                ('destinations', models.ManyToManyField(help_text='may be bind to multiple destinations', to='destinations.destination')),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.language')),
                ('meeting_point', models.ForeignKey(blank=True, help_text='meeting point for this experience', null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.meetingpoint')),
            ],
            options={
                'db_table': 'experiences',
                'ordering': ('name',),
                'unique_together': {('name', 'slug')},
            },
        ),
    ]
