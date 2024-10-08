# Generated by Django 5.0.3 on 2024-05-31 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0083_alter_parentexperience_second_purchase_discount'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='product',
            options={'get_latest_by': 'created_at', 'ordering': ('-created_at',)},
        ),
        migrations.AddField(
            model_name='product',
            name='price_is_special',
            field=models.BooleanField(default=False),
        ),
    ]
