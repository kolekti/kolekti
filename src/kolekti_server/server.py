import os
import time
import sys
#import paste
#from paste import httpserver
import cherrypy
from threading import Thread
import wx
import json

import webbrowser


TB_CLOSE = wx.NewId()
TB_RESTART = wx.NewId()
TB_ST_FF = wx.NewId()
TB_ST_AMAYA = wx.NewId()
TB_ST_INKSCAPE = wx.NewId()




class KolektiHttp(Thread):
    def run(self):
        from kolekti_server.wsgi import application

        cp_config = {'global': {
                'log.screen': True,
                'log.error_file': 'kolekti.err',
                'log.access_file': 'kolekti.log'
                }}

        cherrypy.config.update(cp_config)
        cherrypy.tree.graft(application, '/')        
        
        # Unsubscribe the default server
        cherrypy.server.unsubscribe()

        # Instantiate a new server object
        server = cherrypy._cpserver.Server()

        # Configure the server object
        server.socket_host = "127.0.0.1"
        server.socket_port = 8080
        server.thread_pool = 30

        # For SSL Support
        # server.ssl_module            = 'pyopenssl'
        # server.ssl_certificate       = 'ssl/certificate.crt'
        # server.ssl_private_key       = 'ssl/private.key'
        # server.ssl_certificate_chain = 'ssl/bundle.crt'
        
        # Subscribe this server
        server.subscribe()

        # Start the server engine 
        cherrypy.engine.start()
        cherrypy.engine.block()

class KolektiTray(wx.App):
    def OnInit(self):
        try: 
            self.icon = wx.Icon('kolekti.ico', wx.BITMAP_TYPE_ICO)
            self.tb = wx.TaskBarIcon()
            self.tb.SetIcon(self.icon, "Kolekti Server")
            self.tb.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnRightClick)
            wx.EVT_MENU(self.tb, TB_CLOSE, self.kexit)
            self.httpThread = KolektiHttp()
            self.httpThread.daemon = True
            self.httpThread.start()
            webbrowser.open_new('http://localhost:8080')
        except :
            self.OnException()
            
        return True

    def OnRightClick(self, event):
        try:
            menu = wx.Menu()
            menu.Append(TB_CLOSE, "Arreter Kolekti Serveur")
            self.tb.PopupMenu(menu)
            menu.Destroy()
        except:
            self.OnException()

    def OnException(self):
        time.sleep(3)
        self.kexit()

    def kexit(self, event=None):
        self.httpThread._Thread__stop()
        self.httpThread.join()
        self.tb.Destroy()
        self.looping = False
        
    def MainLoop(self):
        self.looping = True
        myEventLoop = wx.EventLoop()
        prevEventLoop = wx.EventLoop.GetActive()
        wx.EventLoop.SetActive(myEventLoop)
        
        lastCheck = 0
        while self.looping:
            # Process GUI events last
            while myEventLoop.Pending():
                myEventLoop.Dispatch()
                
            time.sleep(0.1)
            self.ProcessIdle()
        wx.EventLoop.SetActive(prevEventLoop)


def bootstrap():
    
    # registers kolekti projects in windows libraries
    os.environ['DJANGO_SETTINGS_MODULE']='kolekti_server.settings'
    
    import shutil
    from lxml import etree as ET
    import django
    from django.conf import settings

    if not os.path.exists(os.path.join(settings.KOLEKTI_BASE, '.logs')):
        os.makedirs(os.path.join(settings.KOLEKTI_BASE, '.logs'))
    
    django.setup()
    from django.contrib.auth.models import User
    from kserver_saas.models import Project, UserProfile, UserProject
    from django.core import management
    from django.core.exceptions import ObjectDoesNotExist

    
    if os.path.exists(settings.DB_NAME):
        shutil.move(settings.DB_NAME, settings.DB_NAME+"_backup")
    management.call_command('migrate', verbosity=0, interactive=False)
    management.call_command('loaddata','singleuser', verbosity=0, interactive=False)
    user = User.objects.get()

    for project_dir in os.listdir(os.path.join(settings.KOLEKTI_BASE)):
        print project_dir
        try:
            project_path = os.path.join(settings.KOLEKTI_BASE, project_dir)
            project_settings = ET.parse(os.path.join(project_path, 'kolekti', 'settings.xml')).getroot()
            if project_settings.xpath('string(/settings/@version)') != '0.7':
                continue
            lang = project_settings.xpath('string(/settings/@sourcelang)')
            try:
                project = Project.objects.get(directory = project_dir)
            except ObjectDoesNotExist:
                project = Project(
                    name = project_dir,
                    directory = project_dir,
                    description = project_dir,
                    owner = user,
                    )
                project.save()
            try:
                userproject = UserProject.objects.get(
                    project = project,
                    user = user
                    )
            except ObjectDoesNotExist:
                userproject = UserProject(
                    project = project,
                    user = user,
                    is_saas = False,
                    is_admin = True,
                    srclang = lang,
                    publang = lang
                    )
                userproject.save()
            
            userprofile = UserProfile.objects.get()
            userprofile.activeprojects = userproject
            userprofile.save()

        except:
            import traceback
            print traceback.format_exc()
            continue

if __name__ == '__main__':
    if len(sys.argv) == 1:
        systray = KolektiTray()
        systray.MainLoop()
    else:
        if sys.argv[1] == "bootstrap":
            bootstrap()
        else:
            sys.exit(1)
    sys.exit(0)
