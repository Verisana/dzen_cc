# Generated by Django 2.1.4 on 2019-01-11 15:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_sync_bot', '0010_placestosell_keyword_ident'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='placestosell',
            name='keyword_ident',
        ),
    ]