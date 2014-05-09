#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2010 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.



""" server module
This module contains the main server classes for kolekti framework

"""
__author__  = '''Stéphane Bonhomme <stephane@exselt.com>'''

import sys
import time
import os

from optparse import OptionParser
from threading import Thread
import kolekti.logger

try:
    import wx
except ImportError,e :
    wx = None

# from utils.userdata.sessionservice import SessionService
# from utils.userdata.profileservice import ProfileService
from kolekti.utils.locking.lockservice import LockService

from kolekti.http.threadedhttpserver import ThreadedHTTPServer
from kolekti.http.requesthandler import RequestHandler

from kolekti.kolekticonf import conf
from kolekti.bootstrap import BootstrapLib

if wx is not None:
    TB_CLOSE = wx.NewId()

class KolektiHttp(Thread):
    """ Main Thread for http requests
        Starts ThreadedHTTPServer
        Inits Lock, Session, Profile services (borgs)

    """

    _NB_THREADS = 10

    def __init__(self):
        super(KolektiHttp, self).__init__()
        try:
            BootstrapLib().copyLibs()
        except:
            pass

    def run(self):
        self._starthttp()

    def _starthttp(self, host="", port=8800, verbose=False):
        """starts a kolekti server services and http threads"""

        handler = RequestHandler
        server = ThreadedHTTPServer

        locksfile=conf.get('locksfile')

        if conf.get('lockservice'):
            LockService().initService(locksfile)
        if conf.get('sessionservice'):
            SessionService().initService()
        if conf.get('profileservice'):
            ProfileService().initService()

        directory = conf.get('basedir')
        port = conf.get('port')

        handler.AUTH_FILE = os.path.join(directory, '_conf.xml')
        handler.TMPDIR = conf.get('tmpdir')
        handler.IFACE_CLASS = None
        handler.verbose = verbose
        handler.basedir = directory
        server.verbose = verbose

        self.runner = server((host, port), handler, self._NB_THREADS)
        try:
            sys.stderr.write("Starting server\n")
            self.runner.serve_forever()
        except:
            sys.stderr.write("Stopping server\n")
        self.runner.server_close()

    def stophttp(self):
        #self.runner.server_close()
        self._Thread__stop()


class KolektiServerBatch(object):
    '''
    Main server application :
    - no systray icon (batch mode)
    - starts a http server thread.
    '''

    def MainLoop(self, daemonize=False):
        self.looping = not daemonize
        self.start()
        while self.looping:
            time.sleep(0.1)

    def exit(self, event=None):
        logger.dbgexc()
        self.httpThread.stophttp()
        logger.shutdown()
        self.looping = False

    def start(self):
        """
        Start Kolekti Server
        """
        self.httpThread = KolektiHttp()
        self.httpThread.start()


if wx is not None:
    class KolektiServer(wx.App,KolektiServerBatch):
        '''Main server application using systray commands

        sets the systray icon and manage its menu
        starts a main http server thread.
        '''

        def OnInit(self):
            """ Called at application startup

            Inits the systray menu
            Starts the main http thread

            """
            path = conf.get('appdir')
            try:

                self.icon = wx.Icon(os.path.join(path, 'kolekti.ico'), wx.BITMAP_TYPE_ICO)
                self.tb = wx.TaskBarIcon()
                self.tb.SetIcon(self.icon, "Kolekti Server Status * %s" % conf.get('tmpdir'))
                self.tb.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnRightClick)
                wx.EVT_MENU(self.tb, TB_CLOSE, self.exit)
            except:
                self.tb.Destroy()
                self.looping = False
            self.start()
            return True

        def OnRightClick(self, event):
            """ Handler for right click on systray icon
            """
            try:
                menu = wx.Menu()
                menu.Append(TB_CLOSE, "Arreter Kolekti Serveur")
                self.tb.PopupMenu(menu)
                menu.Destroy()
            except:
                self.OnException()

        def OnException(self):
            self.tb.Destroy()
            self.looping = False
            self.exit()


        def MainLoop(self):
            """ WX app main loop"""
            self.looping = True
            myEventLoop = wx.EventLoop()
            prevEventLoop = wx.EventLoop.GetActive()
            wx.EventLoop.SetActive(myEventLoop)

            while self.looping:
                # Process GUI events last
                while myEventLoop.Pending():
                    myEventLoop.Dispatch()

                    time.sleep(0.1)
                    self.ProcessIdle()

                wx.EventLoop.SetActive(prevEventLoop)


class NullDevice:
    """Fake devices for stdout and stderr"""
    def write(self,s):
        pass



if __name__ == '__main__':
    usage = "usage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-b", "--batch", help="Start kolekti without systray",
                      dest="batch", default=False, action="store_true")
    parser.add_option("-q", "--quiet", help="Disable stdout and stderr",
                      dest="quiet", default=False, action="store_true")
    (options, args) = parser.parse_args()

    if options.batch or wx is None:
        kserver = KolektiServerBatch()
    else:
        kserver = KolektiServer(clearSigInt=False)

    if options.quiet:
        sys.stderr=NullDevice()
        sys.stdout=NullDevice()
    try:
        kserver.MainLoop()
    except:
        kserver.exit()
