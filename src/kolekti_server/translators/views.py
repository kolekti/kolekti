import os
import json
import tempfile
from lxml import etree as ET

from django.views.static import serve
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.generic import View,TemplateView, ListView
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives

import logging
logger = logging.getLogger('kolekti.'+__name__)

# kolekti imports

from kserver_saas.models import Project, UserProject
from kserver.views import LoginRequiredMixin, ReleaseAllStatesView

from models import TranslatorRelease
from forms import UploadTranslationForm

from kolekti.common import kolektiBase, KolektiValidationError
from kolekti.publish import ReleasePublisher
from kolekti.translation import  TranslationImporter

def in_translator_group(user):
    if user:
        return user.groups.filter(name='translator').count() == 1
    return False

class TranslatorsSharedMixin(kolektiBase):
   
    def project(self, project):
        projectpath = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project)
        # up = UserProject.objects.get(user = self.request.user, project__directory = project)
        self.set_project(projectpath, self.request.user.username)
        # self.project_activate(up)
        
    def project_languages(self, project):
        try:
            project_settings = ET.parse(os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project, 'kolekti','settings.xml'))
            return ([l.text for l in project_settings.xpath('/settings/languages/lang')],
                    [l.text for l in project_settings.xpath('/settings/releases/lang')],
                    project_settings.xpath('string(/settings/@sourcelang)'))
        except IOError:
            return ['en'],['en','fr','de'],'en'
        except AttributeError:
            return ['en'],['en','fr','de'],'en'


        

    
class TranslatorsMixin(TranslatorsSharedMixin):
    @method_decorator(user_passes_test(in_translator_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(TranslatorsMixin,  self).dispatch(*args, **kwargs)

    def send_mail_translation_added(self, project, release, lang, user):
        dst = [up.user.email for up in UserProject.objects.filter(project__directory = project, is_admin = True)]
        mail_params = {
            'hostname':settings.HOSTNAME,
            'project':project,
            'release':release,
            'lang':lang,
            'user':user.username,
            'useremail':user.email,
            }
        subject = '[kolekti] new translation %s [%s]'%(release,lang)

        text_content = """
        Dear kolekti user,
        
        %(user)s added a  new translation [%(lang)s] of the release %(release)s in the project %(project)s

        https://%(hostname)s/translators/%(project)s/%(release)s/

        You are recevieng this email because you are adminstrator for the project %(project)s on  %(hostname)s. This email has been automatically generated, please do not reply.

        The Kolekti Team.
        """%mail_params
        
        html_content = """
        <p>Dear kolekti user,</p>
        
        <p><a href="mailto:%(useremail)s">%(user)s</a> added a new translation [%(lang)s] of the release <em>%(release)s</em> in the project <em>%(project)s</em>.

        <a href="https://%(hostname)s/translators/%(project)s/%(release)s/">Open in kolekti</a> or copy the link in your web browser<p>
        <pre>https://%(hostname)s/translators/%(project)s/%(release)s/</pre>
        <p><small>You are recevieng this email because you are adminstrator for the project %(project)s on %(hostname)s. This email has been automatically generated, please do not reply.</small></p>

        The Kolekti Team.
        """%mail_params

        msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, dst, cc=[user.email])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

class TranslatorsHomeView(TranslatorsMixin, TemplateView):
    template_name = "translators_home.html"
    def get(self, request, project = None, release = None):
        if project is None:
            releases = TranslatorRelease.objects.filter(user = request.user).order_by("project")
        else:
            releases = TranslatorRelease.objects.filter(user = request.user, project__directory = project)
            if release is not None:
                releases = releases.filter(release_name = release)
        context = {'releases':[]}
        for release in releases:
            context['releases'].append({
                'self' : release,
                'langs': self.project_languages(release.project.directory)
                })
            
        return self.render_to_response(context)

class TranslatorsReleaseStatusesView(TranslatorsMixin, ReleaseAllStatesView):
    def get(self, request, project):
        self.project(project)        
        return super(TranslatorsReleaseStatusesView, self).get(request)
    
class TranslatorsLangsView(TranslatorsMixin, View):
    def get(self, request, project):
        return HttpResponse(json.dumps(self.project_languages(project)),content_type="application/json")

class TranslatorsDocumentsView(TranslatorsMixin, View):
    def get(self, request, project):
        logger.debug('documents')
        release_path = request.GET.get('release')
        assembly_name = release_path.rsplit('/',1)[1]
        lang = request.GET.get('lang',"")
        projectpath = os.path.join(settings.KOLEKTI_BASE, request.user.username, project)
        publisher = ReleasePublisher(release_path, projectpath, langs = [lang])
        res = [(l, p.replace('/releases/',''), e) for l, p, e in publisher.documents_release(assembly_name)]
        logger.debug(res)
        return HttpResponse(json.dumps(res),content_type="application/json")
        
class TranslatorsPublishView(TranslatorsMixin, View):
    def get(self, request, project):
        try:
            release_path = request.GET.get('release')
            assembly_name = release_path.rsplit('/',1)[1]
            lang = request.GET.get('lang',"")
            projectpath = os.path.join(settings.KOLEKTI_BASE, request.user.username, project)
            publisher = ReleasePublisher(release_path, projectpath, langs = [lang])
            res = list(publisher.publish_assembly(assembly_name + "_asm"))
        except:
            logger.exception('translators publication error [%s/%s]'%(project,release_path))
            res = {'status':'error'}
            
        return HttpResponse(json.dumps(res),content_type="application/json")
        
class TranslatorsSourceZipView(TranslatorsMixin, View):
    def get(self, request, project, release):
        sourcelang = request.GET.get('lang')
        projectpath = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project)
        self.set_project(projectpath)
        zipname = "%s_%s_%s"%(project, release, sourcelang)
        # to be set with release sourcelang
        langs = [sourcelang]
        z = self.zip_release(release, langs)
        response = HttpResponse(z, content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s.zip"%(zipname,)
        return response

class TranslatorsSourceAssemblyView(TranslatorsMixin, View):
    def get(self, request, project, release):
        lang = request.GET.get('lang')
        assembly = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, 'releases', release,'sources',lang, 'assembly',release+'_asm.html')
        return serve(request, os.path.basename(assembly), os.path.dirname(assembly))

class TranslatorsAssemblyUploadView(TranslatorsMixin, View):
    def post(self, request, project, release):
        res=[]
        form = UploadTranslationForm(request.POST, request.FILES)
        logger.debug(form.is_valid())
        if form.is_valid():
            self.project(project)
            uploaded_file = request.FILES[u'upload_file']
            path = tempfile.mkdtemp()
            with open(os.path.join(path,uploaded_file.name), "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            try:
                importer = TranslationImporter(project_path)
                with open(os.path.join(path, uploaded_file.name)) as f:
                   src = f.read() 

                assembly_info = importer.import_assembly(src, dry_run = True)
                
            except KolektiValidationError, e:                
                logger.exception('error in translation import')
                return HttpResponse(json.dumps({"status":"error","message":str(e)}),content_type="text/plain")

            except:
                logger.exception('unexpected error in translation import')
                return HttpResponse(json.dumps({"status":"error","message":str(e)}),content_type="text/plain")

            return HttpResponse(json.dumps({"status":"success","message":'upload successful'}),content_type="text/plain")
        else:
            logger.debug(form)
            return HttpResponse(json.dumps({"status":"error","message":"select a file"}),content_type="text/plain")
    
class TranslatorsUploadView(TranslatorsMixin, View):
    def post(self, request, project, release):
        res=[]
        form = UploadTranslationForm(request.POST, request.FILES)
        logger.debug(form.is_valid())
        if form.is_valid():
            self.project(project)
            uploaded_file = request.FILES[u'upload_file']
            lang = request.POST['lang']
            path = tempfile.mkdtemp()
            logger.debug(path)
            logger.debug(dir(uploaded_file))
            with open(os.path.join(path,uploaded_file.name), "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
#            self.write_chunks(uploaded_file.chunks, path +'/'+ uploaded_file.name, mode = "wb") 
            try:
                project_path = os.path.join(settings.KOLEKTI_BASE, request.user.username, project)

                importer = TranslationImporter(project_path)
                files = importer.import_files(path, uploaded_file.name, uploaded_file.content_type, release, lang)
                importer.commit(files)
                
            except KolektiValidationError, e:                
                logger.exception('error in translation import')
                return HttpResponse(json.dumps({"status":"error","message":str(e)}),content_type="text/plain")

            except:
                logger.exception('unexpected error in translation import')
                return HttpResponse(json.dumps({"status":"error","message":str(e)}),content_type="text/plain")

            return HttpResponse(json.dumps({"status":"success","message":'upload successful'}),content_type="text/plain")
        else:
            logger.debug(form)
            return HttpResponse(json.dumps({"status":"error","message":"select a file"}),content_type="text/plain")

        
class TranslatorsCommitLangView(TranslatorsMixin, View):
    def post(self, request, project, release, lang):
        releasedir = '/'.join(['/releases', release, 'sources', lang])
        assembly = '/'.join([releasedir, 'assembly',release+'_asm.html'])
        state = "publication"
        self.project(project)
        try:
            self.syncMgr.add_resource(releasedir)
        except:
            logger.debug('resource already added')
        self.syncMgr.propset("release_state", state, assembly)
        commitmsg = 'validate translation'
        self.syncMgr.commit(releasedir, commitmsg)
        self.send_mail_translation_added(project, release, lang, request.user)
        
        return HttpResponse(json.dumps({"status":"success","message":'Translation completed'}),content_type="text/plain")




class TranslatorsStaticView(TranslatorsMixin, View):
    def get(self, request, project, release, path):
        logger.debug('translators static')
        try:
            try:
                TranslatorRelease.objects.get(user = request.user, project__directory = project, release_name = release)
            except TranslatorRelease.DoesNotExist:
                return HttpResponse(status=404)            
            projectpath = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project)
            path = "/releases/"+release+"/"+path
            logger.debug("serve %s/%s", path, projectpath)
            return serve(request, path, projectpath)
        except:
            logger.exception('static error')
            return HttpResponse(status=500)            



# TRanslation assignment, for admin users of project
        
class TranslatorsAdminMixin(TranslatorsSharedMixin):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(TranslatorsAdminMixin, cls).as_view(**initkwargs)
        if settings.KOLEKTI_MULTIUSER:
            return login_required(view)
        else:
            return view
    
class TranslatorsAdminView(TranslatorsAdminMixin, TemplateView):
    template_name = "translators_admin.html"
    def get(self, request, project):
        try:
            uesrproject = UserProject.objects.get(user = request.user, project__directory = project, is_admin = True)
        except  UserProject.DoesNotExist:
            return HttpResponse(status=401)
        releasepath = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, 'releases')
        releases = []
        for release in os.listdir(releasepath):
            releaseinfo = {'langs':[], 'name':release}
            for lang in os.listdir(os.path.join(releasepath, release, 'sources')):
                    assemblypath = os.path.join(releasepath, release, 'sources', lang, 'assembly', release + '_asm.html')
                    if os.path.exists(assemblypath):
                        releaseinfo['langs'].append({'lang': lang})
                    
            releaseinfo.update({
                'translators': TranslatorRelease.objects.filter(release_name = release, project__directory = project)
                })
            releases.append(releaseinfo) 
        context = {
            'translators': User.objects.filter(groups__name='translator'),
            'releases':releases,
            'languages':self.project_languages(project),
            'project': Project.objects.get(directory = project)
            }            
        return self.render_to_response(context)

class TranslatorsAdminAddView(TranslatorsAdminMixin, TemplateView):
    def post(self, request, project, release):
        username = request.POST.get('translator')
        user = User.objects.get(username = username)
        _project = Project.objects.get(directory = project)
        try:
            tr = TranslatorRelease.objects.get(release_name = release, user = user, project = _project)
        except TranslatorRelease.DoesNotExist:
            # checkout 
                    
            tr = TranslatorRelease.objects.create(project = _project, release_name = release, user = user)
            tr.save()
        return HttpResponseRedirect(reverse('translators_admin', kwargs = {'project':project}))

class TranslatorsAdminRemoveView(TranslatorsAdminMixin, TemplateView):
    def post(self, request, project, release):
        username = request.POST.get('translator')
        user = User.objects.get(username = username)
        try:
            tr = TranslatorRelease.objects.get(release_name = release, project__directory = project, user = user)
            logger.debug(tr)
            tr.delete()
            
        except TranslatorRelease.DoesNotExist:
            logger.debug('not found')
        return HttpResponseRedirect(reverse('translators_admin', kwargs = {'project':project}))
    
