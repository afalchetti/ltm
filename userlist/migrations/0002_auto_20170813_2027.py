# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-08-13 20:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userlist', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='address',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='address'),
        ),
        migrations.AddField(
            model_name='user',
            name='phone',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='phone'),
        ),
    ]