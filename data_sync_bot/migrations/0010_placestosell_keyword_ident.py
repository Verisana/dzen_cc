# Generated by Django 2.1.4 on 2019-01-11 15:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_sync_bot', '0009_goodsbase_keyword_ident'),
    ]

    operations = [
        migrations.AddField(
            model_name='placestosell',
            name='keyword_ident',
            field=models.CharField(blank=True, max_length=64, null=True, unique=True),
        ),
    ]
