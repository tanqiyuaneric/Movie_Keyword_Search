# Generated by Django 4.2.4 on 2023-08-18 17:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0006_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='is_review',
            field=models.BooleanField(default=False),
        ),
    ]