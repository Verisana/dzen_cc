# Generated by Django 2.1.4 on 2019-01-17 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_sync_bot', '0015_auto_20190116_1415'),
    ]

    operations = [
        migrations.AddField(
            model_name='salesdata',
            name='is_uploaded_quickresto',
            field=models.BooleanField(default=False),
        ),
    ]