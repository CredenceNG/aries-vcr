# Generated by Django 2.2.9 on 2019-12-18 22:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('icat_hooks', '0004_auto_20191213_1723'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='hookablecredential',
            index=models.Index(fields=['corp_num', 'topic_status'], name='new_hook_idx'),
        ),
    ]
