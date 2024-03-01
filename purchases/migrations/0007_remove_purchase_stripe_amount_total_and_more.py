# Generated by Django 5.0.1 on 2024-03-01 15:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0006_alter_purchase_options_purchase_stripe_amount_total_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='purchase',
            name='stripe_amount_total',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='stripe_payment_status',
        ),
        migrations.AddField(
            model_name='purchase',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
