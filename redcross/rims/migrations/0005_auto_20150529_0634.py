# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0004_auto_20150515_0706'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={},
        ),
        migrations.AddField(
            model_name='inventoryitem',
            name='modifiedMicroseconds',
            field=models.IntegerField(default=0, help_text=b'modification microsecond offset'),
            preserve_default=True,
        ),
    ]
