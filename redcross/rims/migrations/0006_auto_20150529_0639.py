# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0005_auto_20150529_0634'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'get_latest_by': 'modified'},
        ),
    ]
