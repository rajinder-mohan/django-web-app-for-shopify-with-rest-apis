# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-17 11:59
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0006_accountdetail_token_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accountdetail',
            name='token_time',
            field=models.DateTimeField(default=datetime.datetime(2017, 11, 17, 11, 59, 14, 688284)),
        ),
    ]
