# Generated by Django 5.0.3 on 2024-05-14 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0007_remove_purchase_stripe_amount_total_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchase',
            name='error_code',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='purchase',
            name='error_message',
            field=models.TextField(blank=True, max_length=600, null=True),
        ),
    ]
