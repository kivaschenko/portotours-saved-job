# Generated by Django 5.0.1 on 2024-04-23 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0057_experiencecategory_parentexperience_categories'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='experiencecategory',
            options={'ordering': ('name',), 'verbose_name_plural': 'Experience Categories'},
        ),
        migrations.AlterField(
            model_name='experiencecategory',
            name='slug',
            field=models.SlugField(blank=True, help_text='Category name max 60 characters, if empty will be auto-generated from name', max_length=60, unique=True),
        ),
    ]
