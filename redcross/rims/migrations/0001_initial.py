# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DRNumber',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('dr', models.CharField(default=b'N/A', help_text=b'Disaster Relief Operations number (large disasters only).', max_length=10)),
                ('name', models.CharField(default=b'No Name Required', help_text=b'description of the Disaster Operation', max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=0, help_text=b'Number of product units (each, boxes, cases, ...) of this type at the site containing this product')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProductInformation',
            fields=[
                ('code', models.CharField(default=b'D11', max_length=10, serialize=False, primary_key=True, help_text=b'Unique Red Cross code for this product')),
                ('name', models.CharField(default=b'', help_text=b'Name of this product', max_length=50)),
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
            name='Site',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'', help_text=b'Name of this site', max_length=50)),
                ('type', models.CharField(default=b'delivery', help_text=b'Delivery or Inventory site type', max_length=20, choices=[(b'delivery', b'delivery'), (b'inventory', b'inventory')])),
                ('address1', models.CharField(default=b'', help_text=b'Site name for this inventory site', max_length=50)),
                ('address2', models.CharField(default=b'', help_text=b'Street address of this inventory site', max_length=50)),
                ('address3', models.CharField(default=b'', help_text=b'Town address of this inventory site', max_length=50)),
                ('contactName', models.CharField(default=b'', help_text=b'Primary cnotact name', max_length=50)),
                ('contactPhone', models.CharField(default=b'', help_text=b'Primary contact phone number', max_length=25)),
                ('notes', models.TextField(default=b'', help_text=b'Additional information about the site', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TransactionPrefix',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prefix', models.CharField(default=b'P', help_text=b'Code used to identify inventory transaction types', max_length=5)),
                ('transaction', models.CharField(default=b'Physical Inventory', help_text=b'description of the transaction prefix code', max_length=50)),
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
            model_name='productinformation',
            name='unitOfMeasure',
            field=models.ForeignKey(help_text=b'How are these measured (EACH, BOX, ...)?', to='rims.UnitOfMeasure'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='information',
            field=models.ForeignKey(help_text=b'The detailed information about this product type', to='rims.ProductInformation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='product',
            name='site',
            field=models.ForeignKey(help_text=b'The site containing this product', to='rims.Site'),
            preserve_default=True,
        ),
    ]
