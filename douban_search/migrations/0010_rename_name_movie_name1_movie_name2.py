# Generated by Django 4.2.4 on 2023-08-18 19:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0009_alter_keyword_count'),
    ]

    operations = [
        migrations.RenameField(
            model_name='movie',
            old_name='name',
            new_name='name1',
        ),
        migrations.AddField(
            model_name='movie',
            name='name2',
            field=models.CharField(max_length=250, null=True),
        ),
    ]