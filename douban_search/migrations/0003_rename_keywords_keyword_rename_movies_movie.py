# Generated by Django 4.2.4 on 2023-08-18 07:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0002_movies_url'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Keywords',
            new_name='Keyword',
        ),
        migrations.RenameModel(
            old_name='Movies',
            new_name='Movie',
        ),
    ]
