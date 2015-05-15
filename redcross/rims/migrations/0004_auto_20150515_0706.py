# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0003_auto_20150510_0743'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='modified',
            field=models.DateTimeField(help_text=b'last modified on this date', auto_now=True, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='inventoryitem',
            name='modifier',
            field=models.CharField(default=b'admin', help_text=b'user that last modified this record', max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productinformation',
            name='modified',
            field=models.DateTimeField(help_text=b'last modified on this date', auto_now=True, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='productinformation',
            name='modifier',
            field=models.CharField(default=b'admin', help_text=b'user that last modified this record', max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='modified',
            field=models.DateTimeField(help_text=b'last modified on this date', auto_now=True, auto_now_add=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='modifier',
            field=models.CharField(default=b'admin', help_text=b'user that last modified this record', max_length=50, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='site',
            name='number',
            field=models.AutoField(help_text=b'unique site number', serialize=False, primary_key=True),
            preserve_default=True,
        ),
    ]
