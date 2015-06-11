# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0009_auto_20150605_0651'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='modified',
            field=models.DateTimeField(default=None, help_text=b'last modified on this date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productinformation',
            name='modified',
            field=models.DateTimeField(default=None, help_text=b'last modified on this date', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='modified',
            field=models.DateTimeField(default=None, help_text=b'last modified on this date', blank=True),
            preserve_default=True,
        ),
    ]
