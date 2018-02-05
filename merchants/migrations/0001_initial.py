# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-11-11 13:18
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shopify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccessToken',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='AccountDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('platform', models.CharField(max_length=200)),
                ('username', models.CharField(blank=True, max_length=500)),
                ('shopify_domain', models.CharField(max_length=255, unique=True)),
                ('main_domain', models.CharField(max_length=255, unique=True)),
                ('token', models.CharField(max_length=500)),
                ('status', models.IntegerField(default=0)),
                ('is_deleted', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DenyAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchants.AccountDetail')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopify.Account')),
            ],
        ),
        migrations.CreateModel(
            name='ProductDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(max_length=200)),
                ('PlatformProductId', models.BigIntegerField()),
                ('merchant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchants.AccountDetail')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopify.Products')),
                ('vendor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='shopify.Account')),
            ],
        ),
        migrations.AddField(
            model_name='accesstoken',
            name='merchant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='merchants.AccountDetail'),
        ),
    ]
