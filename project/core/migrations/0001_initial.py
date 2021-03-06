# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-01 17:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Convocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number_roman', models.CharField(max_length=5, verbose_name='номер (римский)')),
                ('number_arabic', models.SmallIntegerField(verbose_name='номер (арабский)')),
            ],
            options={
                'verbose_name': 'созыв',
                'ordering': ('number_arabic',),
                'verbose_name_plural': 'созывы',
            },
        ),
        migrations.CreateModel(
            name='Council',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100, unique=True, verbose_name='название')),
            ],
            options={
                'verbose_name': 'совет',
                'ordering': ('title',),
                'verbose_name_plural': 'городской совет',
            },
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60, unique=True, verbose_name='название')),
                ('date', models.DateField(verbose_name='дата')),
            ],
            options={
                'verbose_name': 'сессию',
                'ordering': ('title',),
                'verbose_name_plural': 'сессии',
            },
        ),
        migrations.CreateModel(
            name='Vote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(verbose_name='название')),
                ('types', models.SmallIntegerField(choices=[(1, 'За основу'), (2, 'За пропозицію'), (3, 'В цілому')], verbose_name='тип')),
                ('convocation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Convocation', verbose_name='созыв')),
                ('council', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Council', verbose_name='городской совет')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Session', verbose_name='сессия')),
            ],
            options={
                'verbose_name': 'голосование',
                'verbose_name_plural': 'голосования',
            },
        ),
        migrations.AlterUniqueTogether(
            name='convocation',
            unique_together=set([('number_roman', 'number_arabic')]),
        ),
    ]
