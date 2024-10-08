# Generated by Django 5.0.3 on 2024-05-30 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0082_alter_parentexperience_increase_percentage_old_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentexperience',
            name='second_purchase_discount',
            field=models.PositiveSmallIntegerField(blank=True, default=20, help_text='Secondary purchase discount in EUR from price for secondary products', null=True, verbose_name='2ND PRODUCT DISCOUNT'),
        ),
    ]
