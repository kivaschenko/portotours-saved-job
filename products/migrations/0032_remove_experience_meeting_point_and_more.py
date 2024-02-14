# Generated by Django 5.0.1 on 2024-02-14 13:34

import datetime
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0031_parentexperience_is_private_and_more'),
        ('schedule', '0014_use_autofields_for_pk'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='experience',
            name='meeting_point',
        ),
        migrations.RemoveField(
            model_name='experience',
            name='price',
        ),
        migrations.RemoveField(
            model_name='experience',
            name='price_changed_timestamp',
        ),
        migrations.RemoveField(
            model_name='experience',
            name='price_currency',
        ),
        migrations.RemoveField(
            model_name='product',
            name='experience',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_expired',
        ),
        migrations.RemoveField(
            model_name='product',
            name='is_paid',
        ),
        migrations.RemoveField(
            model_name='product',
            name='name',
        ),
        migrations.RemoveField(
            model_name='product',
            name='parent_experience_id',
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='child_discount',
            field=models.PositiveSmallIntegerField(blank=True, default=33, help_text='Child discount in % from price for child products', null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='child_price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='increase_percentage_old_price',
            field=models.IntegerField(blank=True, default=33, help_text='The percentage to increase old price automatically.', null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='meeting_point',
            field=models.ForeignKey(blank=True, help_text='meeting point for this experience', null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.meetingpoint'),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='old_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='For marketing purposes, this old price will be higher than the new one.', max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='price_changed_timestamp',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='price_currency',
            field=models.CharField(blank=True, default='eur', max_length=3, null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='use_auto_increase_old_price',
            field=models.BooleanField(default=False, help_text='If true, the old price is automatically increased'),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='use_child_discount',
            field=models.BooleanField(default=True, help_text="If the children's discount percentage is included and the percentage is specified, then when saving, it automatically recalculates the children's price depending on the main price f the amount of the discount in percent"),
        ),
        migrations.AddField(
            model_name='product',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='expired_time',
            field=models.DateTimeField(default=datetime.datetime(2024, 2, 14, 14, 34, 54, 229018)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='product',
            name='language',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.language'),
        ),
        migrations.AddField(
            model_name='product',
            name='occurrence',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='schedule.occurrence'),
        ),
        migrations.AddField(
            model_name='product',
            name='parent_experience',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.parentexperience'),
        ),
        migrations.AddField(
            model_name='product',
            name='session',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='sessions.session'),
        ),
        migrations.AddField(
            model_name='product',
            name='status',
            field=models.CharField(blank=True, choices=[('Pending', 'Pending'), ('Cancelled', 'Cancelled'), ('Expired', 'Expired'), ('Processing', 'Processing'), ('Payment', 'Payment'), ('Completed', 'Completed')], default='Pending', max_length=30, null=True),
        ),
    ]
