# Generated by Django 5.0.1 on 2024-01-28 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_meetingpoint_auto_update_address_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Language',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbreviation', models.CharField(max_length=3)),
                ('name', models.CharField(max_length=60)),
            ],
            options={
                'ordering': ('name',),
                'unique_together': {('abbreviation', 'name')},
            },
        ),
    ]
