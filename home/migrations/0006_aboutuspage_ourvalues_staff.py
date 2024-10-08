# Generated by Django 5.0.3 on 2024-05-30 10:15

import ckeditor.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_alter_page_content_alter_page_keywords_and_more'),
        ('products', '0083_alter_parentexperience_second_purchase_discount'),
    ]

    operations = [
        migrations.CreateModel(
            name='AboutUsPage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text="Title of the page, max 120 characters, for example 'About Us' text", max_length=120, unique=True)),
                ('intro_text', ckeditor.fields.RichTextField(blank=True, help_text='Under title text block markdown content of the page, max 1000 characters', max_length=1000, null=True)),
                ('our_mission_title', models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True)),
                ('our_mission_text', ckeditor.fields.RichTextField(blank=True, help_text='Under Our Mission title text block markdown content of the page, max 1000 characters', max_length=1000, null=True)),
                ('our_values_title', models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True)),
                ('our_team_title', models.CharField(blank=True, help_text='max 120 characters', max_length=120, null=True)),
                ('our_team_text', ckeditor.fields.RichTextField(blank=True, help_text='max 1000 characters', max_length=1000, null=True)),
                ('slug', models.SlugField(blank=True, help_text='Slug of the page, if blank, will be generated automatically from the title, max 255 characters', max_length=255, null=True, unique=True)),
                ('page_title', models.CharField(blank=True, help_text='SEO title for header in search list, max 120 characters', max_length=60, null=True)),
                ('page_description', models.TextField(blank=True, help_text='SEO page description, max 500 characters', max_length=600, null=True)),
                ('keywords', models.TextField(blank=True, help_text='SEO keywords', max_length=500, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.language')),
            ],
            options={
                'ordering': ('title',),
            },
        ),
        migrations.CreateModel(
            name='OurValues',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon_img', models.ImageField(blank=True, null=True, upload_to='about_us/images/')),
                ('value_tittle', models.CharField(help_text='max 120 characters', max_length=120, unique=True)),
                ('value_text', ckeditor.fields.RichTextField(help_text='max 1000 characters', max_length=1000)),
                ('about_us_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='our_values', to='home.aboutuspage')),
            ],
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(help_text='Full name of the staff member', max_length=120, unique=True)),
                ('position', models.CharField(help_text='Position of the staff member', max_length=120)),
                ('description', models.TextField(blank=True, help_text='Description of the staff member', max_length=1000, null=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='staff_photos/')),
                ('about_us_page', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='staff', to='home.aboutuspage')),
            ],
        ),
    ]
