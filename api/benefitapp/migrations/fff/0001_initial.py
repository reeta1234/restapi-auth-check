# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Albums',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=50, null=True, db_column='Title', blank=True)),
                ('description', models.CharField(max_length=500, null=True, db_column='Description', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'albums',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=50, db_column='name')),
                ('description', models.CharField(max_length=255, null=True, db_column='description', blank=True)),
                ('create_date', models.DateTimeField(default=datetime.datetime(2016, 1, 19, 10, 44, 19, 825848), db_column='create_date')),
            ],
            options={
                'db_table': 'category',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('comment', models.CharField(max_length=500, null=True, db_column='Comment', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'comments',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Documents',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=75, null=True, db_column='Title', blank=True)),
                ('description', models.CharField(max_length=500, null=True, db_column='Description', blank=True)),
                ('docurl', models.CharField(max_length=100, null=True, db_column='DocUrl', blank=True)),
                ('scope', models.CharField(max_length=1, null=True, db_column='Scope', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'documents',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Favorites',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('type', models.CharField(default='F', max_length=1, db_column='Type')),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'favorites',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Followings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'followings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Galary',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=45, null=True, db_column='Title', blank=True)),
                ('imageurl', models.CharField(max_length=100, null=True, db_column='ImageUrl', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'galary',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Imagetag',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('tagtext', models.CharField(max_length=255, db_column='TagText')),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'imagetag',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Messages',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('message', models.CharField(max_length=500, null=True, db_column='Message', blank=True)),
                ('readdate', models.DateTimeField(null=True, db_column='ReadDate', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
                ('messagecol', models.CharField(max_length=45, null=True, db_column='Messagecol', blank=True)),
            ],
            options={
                'db_table': 'messages',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=100, null=True, db_column='Title', blank=True)),
                ('description', models.CharField(max_length=250, null=True, db_column='Description', blank=True)),
                ('scope', models.CharField(max_length=1, db_column='Scope')),
                ('type', models.CharField(max_length=1, db_column='Type')),
                ('posturl', models.CharField(max_length=100, null=True, db_column='PostUrl', blank=True)),
                ('thumbnailurl', models.CharField(max_length=100, null=True, db_column='ThumbnailUrl', blank=True)),
                ('length', models.CharField(max_length=20, null=True, db_column='Length', blank=True)),
                ('poststatus', models.IntegerField(default=0, db_column='PostStatus')),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'verbose_name': 'post',
                'db_table': 'post',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Postcategory',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'postcategory',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Postlikes',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'postlikes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Postratings',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('rating', models.DecimalField(null=True, decimal_places=1, max_digits=2, db_column='Rating', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'postratings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Postsharings',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('profileid', models.IntegerField(null=True, db_column='ProfileId', blank=True)),
                ('sharedto', models.CharField(max_length=50, null=True, db_column='SharedTo', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'postsharings',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Poststatistics',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('totalview', models.IntegerField(default=0, db_column='TotalView')),
                ('totalrating', models.IntegerField(default=0, db_column='TotalRating')),
                ('totallike', models.IntegerField(default=0, db_column='TotalLike')),
                ('totalsharing', models.IntegerField(default=0, db_column='TotalSharing')),
            ],
            options={
                'db_table': 'poststatistics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Products',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('title', models.CharField(max_length=50, null=True, db_column='Title', blank=True)),
                ('description', models.CharField(max_length=500, null=True, db_column='Description', blank=True)),
                ('price', models.DecimalField(null=True, decimal_places=2, max_digits=6, db_column='Price', blank=True)),
                ('imageurl', models.CharField(max_length=100, null=True, db_column='ImageUrl', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'verbose_name': 'Product',
                'db_table': 'products',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Profileanswers',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('answer', models.CharField(max_length=500, null=True, db_column='Answer', blank=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'profileanswers',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Profilecategory',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'profilecategory',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Profiles',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('firstname', models.CharField(max_length=45, null=True, db_column='FirstName')),
                ('lastname', models.CharField(max_length=45, null=True, db_column='LastName', blank=True)),
                ('gender', models.CharField(max_length=1, null=True, db_column='Gender', blank=True)),
                ('age', models.CharField(max_length=10, null=True, db_column='Age', blank=True)),
                ('profilephoto', models.CharField(max_length=50, null=True, db_column='ProfilePhoto', blank=True)),
                ('bio', models.TextField(null=True, db_column='Bio', blank=True)),
                ('type', models.CharField(max_length=1, null=True, db_column='Type', blank=True)),
                ('location', models.CharField(max_length=45, null=True, db_column='Location', blank=True)),
                ('referalcode', models.CharField(max_length=10, null=True, db_column='ReferalCode', blank=True)),
                ('defaultpage', models.CharField(max_length=75, null=True, db_column='DefaultPage', blank=True)),
                ('updatedate', models.DateTimeField(null=True, db_column='UpdateDate', blank=True)),
            ],
            options={
                'verbose_name': 'Profile',
                'db_table': 'profiles',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Profilestatistics',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('totalfollowers', models.IntegerField(null=True, db_column='TotalFollowers', blank=True)),
                ('totallikes', models.IntegerField(null=True, db_column='TotalLikes', blank=True)),
                ('totalpost', models.IntegerField(null=True, db_column='TotalPost', blank=True)),
                ('totalrating', models.IntegerField(null=True, db_column='TotalRating', blank=True)),
            ],
            options={
                'db_table': 'profilestatistics',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Questions',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('question', models.CharField(max_length=500, null=True, db_column='Question', blank=True)),
            ],
            options={
                'db_table': 'questions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('email', models.EmailField(max_length=100, db_column='Email')),
                ('password', models.CharField(max_length=45, db_column='Password', validators=[django.core.validators.MinLengthValidator(6)])),
                ('logintype', models.CharField(max_length=1, null=True, db_column='LoginType', blank=True)),
                ('ssotoken', models.CharField(max_length=255, db_column='SSOToken')),
                ('hash', models.CharField(max_length=100, db_column='hash')),
                ('is_active', models.IntegerField(default=0, db_column='is_active')),
                ('isfirsttimelogin', models.IntegerField(default=0, db_column='isFirstTimeLogin')),
                ('usercode', models.CharField(max_length=30, db_column='usercode')),
                ('blockuser', models.IntegerField(default=0, db_column='BlockUser')),
                ('createdate', models.DateTimeField(default=datetime.datetime(2016, 1, 19, 10, 44, 19, 822640), db_column='CreateDate')),
                ('lastlogindate', models.DateTimeField(null=True, db_column='LastLoginDate', blank=True)),
            ],
            options={
                'verbose_name': 'User',
                'db_table': 'users',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='userSocailProfile',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('profiletype', models.CharField(max_length=1, null=True, db_column='profileType', blank=True)),
                ('profileid', models.CharField(max_length=255, null=True, db_column='profileId', blank=True)),
            ],
            options={
                'db_table': 'userSocailProfile',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Videoviewhistory',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('createdate', models.DateTimeField(null=True, db_column='CreateDate', blank=True)),
            ],
            options={
                'db_table': 'videoviewhistory',
                'managed': False,
            },
        ),
    ]
