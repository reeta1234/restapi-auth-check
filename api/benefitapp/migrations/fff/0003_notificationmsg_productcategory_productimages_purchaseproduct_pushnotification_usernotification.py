# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benefitapp', '0002_auto_20160201_1125'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notificationmsg',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=100, null=True, db_column='Title', blank=True)),
                ('message', models.CharField(max_length=250, null=True, db_column='Message', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'notificationmsg',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Productcategory',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'productcategory',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Productimages',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('images', models.CharField(max_length=100, null=True, db_column='Images', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'productimages',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Purchaseproduct',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('price', models.DecimalField(null=True, decimal_places=2, max_digits=6, db_column='Price', blank=True)),
                ('shipping', models.CharField(max_length=100, null=True, db_column='Shipping', blank=True)),
                ('tax', models.DecimalField(null=True, decimal_places=2, max_digits=6, db_column='Tax', blank=True)),
                ('transactionid', models.CharField(max_length=50, null=True, db_column='TransactionId', blank=True)),
                ('paymentstatus', models.CharField(max_length=50, null=True, db_column='PaymentStatus', blank=True)),
                ('platform', models.CharField(max_length=50, null=True, db_column='Platform', blank=True)),
                ('environment', models.CharField(max_length=50, null=True, db_column='Environment', blank=True)),
                ('paypalsdkversion', models.CharField(max_length=50, null=True, db_column='PaypalSdkVersion', blank=True)),
                ('intent', models.CharField(max_length=50, null=True, db_column='Intent', blank=True)),
                ('paymenttime', models.CharField(max_length=50, null=True, db_column='PaymentTime', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'purchaseproduct',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Pushnotification',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('message', models.CharField(max_length=255, null=True, db_column='Message', blank=True)),
                ('is_post_read', models.CharField(max_length=1, null=True, db_column='isPostRead', blank=True)),
                ('is_push_read', models.CharField(max_length=1, null=True, db_column='isPushRead', blank=True)),
                ('is_deliver', models.CharField(max_length=1, null=True, db_column='isDeliver', blank=True)),
                ('action_id', models.IntegerField(db_column='ActionId')),
                ('action_type', models.CharField(max_length=50, null=True, db_column='ActionType', blank=True)),
                ('status', models.CharField(max_length=1, null=True, db_column='Status', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'pushnotification',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Usernotification',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('is_send', models.CharField(max_length=1, null=True, db_column='is_send', blank=True)),
                ('is_read', models.CharField(max_length=1, null=True, db_column='is_read', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'usernotification',
                'managed': False,
            },
        ),
    ]
