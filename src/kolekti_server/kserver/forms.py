from django import forms
from django.utils.translation import ugettext_lazy as _
from registration.forms import RegistrationForm


class UploadFileForm(forms.Form):
    upload_file  = forms.FileField()
    path  = forms.CharField()


class kolektiRegistrationForm(RegistrationForm):
    firstname = forms.CharField(max_length = 32, required = False)
    lastname  = forms.CharField(max_length = 32, required = False)
    company = forms.CharField(max_length = 255, required = False)
    address = forms.CharField(widget=forms.Textarea, required = False)
    city = forms.CharField(max_length = 255,  required = False)
    zipcode = forms.CharField(max_length = 32, required = False)
    phone = forms.CharField(max_length = 32,  required = False)
    cgv = forms.BooleanField(widget=forms.CheckboxInput,
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")}
                         )
        
class NewProjectForm(forms.Form):
    projectname = forms.CharField(max_length = 32)
#    template = forms.ModelChoiceField(queryset = Template.objects.filter(pack__name="saas"))
    
    
