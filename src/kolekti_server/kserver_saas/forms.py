# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2016 Stéphane Bonhomme (stephane@exselt.com)
import logging
logger = logging.getLogger('kolekti.'+__name__)

from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm
from django.utils.text import get_valid_filename

from kserver_saas.models import Project

class UserProfileForm(forms.Form):
    firstname = forms.CharField(max_length = 32, required = False, label = "Prénom")
    lastname  = forms.CharField(max_length = 32, required = False, label = "Nom")
    company = forms.CharField(max_length = 255, required = False, label = "Société")
    address = forms.CharField(widget=forms.Textarea, required = False, label="Adresse")
    city = forms.CharField(max_length = 255,  required = False, label="Ville")
    zipcode = forms.CharField(max_length = 32, required = False, label="Code postal")
    phone = forms.CharField(max_length = 32,  required = False, label="Téléphone")
    

class kolektiRegistrationForm(RegistrationForm, UserProfileForm):
    cgv = forms.BooleanField(widget=forms.CheckboxInput,
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")}
                         )
        
class NewProjectForm(forms.Form):
    
    projectname = forms.CharField(max_length = 32)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        
        return super(NewProjectForm, self).__init__(*args, **kwargs)
    
    def clean_projectname(self):
        dirname = "%05d_%s"%(self.user.pk, get_valid_filename(self.cleaned_data['projectname']))
        logger.debug(dirname)
        logger.debug(self.user)
        try:
            prj = Project.objects.get(owner = self.user, directory = dirname)
            logger.debug('exists')
            raise forms.ValidationError("project already exists")
        except Project.DoesNotExist:
            return self.cleaned_data['projectname']
    
