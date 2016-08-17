# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('kserver', '0002_sharelink'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='svn_pass',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='template',
            name='svn_user',
            field=models.CharField(default=b'', max_length=255),
            preserve_default=True,
        ),
    ]
