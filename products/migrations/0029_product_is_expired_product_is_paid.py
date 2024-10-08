# Generated by Django 5.0.1 on 2024-02-07 16:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0028_alter_product_adults_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='product',
            name='is_paid',
            field=models.BooleanField(default=False),
        ),
    ]
