# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('benefitapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Commentlikes',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'commentlikes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Productstatistics',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('totalview', models.IntegerField(default=0, db_column='TotalView')),
                ('totalsharing', models.IntegerField(default=0, db_column='TotalSharing')),
            ],
            options={
                'db_table': 'productstatistics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Userblock',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'userblock',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='category',
            options={'managed': False, 'verbose_name': 'Category'},
        ),
    ]
