import os
import time
import sys
#import paste
#from paste import httpserver
import cherrypy
from threading import Thread
import wx
import json


TB_CLOSE = wx.NewId()
TB_RESTART = wx.NewId()
TB_ST_FF = wx.NewId()
TB_ST_AMAYA = wx.NewId()
TB_ST_INKSCAPE = wx.NewId()




class KolektiHttp(Thread):
    def run(self):
        from kolekti_server.wsgi import application
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

if __name__ == '__main__':

    # get userdir
    userdir = os.path.expanduser("~")
    print userdir
    configfile = os.path.join(userdir,".kolekti")
    # check config
    try:
        with open(configfile) as f:
            conf_dict = json.load(f)
        print "config.json ok"
    except:
        print "config.json not found"
        try:
            print "reading ini file"
            import ConfigParser
            Config = ConfigParser.ConfigParser()
            Config.read("kolekti.ini")
            projects_path = Config.get('InstallSettings','projectspath')
            print "reading ini file done", projects_path
        except:
            import traceback
            print traceback.format_exc()
            projects_path = "C:\\kolekti\\projects"
        conf_dict= {"projects_dir": projects_path,
                    "active_project":""}
        with open(configfile,"w") as f:
            f.write(json.dumps(conf_dict))
        print "%s config.json w"%os.getcwd() 
    print conf_dict
    systray = KolektiTray()
    systray.MainLoop()
    sys.exit(0)
