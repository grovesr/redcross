# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0002_auto_20150407_1020'),
    ]

    operations = [
        migrations.AlterField(
            model_name='site',
            name='address2',
            field=models.CharField(default=b'', max_length=50, null=True, help_text=b'Street address of this inventory site', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='address3',
            field=models.CharField(default=b'', max_length=50, null=True, help_text=b'Town address of this inventory site', blank=True),
            preserve_default=True,
        ),
    ]
