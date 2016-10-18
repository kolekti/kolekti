# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
import os
import logging
logger = logging.getLogger('kolekti.'+__name__)
    
from django.conf import settings
from django.http import HttpResponseRedirect
from django.forms.models import model_to_dict
from django.views.generic import View, TemplateView
from django.dispatch import receiver
from django.shortcuts import render
from django.utils.text import get_valid_filename
from registration.signals import user_registered, user_activated
from registration.backends.default.views import RegistrationView as DefaultRegistrationView

from kserver_saas.models import UserProfile, Pack, Project

from kserver_saas.models import UserProfile, Pack, Template, UserProject, Project
from kserver.views import kolektiMixin
from kserver_saas.forms import kolektiRegistrationForm, NewProjectForm, UserProfileForm
#from kserver.svnutils import SVNUserManager, SVNProjectCreator
from kserver_saas.svnutils import SVNProjectCreator
from kolekti.synchro import SVNProjectManager, ExcSyncNoSync

class KolektiSaasMixin(object):
    def _project_starters(self, user, from_form = None, from_template = None):
        starters = []
        for pack in Pack.objects.all():
            for template in pack.templates.all():
                if unicode(template.pk) == from_template:
                    logger.debug('from template')
                    form = from_form
                else:
                    form = NewProjectForm(user = user)
                starters.append({'name':template.name,
                                 'description':template.description,
                                 'pack':pack.description,
                                 'id':template.pk,
                                 'idpack':pack.pk,
                                 'form':form})
        # logger.debug(starters)
        # TODO : add remote svn account  if ingroup user, remotesvn
        return starters

class KolektiSaasMiddleware(KolektiSaasMixin):
    """ redirects to project vcreation when no currect project is set
        sets request.kolekti_userproject and request.kolekti_projectpath
    """
    def process_request(self,request):
        request.kolekti_userproject = None
        request.kolekti_projectpath = ''

        
        if request.path[:7] == '/admin/':
            return None
        
        if request.user.is_authenticated():
            try:
                request.kolekti_userproject = request.user.userprofile.activeproject
                request.kolekti_projectpath = os.path.join(settings.KOLEKTI_BASE, request.user.username, request.kolekti_userproject.project.directory)
        
            except:    
                logger.warning('user %s has no active_project', str(request.user))
                return None
                return render(request,'welcome.html', dictionary={"project_starters":self._project_starters(request.user)})
        return None


class SaasProjectsView(KolektiSaasMixin, kolektiMixin, View):
    template_name = "welcome.html"

        
    def get(self, request, require_svn_auth=False, project_folder="", project_url=""):
        
        context = self.get_context_data({
            "require_svn_auth":require_svn_auth,
            "project_starters":self._project_starters(request.user),
            "projecturl":"",
        })
            
        return self.render_to_response(context)

    def post(self, request):
        ## return post from one of the starters list
        form = NewProjectForm(request.POST, user = request.user)
        template_id = request.POST.get('template_id')
        logger.debug(request.POST)
        logger.debug('----------------')
        if form.is_valid():
            template = Template.objects.get(pk = template_id)
            project_directory = "%05d_%s"%(request.user.pk, get_valid_filename(form.cleaned_data['projectname']))

            logger.debug('--------------- create svn repository')            
            # create svn project
#            pm = SVNProjectCreator()
#            pm.create_from_template(template.svn, project_directory, request.user.username)
            logger.debug('--------------- create project object')
            
            project = Project(name = form.cleaned_data['projectname'],
                              description = "Saas demo project",
                              directory = project_directory,
                              owner = request.user,
                              template = template
                              )
                              
            project.save()
            
            logger.debug('--------------- create user project')
            # adds user to project
            up = UserProject(user = request.user,
                             project = project,
                             is_saas = True,
                             is_admin = True)
                             
            up.save()
            logger.debug('--------------- set kolekti project')
            projectpath = os.path.join(settings.KOLEKTI_BASE, request.user.username, project.directory)
            self.set_project(projectpath)
            logger.debug('--------------- activate')
            self.project_activate(up)
            logger.debug('--------------- end ')
            return HttpResponseRedirect('/') 
        else:
            context = self.get_context_data({
                "project_starters":self._project_starters(request.user, form, template_id),
                "projecturl":"",
            })
            
        return self.render_to_response(context)

class UserProfileView(kolektiMixin, View):
    template_name = "registration/profile.html"
    def get(self, request):
        profile = request.user.userprofile
        profile_dict = model_to_dict(profile)
        profile_dict.update({
            "firstname":request.user.first_name,
            "lastname":request.user.last_name
        })
        
        form = UserProfileForm(profile_dict)
        context = self.get_context_data()
        context.update({
            "form" : form
            })
        return self.render_to_response(context)

    def post(self, request):
        form = UserProfileForm(request.POST)
        if form.is_valid():
            request.user.first_name = form.cleaned_data['firstname']
            request.user.last_name = form.cleaned_data['lastname']
            request.user.save()
            up = request.user.userprofile
            up.company = form.cleaned_data['company']
            up.address = form.cleaned_data['address']
            up.city = form.cleaned_data['city']
            up.zipcode = form.cleaned_data['zipcode']
            up.phone = form.cleaned_data['phone']
            up.save()
            return HttpResponseRedirect('/')
        else:
            context = self.get_context_data()
            context.update({
                "form" : form
            })
            return self.render_to_response(context) 
        
class RegistrationView(DefaultRegistrationView):
    form_class = kolektiRegistrationForm
            
    def register(self,request, **cleaned_data):
        
        user = super(RegistrationView, self).register(request, **cleaned_data)
        #svnum = SVNUserManager()
        user.firstname = cleaned_data['firstname']
        user.lastname = cleaned_data['lastname']
        user.save()
        #svnum.add_user(user.username, cleaned_data['password1'])
        return user
        
        
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




    
