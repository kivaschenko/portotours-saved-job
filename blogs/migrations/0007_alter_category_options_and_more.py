# Generated by Django 5.0.3 on 2024-05-17 09:50

import ckeditor.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blogs', '0006_blog_experience_recommendations_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ('name',), 'verbose_name': 'category', 'verbose_name_plural': 'categories'},
        ),
        migrations.RemoveField(
            model_name='blog',
            name='recommendations_slogan',
        ),
        migrations.AlterField(
            model_name='blockblog',
            name='text',
            field=ckeditor.fields.RichTextField(blank=True, help_text='maximum length of text block 10000 characters', max_length=10000, null=True),
        ),
    ]
