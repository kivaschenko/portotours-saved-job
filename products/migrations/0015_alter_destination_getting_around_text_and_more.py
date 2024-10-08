# Generated by Django 5.0.1 on 2024-02-01 14:09

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_alter_destination_getting_around_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='destination',
            name='getting_around_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='max 6000 characters', max_length=6000, null=True),
        ),
        migrations.AlterField(
            model_name='destination',
            name='introduction_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='max 6000 characters', max_length=6000, null=True),
        ),
        migrations.AlterField(
            model_name='destination',
            name='travel_tips_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='max 6000 characters', max_length=6000, null=True),
        ),
        migrations.AlterField(
            model_name='destination',
            name='when_to_visit_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='max 6000 characters', max_length=6000, null=True),
        ),
    ]
