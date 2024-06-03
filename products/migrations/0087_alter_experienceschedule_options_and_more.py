# Generated by Django 5.0.3 on 2024-06-03 17:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0086_experiencecategory_card_image_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='experienceschedule',
            options={'ordering': ('time',)},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'get_latest_by': 'created_at', 'ordering': ('created_at',)},
        ),
        migrations.CreateModel(
            name='ExperienceOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Option name max 60 characters', max_length=60)),
                ('description', models.CharField(blank=True, help_text='Option description max 255 characters', max_length=255)),
                ('priority_number', models.IntegerField(blank=True, default=0, help_text='The higher the value of the priority number, the higher it appears in the list', null=True, verbose_name='Priority')),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('language', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='products.language')),
            ],
            options={
                'ordering': ('-priority_number',),
                'unique_together': {('name', 'language')},
            },
        ),
    ]
