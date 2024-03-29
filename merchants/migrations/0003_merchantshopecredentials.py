# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-14 07:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('merchants', '0002_auto_20171111_1403'),
    ]

    operations = [
        migrations.CreateModel(
            name='MerchantShopeCredentials',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=200, null=True)),
                ('secret', models.CharField(blank=True, max_length=200, null=True)),
                ('platform', models.CharField(default='Shopify', max_length=100)),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchants.AccountDetail')),
            ],
        ),
    ]
