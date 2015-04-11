# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rims', '0006_auto_20150407_2333'),
    ]

    operations = [
        migrations.CreateModel(
            name='InventoryItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=0, help_text=b'Number of inventory units (each, boxes, cases, ...) of this type at the site containing this product')),
                ('information', models.ForeignKey(help_text=b'The detailed information about this product type', to='rims.ProductInformation')),
                ('site', models.ForeignKey(help_text=b'The site containing this inventory', to='rims.Site')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='product',
            name='information',
        ),
        migrations.RemoveField(
            model_name='product',
            name='site',
        ),
        migrations.DeleteModel(
            name='Product',
        ),
    ]
