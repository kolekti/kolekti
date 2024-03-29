import os
import json
import tempfile
import urllib2
import shutil
import time
from lxml import etree as ET
import pysvn
import subprocess
import datetime

from django.views.static import serve
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.generic import View,TemplateView, ListView
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.core.mail import EmailMultiAlternatives
from django.utils.cache import add_never_cache_headers

import logging
logger = logging.getLogger('kolekti.'+__name__)

# kolekti imports

from kserver_saas.models import Project, UserProject
from kserver.views import LoginRequiredMixin, kolektiMixin, ReleaseStatesView

from .models import TranslatorRelease
from .forms import UploadTranslationForm, UploadAssemblyForm, UploadCertificateForm, CertifyDocumentForm 

from kolekti.common import kolektiBase, KolektiValidationError, KolektiValidationMissing 
from kolekti.publish import ReleasePublisher
from kolekti.translation import  TranslatorSynchro, TranslationImporter, AssemblyImporter, TranslatorInitProject

def in_translator_group(user):
    if user:
        return user.groups.filter(name='translator').count() == 1
    return False



class PostCommit(object):
        
        def get_changed(self, revision, repo):
            cmd = subprocess.Popen(['/usr/bin/svnlook', 'changed', '-r', str(revision), repo], stdout = subprocess.PIPE)
            for line in cmd.stdout.readlines():
                yield line
                
        def get_author(self, revision, repo):
            cmd = subprocess.Popen(['/usr/bin/svnlook', 'author', '-r', str(revision), repo], stdout = subprocess.PIPE)
            author = cmd.stdout.read()
            return author.strip()
                
        def handle(self, *args, **options):
            logger.debug('handle')
            try:
                from django.conf import settings
                logger.debug(str(datetime.datetime.now()))
                revision = options['revision']
                repo = options['repo']
                project = repo.split('/')[-1]
                user = self.get_author(revision, repo)
                logger.debug("author : [%s]"%user)
                
                try:
                    acllist = TranslatorRelease.objects.exclude(user__username = user).filter(project__directory = project)
                    logger.debug(acllist)
                except TranslatorRelease.DoesNotExist:
                    raise Exception('No update for "%d" ' % revision)
                seen = set()
                client = pysvn.Client()

                for mf in self.get_changed(revision, repo):
                    logger.debug(mf)
                    mf = mf[4:]
                    chunks = mf.split('/')
                    if len(chunks)>1 and chunks[0] == "releases":
                        if not chunks[1] in seen:
                            seen.add(chunks[1])
                            updates = acllist.filter(release_name = chunks[1])
                            for update in updates:
                                path = os.path.join(settings.KOLEKTI_BASE, update.user.username, update.project.directory, 'releases', update.release_name)
                                client.update(path)
                                logger.debug(path+" updated")
                    
                logger.debug('update succesfully completed')
            except:
                logger.exception('update command failed')


class TranslatorsHook(View):
    def get(self, request, rev, path):
        if 'HTTP_X_SOURCE' in request.META:
            try:
                options = {'revision':rev, 'repo':path}
                pc = PostCommit()
                pc.handle(**options)
                return HttpResponse("ok")
            except:
                logger.exception('could not execute hook')
                raise
        raise Http404
    
class TranslatorsSharedMixin(kolektiMixin):
    def get_context_data(self, data={}, **kwargs):
        try:
            context = super(kolektiMixin, self).get_context_data(**kwargs)
        except AttributeError:
            context = {}
        kolekti = None
        if 'project' in data.keys():
            project = data['project']
            project_path = os.path.join(settings.KOLEKTI_BASE, self.request.user.username, project)
            kolekti = kolektiBase(settings.KOLEKTI_BASE, self.request.user.username, project)
            
            context.update({
                'default_lang' : kolekti.project_default_language(),
            })

            if not 'lang' in data.keys():
                context.update({
                    'lang' : kolekti.project_default_language()
                })
                
        context.update({
            'user_groups': self.request.user.groups.all()
            })
        
        context.update(data)
        return context, kolekti
           
    def project_languages(self, kolekti):
        try:
            project_settings = kolekti.parse('/kolekti/settings.xml')
            return (
                sorted([l.text for l in project_settings.xpath('/settings/languages/lang')]),
                sorted([l.text for l in project_settings.xpath('/settings/releases/lang')]),
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

class TranslatorsHomeMixin(TranslatorsMixin):
    def get_context_data(self, data={}, **kwargs):
        context, kolekti = super(TranslatorsHomeMixin, self).get_context_data(data, **kwargs)

        if 'project' in data.keys():
            releases = TranslatorRelease.objects.filter(user = request.user, project__directory = project).order_by("release_name")
            if 'release' in data.keys():
                releases = releases.filter(release_name = release)
        else:
            releases = TranslatorRelease.objects.filter(user = self.request.user).order_by("project", "release_name")

        form = UploadAssemblyForm()
        context.update({'upload_form':form, 'releases':releases})
        return context, kolekti

    def post(self, request, project = None, release = None):
        res=[]
        form = UploadTranslationForm(request.POST, request.FILES)
        logger.debug(form.is_valid())
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            assembly = uploaded_file.read() 
            importer = TranslationImporter()
            if release is None:
                release = importer.guess_release(assembly)
            if project is None:
                project = TranslatorRelease.objects.get(release = release).project
                
            importer.import_assembly(assembly, check = True)
        else:
            context = {}        
            return self.render_to_response(context)
        return HttpResponseRedirect(request.path)

class TranslatorsHomeView(TranslatorsHomeMixin, TemplateView):    
    template_name = "translators_home.html"
    def get(self, request):
        context, kolekti = self.get_context_data()
        return self.render_to_response(context)

class TranslatorsProjectView(TranslatorsHomeMixin, TemplateView):    
    template_name = "translators_home.html"
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        return self.render_to_response(context)

class TranslatorsCheckUpdateView(TranslatorsMixin, TemplateView):    
    template_name = "translators_check_updates.html"
    def get(self, request):
        notifications = {}
        treleases = TranslatorRelease.objects.filter(user = self.request.user).order_by("project", "release_name")
        for trelease in treleases:
            TranslatorInitProject(self.request.user.username, trelease.project.directory)            
            context, kolekti = self.get_context_data({'project':trelease.project.directory})
            
            sync_mgr = TranslatorSynchro(*kolekti.args, release=trelease.release_name)
            notif = sync_mgr.update_release()
            notifications[trelease]=notif
            context, kolekti = self.get_context_data({'notifications':notifications})                
        return self.render_to_response(context)

class TranslatorsUpdateView(TranslatorsMixin, TemplateView):    
    template_name = "translators_check_update.html"
    def get(self, request, project, release):
        context, kolekti = self.get_context_data({'project':project, 'release':release})        
        return self.render_to_response(context)

class TranslatorsReleaseView(TranslatorsHomeMixin, TemplateView):    
    template_name = "translators_home.html"
    def get(self, request, project, release):            
        context, kolekti = self.get_context_data({'project':project, 'release':release})
        return self.render_to_response(context)
            
class TranslatorsReleaseStatusesView(TranslatorsMixin, ReleaseStatesView):
    def get(self, request, project, release):
        context, kolekti = self.get_context_data({'project':project, 'release':release})
        sync_mgr = TranslatorSynchro(*kolekti.args, release=release)  
        release_langs = self.project_languages(kolekti)[1]
        states = []
        for lang in release_langs:
            state = sync_mgr.lang_state(lang)
            if state == "source_lang":
                states.insert(0,(lang, state))
            else:
                states.append((lang, state))
        return HttpResponse(json.dumps(states),content_type="application/json")
    
class TranslatorsLangsView(TranslatorsMixin, View):
    def get(self, request, project):
        context, kolekti = self.get_context_data({'project':project})
        return HttpResponse(json.dumps(self.project_languages(kolekti)),content_type="application/json")


class TranslatorsDocumentsView(TranslatorsMixin, View):
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({'project':project, 'release':release, 'lang':lang})
        publisher = ReleasePublisher('/releases/'+release, *kolekti.args, langs = [lang])
        res = {}
        sync_mgr = TranslatorSynchro(*kolekti.args, release=release)  
        res['state'] = sync_mgr.lang_state(lang)
        res['docs'] = []
        try:
            for item in publisher.documents_release(release):
                logger.debug(item)
                l, p, r, e, t = item
                try:
                    v = kolekti.list_directory(p[1:]+'.cert')
                except OSError:
                    v = []
                
                res['docs'].append((l, p.replace('/releases/',''), e, v, t, r))
        except:
            logger.exception('could not get documents for release')
        return HttpResponse(json.dumps(res), content_type="application/json")
        
class TranslatorsPublishView(TranslatorsMixin, View):
    def get(self, request, project, release, lang):
        try:
            context, kolekti = self.get_context_data({'project':project,'release':release, 'lang':lang})
            publisher = ReleasePublisher('/releases/'+release, *kolekti.args, langs = [lang])
            return StreamingHttpResponse(
                self.format_iterator(publisher.publish_assembly(release + "_asm"), project , template = "translators_publication_iterator.html"),
                content_type="text/html"
                )

        except:
            logger.exception('translators publication error [%s/%s]'%(project,release))
            res = {'status':'error'}
            
        return HttpResponse(json.dumps(res),content_type="application/json")
        
class TranslatorsSourceZipView(TranslatorsMixin, View):
    def get(self, request, project, release, lang):
        context, kolekti = self.get_context_data({
            "project":project,
            "release":release,
            'lang':lang,
            })
        
        zipname = "%s_%s_%s"%(project, release, lang)
        z = kolekti.zip_release(release, [lang])
        response = HttpResponse(z, content_type="application/zip")
        response['Content-Disposition'] = "attachment; filename=%s.zip"%(zipname,)
        return response

class TranslatorsSourceAssemblyView(TranslatorsMixin, View):
    def get(self, request, project, release, lang):
        assembly = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, 'releases', release,'sources',lang, 'assembly',release+'_asm.html')
        return serve(request, os.path.basename(assembly), os.path.dirname(assembly))

class TranslatorsCertificatesView(TranslatorsMixin, View):
    def get(self, request, project, certpath):
        path = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases", certpath + u'.cert')
        try:
            res = list(os.listdir(path))
        except OSError:
            res=[]
        return HttpResponse(json.dumps(res))

class TranslatorsCertifyDocumentView(TranslatorsMixin, View):
    def _create_certificate(self, certpath):
        with open(os.path.join(certpath, 'kolekti.cert'), 'w') as cf:
            cert = ET.Element('cert')
            ET.SubElement(cert,'property',name="time", value=unicode(time.time()))
            ET.SubElement(cert,'property',name="author", value=self.request.user.username)
            ET.SubElement(cert,'property',name="instance", value=settings.HOSTNAME)
            cf.write(ET.tostring(cert, encoding="utf-8"))
            
            
    def post(self, request, project, release, lang):
        form = CertifyDocumentForm(request.POST)
        if form.is_valid():
            context, kolekti = self.get_context_data({
                "project":project,
                "release":release,
                })
            docpath = request.POST[u'path']
            certpath = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases", docpath + '.cert')
            doc_res = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases", docpath)
            sync_mgr = TranslatorSynchro(*kolekti.args, release = release)

            assembly_res = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases", release, "sources", lang, "assembly", release + "_asm.html")
            sync_mgr._client.propset( 'release_state', 'publication', assembly_res)
            
                # adds publications to svn
            try:
                sync_mgr._client.add(doc_res, recurse = False, add_parents = True)                
            except:
                logger.exception('Document already under version control')
                pass
            
            if not os.path.exists(certpath):
                os.makedirs(certpath)
            self._create_certificate(certpath)
            try:
                sync_mgr._client.add(certpath, recurse = True, add_parents = True)
            except:
                logger.exception('Certificate already under version control')
                pass

            release_res = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases", release)
            try:
                rev = sync_mgr._client.checkin(release_res, "translator validation", recurse = True)
                logger.debug('rev %s'%str(rev)) 
                return HttpResponse(json.dumps({"status":"success","message":'certification successful'}),content_type="text/plain")
            except:
                logger.exception('could not check in')
        return HttpResponse(json.dumps({"status":"error","message":'certification failed'}),content_type="text/plain")
    
class TranslatorsCertificateUploadView(TranslatorsMixin, View):
    def post(self, request, project, release, lang):
        form = UploadCertificateForm(request.POST, request.FILES)
        logger.debug(request.POST)
        logger.debug(form.is_valid())
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            docpath = request.POST[u'path']
#            path = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases",  release , 'certificates' , lang)
            path = os.path.join(settings.KOLEKTI_BASE, request.user.username, project, "releases", release, docpath + '.cert')
            try:
                os.makedirs(path)
            except:
                pass
            logger.debug(path)
            with open(os.path.join(path,uploaded_file.name), "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            return HttpResponse(json.dumps({"status":"success","message":'upload successful',"filename":uploaded_file.name, "path": docpath}),content_type="text/plain")        
                
        return HttpResponse(json.dumps({"status":"error","message":'upload failed'}),content_type="text/plain")
#        return HttpResponseRedirect(reverse('translators_home'))
    
class TranslatorsAssemblyUploadView(TranslatorsMixin, View):
    def post(self, request):
        res=[]
        form = UploadAssemblyForm(request.POST, request.FILES)
        
        logger.debug(form.is_valid())
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            path = tempfile.mkdtemp()
            project = request.POST.get('project', None)
            release = request.POST.get('release', None)
            lang = request.POST.get('lang', None)
            if not len(project):
                project = None
            if not len(release):
                release = None
            if not len(lang):
                lang = None
            with open(os.path.join(path,uploaded_file.name), "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
            try:
                
                importer = AssemblyImporter(settings.KOLEKTI_BASE, request.user.username, project, release)
                with open(os.path.join(path, uploaded_file.name)) as f:
                   src = f.read() 

                assembly_info = importer.import_assembly(src, lang, check = True)
                
            except KolektiValidationError, e:                
                logger.exception('error in translation import')
                return HttpResponse(json.dumps({"status":"error","message":str(e)}),content_type="text/plain")

            except KolektiValidationMissing, e:                
                logger.exception('missing information in metadata')
                return HttpResponse(json.dumps({"status":"missing","message":str(e)}),content_type="text/plain")

            except ET.XMLSyntaxError, e:
                logger.exception('XML syntax error')
                return HttpResponse(json.dumps({"status":"missing","message":"XML syntax Error : " + str(e)}),content_type="text/plain")
                          
            except:
                logger.exception('unexpected error in translation import')
                return HttpResponse(json.dumps({"status":"error","message":'unexpected error'}),content_type="text/plain")


            
            finally:
                shutil.rmtree(path)

            assembly_path = os.path.join(
                settings.KOLEKTI_BASE,
                request.user.username,
                assembly_info['project'],
                'releases',
                assembly_info['release'],
                'sources',
                assembly_info['lang'],
                'assembly',
                assembly_info['release']+ '_asm.html')
            
            sync_mgr = TranslatorSynchro(settings.KOLEKTI_BASE, request.user.username, assembly_info['project'], release = assembly_info['release'])
#            sync_mgr._client.propset("release_state", "validation", assembly_path)
            rev = sync_mgr._client.checkin(assembly_path, "translator validation")
            return HttpResponse(json.dumps({"status":"success","message":'upload successful','info':assembly_info}),content_type="text/plain")
        else:
            logger.debug(form)
            return HttpResponse(json.dumps({"status":"error","message":"select a file"}),content_type="text/plain")
    
class TranslatorsUploadView(TranslatorsMixin, View):
    def post(self, request, project, release):
        res=[]
        form = UploadTranslationForm(request.POST, request.FILES)
        logger.debug(form.is_valid())
        if form.is_valid():
            uploaded_file = request.FILES[u'upload_file']
            lang = request.POST['lang']
            path = tempfile.mkdtemp()
            with open(os.path.join(path,uploaded_file.name), "wb") as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)

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
        assembly_path = os.path.join(
            settings.KOLEKTI_BASE,
            request.user.username,
            project,
            'releases',
            release,
            'sources',
            lang,
            'assembly',
            release + '_asm.html')
        
        state = "validation"
        sync_mgr = TranslatorSynchro(settings.KOLEKTI_BASE, request.user.username, project, release)  
        sync_mgr._client.propset("release_state", state, assembly_path)
        commitmsg = 'validate translation'
        sync_mgr._client.checkin(assembly_path, commitmsg)
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
            response = serve(request, path, projectpath)
            add_never_cache_headers(response)
            return response
        except:
            logger.exception('static error')
            return HttpResponse(status=500)            


# Translation assignment, for admin users of project
        
class TranslatorsAdminMixin(TranslatorsSharedMixin):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super(TranslatorsAdminMixin, cls).as_view(**initkwargs)
        return login_required(view)
        
class TranslatorsAdminView(TranslatorsAdminMixin, TemplateView):
    template_name = "translators_admin.html"
    def get(self, request, project):
        try:
            userproject = UserProject.objects.get(user = request.user, project__directory = project, is_admin = True)
        except  UserProject.DoesNotExist:
            return HttpResponse(status=401)
        context, kolekti = self.get_context_data({'project':project})
        releases = []
        for release in kolekti.list_directory('/releases'):
            if not kolekti.exists('/releases/%s/sources'%release):
                continue
            releaseinfo = {'langs':[], 'name':release}
            for lang in kolekti.list_directory('/releases/%s/sources'%release):
                assemblypath = '/releases/%s/sources/%s/assembly/%s_asm.html'%(release, lang, release)
                if kolekti.exists(assemblypath):
                    releaseinfo['langs'].append({'lang': lang})
                    
            releaseinfo.update({
                'translators': TranslatorRelease.objects.filter(release_name = release, project__directory = project)
            })
            releases.append(releaseinfo)

        userprojects = UserProject.objects.filter(user = self.request.user)
        userproject = userprojects.get(project__directory = project)
        projects = []
        for up in userprojects:
            pproject={
                'userproject':up,
                'name':up.project.name,
                'id':up.project.pk,
            }
            projects.append(pproject)
        
        context.update({
            'translators': User.objects.filter(groups__name='translator'),
            'releases':sorted(releases, key=lambda x: x['name']),
            'filter' : True,
            #            'languages':self.project_languages(project),

            })

        return self.render_to_response(context)

class TranslatorsAdminReleaseView(TranslatorsAdminMixin, TemplateView):
    template_name = "translators_admin.html"
    def get(self, request, project, release):
        try:
            userproject = UserProject.objects.get(user = request.user, project__directory = project, is_admin = True)
        except  UserProject.DoesNotExist:
            return HttpResponse(status=401)
        context, kolekti = self.get_context_data({'project':project})
        if not kolekti.exists('/releases/%s/sources'%release):
            raise
        releaseinfo = {'langs':[], 'name':release}
        for lang in kolekti.list_directory('/releases/%s/sources'%release):
            assemblypath = '/releases/%s/sources/%s/assembly/%s_asm.html'%(release, lang, release)
            if kolekti.exists(assemblypath):
                releaseinfo['langs'].append({'lang': lang})
                    
        releaseinfo.update({
            'translators': TranslatorRelease.objects.filter(release_name = release, project__directory = project)
        })

        userprojects = UserProject.objects.filter(user = self.request.user)
        userproject = userprojects.get(project__directory = project)
        projects = []
        for up in userprojects:
            pproject={
                'userproject':up,
                'name':up.project.name,
                'id':up.project.pk,
            }
            projects.append(pproject)
        
        context.update({
            'translators': User.objects.filter(groups__name='translator'),
            'releases':[releaseinfo],
#            'languages':self.project_languages(project),
            })

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
        return HttpResponseRedirect(reverse('translators_admin_release', kwargs = {'release':release, 'project':project}))

class TranslatorsAdminRemoveView(TranslatorsAdminMixin, TemplateView):
    def post(self, request, project, release):
        username = request.POST.get('translator')
        user = User.objects.get(username = username)
        try:
            tr = TranslatorRelease.objects.get(release_name = release, project__directory = project, user = user)
            tr.delete()
            
        except TranslatorRelease.DoesNotExist:
            logger.debug('not found')
            
        return HttpResponseRedirect(reverse('translators_admin_release', kwargs = {'release':release, 'project':project}))

    
class TranslatorsAdminReleaseStatusesView(TranslatorsAdminMixin, ReleaseStatesView):
    def get(self, request, project, release):
        return super(TranslatorsAdminReleaseStatusesView, self).get(request, project, release)
