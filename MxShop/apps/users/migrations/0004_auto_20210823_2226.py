# Generated by Django 3.1.5 on 2021-08-23 22:26

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210823_1659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifycode',
            name='add_time',
            field=models.DateTimeField(default=datetime.datetime(2021, 8, 23, 22, 26, 57, 671915), verbose_name='添加时间'),
        ),
    ]
