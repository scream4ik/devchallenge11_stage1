# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-02 15:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20170502_1223'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='result',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'Принято'), (2, 'Не принято')], null=True, verbose_name='решение'),
        ),
    ]
