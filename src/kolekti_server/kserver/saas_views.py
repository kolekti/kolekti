# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import logging
logger = logging.getLogger(__name__)
    


from django.views.generic import View
from django.dispatch import receiver
from django.utils.text import get_valid_filename
from registration.signals import user_registered, user_activated
from registration.backends.default.views import RegistrationView as DefaultRegistrationView

from kserver.models import UserProfile, Pack
from kserver.views import kolektiMixin
from kserver.forms import kolektiRegistrationForm, NewProjectForm
from kserver.svnutils import SVNUserManager
from kolekti.synchro import SVNProjectManager, ExcSyncNoSync

class SaasProjectsView(kolektiMixin, View):
    template_name = "saas/projects.html"

    def _project_starters(self):
        starters = []
        for pack in Pack.objects.all():
            for template in pack.templates.all():
                form = NewProjectForm()
                starters.append({'name':template.name,
                                 'description':template.description,
                                 'pack':pack.description,
                                 'id':template.pk,
                                 'idpack':pack.pk,
                                 'form':form})
        #TODO : add remote svn account  if ingroup user, remotesvn
        return starters

        
    def get(self, request, require_svn_auth=False, project_folder="", project_url=""):
        
        context = self.get_context_data({
            "require_svn_auth":require_svn_auth,
            "project_starters":self._project_starters(),
            "projecturl":"",
        })
            
        return self.render_to_response(context)

    def post(self, request):

        form = NewProjectForm(request.POST)
        if form.is_valid():
            template_id = request.POST.get('template_id')
            template = Template.object.get(pk = template_id)
            # create svn project
            pm = SVNProjectManager()
            pm.create_from_template(template.svn, form.cleaned_data['projectname'], request.user.username)
            project_directory = "%5d_%s"%(request.user.pk, get_valid_filename(form.cleaned_data['projectname']))
            project = Project(name = form.cleaned_data['projectname'],
                              description = "Saas demo project",
                              directory = project_directory,
                              owner = request.user,
                              template = template
                              )
                              
                              
            # adds user to project
            up = UserProject(user =  
            # checkout project
            sync.checkout_project(project_folder, project_url)

        
        sync = SVNProjectManager(settings.KOLEKTI_BASE,username,password)
        if project_url=="":
        # create local project
            #sync.export_project(project_folder)
            self.create_project(project_folder, os.path.join(settings.KOLEKTI_BASE, self.user.username))
            self.project_activate(project_folder)
            return self.get(request)
        else:
            try:

                return self.get(request)
            except ExcSyncNoSync:
                return self.get(request, require_svn_auth=True, project_folder=project_folder, project_url=project_url)

class RegistrationView(DefaultRegistrationView):
    form_class = kolektiRegistrationForm
    def register(self,request, **cleaned_data):
        user = super(RegistrationView, self).register(request, **cleaned_data)
        svnum = SVNUserManager()
        svnum.add_user(user.username, cleaned_data['password1'])
        
        
@receiver(user_registered)
def user_registered_callback(sender, **kwargs):
    user = kwargs['user']
    request = kwargs['request']
    logger.debug("User Registered!")
    profile = UserProfile(user = user,
                          company = request.POST.get('company',''),
                          address = request.POST.get('address',''),
                          zipcode = request.POST.get('zipcode',''),
                          city = request.POST.get('city',''),
                          phone = request.POST.get('phone','')
                      )
    profile.save()
    
@receiver(user_activated)
def user_activated_callback(sender, **kwargs):
    user = kwargs['user']
    logger.debug("User Activated!")    




    
