# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0003_auto_20150407_1023'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='quantity',
            field=models.PositiveIntegerField(default=0, help_text=b'Number of product units (each, boxes, cases, ...) of this type at the site containing this product'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='address1',
            field=models.CharField(default=b'', help_text=b'First street address of this site', max_length=50),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='address2',
            field=models.CharField(default=b'', max_length=50, null=True, help_text=b'Second street address of this site', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='address3',
            field=models.CharField(default=b'', max_length=50, null=True, help_text=b'Third street address of this site', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='region',
            field=models.CharField(default=b'Northestern New York', help_text=b'Red Cross region', max_length=20, choices=[(b'Northestern New York', b'Northeastern New York'), (b'Western New York', b'Western New York')]),
            preserve_default=True,
        ),
    ]
