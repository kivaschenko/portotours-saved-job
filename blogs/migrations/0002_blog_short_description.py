# Generated by Django 5.0.1 on 2024-02-19 17:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='short_description',
            field=models.TextField(blank=True, help_text='300 characters, max', max_length=300, null=True),
        ),
    ]
