# Generated by Django 5.1 on 2024-08-08 08:46

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_post'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='order',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='post',
            name='upload_time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
