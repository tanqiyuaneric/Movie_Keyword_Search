# Generated by Django 4.2.4 on 2023-08-19 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0013_comment_emotion'),
    ]

    operations = [
        migrations.AddField(
            model_name='keyword',
            name='emotion',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='keyword',
            name='keyword2',
            field=models.CharField(max_length=250, null=True),
        ),
    ]
