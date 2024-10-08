# Generated by Django 5.0.1 on 2024-04-01 11:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attractions', '0008_alter_tagattraction_icon_img'),
        ('destinations', '0004_remove_faqdestination_parent_destination_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='destination',
            name='top_attractions',
            field=models.ManyToManyField(blank=True, null=True, related_name='top_attractions', to='attractions.attraction'),
        ),
    ]
