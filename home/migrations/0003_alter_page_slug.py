# Generated by Django 5.0.1 on 2024-04-04 11:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_page'),
    ]

    operations = [
        migrations.AlterField(
            model_name='page',
            name='slug',
            field=models.SlugField(blank=True, help_text='Slug of the page, if blank, will be generated automatically from the title', max_length=60, null=True, unique=True),
        ),
    ]
