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

from django.utils.text import get_valid_filename

from publish_utils import PublisherMixin, PublisherExtensions, ReleasePublisherExtensions
from common import kolektiBase, XSLExtensions, LOCAL_ENCODING
from kolekti import plugins

logger = logging.getLogger(__name__)


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
#        logger.debug("kolekti %s"%self._version)

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
        return pl(*self.args, lang = self._publang)
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
#        logger.debug(ET.tostring(assembly)[:1000])
        
        # apply pre-assembly filtering  
        s = self.get_xsl('criteria', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly)
        self.log_xsl(s.error_log)
                        
        s = self.get_xsl('filter-assembly', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly)
        self.log_xsl(s.error_log)

        # process id and links
        s = self.get_xsl('process-id', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly)
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

            logger.exception("W: unable to create assembly directory")

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


        logger.debug('********************************** create settings')
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

        logger.debug('********************************** copy scripts resources')
        for profile in xjob.xpath("/job/profiles/profile[@enabled='1']"):
            # logger.debug(profile)
            s = self.get_xsl('filter', PublisherExtensions, profile=profile, lang=self._publang)
            fassembly = s(assembly)
            logger.debug('********************************** copy media')
            for event in self.copy_media(fassembly, profile, assembly_dir):
                events.append(event)

            for event in self.copy_variables(fassembly, profile, assembly_dir):
                events.append(event)

            # copy scripts resources
            for script in xjob.xpath("/job/scripts/script[not(.//script)][@enabled = 1]|/job/scripts/script[.//script][@enabled = 1]/*/script"):
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

                    logger.exception("resources for script %s not found"%scriptlabel)
                    
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

                    logger.exception("variables for script %s not found"%scriptlabel)

        return assembly, assembly_dir, pubname, events 



    def publish_job(self, assembly, xjob):
        """publishes a an assembly for every profile in xjob
           invoke publication scripts for every publication
            iterator : yields a result for each selected profile / script 
           """ 
        assembly_dir = self.assembly_dir(xjob)
#        date = self.get_date(self._publang)
#        hour = self.get_hour(self._publang)
#        revison = self.get_revision()
        author = self._author
        
        res=[]

        yield {'event':'job', 'label':xjob.get('id')}

        for profile in xjob.xpath('/job/profiles/profile'):
            if profile.get('enabled','0') == '1':
                profilename = profile.find('label').text

                yield {'event':'profile', 'label':'%s [%s]'%(profilename, self._publang)}

                # creates the document (pivot) file
                try:
                    pivot = self.publish_profile(assembly, profile, assembly_dir)
                except:
                    pivot = None
                    import traceback
                    logger.exception("Assembly Error")
                    yield {
                        'event':'error',
                        'msg':"erreur lors de l'assemblage",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
                    continue
                # invoke scripts
#                logger.debug( "starting scripts %s", profilename)
                logger.debug(ET.tostring(xjob))
                    
                for output in xjob.xpath("/job/scripts/script[@enabled = 1][.//script]"):
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
                            logger.exception("Script %s finished with errors"%scriptlabel)
                            yield {
                                'event':'error',
                                'msg':"Erreur d'execution du script %s"%scriptlabel,
                                'stacktrace':traceback.format_exc(),
                                'time':time.time(),
                                }
                            
                    yield {
                        'event':'result',
                        'script':scriptlabel,
                        'docs':outdata,
                        'steps':listres,
                        'time':time.time()
                    }
                        
                for script in xjob.xpath("/job/scripts/script[@enabled = 1][not(.//script)]"):
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
                        logger.exception("Script %s finished with errors"%script.find('label').text)
                        yield {
                            'event':'error',
                            'msg':"Erreur d'execution du script %s"%script.find('label').text,
                            'stacktrace':traceback.format_exc(),
                            'time':time.time(),
                            }
                if self._cleanup:
                    self.delete_resource(self.pubdir(assembly_dir, profile)+ "/document.xhtml")


        return 


    def publish_profile(self, assembly, profile, assembly_dir):
        """produces the pivot file from the assembly:
        apply profile filters,
        generate toc & index
        substitutes variables in content"""
        
        logger.info("* Publishing profile %s"%profile.xpath('string(label)'))

        pubdir = self.pubdir(assembly_dir, profile)
#        logger.debug('profile pub dir %s', pubdir)
        try:
            # logger.debug(assembly)
            # criteria
            s = self.get_xsl('criteria', self.getPublisherExtensions(), profile=profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            # filter
#            logger.debug("filter on profile")
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

            processed_id = assembly.xpath('/h:html/h:head/h:meta[@name="kolekti:processedid"][@content="yes"]', namespaces=self.nsmap)
            if len(processed_id):
                # process links
                s = self.get_xsl('broken-links', self.getPublisherExtensions(), profile = profile, lang=self._publang)
                assembly = s(assembly)
                self.log_xsl(s.error_log)
            else:
                # process links
                s = self.get_xsl('links', self.getPublisherExtensions(), profile = profile, lang=self._publang)
                assembly = s(assembly)
                self.log_xsl(s.error_log)

            # make index
            if assembly.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap):
                s = self.get_xsl('index', self.getPublisherExtensions(), profile = profile, lang=self._publang)
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
            logger.exception(s.error_log)
            logger.error("Error in publication process (xsl)")
            raise

        except:
            logger.exception("Error in publication process")
            raise
        
        # write pivot
        pivot = assembly
        pivfile = pubdir + "/document.xhtml"
        self.xwrite(pivot, pivfile, sync = False)
        pivfile = pubdir + "/" + get_valid_filename(profile.find('label').text) + ".xhtml"
        self.xwrite(pivot, pivfile, sync = False)  

        return pivot

    # create settings.xml file in assembly directory
    def create_settings(self, xjob, pubname, assembly_dir):
        try:
            self.makedirs(assembly_dir + "/kolekti")
        except:
            logger.exception("W: unable to create kolekti subdirectory")


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
                logger.exception('makedir failed')
                import traceback
                yield {
                        'event':'warning',
                        'msg':"impossible de créer le dossier de variables",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
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
                
        # copy generic variable file
        
        src_variables = [("kolekti/publication-templates/share", "labels.xml")]
        for srcdir, srcfile in src_variables:
            try:
                self.makedirs(assembly_dir + "/" +srcdir)
            except OSError:
                pass
            try:
                self.copyFile(srcdir + '/' + srcfile, assembly_dir + '/' + srcdir + '/' + srcfile)
            except:
                logger.exception('could not copy variable file')
                import traceback
                yield {
                    'event':'warning',
                    'msg':"fichier introuvable %s"%(srcdir.encode('utf-8') + '/' + srcfile.encode('utf-8'),),
                    'stacktrace':traceback.format_exc(),
                    'time':time.time(),
                    }
            
    # copy media to assembly space
    def copy_media(self, assembly, profile, assembly_dir):
        for med in assembly.xpath('//h:img[@src]|//h:embed[@src]|//h:a[@class="resource"][starts-with(@href, "/sources")]', namespaces=self.nsmap):
            if med.tag == "{%(h)s}a"%self.nsmap:
                ref = med.get('href')
            else:
                ref = med.get('src')

            ref = self.substitute_criteria(ref, profile)
            if ref[0] == '/':
                ref = ref[1:]
#            med.set('src',ref)
            logger.debug('image src : %s'%ref)
            try:
                refdir = "/".join([assembly_dir]+ref.split('/')[:-1])
                # refdir = os.path.join(assembly_dir + '/' + os.path.dirname(ref))
                self.makedirs(refdir)
            except OSError:
                logger.exception('makedir failed')
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
            logger.error("Script %s not found" %name)
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
            logger.exception('Unable to copy script libs')
            raise
        
        params = {}
        try:
            params = {}
            for p in script.xpath('parameters/parameter'):
                params.update({p.get('name'):p.get('value')})

            for pdef in scrdef.xpath('parameters/parameter'):
                pname = pdef.get('name')
                pval =  params.get(pname)
                logger.debug("copy libs %s %s"%(pname, pval))
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
            logger.exception("[Script %s] could not copy resources"%scriptlabel)
            raise
        
        
    def copy_script_variables(self, script, profile, assembly_dir):
        scriptlabel = script.find('filename').text
        scriptlabel = self.substitute_criteria(scriptlabel, profile)
        for variable in re.findall('{[ /a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+}', scriptlabel):
            # logger.debug(variable)
            splitVar = variable[1:-1].split(':')
            sheet = splitVar[0].strip()
            if sheet[0] != "/":
                variables_file = self.get_base_variable(sheet)
            else:
                variables_file = sheet
            srcdir,filer = variables_file.rsplit("/",1)
            self.script_copy(filer, srcdir, assembly_dir, 'xml')


    def start_script(self, script, profile, assembly_dir, inputs):
        # logger.debug(inputs)
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
        logger.debug('start script %s', name)
        params = {}
        for p in script.xpath('parameters/parameter'):
            params.update({p.get('name'):p.get('value')})


        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            logger.error("Impossible de trouver la définition du script: %s" %scriptlabel)
            raise


        # get the pivot ET document
        if isinstance(inputs, ET._ElementTree):
            pivot = inputs
            logger.debug('inputs ET %s', str(inputs)[:100])
        else:
            pivot = None
            for item in inputs:
                logger.debug(item)
                if item.get('type','') == 'pivot':
                    if 'ET' in item.keys():
                        pivot = item['ET']
                    if "file"  in item.keys():
                        pivot = self.parse(item['file'])
                    if "data" in  item.keys():
                        pivot = self.parse_string(item['data'])


        
        # shall we filter the pivot before applying the script
        if 'pivot_filter' in params :
            xfilter = params['pivot_filter']
            xdir = scrdef.xpath("string(parameters/parameter[@name='pivot_filter']/@dir)")
            xf = self.get_xsl(xfilter, xsldir = xdir)
            inputs = fpivot = xf(pivot)
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
                    logger.exception("Impossible de charger le script %(label)s"%{'label': scriptlabel.encode('utf-8')})
                    raise

                res = plugin(script, profile, assembly_dir, inputs)
                logger.debug("%(label)s ok"% {'label': scriptlabel.encode('utf-8')})

                
            elif stype=="shell":
                import platform
                system = platform.system()
                try:
                    cmd=scrdef.find("cmd[@os='%s']"%system).text
                except:
                    cmd=scrdef.xpath("cmd[not(@os)]")[0].text

                # if pivot on the command line, write the ET pivot into pivfile
                if cmd.find("_PIVOT_") >= 0:
                    self.xwrite(fpivot, pivfile, pretty_print = False, sync = False)
                    
                # if get file with local url                
                if cmd.find("_PIVLOCAL_") >= 0:
                    localdocument = fpivot
                    for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
                        localsrc = self.getOsPath(str(media.get('src')))
                        media.set('src', localsrc)

                cmd=self._substscript(cmd, subst, profile)
                cmd=cmd.encode(LOCAL_ENCODING)
                logger.debug(cmd)
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
                            logger.info("Attention %(warn)s"% {'warn': line})
                        elif re.search('error', line) or re.search('not found', line):
                            logger.error(line)
                            logger.error("Erreur lors de l'exécution de la commande : %(cmd)s:\n  %(error)s"%{'cmd': cmd.decode(LOCAL_ENCODING).encode('utf-8'),'error': line.encode('utf-8')})
                            has_error = True

                    # if no error display link
    
                    if not has_error:
                        xl=scrdef.find('link')
                        outfile=self._substscript(xl.get('name'), subst, profile)
                        outref=self._substscript(xl.get('ref'), subst, profile)
                        outtype=scrdef.get('output')
                        logger.debug("Exécution du script %(label)s réussie"% {'label': scriptlabel.encode('utf-8')})
                        res=[{"type":outtype, "label":outfile, "url":outref, "file":outref}]
                        
                except:
                    import traceback
                    logger.debug(traceback.format_exc())
                    logger.error("Erreur lors de l'execution du script %(label)s"% {'label': scriptlabel.encode('utf-8')})
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
                        logger.error("Impossible d'exécuter le script %(label)s"%{'label': label.encode('utf-8')})
                        raise
                    errors = set()
                    for err in xslt.error_log:
                        if not err.message in errors:
                            logger.debug(err.message)
                            errors.add(err.message)
                    logger.info("Exécution du script %(label)s réussie"%{'label': label.encode('utf-8')})

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
                    logger.error("Erreur lors de l'execution du script %(label)s"% {'label': scriptlabel.encode('utf-8')})
                    raise
            
        except:
            import traceback
            logger.debug(traceback.format_exc())
            logger.error("Impossible d'exécuter un script du job %(label)s"% {'label': scriptlabel.encode('utf-8')})
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

        logger.debug(("script less compile to",destcd))
        
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
            logger.info(out)

            if not exccmd.returncode == 0:
                err=exccmd.stderr.read()
                logger.debug(err)
                raise
        except:
            dbgexc()
            


    def script_copy(self, filer, srcdir, targetroot, ext):

        # copies file [srcdir]/[filer].[ext] to
        # [targetroot]/[srcdir]/[filer].[ext]
        # also copies recursively [filer].parts directory
        
        logger.debug("script copy %s %s %s %s", filer, srcdir, targetroot, ext)
        srcpath = self.get_base_template(srcdir)
        destpath = unicode(targetroot + "/" + srcdir)
        
        try:
            self.makedirs(destpath)
        except OSError:
            pass
        if filer is None:
            self.copyDirs(srcdir, destpath, sync = not self._draft)
        else:
            try:
                source= u"%s/%s.%s"%(srcdir,filer,ext)
                dest=   u"%s/%s.%s"%(destpath,filer,ext)
                logger.debug('copy resource %s -> %s'%(source, dest))
                self.copyFile(source, dest, sync = not self._draft)
            except:
                import traceback
                logger.error("Impossible de copier la ressource %s"%source)
                logger.debug(traceback.format_exc())
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
                    self.copyDirs(source,target, sync = not self._draft)

            except:
                logger.exception("Impossible de copier la ressource %s"%source)
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
        logger.debug("publish toc %s",toc)
        
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
        logger.debug('********************************** CREATE ASSEMBLY')

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
            
                logger.debug('********************************** PUBLISH ASSEMBLY')
                
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
                        logger.debug('Warning: could not remove tmp dir')
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
                mfevents = {
                    "event":"publication",
                    "path":assembly_dir,
                    "name":self.basename(pubname),
                    "title":pubtitle,
                    "time": int(time.time()),
                    "content":pubevents,
                    }
                self.write(json.dumps(mfevents), assembly_dir+"/manifest.json", sync = False)
    
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

    def make_release(self, toc, job, release_dir=None):
        """ releases a kolekti toc, using the profiles sets present in jobs list"""
        # toc = xjob.xpath('string(/*/*[self::toc]/@value)')
        res = []
        # toc = self.get_base_toc(toc) + ".html"
        
        logger.debug("release toc %s",toc)
        if isinstance(toc,ET._ElementTree):
            xtoc = toc
            if release_dir is None:
                raise Exception('Toc in xml format, with no release name provided')
        else:
            xtoc = self.parse(toc)
            for m in xtoc.xpath("/h:html/h:head/h:meta[starts-with(@name,'kolekti.')]",namespaces=self.nsmap):
                m.getparent().remove(m)
            ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.toc","content": toc})
            
        if isinstance(job,ET._ElementTree):
            xjob = job.getroot()
        else:
            xjob = self.parse(job).getroot()
            ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.job","content": job})

        release_dir = xjob.get('pubdir', release_dir)
        release_name = xjob.get('releasename', release_dir)
        release_index = xjob.get('releaseindex', "")
        release_prev_index = xjob.get('releaseprev')
        xjob.set('id',release_dir + '_asm')
        ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.project","content": self._project})
        ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.releasedir","content": release_dir})
        ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.releasename","content": release_name})
        ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.releaseindex","content": release_index})
        if not(release_prev_index is None):
            ET.SubElement(xtoc.xpath("/h:html/h:head",namespaces=self.nsmap)[0], "{http://www.w3.org/1999/xhtml}meta", attrib = {"name":"kolekti.releaseprev","content": release_prev_index})
        # logger.debug(ET.tostring(xtoc)[:1000])
        # assembly
        logger.debug('********************************** CREATE ASSEMBLY')
        try:
            assembly, assembly_dir, pubname, events = self.publish_assemble(xtoc, xjob)
            create_event = {
                "lang":self._publang,
                "assembly_dir":assembly_dir,
                "pubname":pubname,
                "releasedir":release_dir,
                "releasename":release_name,
                "releaseindex":release_index,
                "releaseprev":release_prev_index,                    
                "datetime":time.time(),

                "toc":xtoc.xpath('string(/h:html/h:head/h:meta[@name="kolekti.toc"]/@content)',namespaces=self.nsmap),
                "job":xtoc.xpath('string(/h:html/h:head/h:meta[@name="kolekti.job"]/@content)',namespaces=self.nsmap),
                }
            self.write(json.dumps(create_event), assembly_dir+"/release_info.json", sync = True)
            create_event.update({
                "event":"release_creation",
                "content":events,
            })
            res.append(create_event)

            # filter assembly with profiles
            from release import Release
            release = Release(*self.args, release=release_dir)
            release.apply_filters(self._publang)
            
            
        except:
            import traceback
            logger.exception('could not create assembly')
            errev = {
                'event':'error',
                'msg':" ",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            res.append(errev)

        self.write(json.dumps(res), '/releases/' + release_dir + "/manifest.json", sync = False)
#        assembly_path = "/".join(['releases', release_dir,'sources',self._publang,'assembly',pubname+'_asm.html'])
        
        return res

    # copies the job in release directory
    def create_settings(self, xjob, pubname, assembly_dir):
        try:
            self.makedirs(assembly_dir + "/kolekti/publication-parameters")
        except:
            logger.debug("W: unable to create release publication parameters directory")
            import traceback
            logger.debug(traceback.format_exc())

        self.xwrite(xjob, assembly_dir + "/kolekti/publication-parameters/" + pubname + ".xml")


class ReleaseTranslation(Publisher):
    def __init__(self, release_dir, *args, **kwargs):
        self._publangs = None
        if kwargs.has_key('lang'):
            self._publang = kwargs.get('lang')
            kwargs.pop('lang')
        self._release_dir = release_dir
        super(ReleaseTranslation, self).__init__(*args, **kwargs)
        if self._publangs is None:
            self._publangs = self.project_settings.xpath("/settings/languages/lang/text()")
        self._cleanup = False
        
    def getPublisherExtensions(self):        
        return ReleasePublisherExtensions

    def check_assembly(self, assembly):
        pass
    
class ReleasePublisher(Publisher):
    def __init__(self, release_dir, *args, **kwargs):
        self._publangs = None
        if kwargs.has_key('langs'):
            self._publangs = kwargs.get('langs')
            kwargs.pop('langs')
        self._release_dir = release_dir
        super(ReleasePublisher, self).__init__(*args, **kwargs)
        if self._publangs is None:
            self._publangs = self.project_settings.xpath("/settings/languages/lang/text()")
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
        
    def publish_assembly(self, assembly, active_profiles = None, active_outputs = None):
        try :
            xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ assembly +'.xml')
            logger.debug(active_profiles)
            logger.debug(active_outputs)
        except:
            import traceback
            errev = {
                'event':'error',
                'msg':"parametres de publication invalides",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            yield errev

        if active_profiles is not None:
            for p in xjob.xpath('/job/profiles/profile'):
                if p.find('label').text in active_profiles:
                    p.set('enabled', '1')
                else:
                    p.set('enabled', '0')

        has_output = False                    
        if active_outputs is not None:
            for o in xjob.xpath('/job/scripts/script'):
                o.set('enabled', '0')
                if o.find('label').text in active_outputs:
                    if o.get('multilang') is None:
                        o.set('enabled', '1')
                        has_output = True
        if has_output :
            for ev in self.publish_release(assembly, xjob):
                yield ev
                
        # has_output = False                    
        # if active_outputs is not None:
        #     for o in xjob.xpath('/job/scripts/script'):
        #         o.set('enabled', '0')
        #         if o.find('label').text in active_outputs:
        #             if o.get('multilang'):
        #                 o.set('enabled', '1')
        #                 has_output = True                        
        # if has_output :
        #     for ev in self.publish_release_multilang(assembly, xjob):
        #         yield ev            
            
        return

    def publish_assembly_multilang(self, assembly, active_profiles = None, active_outputs = None):
        """ publish an assembly in several languages to produce one document"""        
        try :
            xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ assembly +'.xml')
        except:
            import traceback
            errev = {
                'event':'error',
                'msg':"parametres de publication invalides",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            yield errev

        if active_profiles is not None:
            for p in xjob.xpath('/job/profiles/profile'):
                if p.find('label').text in active_profiles:
                    p.set('enabled', '1')
                else:
                    p.set('enabled', '0')

        has_output = False
        if active_outputs is not None:
            for o in xjob.xpath('/job/scripts/script[@multilang]'):
                o.set('enabled', '0')
                if o.find('label').text in active_outputs:
                    if o.get('multilang'):
                        o.set('enabled', '1')
                        has_output = True
        if has_output:
            for ev in self.publish_release_multilang(assembly, xjob):
                yield ev
        return

    
    def release_script_filename(self, release, lang, profile, script):
        scriptname = script.get('name')
        if scriptname == "multiscript":
            scriptname = script.xpath('string(publication/script[last()]/@name)')
        try:
            filename = self.substitute_criteria(script.find('filename').text, profile, extra = {'LANG':lang})
            filename = self.substitute_variables(filename, profile, extra = {'LANG':lang})
        except:
            return None
        try:
            profilepath = self.substitute_criteria(profile.find('dir').get('value'), profile, extra = {'LANG':lang})
            profilepath = self.substitute_criteria(profilepath, profile, extra = {'LANG':lang})
        except:
            logger.exception('unable to get profile path')
            

        # get link
        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%scriptname)[0]
        except IndexError:
            logger.exception("Script %s not found" %scriptname)
            return '', None, ''
        
        link = scrdef.find('link').get('ref')
        ptype = scrdef.find('link').get('type')
        link = link.replace('_PUBURI_', '/'.join([profilepath, lang]))
        link = link.replace('_PUBNAME_', filename)
        filepath = '/'.join(['/releases', release, link])
        return filepath, ptype, link
   
    def documents_release(self, release):
        try :
            xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ release +'_asm.xml')
        except:
            import traceback
            errev = {
                'event':'error',
                'msg':"parametres de publication invalides",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            logger.exception('unable to get pub params')
            yield errev, None, None, None
            return
        try:
            for jobscript in xjob.xpath('/job/scripts/script'):
                jobscript.set("enabled","0")
                for jobprofile in xjob.xpath('/job/profiles/profile[@enabled="1"]'):
                    for lang in self._publangs:
                        self._publang = lang
                        if self.exists(self._release_dir + '/sources/' + lang):
                            ref, reftype, link = self.release_script_filename(release, lang, jobprofile, jobscript)                
                            logger.debug(jobprofile.find('label').text)
                            logger.debug(link)
                            logger.debug(self.exists(ref))
                            logger.debug(reftype)
                            yield (jobprofile.find('label').text, link, ref, self.exists(ref), reftype)

        except:
            logger.exception('documents release error')
        return
                
    def publish_simple_pdf(self, assembly):
        try :
            xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ assembly +'.xml')
        except:
            import traceback
            errev = {
                'event':'error',
                'msg':"parametres de publication invalides",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            pubevents.append(errev)
            yield errev

        for jobscript in xjob.xpath('/job/scripts/script'):
            jobscript.set("enabled","0")
        for jobprofile in xjob.xpath('/job/profiles/profile'):
            jobprofile.find('dir').set('value',get_valid_filename(jobprofile.find('label').text))
            
        script = ET.XML("""
        <script name="weasyprint" enabled="1">
        <label>WPpdf</label>
        <filename>draft_{LANG}</filename>
        <parameters>
        <parameter name="CSS" value="revue_pdfA4"/>
        <parameter name="two_passes" value="no"/>
        </parameters>
        </script>""")
        xjob.xpath('/job/scripts')[0].append(script)

#        logger.debug(ET.tostring(xjob))
        
        for ev in self.publish_release(assembly, xjob):
            yield ev

        return

    def merge_pivots(self, pivots, listlang):
        srclang = 'en'
        
        pivot = ET.XML("<html xmlns='http://www.w3.org/1999/xhtml'><head></head><body></body></html>")
        head = pivot.xpath('/h:html/h:head', namespaces=self.nsmap)[0]
        body = pivot.xpath('/h:html/h:body', namespaces=self.nsmap)[0]
        srchead = pivots[srclang].xpath("/h:html/h:head", namespaces=self.nsmap)[0]
        for el in srchead:
            head.append(el)
            
        for pivlang in listlang:
            xpiv = pivots[pivlang]
            srcbody = xpiv.xpath('/h:html/h:body/*', namespaces=self.nsmap)
            div = ET.SubElement(body, '{http://www.w3.org/1999/xhtml}div', attrib = {"class":"body-lang", "data-lang":pivlang})
            for el in srcbody:
                div.append(el)
        
        return pivot
    
    def publish_release_multilang(self, assembly, xjob):
        """ publish an assembly in several languages to produce one document
            iterates on languages, profiles and outputs
        """
        pubevents = []
        logger.debug('publish')
        logger.debug(self._publangs)
        xassemblies = {}
        publangs = []        
        try :
            langspec = self.parse(self._release_dir + '/sources/share/multilang.xml')
            for lang in langspec.xpath('/languages/language'):
                publangs.append(lang.text)
        except:
            import traceback
            errevt = {
                'event':'error',
                'msg':"impossible de lire la liste des langues",
                'stacktrace':traceback.format_exc(),
                'time':time.time(),
            }
            logger.exception("unable to read language list for  %s"%assembly)
            yield errevt
            return
        
        try :
            for lang in publangs:
                langpubevt = []                
                self._publang = lang
                try:
                    xassemblies[lang] = self.parse(self._release_dir + '/sources/' + self._publang + '/assembly/'+ assembly + '.html')
                except:
                    import traceback
                    errevt = {
                        'event':'error',
                        'msg':"impossible de lire l'assemblage",
                        'stacktrace':traceback.format_exc(),
                        'time':time.time(),
                        }
                    logger.exception("unable to read assembly %s"%assembly)
                    langpubevt.append(errevt)
                    yield errevt
                    return
                
            for profile in xjob.xpath('/job/profiles/profile'):
                if profile.get('enabled','0') == '1':
                    xpivots = {}
                    profilename = profile.find('label').text
                    for lang in publangs:
                        self._publang = lang
                        assembly_dir = self.assembly_dir(xjob)
                        try:
                            xpivots[lang] = self.publish_profile(xassemblies[lang], profile, assembly_dir)
                        except:
                            import traceback
                            logger.exception("Assembly Error")
                            yield {
                                'event':'error',
                                'msg':"erreur lors de l'assemblage",
                                'stacktrace':traceback.format_exc(),
                                'time':time.time(),
                            }
                    
                    self._publang = "share"                    
                    # invoke scripts
                    pivot = self.merge_pivots(xpivots, publangs)

                    logger.debug("multiscripts")                    
                    for output in xjob.xpath("/job/scripts/script[@enabled = 1][.//script]"):
                        indata = ET.ElementTree(pivot)
                        listres = []
                        for script in output.xpath('publication/script'):
                            scriptlabel = script.xpath('string(ancestor::script/label)')
                            logger.debug(scriptlabel)
                            logger.debug(indata)
                            try:
                                outdata = self.start_script(script, profile, assembly_dir, indata)
                                listres.append(outdata)
                                indata = outdata
                            except:
                                import traceback
                                logger.exception("Script %s finished with errors"%scriptlabel)
                                yield {
                                    'event':'error',
                                    'msg':"Erreur d'execution du script %s"%scriptlabel,
                                    'stacktrace':traceback.format_exc(),
                                    'time':time.time(),
                                }
                            
                        yield {
                            'event':'result',
                            'script':scriptlabel,
                            'docs':outdata,
                            'steps':listres,
                            'time':time.time()
                        }
                        
                    logger.debug("scripts")                                            
                    for script in xjob.xpath("/job/scripts/script[@enabled = 1][not(.//script)]"):
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
                            logger.exception("Script %s finished with errors"%script.find('label').text)
                            yield {
                                'event':'error',
                                'msg':"Erreur d'execution du script %s"%script.find('label').text,
                                'stacktrace':traceback.format_exc(),
                                'time':time.time(),
                            }
                            
                    logger.debug("cleanup")                                                                        
                    if self._cleanup:
                        self.delete_resource(self.pubdir(assembly_dir, profile)+ "/document.xhtml")

                
                pubres = {"event":"publication_dir", "path":self._release_dir}
                langpubevt.append(pubres)
                yield pubres
                pubevents.append({'event':'lang', 'label':lang, 'content':langpubevt})
        except:
            import traceback
            logger.exception('erreur lors de la publication')
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
                                if event2.get('event','') == "lang" and event2.get('label','') in publangs:
                                    event2.update({'content':[]})
                except IOError:
                    mfevents = []
                     
                mfevents.append({
                    "event":"release_publication",
                    "path":self._release_dir,
                    "time": int(time.time()),
                    "content":pubevents,
                    })
                self.write(json.dumps(mfevents), self._release_dir + '/manifest.json', sync = False)
    
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


    def publish_release(self, assembly, xjob):
        """ publish an assembly one document per language
            iterates on languages, profiles and outputs
        """
        pubevents = []
        logger.debug('publish_release')
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
                    logger.exception("unable to read assembly %s"%assembly)
                    langpubevt.append(errevt)
                    yield errevt
                    return


                for pubres in self.publish_job(xassembly, xjob.getroot()):
                    langpubevt.append(pubres)
                    yield pubres
                
                pubres = {"event":"publication_dir", "path":self._release_dir}
                langpubevt.append(pubres)
                yield pubres
                pubevents.append({'event':'lang', 'label':lang, 'content':langpubevt})
        except:
            import traceback
            logger.exception('erreur lors de la publication')
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
                                if event2.get('event','') == "lang" and event2.get('label','') in self._publangs:
                                    event2.update({'content':[]})
                except IOError:
                    mfevents = []
                     
                mfevents.append({
                    "event":"release_publication",
                    "path":self._release_dir,
                    "time": int(time.time()),
                    "content":pubevents,
                    })
                self.write(json.dumps(mfevents), self._release_dir + '/manifest.json', sync = False)
    
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
        logger.debug("validate release %s %s"%(self._release_dir, self._publangs))
        try:
            mf = json.loads(self.read(self._release_dir + "/manifest.json"))
            assembly = self._release_dir.rsplit('/',1)[1]
            xjob = self.parse(self._release_dir + '/kolekti/publication-parameters/'+ assembly +'_asm.xml')
            profilename = ""
            for event in mf:
#                logger.debug(event['event'])
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
                                    print "validate:", puboutput, scriptname
                                    resscript = self.validate_script(xjob, profilename, scriptname, puboutput)
                                    if resscript is not None:
                                        lgvalevent_content.append(resscript)
                                        yield resscript
                            if len(lgvalevent_content):
                                valevents.append({'event':'lang', 'label':self._publang, 'content':lgvalevent_content})
                                
        except:
            import traceback
            logger.exception('erreur lors de la validation')
#            logger.debug(traceback.format_exc())
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
                self.write(json.dumps(mf), self._release_dir + '/manifest.json', sync = False)
    
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
