# Generated by Django 5.0.1 on 2024-02-29 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0005_purchase_stripe_checkout_session_id'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='purchase',
            options={'ordering': ('-timestamp',)},
        ),
        migrations.AddField(
            model_name='purchase',
            name='stripe_amount_total',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='purchase',
            name='stripe_payment_status',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
