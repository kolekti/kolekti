import logging
logger = logging.getLogger('kolekti.'+__name__)

from django import forms

class UploadTranslationForm(forms.Form):
    upload_file  = forms.FileField()
    lang  = forms.CharField()

class UploadAssemblyForm(forms.Form):
    upload_file  = forms.FileField()
