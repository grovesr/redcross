# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0006_auto_20150529_0639'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='site',
            name='region',
        ),
        migrations.AddField(
            model_name='site',
            name='county',
            field=models.CharField(default=b'', help_text=b'County where site is located', max_length=50),
            preserve_default=True,
        ),
    ]
