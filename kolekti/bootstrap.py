# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
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


""" Bootstrap script """

__author__ = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os
import shutil
import re
import gettext

from lxml import etree as ET
 
from kolekti.kolekticonf import conf
from kolekti.utils.i18n.i18n import tr

class BootstrapLib:

    def __init__(self):
        self.fmkui = os.path.join(conf.get('fmkdir'), 'utils', 'ui', 'lib')
        self.appui = os.path.join(conf.get('appdir'), 'ui')
        self.lib = os.path.join(conf.get('basedir'), '_lib')

    def copy_libs(self):
        ''' Copy ui dirs in _lib dir of application '''
        try:
            shutil.rmtree(self.lib)
        except:
            pass
        # Create lib dir
        self.create_dir(self.lib)
        self.create_dir(os.path.join(self.lib,'kolekti'))
        self.create_dir(os.path.join(self.lib,'app'))
        # Copy framework lib
        self.copy_files(self.fmkui, True)
        # Copy application lib
        self.copy_files(self.appui)
        self.generate_i18n_files()

    def copy_files(self, path, fmk=False):
        ''' Recurcive function to copy all folders and files '''
        for dir in os.listdir(path):
            newpath = os.path.join(path, dir)

            # Replace dir by new lib dir
            if fmk:
                libpath = newpath.replace(self.fmkui, os.path.join(self.lib,'kolekti'))
            else:
                libpath = newpath.replace(self.appui, os.path.join(self.lib,'app'))

            # If path is dir we create the directory and call again the function
            if os.path.isdir(newpath):
                self.create_dir(libpath)
                self.copy_files(newpath, fmk)
            else:
                try:
                    # Try to copy file
                    shutil.copy(newpath, libpath)
                except:
                    pass

    def create_dir(self, path):
        ''' Create directory if not already exist '''
        if not os.path.exists(path):
            os.mkdir(path)

    def copy_base_template(self):
        apptpl = os.path.join(conf.get('appdir'), 'server_root', '_base_template')
        btpl = os.path.join(conf.get('basedir'), '_base_template')
        if os.path.exists(btpl):
            shutil.rmtree(btpl)
        shutil.copytree(apptpl, btpl, ignore=shutil.ignore_patterns(('.svn',)))

    def __get_i18n_scripts(self, path, i18n, ignore_patterns=(".svn")):
        """ get all i18n in scripts files """
        for ldir in os.listdir(path):
            if ldir.startswith(ignore_patterns) or ldir.endswith(ignore_patterns):
                continue
            else:
                newpath = os.path.join(path, ldir)
                if os.path.isdir(newpath):
                    self.__get_i18n_scripts(newpath, i18n, ignore_patterns)
                elif newpath[-3:] == ".js":
                    fp = open(newpath, 'r')
                    for l in fp.readlines():
                        res = re.search('i18n\("\[[0-9]+\].+"[,)]', l)
                        if res:
                            l = l[res.start()+6:res.end()-2]
                            i18n.add(l)
                    fp.close()
                    
    def generate_i18n_files(self):
        ''' Generate javascripts file for i18n '''
        confxml = ET.parse(os.path.join(conf.confdir, 'config.xml'))

        i18n = set()
        # get translation string
        self.__get_i18n_scripts(os.path.join(self.fmkui,'scripts'), i18n)
        self.__get_i18n_scripts(os.path.join(self.appui,'scripts'), i18n)

        for lang in confxml.xpath('/config/locale/lang/@value'):
            translation = gettext.translation('kolekti',conf.get('localedir'),languages=[lang])

            localepath = os.path.join(self.lib, 'kolekti', 'scripts', 'locale', lang)
            if not os.path.exists(localepath):
                os.makedirs(localepath)
            fp = open(os.path.join(localepath, 'kolekti.js'), 'w')
            buf = u"var kolekti_gettext = {"
            for msgid in i18n:
                params = {}
                for p in re.findall("%\(.+\)s", msgid):
                    code = p[2:-2]
                    params[code] = p
                msgid = msgid.decode('utf-8')
                s = tr(msgid, params)
                t = s.i18n(translation)
                buf +='"%s":'%(msgid,)
                buf +='"%s",'%(t,)
            fp.write("%s};\n\n" %buf[:-1].encode('utf-8'))
            fp.write("""function i18n(text, params) {
    var res;

    try {
        res = kolekti_gettext[text];
    } catch(e) {
        res = text;
    }

    for(var p in params)
        res = res.replace("%("+p+")s", params[p]);

    return res;
}""")
            fp.close()
