# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import logging
logger = logging.getLogger('kolekti.'+__name__)

from django.db import models
from django.contrib.auth.models import User as DefaultUser
from django.contrib.auth.hashers import (check_password, )

class User(DefaultUser):
    class Meta:
        proxy = True
        
    def check_password(self, raw_password):
        """
        Returns a boolean of whether the raw_password was correct. Handles
        hashing formats behind the scenes.
        """
        def setter(raw_password):
            self.set_password(raw_password)
            self.save(update_fields=["password"])
        return check_password(raw_password, self.password, None)
                                                            
