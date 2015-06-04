# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0007_auto_20150602_0628'),
    ]

    operations = [
        migrations.AddField(
            model_name='productinformation',
            name='modifiedMicroseconds',
            field=models.IntegerField(default=0, help_text=b'modification microsecond offset'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='site',
            name='modifiedMicroseconds',
            field=models.IntegerField(default=0, help_text=b'modification microsecond offset'),
            preserve_default=True,
        ),
    ]
