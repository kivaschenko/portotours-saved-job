# Generated by Django 5.0.3 on 2024-05-28 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0081_parentexperience_second_purchase_discount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentexperience',
            name='increase_percentage_old_price',
            field=models.IntegerField(blank=True, default=33, help_text='The percentage between old price and price.', null=True, verbose_name='Discount '),
        ),
        migrations.AlterField(
            model_name='parentexperience',
            name='second_purchase_discount',
            field=models.PositiveSmallIntegerField(blank=True, default=20, help_text='Secondary purchase discount in EUR from price for secondary products', null=True, verbose_name='Applied Price'),
        ),
    ]
