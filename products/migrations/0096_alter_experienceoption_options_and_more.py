# Generated by Django 5.0.3 on 2024-06-12 11:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0095_alter_experienceoption_options_alter_product_options_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='experienceoption',
            options={'ordering': ('-priority_number',), 'verbose_name': 'Optional Extras', 'verbose_name_plural': 'Optional Extras'},
        ),
        migrations.AlterModelOptions(
            name='productoption',
            options={'ordering': ['experience_option'], 'verbose_name': 'Order Optional Extras', 'verbose_name_plural': 'Order Optional Extras'},
        ),
    ]
