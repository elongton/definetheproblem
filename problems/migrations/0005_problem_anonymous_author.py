# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-22 21:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('problems', '0004_problem_rootproblem'),
    ]

    operations = [
        migrations.AddField(
            model_name='problem',
            name='anonymous_author',
            field=models.BooleanField(default=False),
        ),
    ]