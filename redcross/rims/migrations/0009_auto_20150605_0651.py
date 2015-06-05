# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0008_auto_20150603_0706'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 5, 10, 51, 31, 253029, tzinfo=utc), help_text=b'last modified on this date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productinformation',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 5, 10, 51, 31, 251898, tzinfo=utc), help_text=b'last modified on this date'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 6, 5, 10, 51, 31, 250680, tzinfo=utc), help_text=b'last modified on this date'),
            preserve_default=True,
        ),
    ]
