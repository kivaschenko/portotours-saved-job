# Generated by Django 5.0.1 on 2024-02-06 20:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0026_experience_price_changed_timestamp_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stripe_price',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
