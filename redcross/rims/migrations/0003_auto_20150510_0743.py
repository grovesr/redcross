# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0002_inventoryitem_deleted'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='inventoryitem',
            options={'get_latest_by': 'modified'},
        ),
        migrations.AddField(
            model_name='productinformation',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 10, 11, 43, 26, 648553, tzinfo=utc), auto_now=True, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productinformation',
            name='modifier',
            field=models.CharField(default=b'admin', max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='site',
            name='modified',
            field=models.DateTimeField(default=datetime.datetime(2015, 5, 10, 11, 43, 38, 634909, tzinfo=utc), auto_now=True, auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='site',
            name='modifier',
            field=models.CharField(default=b'admin', max_length=50, blank=True),
            preserve_default=True,
        ),
    ]
