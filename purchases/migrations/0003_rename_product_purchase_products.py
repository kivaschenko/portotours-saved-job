# Generated by Django 5.0.1 on 2024-02-08 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0002_remove_purchase_stripe_checkout_session_id_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='purchase',
            old_name='product',
            new_name='products',
        ),
    ]
