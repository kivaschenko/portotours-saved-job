# Generated by Django 5.0.1 on 2024-03-29 19:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0044_remove_experience_languages_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='title_description',
            field=models.CharField(blank=True, help_text='Title for full description, max 255 characters', max_length=255, null=True),
        ),
    ]
