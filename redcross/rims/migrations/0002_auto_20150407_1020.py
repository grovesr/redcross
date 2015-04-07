# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='type',
        ),
        migrations.AddField(
            model_name='site',
            name='region',
            field=models.CharField(default=b'Northestern New York', help_text=b'Delivery or Inventory site type', max_length=20, choices=[(b'Northestern New York', b'Northeastern New York'), (b'Western New York', b'Western New York')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='contactName',
            field=models.CharField(default=b'', help_text=b'Primary contact name', max_length=50),
            preserve_default=True,
        ),
    ]
