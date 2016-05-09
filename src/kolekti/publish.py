# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

from datetime import datetime
import time
import urllib
import re
import os
import copy
import logging
import json
from lxml import etree as ET

from publish_utils import PublisherMixin, PublisherExtensions, ReleasePublisherExtensions
from common import kolektiBase, XSLExtensions, LOCAL_ENCODING
from kolekti import plugins

class Publisher(PublisherMixin, kolektiBase):
    """Manage all publication process functions, assembly tocs, filters assemblies, invoke scripts
       instaciation parameters : lang + superclass parameters
    """
    def __init__(self, *args,**kwargs):
        super(Publisher, self).__init__(*args, **kwargs)

        # moved to PublisherMixin init
        #if self._publang is None:
        #    self._publang = self._config.get("sourcelang","en")
        self._cleanup = True
        logging.debug("kolekti %s"%self._version)

    def getPublisherExtensions(self):        
        return PublisherExtensions
    
    def _variable(self, varfile, name):
        """returns the actual value for a variable in a given xml variable file"""
        fvar = self.get_base_variable(varfile)
        xvar = self.parse(fvar)
        
        var = xvar.xpath('string(//h:variable[@code="%s"]/h:value[crit[@name="lang"][@value="%s"]]/h:content)'%(name,self._publang),
                         namespaces=self.nsmap)
        return unicode(var)


    def get_script(self, plugin):

        # imports a script python module
        pm = getattr(plugins,plugin)
        pl  = getattr(pm, "plugin")
        return pl(self._path, lang = self._publang)
        #return plugins.getPlugin(plugin,self._path)


    def check_modules(self, xtoc):
        for refmod in xtoc.xpath("//h:a[@rel = 'kolekti:topic']/@href",namespaces=self.nsmap):
            try:
                path = self.process_path(refmod)
                self.parse_html(path)
            except IOError:
                import traceback
                yield  {
                        'event':'error',
                        'msg':"module %s non trouvé"%path.encode('utf-8'),
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }  
            except ET.XMLSyntaxError, e:
                import traceback
                yield  {
                        'event':'error',
                        'msg':"erreur dans %s : %s"%(path.encode('utf-8'), str(e)),
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }  

        
    def publish_assemble(self, xtoc, xjob):
        events = []
        """create and return an assembly from the toc using the xjob critria for filtering"""
        assembly_dir = self.assembly_dir(xjob)

        # produce assembly document from toc and topics
        xsassembly = self.get_xsl('assembly', PublisherExtensions, lang=self._publang)
        assembly = xsassembly(xtoc, lang="'%s'"%self._publang)
        self.log_xsl(xsassembly.error_log)
        
        # apply pre-assembly filtering  
        s = self.get_xsl('criteria', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly)
        self.log_xsl(s.error_log)
                        
        s = self.get_xsl('filter', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly, action="'assemble'")
        self.log_xsl(s.error_log)

        # calculate the publication name
        pubname = xjob.get('id','')
        pubname = self.substitute_criteria(pubname, xjob)
        
        if self._draft:
            pubname += "_draft"
            
        try:
            self.makedirs(assembly_dir + "/sources/" + self._publang + "/assembly")
        except:
            import traceback
            events.append({
                        'event':'error',
                        'msg':"Impossible de créer le dossier destination",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        })

            logging.debug("W: unable to create assembly directory")
            logging.debug(traceback.format_exc())
            return assembly, assembly_dir, pubname, events

        try:
            self.xwrite(assembly, assembly_dir + "/sources/"+ self._publang + "/assembly/" + pubname + ".html")
        except:
            import traceback
            events.append({
                        'event':'error',
                        'msg':"Impossible de créer le fichier assemblage",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        })

            return assembly, assembly_dir, pubname, events


        logging.debug('********************************** create settings')
        try:
            self.create_settings(xjob, pubname, assembly_dir)
        except:
            import traceback
            events.append({
                        'event':'error',
                        'msg':"Impossible de créer le fichier de parametres",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        })

            return assembly, assembly_dir, pubname, events

        logging.debug('********************************** copy scripts resources')
        for profile in xjob.xpath("/job/profiles/profile[@enabled='1']"):
            # logging.debug(profile)
            s = self.get_xsl('filter', PublisherExtensions, profile=profile, lang=self._publang)
            fassembly = s(assembly)
            logging.debug('********************************** copy media')
            for event in self.copy_media(fassembly, profile, assembly_dir):
                events.append(event)

            for event in self.copy_variables(fassembly, profile, assembly_dir):
                events.append(event)

            # copy scripts resources
            for script in xjob.xpath("/job/scripts/script[not(@name='multiscript')][@enabled = 1]|/job/scripts/script[@name='multiscript'][@enabled = 1]/*/script"):
                scriptlabel = script.xpath('string(label|ancestor::script/label)')
                try:
                    self.copy_script_params(script, profile, assembly_dir)
                except:
                    import traceback
                    print traceback.format_exc()
                    events.append({
                        'event':'error',
                        'msg':"Impossible de copier les parametres du script %s"%scriptlabel,
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        })

                    logging.error("resources for script %s not found"%scriptlabel)
                    logging.debug(traceback.format_exc())
                    
            for script in xjob.xpath("/job/scripts/script[@enabled = 1]"):
                scriptlabel = script.xpath('string(label|ancestor::script/label)')
                try:
                    self.copy_script_variables(script, profile, assembly_dir)
                except:
                    import traceback
                    print traceback.format_exc()
                    events.append({
                        'event':'error',
                        'msg':"Impossible de copier les variables du script %s"%scriptlabel,
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        })

                    logging.error("variables for script %s not found"%scriptlabel)
                    logging.debug(traceback.format_exc())

        return assembly, assembly_dir, pubname, events 



    def publish_job(self, assembly, xjob):
        """publishes a an assembly for every profile in xjob
           invoke publication scripts for every publication
            iterator : yields a result for each selected profile / script 
           """ 
        assembly_dir = self.assembly_dir(xjob)
        res=[]

        yield {'event':'job', 'label':xjob.get('id')}

        for profile in xjob.xpath('/job/profiles/profile'):
            if profile.get('enabled','0') == '1':
                profilename = profile.find('label').text

                yield {'event':'profile', 'label':profilename}

                # creates the document (pivot) file
                try:
                    pivot = self.publish_profile(assembly, profile, assembly_dir)
                except:
                    import traceback
                    logging.error("Assembly Error")
                    yield {
                        'event':'error',
                        'msg':"erreur lors de l'assemblage",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
                    logging.debug(traceback.format_exc())
                    
                # invoke scripts
                for output in xjob.xpath("/job/scripts/script[@enabled = 1][@name='multiscript']"):
                    indata = pivot
                    listres = []
                    for script in output.xpath('publication/script'):
                        scriptlabel = script.xpath('string(ancestor::script/label)')
                        try:
                            outdata = self.start_script(script, profile, assembly_dir, indata)
                            listres.append(outdata)
                            indata = outdata
                        except:
                            import traceback
                            logging.error("Script %s finished with errors"%scriptlabel)
                            yield {
                                'event':'error',
                                'msg':"Erreur d'execution du script %s"%scriptlabel,
                                'stacktrace':traceback.format_exc(),
                                'time':time.time(),
                                }
                            logging.debug(traceback.format_exc())
                            
                    yield {
                        'event':'result',
                        'script':scriptlabel,
                        'docs':outdata,
                        'steps':listres,
                        'time':time.time()
                    }
                        
                for script in xjob.xpath("/job/scripts/script[@enabled = 1][not(@name='multiscript')]"):
                    try:
                        resscript = self.start_script(script, profile, assembly_dir, pivot)
                        yield {
                            'event':'result',
                            'script':script.find('label').text,
                            'docs':resscript,
                            'time':time.time(),
                            }
                    except:
                        import traceback
                        logging.error("Script %s finished with errors"%script.find('label').text)
                        yield {
                            'event':'error',
                            'msg':"Erreur d'execution du script %s"%script.find('label').text,
                            'stacktrace':traceback.format_exc(),
                            'time':time.time(),
                            }
                        logging.debug(traceback.format_exc())
                if self._cleanup:
                    self.delete_resource(self.pubdir(assembly_dir, profile)+ "/document.xhtml")


        return 


    def publish_profile(self, assembly, profile, assembly_dir):
        """produces the pivot file from the assembly:
        apply profile filters,
        generate toc & index
        substitutes variables in content"""
        
        logging.info("* Publishing profile %s"%profile.xpath('string(label)'))

        pubdir = self.pubdir(assembly_dir, profile)

        try:
            # logging.debug(assembly)
            # criteria
            s = self.get_xsl('criteria', self.getPublisherExtensions(), profile=profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            # filter
            logging.debug("filter on profile")
            s = self.get_xsl('filter', self.getPublisherExtensions(), profile=profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            s = self.get_xsl('filter-empty-sections')
            assembly = s(assembly)
            self.log_xsl(s.error_log)            

            # substvars
            s = self.get_xsl('variables', self.getPublisherExtensions(), profile = profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)

            # process links
            s = self.get_xsl('links', self.getPublisherExtensions(), profile = profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)

            # make index
            if assembly.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap):
                s = self.get_xsl('index')
                assembly = s(assembly)
                self.log_xsl(s.error_log)

            # make toc
            # if assembly.xpath("//h:div[@class='TOC']", namespaces=self.nsmap):
            s = self.get_xsl('toc')
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            # revision notes
            # s = self.get_xsl('csv-revnotes')
            # assembly = s(assembly)

            # cleanup title levels
            
            # s = self.get_xsl('titles', self.getPublisherExtensions(), profile = profile, lang=self._publang)
            # assembly = s(assembly)
            
        except ET.XSLTApplyError, e:
            logging.debug(s.error_log)
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Error in publication process (xsl)")
            raise

        except:
            import traceback
            print traceback.format_exc()
            logging.debug(traceback.format_exc())
            logging.error("Error in publication process")
            raise
        
        # write pivot
        pivot = assembly
        pivfile = pubdir + "/document.xhtml"
        #print pivot
        self.xwrite(pivot, pivfile, sync = False)
        return pivot

    # create settings.xml file in assembly directory
    def create_settings(self, xjob, pubname, assembly_dir):
        try:
            self.makedirs(assembly_dir + "/kolekti")
        except:
            logging.debug("W: unable to create kolekti subdirectory")
            import traceback
            logging.debug(traceback.format_exc())


    # copy used variables xml files into assembly space
    def copy_variables(self, assembly, profile, assembly_dir):
        for varelt in assembly.xpath('//h:var[contains(@class,":")]', namespaces=self.nsmap):
            vardecl = varelt.get('class')
            varfile, varname = vardecl.split(':')
            if '/' in varfile:
                srcfile = varfile
            else:
                srcfile = '/' + "/".join(['sources',self._publang,'variables',varfile])
            srcfile = self.substitute_criteria(srcfile,profile) + ".xml"
            try:
                self.makedirs(self.dirname(assembly_dir + "/" +srcfile))
            except OSError:
                logging.debug('makedir failed')
                import traceback
                yield {
                        'event':'warning',
                        'msg':"impossible de créer le dossier de variables",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
                logging.debug(traceback.format_exc())
            try:
                self.copyFile(srcfile, assembly_dir + '/' + srcfile)
                
            except:
                import traceback
                yield {
                        'event':'warning',
                        'msg':"fichier introuvable %s"%(srcfile.encode('utf-8'),),
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }

            
    # copy media to assembly space
    def copy_media(self, assembly, profile, assembly_dir):
        for med in assembly.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):
            ref = med.get('src')
            ref = self.substitute_criteria(ref, profile)
            if ref[0] == '/':
                ref = ref[1:]
#            med.set('src',ref)
            logging.debug('image src : %s'%ref)
            try:
                refdir = "/".join([assembly_dir]+ref.split('/')[:-1])
                # refdir = os.path.join(assembly_dir + '/' + os.path.dirname(ref))
                self.makedirs(refdir)
            except OSError:
                logging.debug('makedir failed')
                import traceback
                logging.debug(traceback.format_exc())
            try:
                self.copyFile(ref, assembly_dir + '/' + ref)
            except:
                import traceback
                yield {
                        'event':'warning',
                        'msg':"fichier introuvable %s"%(ref.encode('utf-8'),),
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
                
        return

                
    def copy_script_params(self, script, profile, assembly_dir):
        pubdir = self.pubdir(assembly_dir, profile)
        name = script.get('name')
        scriptlabel = script.xpath('string(label|ancestor::script/label)')
        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            logging.error("Script %s not found" %name)
            raise
        # copy variable files used in scripts definitions
        
        # copy libs
        try:
            stype = scrdef.get('type')
            if stype=="plugin":
                label = scrdef.get('id')
                plugname=scrdef.find("plugin").text
                plugin = self.get_script(plugname)
                plugin.copylibs(assembly_dir, label)
        except:
            logging.error('Unable to copy script libs')
            import traceback
            logging.debug(traceback.format_exc())
            raise
        
        params = {}
        try:
            params = {}
            for p in script.xpath('parameters/parameter'):
                params.update({p.get('name'):p.get('value')})

            for pdef in scrdef.xpath('parameters/parameter'):
                pname = pdef.get('name')
                pval =  params.get(pname)
                logging.debug("copy libs %s %s"%(pname, pval))
                if pval is not None and pdef.get('type')=='filelist':
                    srcdir = unicode(self.substitute_criteria(pdef.get('dir'), profile))
                    if pdef.get('ext') == "less":
                        # TODO less compil
                        self.script_lesscompile(pval,
                                                srcdir,
                                                assembly_dir,
                                                '%s/%s'%(label,copyto))
                            
                    else:
                        try:
                            self.script_copy(filer = pval,
                                            srcdir = srcdir,
                                            targetroot = assembly_dir,
                                            ext = pdef.get('ext'))
                        except:
                            #only raise an exception if onfail attribute = silent
                            if pdef.get('onfail') != 'silent':
                                raise
                            
                if pdef.get('type')=='resource':
                    filer = pdef.get('file')
                    if not filer is None:
                        filer = unicode(filer)
                    srcdir = unicode(self.substitute_criteria(pdef.get('dir'), profile))
                    try:
                        self.script_copy(filer = filer,
                                        srcdir = srcdir,
                                        targetroot = assembly_dir,
                                        ext = pdef.get('ext'))
                    except:
                        #only raise an exception if onfail attribute = silent
                        if pdef.get('onfail') != 'silent':
                            raise

        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("[Script %s] could not copy resources"%scriptlabel)
            raise
        
        
    def copy_script_variables(self, script, profile, assembly_dir):
        scriptlabel = script.find('filename').text
        scriptlabel = self.substitute_criteria(scriptlabel, profile)
        for variable in re.findall('{[ /a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+}', scriptlabel):
            # logging.debug(variable)
            splitVar = variable[1:-1].split(':')
            sheet = splitVar[0].strip()
            if sheet[0] != "/":
                variables_file = self.get_base_variable(sheet)
            else:
                variables_file = sheet
            srcdir,filer = variables_file.rsplit("/",1)
            self.script_copy(filer, srcdir, assembly_dir, 'xml')


    def start_script(self, script, profile, assembly_dir, pivot):
        res = None
        #print "script",self._publang, ET.tostring(profile)
        #print self.substitute_criteria(unicode(script.xpath("string(filename)")),profile)
        pubdir = self.pubdir(assembly_dir, profile)
        scriptlabel = script.xpath('string(label|ancestor::script/label)')
        label =  self.substitute_variables(self.substitute_criteria(unicode(profile.xpath('string(label)')),profile), profile, {"LANG":self._publang})
        filename = script.xpath('string(filename|ancestor::script/filename)')
        pubname = self.substitute_variables(self.substitute_criteria(unicode(filename),profile), profile, {"LANG":self._publang})
        #print pubname
        name=script.get('name')
        params = {}
        for p in script.xpath('parameters/parameter'):
            params.update({p.get('name'):p.get('value')})


        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            logging.error("Impossible de trouver la définition du script: %s" %scriptlabel)
            raise

        
        # shall we filter the pivot before applying the script
        if 'pivot_filter' in params :
            xfilter = params['pivot_filter']
            xdir = scrdef.xpath("string(parameters/parameter[@name='pivot_filter']/@dir)")
            xf = self.get_xsl(xfilter, xsldir = xdir)
            fpivot = xf(pivot)
            self.log_xsl(xf.error_log)
            
            pivfile = pubdir + "/filtered_" + pubname + ".xhtml"
            self.xwrite(fpivot, pivfile, pretty_print = False, sync = False)
        else:
            fpivot = pivot
            pivfile = pubdir + "/document.xhtml"

        subst = copy.copy(params)
        
        subst.update({
            "APPDIR":self._appdir,
            "PUBDIR":self.getOsPath(pubdir),
            "SRCDIR":self.getOsPath(assembly_dir),
            "BASEURI":self.getUrlPath(assembly_dir) + '/',
            "PUBURI":pubdir,
            "PUBNAME": pubname,
            "PIVOT": self.getOsPath(pivfile)
            })

        stype = scrdef.get('type')
        try:
            if stype=="plugin":
#                from kolekti.plugins import getPlugin
                
                plugname=scrdef.find("plugin").text
                try:
                    plugin = self.get_script(plugname)
                except:
                    logging.error("Impossible de charger le script %(label)s"%{'label': scriptlabel.encode('utf-8')})
                    import traceback
                    logging.debug(traceback.format_exc())
                    raise

                res = plugin(script, profile, assembly_dir, fpivot)
                logging.debug("%(label)s ok"% {'label': scriptlabel.encode('utf-8')})

                
            elif stype=="shell":
                import platform
                system = platform.system()
                try:
                    cmd=scrdef.find("cmd[@os='%s']"%system).text
                except:
                    cmd=scrdef.xpath("cmd[not(@os)]")[0].text

                # if get file with local url                
                if cmd.find("_PIVLOCAL_") >= 0:
                    localdocument = fpivot
                    for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
                        localsrc = self.getOsPath(str(media.get('src')))
                        media.set('src', localsrc)

                cmd=self._substscript(cmd, subst, profile)
                cmd=cmd.encode(LOCAL_ENCODING)
                logging.debug(cmd)
                print "--------------"
                print cmd
                print subst
                try:
                    import subprocess
                    exccmd = subprocess.Popen(cmd, shell=True,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              close_fds=False)
                    err=exccmd.stderr.read()
                    out=exccmd.stdout.read()
                    exccmd.communicate()
                    err=err.decode(LOCAL_ENCODING)
                    out=out.decode(LOCAL_ENCODING)
                    has_error = False
                    for line in err.split('\n'):
                        # Doesn't display licence warning
                        if re.search('license.dat', line):
                            continue
                        # display warning or error
                        if re.search('warning', line):
                            logging.info("Attention %(warn)s"% {'warn': line})
                        elif re.search('error', line) or re.search('not found', line):
                            logging.error(line)
                            logging.error("Erreur lors de l'exécution de la commande : %(cmd)s:\n  %(error)s"%{'cmd': cmd.decode(LOCAL_ENCODING).encode('utf-8'),'error': line.encode('utf-8')})
                            has_error = True

                    # if no error display link
    
                    if not has_error:
                        xl=scrdef.find('link')
                        outfile=self._substscript(xl.get('name'), subst, profile)
                        outref=self._substscript(xl.get('ref'), subst, profile)
                        outtype=xl.get('type')
                        logging.debug("Exécution du script %(label)s réussie"% {'label': scriptlabel.encode('utf-8')})
                        res=[{"type":outtype, "label":outfile, "url":outref, "file":outref}]
                except:
                    import traceback
                    logging.debug(traceback.format_exc())
                    logging.error("Erreur lors de l'execution du script %(label)s"% {'label': scriptlabel.encode('utf-8')})
                    raise

                finally:
                    exccmd.stderr.close()
                    exccmd.stdout.close()
                    
            elif stype=="xslt":
                try:
                    sxsl=scrdef.find("stylesheet").text
                    ### 
                    xslt_doc=ET.parse(os.path.join(self._appdir,'publication','xsl','plugins',sxsl))
                    xslt=ET.XSLT(xslt_doc)
                    sout=scrdef.find("output").text

                    ###
                    sout=self._substscript(sout, subst, profile)

                    xparams={}
                    for n,v in params.iteritems():
                        xparams[n]="'%s'"%v

                    xparams['LANG']="'%s'"%self._publang
                    xparams['ZONE']="'%s'"%self.critdict.get('zone','')
                    xparams['DOCNAME']="'%s'"%self.docname
                    xparams['PUBDIR']="'%s'"%pubdir

                    docf=xslt(self.pivdocument,**xparams)
                    try:
                        self.model.pubsave(str(docf),'/'.join((label,sout)))
                    except:
                        logging.error("Impossible d'exécuter le script %(label)s"%{'label': label.encode('utf-8')})
                        raise
                    errors = set()
                    for err in xslt.error_log:
                        if not err.message in errors:
                            logging.debug(err.message)
                            errors.add(err.message)
                    logging.info("Exécution du script %(label)s réussie"%{'label': label.encode('utf-8')})

                    # output link to result of transformation
                    #                    yield (self.view.publink(sout.split('/')[-1],
                    #                          label,
                    #                          '/'.join((self.model.local2url(self.model.pubpath), label, sout))))

                    # copy medias
                    #try:
                    #    msrc = self.model.abstractIO.getid(os.path.join(self.model.pubpath, 'medias'))
                    #    dsrc = self.model.abstractIO.getid(os.path.join(self.model.pubpath, str(label), 'medias'))
                    #    self.model.abstractIO.copyDirs(msrc, dsrc)
                    #except OSError:
                    #    pass
                    # make a zip with label directory
                    #zipname=label+".zip"
                    #zippy = self.model._loadMVCobject_('ZipFileIO')
                    #zippy.open(os.path.join(self.model.pubpath,zipname), 'w')
                    #top=os.path.join(self.model.pubpath,label)
                    #for root, dirs, files in os.walk(top):
                    #    for name in files:
                    #        rt=root[len(top) + 1:]
                    #        zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(rt, name)))
                    #zippy.close()

                    # link to the zip
                    #yield (self.view.publink('Zip',
                    #                         label,
                    #                         '/'.join((self.model.local2url(self.model.pubpath), zipname))))
            
                except:
                    logging.error("Erreur lors de l'execution du script %(label)s"% {'label': scriptlabel.encode('utf-8')})
                    raise
            
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Impossible d'exécuter un script du job %(label)s"% {'label': scriptlabel.encode('utf-8')})
            raise
        finally:
            if self._cleanup and 'pivot_filter' in params :
                self.delete_resource(pivfile)
        return res




    def script_lesscompile(self, lessfile, srcdir, pubdir, dstdir):
        srcpath = u'@design/publication/%s' %srcdir
        destcd = unicode(self.__pubdir+'/'+dstdir+'/'+lessfile+'.parts')
        try:
            self.abstractIO.rmdir(destcd)
        except:
            pass

        try:
            source=u"%s/%s.parts"%(srcpath,lessfile)
            if self.abstractIO.exists(source):
                self.abstractIO.copyDirs(source,destcd)
            else:
                self.abstractIO.makedirs(destcd+"/dummy")
        except:
            dbgexc()

        logging.debug(("script less compile to",destcd))
        
        try:
            source= u"%s/%s.%s"%(srcpath,lessfile,"less")
            dest=   u"%s/%s.%s"%(destcd,lessfile,"css")
            nodejs = conf.get('nodejs')
            lessc  = conf.get('lessc')
            sourcefs=self.abstractIO.getpath(source)
            destfs=self.abstractIO.getpath(dest)
            incfs=self.abstractIO.getpath(srcpath)
            cmd=[nodejs,lessc,"-x","--include-path=%s"%incfs,sourcefs,destfs]
            debug(cmd)
            exccmd = subprocess.Popen(cmd,
                                      stdin=subprocess.PIPE,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,                                      
                                      )
            exccmd.wait()
            out=exccmd.stdout.read()
            logging.info(out)

            if not exccmd.returncode == 0:
                err=exccmd.stderr.read()
                logging.debug(err)
                raise
        except:
            dbgexc()
            


    def script_copy(self, filer, srcdir, targetroot, ext):

        # copies file [srcdir]/[filer].[ext] to
        # [targetroot]/[srcdir]/[filer].[ext]
        # also copies recursively [filer].parts directory
        
        logging.debug("script copy %s %s %s %s", filer, srcdir, targetroot, ext)
        srcpath = self.get_base_template(srcdir)
        destpath = unicode(targetroot + "/" + srcdir)
        
        try:
            self.makedirs(destpath)
        except OSError:
            pass
        if filer is None:
            self.copyDirs(srcdir, destpath)
        else:
            try:
                source= u"%s/%s.%s"%(srcdir,filer,ext)
                dest=   u"%s/%s.%s"%(destpath,filer,ext)
                logging.debug('copy resource %s -> %s'%(source, dest))
                self.copyFile(source,dest)
            except:
                import traceback
                logging.error("Impossible de copier la ressource %s"%source)
                logging.debug(traceback.format_exc())
                print traceback.format_exc()
                raise
        
            try:
                source=u"%s/%s.parts"%(srcdir,filer)
                if self.exists(source):
                    target=u"%s/%s.parts"%(destpath,filer)
                    try:
                        self.rmdir(target)
                    except:
                        pass
                    self.copyDirs(source,target)

            except:
                import traceback
                logging.error("Impossible de copier la ressource %s"%source)
                logging.debug(traceback.format_exc())
                print traceback.format_exc()
                raise







                    
class DraftPublisher(Publisher):
    def __init__(self, *args, **kwargs):
        cleanup = True
        if kwargs.has_key('cleanup'):
            cleanup = kwargs.get('cleanup')
            kwargs.pop('cleanup')
        super(DraftPublisher, self).__init__(*args, **kwargs)
        self._draft = True
        self._cleanup = cleanup
        
    def assembly_dir(self, xjob):
        assembly_dir = self.substitute_criteria(xjob.xpath('string(/job/@pubdir)'), xjob)
        assembly_dir = self.substitute_variables(assembly_dir, xjob, {"LANG":self._publang})
        assembly_dir = "/publications/" + assembly_dir
        if assembly_dir[-1] != "/":
            assembly_dir += "/"
        return assembly_dir

    def cleanup_assembly_dir(self, xjob):
        assembly_dir = self.assembly_dir(xjob)
        self.rmtree(assembly_dir + "/sources")
        self.rmtree(assembly_dir + "/kolekti")
        

    # publishes a list of job toc
    
    def publish_draft(self, toc, job, pubtitle=None):
        """ publishes a kolekti toc, with a job"""
        status = True
        # toc = xjob.xpath('string(/*/*[self::toc]/@value)')
        # toc = self.get_base_toc(toc) + ".html"
        logging.debug("publish toc %s",toc)
        
        if isinstance(toc,ET._ElementTree):
            xtoc = toc
        else:
            xtoc = self.parse(toc)

            
        if pubtitle is not None:
            xtoc.xpath("/h:html/h:head/h:title", namespaces=self.nsmap)[0].text = pubtitle

        pubevents = [{"event":"toc",
                    "title":xtoc.xpath("/h:html/h:head/h:title", namespaces=self.nsmap)[0].text,
                    }]

        # path = self.get_base_job(job) + ".xml"
        if isinstance(job,ET._ElementTree):
            xjob = job
        else:
            xjob = self.parse(job)

        # assembly
        logging.debug('********************************** CREATE ASSEMBLY')

        for ev in self.check_modules(xtoc):
            yield ev
            status = (ev.get('event','') != 'error')

            if not status:
                return
        
        try:
            assembly, assembly_dir, pubname, events = self.publish_assemble(xtoc, xjob.getroot())
            for event in events:
                pubevents.append(event)
                yield event
            try:
            
                logging.debug('********************************** PUBLISH ASSEMBLY')
                
                for pubres in self.publish_job(assembly, xjob.getroot()):
                    pubevents.append(pubres)
                    yield pubres
                    
                pubres =  {"event":"publication_dir", "path":assembly_dir}
                pubevents.append(pubres)
                yield pubres

                if self._cleanup:
                    try:
                        self.cleanup_assembly_dir(xjob.getroot())
                    except:
                        logging.debug('Warning: could not remove tmp dir')
            except:
                import traceback
                errev = {
                    'event':'error',
                    'msg':"erreur lors de la publication",
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                }
                pubevents.append(errev)
                yield errev

        
        except:
            import traceback
            errev =  {
                    'event':'error',
                    'msg':"erreur lors de l'assemblage",
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                }
            pubevents.append(errev)
            yield errev
            return

        finally:
            self.purge_manifest_events(pubevents)    
            try:
                manifest = self.getOsPath(assembly_dir + '/manifest.json')
#                mfevents = []
#                if os.path.exists(manifest):
#                    with open(manifest, 'r') as mf:
#                        mfevents = json.loads(mf.read())
                        
                mfevents = {
                    "event":"publication",
                    "path":assembly_dir,
                    "name":self.basename(pubname),
                    "title":pubtitle,
                    "time": int(time.time()),
                    "content":pubevents,
                    }
                with open(manifest, 'w') as mf:
                    mf.write(json.dumps(mfevents))
    
            except:
                import traceback
                yield {
                    'event':'error',
                    'msg':"impossible d'ouvrir le fichier manifeste",
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                    }
            
                return

                
class Releaser(Publisher):
    def __init__(self, *args, **kwargs):
        super(Releaser, self).__init__(*args, **kwargs)
        self._cleanup = False

    def assembly_dir(self, xjob):
        assembly_dir = self.substitute_criteria(xjob.xpath('string(/job/@pubdir)'),xjob)
        assembly_dir = self.substitute_variables(assembly_dir, xjob, {"LANG":self._publang})
        assembly_dir = "/releases/" + assembly_dir
        if assembly_dir[-1] != "/":
            assembly_dir += "/"
        return assembly_dir

    def make_release(self, toc, job, release_name=None):
        """ releases a kolekti toc, using the profiles sets present in jobs list"""
        # toc = xjob.xpath('string(/*/*[self::toc]/@value)')
        res = []
        # toc = self.get_base_toc(toc) + ".html"
        logging.debug("release toc %s",toc)
        if isinstance(toc,ET._ElementTree):
            xtoc = toc
            if release_name is None:
                raise Exception('Toc in xml format, with no release name provided')
        else:
            xtoc = self.parse(toc)
        #        release_name = os.path.splitext(pubdir.rsplit("/", 1)[1])[0]

        if isinstance(job,ET._ElementTree):
            xjob = job.getroot()
        else:
            xjob = self.parse(job).getroot()
        release_name = xjob.get('pubdir', release_name)
        xjob.set('id',release_name + '_asm')

        xtoc.xpath("/h:html/h:head/h:title",namespaces=self.nsmap)[0].text = release_name
        ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "meta", attrib = {"name":"kolekti:releasename","content": release_name})

        # assembly
        logging.debug('********************************** CREATE ASSEMBLY')
        assembly, assembly_dir, pubname, events = self.publish_assemble(xtoc, xjob)
        res.append({"event":"release_creation",
                    "lang":self._publang,
                    "assembly_dir":assembly_dir,
                    "pubname":pubname,
                    "releasename":release_name,
                    "datetime":time.time(),
                    "toc":xtoc.xpath('/html:html/html:head/html:title/text()',namespaces={"html":"http://www.w3.org/1999/xhtml"}),
                    "content":events,
                    })

        # self.write('<publication type="release"/>', assembly_dir+"/.manifest")
        self.write(json.dumps(res), assembly_dir+"/manifest.json")
        assembly_path = "/".join([assembly_dir,'sources',self._publang,'assembly',pubname+'_asm.html'])
        #if self.syncMgr is not None :
        #    try:
        #        self.syncMgr.propset("release_state","sourcelang",assembly_path)
        #            self.syncMgr.add_resource(assembly_path)
        #            self.syncMgr.commit(assembly_path, "Release Creation")
        #            self.syncMgr.commit(assembly_path, "Release Copy %s from %s"%(
        #    except:
        #        import traceback
        #        res.append({
        #            'event':'error',
        #            'msg':"Erreur de synchronisation",
        #            'stacktrace':traceback.format_exc(),
        #            'time':time.time(),
        #            })
                   
        return res

    # copies the job in release directory
    def create_settings(self, xjob, pubname, assembly_dir):
        try:
            self.makedirs(assembly_dir + "/kolekti/publication-parameters")
        except:
            logging.debug("W: unable to create release publication parameters directory")
            import traceback
            logging.debug(traceback.format_exc())

        self.xwrite(xjob, assembly_dir + "/kolekti/publication-parameters/" + pubname + ".xml")





class ReleasePublisher(Publisher):
    def __init__(self, release_dir, *args, **kwargs):
        self._publangs = None
        if kwargs.has_key('langs'):
            self._publangs = kwargs.get('langs')
            kwargs.pop('langs')
        self._release_dir = release_dir
        super(ReleasePublisher, self).__init__(*args, **kwargs)
        if self._publangs is None:
            self._publangs = self._project_settings.xpath("/settings/releases/lang/text()")
        self._cleanup = False
        
    def getPublisherExtensions(self):        
        return ReleasePublisherExtensions

    def get_extensions(self, extclass, **kwargs):
        kwargs.update({"release":self._release_dir})
        return super(ReleasePublisher, self).get_extensions(extclass,  **kwargs)
            
    def assembly_dir(self, xjob = None):
        return self._release_dir
#        assembly_dir = self.substitute_variables(xjob.xpath('string(/job/@pubdir)'),xjob)
#        assembly_dir = self.substitute_criteria(assembly_dir, xjob)
#        assembly_dir = "/releases/" + assembly_dir
#        return assembly_dir

    def cleanup_assembly_dir(self, xjob):
        pass

    def process_path(self, path):
        return self.assembly_dir() + "/" + super(ReleasePublisher,self).process_path(path)
    
    def publish_assembly(self, assembly):
        """ publish an assembly"""
        pubevents = []
        try :
            for lang in self._publangs:
                langpubevt = []
                
                
                self._publang = lang
                try:
                    xassembly = self.parse(self._release_dir + '/sources/' + self._publang + '/assembly/'+ assembly + '.html')
                except:
                    import traceback
                    errevt = {
                        'event':'error',
                        'msg':"impossible de lire l'assemblage",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
                    logging.error("unable to read assembly %s"%assembly)
                    logging.debug(traceback.format_exc())
                    langpubevt.append(errevt)
                    yield errevt
                    return

                xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ assembly +'.xml')
        
                for pubres in self.publish_job(xassembly, xjob.getroot()):
                    langpubevt.append(pubres)
                    yield pubres
                
                pubres = {"event":"publication_dir", "path":self._release_dir}
                langpubevt.append(pubres)
                yield pubres
                pubevents.append({'event':'lang', 'label':lang, 'content':langpubevt})
        except:
            import traceback
            errev = {
                'event':'error',
                'msg':"erreur lors de la publication",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            pubevents.append(errev)
            yield errev

        finally:
            self.purge_manifest_events(pubevents)
            try:
                try:
                    mfevents = json.loads(self.read(self._release_dir + '/manifest.json'))
                    for event in mfevents:
                        if event.get('event','') == "release_publication":
                            for event2 in event.get('content'):
                                if event2.get('event','') == "lang" and event2.get('label','') == lang:
                                    event2.update({'content':[]})
                except IOError:
                    mfevents = []
                     
                mfevents.append({
                    "event":"release_publication",
                    "path":self._release_dir,
                    "time": int(time.time()),
                    "content":pubevents,
                    })
                self.write(json.dumps(mfevents), self._release_dir + '/manifest.json')
    
            except:
                import traceback
                
                yield {
                    'event':'error',
                    'msg':"impossible d'ouvrir le fichier manifeste",
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                    }
            
                return

        return

    def validate_script(self, xjob, profilename, scriptname, puboutput):
        validscripts = xjob.xpath('/job/scripts/script[label = "%s"]/validation/script'%scriptname)
        if not len(validscripts):
            return None
        xprofile = xjob.xpath('/job/profiles/profile[label = "%s"]'%profilename)[0]
        assembly_dir = self.assembly_dir(xjob)
        indata = puboutput
        listres = []
        outdata = None
        for script in validscripts:
            print script.get('name')
            outdata = self.start_script(script, xprofile, assembly_dir, indata)
            listres.append(outdata)
            indata = outdata
        print outdata
        return {
            'event':'result',
            'script':scriptname,
            'docs':outdata,
            'steps':listres,
            'time':time.time()
        }
    
    def validate_release(self):
        """  validation actions for release """
        valevents = []
        try:
            mf = json.loads(self.read(self._release_dir + "/manifest.json"))
            assembly = self._release_dir.rsplit('/',1)[1]
            xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ assembly +'_asm.xml')
            profilename = ""
            for event in mf:
                if event.get('event','') == "release_publication":
                    for event2 in event.get('content'):
                        if event2.get('event','') == "lang" and event2.get('label','') in self._publangs:
                            self._publang = event2.get('label','')
                            lgvalevent_content = []
                            for pubev in event2.get('content'):
                                if pubev.get('event')=="profile":
                                    profilename = pubev.get('label')
                                if pubev.get('event')=="result":
                                    puboutput = pubev.get('docs')
                                    scriptname = pubev.get('script')
                                    resscript = self.validate_script(xjob, profilename, scriptname, puboutput)
                                    if resscript is not None:
                                        lgvalevent_content.append(resscript)
                                        yield resscript
                            if len(lgvalevent_content):
                                valevents.append({'event':'lang', 'label':self._publang, 'content':lgvalevent_content})
                                
        except:
            import traceback
            errev = {
                'event':'error',
                'msg':"erreur lors de la validation",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            valevents.append(errev)
            yield errev

        finally:
            try:
                for event in mf:
                    if event.get('event','') == "release_validation":
                        for event2 in event.get('content'):
                            if event2.get('event','') == "lang" and event2.get('label','') in self._publangs:
                                event2.update({'content':[]})
                                event.get('content').remove(event2)
                    if len(event.get('content')) == 0:
                        mf.remove(event)
                        
                mf.append({
                    "event":"release_validation",
                    "path":self._release_dir,
                    "time": int(time.time()),
                    "content":valevents,
                    })
                self.write(json.dumps(mf), self._release_dir + '/manifest.json')
    
            except:
                import traceback
                
                yield {
                    'event':'error',
                    'msg':"impossible d'ouvrir le fichier manifeste",
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                    }
            
                return

        return 




if __name__ == '__main__':
    base = "/home/waloo/Bureau/kolekti/projets/test-multiscript/"
    p = ReleasePublisher('/releases/test-multiscripts_', base, langs=['de'])
    for e in p.validate_release():
        print e
