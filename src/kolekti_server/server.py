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
                'log.screen': False,
                'log.error_file': '',
                'log.access_file': ''
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
    try:
        import pythoncom
        from win32com.shell import shell, shellcon

        lib = pythoncom.CoCreateInstance(shell.CLSID_ShellLibrary, None, pythoncom.CLSCTX_INPROC, shell.IID_IShellLibrary)
        try:
            lib.SaveInKnownFolder(shell.FOLDERID_Libraries,"kolekti",shellcon.LSF_FAILIFTHERE)
        except:
            pass
        # adds projects folders to library
        from kolekti.settings import settings
        s = settings()
        projectpath = s['InstallSettings']['projectspath']
        for prj in os.listdir(projectpath):
            item = shell.SHCreateItemFromParsingName(os.path.join(projectpath, prj),
                                                     None,
                                                     shell.IID_IShellItem)
            lib.AddFolder(item)
        lib.Commit()

    except:
        pass

if __name__ == '__main__':
    if len(sys.argv) == 1:
        systray = KolektiTray()
        systray.MainLoop()
        sys.exit(0)
    else:
        if sys.argv[1] == "bootstrap":
            bootstrap()

