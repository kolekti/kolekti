# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kserver', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShareLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reportname', models.CharField(max_length=255)),
                ('hashid', models.CharField(max_length=255)),
                ('project', models.ForeignKey(to='kserver.UserProject')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
