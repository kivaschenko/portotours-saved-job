# Generated by Django 5.0.1 on 2024-04-01 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0050_alter_parentexperience_happy_clients_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experience',
            name='recommended_experiences',
        ),
        migrations.AddField(
            model_name='experience',
            name='experience_recommendations',
            field=models.ManyToManyField(to='products.experience'),
        ),
    ]
