import logging
logger = logging.getLogger('kolekti.'+__name__)

from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm
from django.utils.text import get_valid_filename

from kserver.models import Project

class UploadFileForm(forms.Form):
    upload_file  = forms.FileField()
    path  = forms.CharField()


class UserProfileForm(forms.Form):
    firstname = forms.CharField(max_length = 32, required = False)
    lastname  = forms.CharField(max_length = 32, required = False)
    company = forms.CharField(max_length = 255, required = False)
    address = forms.CharField(widget=forms.Textarea, required = False)
    city = forms.CharField(max_length = 255,  required = False)
    zipcode = forms.CharField(max_length = 32, required = False)
    phone = forms.CharField(max_length = 32,  required = False)
    

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
    
