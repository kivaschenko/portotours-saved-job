# Generated by Django 5.0.3 on 2024-05-09 15:01

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0076_remove_experience_traveler_tips_text_2_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='includes_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='List of features INCLUDED in tour, max 10000 characters', max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='not_includes_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='List of features NOT INCLUDED in tour, max 10000 characters', max_length=10000, null=True),
        ),
        migrations.AlterField(
            model_name='experience',
            name='traveler_tips_text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='Max 10000 characters', max_length=10000, null=True),
        ),
    ]
