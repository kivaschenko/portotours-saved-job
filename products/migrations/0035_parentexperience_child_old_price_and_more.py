# Generated by Django 5.0.1 on 2024-02-28 08:08

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0034_remove_product_session_product_session_key'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentexperience',
            name='child_old_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='For marketing purposes, this child old price will be higher than the new one.', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='old_total_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=Decimal('0'), max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='parentexperience',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='For marketing purposes, this adult old price will be higher than the new one.', max_digits=10, null=True),
        ),
    ]
