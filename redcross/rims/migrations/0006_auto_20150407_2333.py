# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0005_auto_20150407_2301'),
    ]

    operations = [
        migrations.AlterField(
            model_name='productinformation',
            name='warehouseLocation',
            field=models.CharField(default=b'', max_length=10, null=True, help_text=b'location of this item in the warehouse', blank=True),
            preserve_default=True,
        ),
    ]
