# Generated by Django 5.0.3 on 2024-05-13 12:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0077_alter_experience_includes_text_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parentexperience',
            name='child_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True),
        ),
    ]
