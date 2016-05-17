# -*- coding: utf-8 -*-
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


import os
import sys
import shutil
import logging
logger = logging.getLogger(__name__)
import re
import tempfile
import subprocess
import platform


from lxml import etree as ET
from kolekti.common import kolektiBase
from kolekti.publish_utils import PublisherMixin, PublisherExtensions, PublishException

class PluginsExtensions(PublisherExtensions):
    def __init__(self, *args, **kwargs):
        self._resdir = "."
        if kwargs.has_key('resdir'):
            self._resdir = kwargs.get('resdir')
            kwargs.pop('resdir')
        super(PluginsExtensions,self).__init__(*args, **kwargs)

    def process_path(self, path):
        return self._resdir + "/" +super(PluginsExtensions, self).process_path(path)
    
    

class plugin(PublisherMixin,kolektiBase):
    _plugin="dummy"
    LOCAL_ENCODING=sys.getfilesystemencoding()

    def __init__(self, *args, **kwargs):
        super(plugin, self).__init__(*args, **kwargs)
        self._plugin = self.__module__.split('.')[-1]
        self._plugindir = os.path.join(self._appdir,'plugins',"_%s"%self._plugin)
        self.__ext = PluginsExtensions
        logging.debug("*********** init plugin with extension %s"%self.__ext)
        self._draft = True
        
    def get_xsl(self, xslfile, **kwargs):
        logger.debug("get xsl from plugin %s"%self._plugindir)
        try:
            xslpath = '/'.join([self.assembly_dir,'kolekti','publication-templates',self._plugin,'xsl'])
            xsl = super(plugin,self).get_xsl(xslfile, extclass = self.__ext,
                                                xsldir = xslpath,
                                                system_path = False,
                                                resdir = self.assembly_dir,
                                                **kwargs)
    
        except:
            xsl = super(plugin,self).get_xsl(xslfile,
                                            extclass = self.__ext,
                                            xsldir = os.path.join(self._plugindir,'xsl'),
                                            system_path = True,
                                            resdir = self.assembly_dir,
                                            **kwargs)
        return xsl
    
    def get_project_xsl(self,xslfile, **kwargs):
        logger.debug("get xsl from plugin %s"%self._plugindir)
        return super(plugin,self).get_xsl(xslfile, extclass = self.__ext,
                                          xsldir = self._plugindir,
                                          system_path = True,
                                          resdir = self.assembly_dir,
                                          **kwargs)


    
    def copyinput(self):
        #        _, tmpname = tempfile.mkstemp(dir = self.getOsPath(self.pubdir(self.assembly_dir, self.profile)))
        _, tmpname = tempfile.mkstemp()
        inputtype = self.scriptspec.get("input")
        print type(self.input)
        for item in self.input:
            if item.get('type', '') == inputtype:
                if 'ET' in item.keys():
                    with open(tmpname, 'w') as tmpfile:
                        tmpfile.write(ET.tostring(item['ET']))
                if "file"  in item.keys():
                    shutil.copy(self.getOsPath(item["file"]), tmpname) 
                if "data" in item.keys():
                    with open(tmpname, 'w') as tmpfile:
                        tmpfile.write(item['data'])
        return tmpname

    def get_command(self):
        return ''
                    
    def start_cmd(self):
        logger.debug("os cmd call from plugin")
        try:
            res = []
            scriptlabel = self.scriptdef.xpath('string(label|ancestor::script/label)')
            system = platform.system()
            logger.debug("platform is %s"%system)
            try:
                cmd = self.scriptspec.find("cmd[@os='%s']"%system).text
            except:
                cmd = self.scriptspec.xpath("cmd[not(@os)]")[0].text

            subst = {}
            for p in self.scriptdef.xpath('parameters/parameter'):
                subst.update({p.get('name'):p.get('value')})
            pubdir = self.pubdir(self.assembly_dir, self.profile)
            subst.update({
                "APPDIR":self._appdir,
                "PLUGINDIR":self._plugindir,
                "PUBDIR":self.getOsPath(pubdir),
                "SRCDIR":self.getOsPath(self.assembly_dir),
                "BASEURI":self.getUrlPath(self.assembly_dir) + '/',
                "PUBURI":pubdir,
                "PUBNAME":self.publication_file,
#                "PIVOT": self.getOsPath(pivfile)
                })

            # if get file with local url                
            if cmd.find("_CMD_") >= 0:
                subst.update({'CMD':self.get_command()})
                
            # if get file with local url                
            if cmd.find("_PIVLOCAL_") >= 0:
                for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
                    localsrc = self.getOsPath(str(media.get('src')))
                    media.set('src', localsrc)

            if cmd.find("_INCOPY_") >= 0:
                tmpfile = self.copyinput()
                print tmpfile
                subst.update({'INCOPY':tmpfile})
                                            
            cmd=self._substscript(cmd, subst, self.profile)
            cmd=cmd.encode(self.LOCAL_ENCODING)
            logger.debug(cmd)

            exccmd = subprocess.Popen(
                cmd,
                shell=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                close_fds=False)
            err=exccmd.stderr.read()
            out=exccmd.stdout.read()
            exccmd.communicate()
            err=err.decode(self.LOCAL_ENCODING)
            out=out.decode(self.LOCAL_ENCODING)
            for line in err.split('\n'):
                # Doesn't display licence warning
                if re.search('license.dat', line):
                    continue
                # display warning or error
                if re.search('warning', line):
                    logger.info("Attention %(warn)s"% {'warn': line})
                elif re.search('error', line) or re.search('not found', line):
                    logger.error(line)
                    errmsg = "Erreur lors de l'exécution de la commande : %(cmd)s:\n  %(error)s"%{'cmd': cmd.decode(self.LOCAL_ENCODING).encode('utf-8'),'error': line.encode('utf-8')}
                    logger.error(errmsg)
                    raise PublishException([errmsg] + err.split('\n'))

            # display link
            
            xl=self.scriptspec.find('link')
            outfile=self._substscript(xl.get('name'), subst, self.profile)
            outref=self._substscript(xl.get('ref'), subst, self.profile)
            outtype=xl.get('type')
            logger.debug("Exécution du script %(label)s réussie"% {'label': scriptlabel.encode('utf-8')})
            res=[{"type":outtype, "label":outfile, "url":outref, "file":outref}]

        except:
            import traceback
            logger.debug(traceback.format_exc())
            print traceback.format_exc()
            logger.error("Erreur lors de l'execution du script %(label)s"% {'label': scriptlabel.encode('utf-8')})
            raise

        finally:
            exccmd.stderr.close()
            exccmd.stdout.close()
        return res

    def process_path(self, path):
        path = super(plugin, self).process_path(path)
        if self.release is None:
            return path
        else:
            return '/releases/' + self.release + '/' +  path
    
    def __call__(self, scriptdef, profile, assembly_dir, inputs):
        self.scriptname = scriptdef.get('name')
        logger.debug("calling script %s", self.scriptname)

        # check if execute in release or not
        self.release = None
        adparts = assembly_dir[1:].split('/')
#        logger.debug("adparts: %s ", str(adparts))
        if len(adparts) == 2 and adparts[0] == "releases":
            self.release = adparts[1]

        # get context    
        self.scriptdef = scriptdef
        self.profile = profile
        self.assembly_dir = assembly_dir

        # normalize pivot / input attribute
        self.pivot = None
        if isinstance(inputs, ET._ElementTree):
            self.pivot = inputs
            self.input = [{'type':'pivot', 'ET':inputs}]
        else:
            for item in inputs:
                if item.get('type','') == 'pivot':
                    if 'ET' in item.keys():
                        self.pivot = item['ET']
                    if "file"  in item.keys():
                        self.pivot = self.parse(item['file'])
                    if "data" in  item.keys():
                        self.pivot = self.parse_string(item['data'])
            self.input = inputs

        # get xml specification for the plugin        
        self.scriptspec = self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%self.scriptname)[0]

        # calculate publication path/filenames
        self.publication_file = self.substitute_variables(self.substitute_criteria(unicode(scriptdef.xpath("string(filename|ancestor::script/filename)")),profile), profile, {"LANG":self._publang})
        
        self.publication_dir = self.pubdir(assembly_dir, profile)
        self.publication_plugin_dir = self.publication_dir+"/"+ self.publication_file #+ "_" + self.scriptname
        try:
            self.makedirs(self.publication_plugin_dir)
        except:
            pass
        return self.postpub()

    def copylibs(self, assembly_dir, label):
        # copy libs from plugin directory to assembly space
        libsdir = os.path.join(self._plugindir,'lib')
        if os.path.exists(libsdir):
            libpdir = os.path.join(self.getOsPath('/'.join([assembly_dir,'kolekti','publication-templates',label])), 'lib')
            try:
                shutil.rmtree(libpdir)
            except:           
                pass
            shutil.copytree(libsdir, libpdir)


    def copymedias(self):
        # copy media from assembly space source to publication directory
        for med in self.pivot.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):

            ref = med.get('src')
            ref = self.substitute_criteria(ref, self.profile)
            try:
                refdir = "/".join([self.publication_plugin_dir]+ref.split('/')[:-1])
                self.makedirs(refdir)
            except OSError:
                logger.debug('makedir failed')
                import traceback
                logger.debug(traceback.format_exc())
            try:
                self.copyFile("/".join([self.assembly_dir,ref]), "/".join([self.publication_plugin_dir,ref]) )
            except:
                logger.debug('unable to copy media')
                import traceback
                logger.debug(traceback.format_exc())

        # copy plugin lib from assembly space to publication directory
        label = self.scriptdef.get('name')
        ass_libdir = '/'.join([self.assembly_dir,'kolekti','publication-templates',label,'lib'])
        if (self.exists(ass_libdir)):
            self.copyDirs(ass_libdir, self.publication_plugin_dir + '/lib')

        
    def postpub(self):
        """
        postpub is the iterator used in plugin
        """
        logger.debug('Dummy plugin')
        return "Dummy plugin"

    def get_script_parameter(self, param):
        try:
            return self.scriptdef.xpath('string(./parameters/parameter[@name="%s"]/@value)'%param)
        except:
            import traceback
            logger.error("Unable to read script parameters: %s"%param)
            logger.debug(traceback.format_exc())
            return None


