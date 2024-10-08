# Generated by Django 5.0.3 on 2024-06-29 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0104_experienceevent_rule_event_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experienceevent',
            name='stop_rule_date',
            field=models.DateField(blank=True, help_text='Date of stop rule. Define and save this before CASCADE delete will running!', null=True),
        ),
        migrations.AlterField(
            model_name='parentexperience',
            name='time_of_day',
            field=models.ManyToManyField(help_text='list of time of day variables', to='products.timeofday'),
        ),
    ]
