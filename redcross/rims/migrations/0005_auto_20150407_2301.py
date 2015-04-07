# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0004_auto_20150407_2300'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.IntegerField(default=0, help_text=b'Number of product units (each, boxes, cases, ...) of this type at the site containing this product'),
            preserve_default=True,
        ),
    ]
