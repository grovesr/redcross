# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('productCode', models.CharField(default=b'D11', max_length=10, serialize=False, primary_key=True, help_text=b'Unique Red Cross code for this product')),
                ('productName', models.CharField(default=b'', help_text=b'Name of this product', max_length=50)),
                ('expendable', models.BooleanField(default=True, help_text=b'Is this product expendable?')),
                ('quantityOfMeasure', models.IntegerField(default=1, help_text=b'How many individual items in each package?')),
                ('costPerItem', models.DecimalField(decimal_places=2, default=0.0, max_digits=7, blank=True, help_text=b'How much does each individual item cost?', null=True)),
                ('cartonsPerPallet', models.IntegerField(default=0, help_text=b'How many of these units fit on one pallet?', null=True, blank=True)),
                ('doubleStackPallets', models.BooleanField(default=False, help_text=b'Can pallets containing these products be stacked?')),
                ('warehouseLocation', models.CharField(default=b'', help_text=b'??????', max_length=10)),
                ('canExpire', models.BooleanField(default=False, help_text=b'Can this product expire?')),
                ('expirationDate', models.DateField(help_text=b'What is the expiration dat, if any?', null=True, blank=True)),
                ('expirationNotes', models.TextField(default=b'', help_text=b'Special expiration notes for this product', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UnitOfMeasure',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'EACH', help_text=b'How are these measured (EACH, BOX, ...)?', max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='product',
            name='unitOfMeasure',
            field=models.OneToOneField(to='rims.UnitOfMeasure', help_text=b'How are these measured (EACH, BOX, ...)?'),
            preserve_default=True,
        ),
    ]
