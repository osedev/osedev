# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2017-08-19 15:17
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('onboarding', '0001_initial'),
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='applicationinstance',
            name='applicant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='applicationinstance',
            name='application',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='instances', to='onboarding.Application'),
        ),
        migrations.AddField(
            model_name='application',
            name='position',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='user.Position'),
        ),
    ]
