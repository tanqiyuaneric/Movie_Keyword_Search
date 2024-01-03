# Generated by Django 4.2.4 on 2024-01-03 03:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('douban_search', '0015_alter_comment_emotion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Keyword_Info',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=1)),
                ('keyword', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='douban_search.keyword')),
                ('movie', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='douban_search.movie')),
            ],
        ),
    ]
