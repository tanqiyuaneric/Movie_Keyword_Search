# Generated by Django 4.2.4 on 2023-08-18 18:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0007_comment_is_review'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='count',
            field=models.IntegerField(default=0),
        ),
    ]
