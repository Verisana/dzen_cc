# Generated by Django 2.1.4 on 2018-12-30 15:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_sync_bot', '0005_auto_20181230_1939'),
    ]

    operations = [
        migrations.AddField(
            model_name='goodsbase',
            name='quickresto_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]