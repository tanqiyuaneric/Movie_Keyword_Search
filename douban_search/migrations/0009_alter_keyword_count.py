# Generated by Django 4.2.4 on 2023-08-18 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0008_keyword_count'),
    ]

    operations = [
        migrations.AlterField(
            model_name='keyword',
            name='count',
            field=models.IntegerField(default=1),
        ),
    ]
