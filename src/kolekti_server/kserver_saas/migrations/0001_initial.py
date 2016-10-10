# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateField()),
                ('active', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField()),
                ('price', models.IntegerField()),
                ('users_saas', models.IntegerField()),
                ('users_svn', models.IntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('directory', models.CharField(max_length=32)),
                ('description', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReleaseFocus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('release', models.CharField(max_length=254)),
                ('assembly', models.CharField(max_length=30)),
                ('lang', models.CharField(max_length=5)),
                ('state', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reportname', models.CharField(max_length=255)),
                ('hashid', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('svn', models.CharField(max_length=255)),
                ('svn_user', models.CharField(default=b'', max_length=255)),
                ('svn_pass', models.CharField(default=b'', max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('company', models.CharField(default=b'', max_length=255)),
                ('address', models.TextField(default=b'', blank=True)),
                ('zipcode', models.CharField(default=b'', max_length=32, blank=True)),
                ('city', models.CharField(default=b'', max_length=255, blank=True)),
                ('phone', models.CharField(default=b'', max_length=32, blank=True)),
                ('created', models.DateField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserProject',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('is_saas', models.BooleanField(default=False)),
                ('is_admin', models.BooleanField(default=False)),
                ('srclang', models.CharField(max_length=5)),
                ('publang', models.CharField(max_length=5)),
                ('project', models.ForeignKey(to='kserver_saas.Project')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='activeproject',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, default=None, blank=True, to='kserver_saas.UserProject', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='sharelink',
            name='project',
            field=models.ForeignKey(to='kserver_saas.UserProject'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='project',
            name='template',
            field=models.ForeignKey(to='kserver_saas.Template'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='pack',
            name='templates',
            field=models.ManyToManyField(to='kserver_saas.Template'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='pack',
            field=models.ForeignKey(to='kserver_saas.Pack'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='project',
            field=models.ForeignKey(to='kserver_saas.Project'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]
