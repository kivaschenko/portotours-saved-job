# Generated by Django 5.0.1 on 2024-03-31 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0045_experience_title_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='experience',
            name='recommended_experiences',
            field=models.ManyToManyField(related_name='recommended', to='products.experience'),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='free_cancellation',
            field=models.BooleanField(default=False, help_text='Free Cancellation is allowed.', null=True),
        ),
        migrations.AddField(
            model_name='parentexperience',
            name='happy_clients_number',
            field=models.IntegerField(default=23),
            preserve_default=False,
        ),
    ]
