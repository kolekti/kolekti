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

from common import kolektiBase, XSLExtensions, LOCAL_ENCODING



class PublisherMixin(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"}
    def __init__(self, *args, **kwargs):
        # intercept lang & draft parameters

        self._publang = None
        if kwargs.has_key('lang'):
            self._publang = kwargs.get('lang')
            kwargs.pop('lang')

        self._draft = False
    
        super(PublisherMixin, self).__init__(*args, **kwargs)

        if self._publang is None:
            self._publang = self._config.get("sourcelang","en")
            
    def process_path(self, path):
        return self.substitute_criteria(path, ET.XML('<criteria/>'))

    def substitute_criteria(self, string, profile, extra={}):
        extra.update({"LANG":self._publang})
        return super(PublisherMixin, self).substitute_criteria(string, profile, extra=extra)

    
    def pubdir(self, assembly_dir, profile):
        # calculates and creates the publication directory
        pubdir = self.substitute_variables(profile.xpath('string(dir/@value)'),profile)
        pubdir = self.substitute_criteria(pubdir, profile)
        pubdir = assembly_dir + "/publications/" + pubdir
        logging.debug('pubdir : %s'%pubdir)

        try:
            self.makedirs(pubdir)
        except:
            logging.debug("publication path %s already exists"%pubdir)
        return pubdir
    
class PublisherExtensions(PublisherMixin, XSLExtensions):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extensions:functions:publication"

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('profile'):
            self._profile = kwargs.get('profile')
            kwargs.pop('profile')
        super(PublisherExtensions,self).__init__(*args, **kwargs)
        

    def gettopic(self, _, *args):
        modid = args[0]
        path = self.process_path(modid)
        upath = self.getUrlPath(path)
        logging.debug("get topic %s -> %s"%(modid,upath))
        return upath

    def gettopic2(self, _, *args):
        modid = args[0]
        path = self.process_path(modid)
        logging.debug("get topic path %s -> %s"%(modid,path))
        return path

    def criteria(self, _, *args):
        logging.debug('xslt ext criteria')
        return self._profile.xpath("criteria/criterion|/job/criteria/criterion")

    def criteria_definitions(self, _, *args):
        logging.debug('xslt ext criteria_definitions')
        return self._project_settings.xpath("/settings/criteria/criterion")

    def lang(self, _, *args):
        logging.debug('lang criteria_definitions')
        return self._publang
    
    def normpath(self, _, *args):
        """Returns normalized path"""

        path = args[0]
        try:
            src  = args[1]
            ndir = src.split('/')[:-1]
        except IndexError:
            ndir=[]
        ndir.extend(path.split('/'))
        newdir=[]
        for i in ndir :
            if i=='':
                pass
            if i=='.':
                pass
            if i=='..':
                newdir.pop()
            else:
                newdir.append(i)
        r= '/'.join(newdir)
        return r
        
    def replace_strvar(self, _, args):
        srcstr = self.substitute_criteria(args, self._profile)
        return self.substitute_variables(srcstr, self._profile)

    def replace_criteria(self, _, args):
        srcstr = args
        r = self.substitute_criteria(srcstr, self._profile)
        return r

    def variable(self, _, *args):
        sheet = self.substitute_criteria(args[0], self._profile)
        variable = self.substitute_criteria(args[1], self._profile)
        return unicode(self.variable_value(sheet, variable, self._profile, {"LANG":self._publang}))

    def evaluate_condition(self, _, args):
        conditions = args.replace(' ','')
        list_conditions = conditions.split(";")
        return ''
    
    def listdir(self, _, *args):
        path = args[0]
        ext = args[1]        
        try:
            return [os.path.splitext(f['name'])[0] for f in self.get_directory(path) if os.path.splitext(f['name'])[1][1:]==ext]
        except:
            return ["Error: path %s does not exist"%path]



def test():
    testprofile = """
    <profile>
    </profile>"""
    profile = ET.XML(testprofile)
    pe = PublisherExtensions(profile)
    pe.listdir('/sources')

class Publisher(PublisherMixin, kolektiBase):
    """Manage all publication process functions, assembly tocs, filters assemblies, invoke scripts
       instaciation parameters : lang + superclass parameters
    """
    def __init__(self, *args,**kwargs):
        super(Publisher, self).__init__(*args, **kwargs)

        # moved to PublisherMixin init
        #if self._publang is None:
        #    self._publang = self._config.get("sourcelang","en")
        
        self.scriptdefs = ET.parse(os.path.join(self._appdir,'pubscripts.xml')).getroot()
        logging.debug("kolekti %s"%self._version)
        
    def _variable(self, varfile, name):
        """returns the actual value for a variable in a given xml variable file"""
        fvar = self.get_base_variable(varfile)
        xvar = self.parse(fvar)
        
        var = xvar.xpath('string(//h:variable[@code="%s"]/h:value[crit[@name="lang"][@value="%s"]]/h:content)'%(name,self._publang),
                         namespaces=self.nsmap)
        return unicode(var)

    def __substscript(self, s, subst, profile):
        """substitues all _NAME_ by its profile value in string s""" 
        for k,v in subst.iteritems():
            s = s.replace('_%s_'%k,v)
        return self.substitute_variables(self.substitute_criteria(s,profile),profile)


		

    def publish_assemble(self, toc, xjob):
        """create and return an assembly from the toc using the xjob critria for filtering"""
        assembly_dir = self.assembly_dir(xjob)

        logging.debug('********************************** process toc')

        xsassembly = self.get_xsl('assembly', PublisherExtensions, lang=self._publang)
        assembly = xsassembly(toc, lang="'%s'"%self._publang)
        self.log_xsl(xsassembly.error_log)

        logging.debug('********************************** filter assembly')
        # criteria
        s = self.get_xsl('criteria', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly)
        self.log_xsl(s.error_log)
                        
        s = self.get_xsl('filter', PublisherExtensions, profile=xjob, lang=self._publang)
        assembly = s(assembly,action="'assemble'")
        self.log_xsl(s.error_log)

        # logging.debug("after cond! %s"%str([ET.tostring(c) for c in assembly.xpath('//*[local-name() = "cond"]')
            

        pubname = xjob.get('id','')
        pubname = self.substitute_criteria(pubname, xjob)
        
        if self._draft:
            pubname += "_draft"
            
        try:
            self.makedirs(assembly_dir + "/sources/" + self._publang + "/assembly")
        except:
            logging.debug("W: unable to create assembly directory")
            import traceback
            logging.debug(traceback.format_exc())
            
        self.xwrite(assembly, assembly_dir + "/sources/"+ self._publang + "/assembly/" + pubname + ".html")


        logging.debug('********************************** create settings')
        self.create_settings(xjob, pubname, assembly_dir)

        logging.debug('********************************** copy scripts resources')
        for profile in xjob.xpath("/job/profiles/profile[@enabled='1']"):
            # logging.debug(profile)
            s = self.get_xsl('filter', PublisherExtensions, profile=profile, lang=self._publang)
            fassembly = s(assembly)
            logging.debug('********************************** copy media')
            self.copy_media(fassembly, profile, assembly_dir)

            # copy scripts resources
            for script in xjob.xpath("/job/scripts/script[@enabled = 1]"):
                try:
                    self.copy_script_params(script, profile, assembly_dir)
                except:
                    import traceback
                    logging.error("resources for script %s not found"%script.get('name'))
                    logging.debug(traceback.format_exc())
                    raise Exception

        return assembly, assembly_dir, pubname 



    def publish_job(self, assembly, xjob):
        """publishes a an assembly for every profile in xjob
           invoke publication scripts for every publication """ 
        assembly_dir = self.assembly_dir(xjob)
        res=[]
        
        # logging.debug(ET.tostring(xjob))
        for profile in xjob.xpath('/job/profiles/profile'):
            #  logging.debug(profile)
            if profile.get('enabled','0') == '1':
                resscripts = []
                # creates the document (pivot) file
                pivot = self.publish_profile(assembly, profile, assembly_dir)
                
                 # invoke scripts
                for script in xjob.xpath("/*/scripts/script[@enabled = 1]"):
                    try:
                        resscript = self.start_script(script, profile, assembly_dir, pivot)
                        resscripts.append({"script":script.get('name'),"docs":resscript})
                    except:
                        import traceback
                        logging.error("Script %s finished with errors"%script.get('name'))
                        logging.debug(traceback.format_exc())
                        raise Exception
                res.append({'profile':profile.find('label').text,
                            'scripts':resscripts,
                            'time':time.time(), #datetime.now(),
                            })
        return res


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
            s = self.get_xsl('criteria', PublisherExtensions, profile=profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            # filter
            logging.debug("filter on profile")
            s = self.get_xsl('filter', PublisherExtensions, profile=profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            s = self.get_xsl('filter-empty-sections')
            assembly = s(assembly)
            self.log_xsl(s.error_log)

            # substvars
            s = self.get_xsl('variables', PublisherExtensions, profile = profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)

            # process links
            s = self.get_xsl('links', PublisherExtensions, profile = profile, lang=self._publang)
            assembly = s(assembly)
            self.log_xsl(s.error_log)

            # make index
            if assembly.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap):
                s = self.get_xsl('index')
                assembly = s(assembly)
                self.log_xsl(s.error_log)

            # make toc
            # if assembly.xpath("//h:div[@class='TOC']", namespaces=self.nsmap):
            s = self.get_xsl('toc')
            assembly = s(assembly)
            self.log_xsl(s.error_log)
            
            # revision notes
            # s = self.get_xsl('csv-revnotes')
            # assembly = s(assembly)

            # cleanup title levels
            
            # s = self.get_xsl('titles', PublisherExtensions, profile = profile, lang=self._publang)
            # assembly = s(assembly)
            
        except ET.XSLTApplyError, e:
            logging.debug(s.error_log)
            logging.error("Error in publication process")
            raise Exception

        except:
            logging.debug(s.error_log)
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Error in publication process")
            raise Exception
        
        # write pivot
        pivot = assembly
        pivfile = pubdir + "/document.xhtml"

        self.xwrite(pivot, pivfile)
        return pivot

    # create settings.xml file in assembly directory
    def create_settings(self, xjob, pubname, assembly_dir):
        pass


 
            
    # copy media to _c, update src attributes in assembly
    def copy_media(self, assembly, profile, assembly_dir):
        for med in assembly.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):
            ref = med.get('src')
            ref = self.substitute_criteria(ref, profile)
            if ref[0] == '/':
                ref = ref[1:]
            med.set('src',ref)
            logging.debug('image src : %s'%ref)
            try:
                refdir = os.path.join(assembly_dir + '/' + os.path.dirname(ref))
                self.makedirs(refdir)
            except OSError:
                logging.debug('makedir failed')
                import traceback
                logging.debug(traceback.format_exc())

            self.copyFile(ref, assembly_dir + '/' + ref)

    def copy_script_params(self, script, profile, assembly_dir):
        pubdir = self.pubdir(assembly_dir, profile)
        name=script.get('name')
        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            logging.error("Script %s not found" %name)
            raise Exception

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
            raise Exception
        
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
                        self.script_copy(filer = pval,
                                         srcdir = srcdir,
                                         targetroot = assembly_dir,
                                         ext = pdef.get('ext'))
                if pdef.get('type')=='resource':
                    filer = unicode(pdef.get('file'))
                    srcdir = unicode(self.substitute_criteria(pdef.get('dir'), profile))
                    self.script_copy(filer = filer,
                                     srcdir = srcdir,
                                     targetroot = assembly_dir,
                                     ext = pdef.get('ext'))

        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("[Script %s] could not copy resources"%name)
            raise Exception
        
        
    


    def start_script(self, script, profile, assembly_dir, pivot):
        res = None
        pubdir = self.pubdir(assembly_dir, profile)
        label =  self.substitute_variables(self.substitute_criteria(unicode(profile.xpath('string(label)')),profile), profile)
        suffix = self.substitute_variables(self.substitute_criteria(unicode(script.xpath("string(suffix[@enabled='1'])")),profile), profile)
        if len(suffix):
            pubname = "%s_%s"%(label, suffix)
        else:
            pubname = label
            
        name=script.get('name')
        params = {}
        for p in script.xpath('parameters/parameter'):
            params.update({p.get('name'):p.get('value')})


        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            logging.error("Impossible de trouver le script: %s" %label)
            raise Exception

        
        # shall we filter the pivot before applying the script
        if 'pivot_filter' in params :
            xfilter = params['pivot_filter']
            xdir = scrdef.xpath("string(parameters/parameter[@name='pivot_filter']/@dir)")
            xf = self.get_xsl(xfilter, xsldir = xdir)
            fpivot = xf(pivot)
            self.log_xsl(xf.error_log)

            pivfile = pubdir + "/filtered_" + pubname + ".xhtml"
            self.xwrite(fpivot, pivfile, pretty_print = False)
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
                from kolekti.plugins import getPlugin
                
                plugname=scrdef.find("plugin").text
                try:
                    plugin = self.get_script(plugname)
                except:
                    logging.error("Impossible de charger le script %(label)s"%{'label': plugname.encode('utf-8')})
                    import traceback
                    logging.debug(traceback.format_exc())
                    raise Exception

                res = plugin(script, profile, assembly_dir, fpivot, self._publang)
            
                #logging.info("%(label)s ok"% {'label': plugname.encode('utf-8')})

                
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

                cmd=self.__substscript(cmd, subst, profile)
                cmd=cmd.encode(LOCAL_ENCODING)
                logging.debug(cmd)
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
                        outfile=self.__substscript(xl.get('name'), subst, profile)
                        outref=self.__substscript(xl.get('ref'), subst, profile)
                        outtype=xl.get('type')
                        logging.debug("Exécution du script %(label)s réussie"% {'label': label.encode('utf-8')})
                        res=[{"type":outtype, "label":outfile, "url":outref}]
                except:
                    import traceback
                    logging.debug(traceback.format_exc())
                    logging.error("Erreur lors de l'execution du script %(label)s"% {'label': label.encode('utf-8')})
                    raise Exception

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
                    sout=self.__substscript(sout, subst, profile)

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
                        raise Exception
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
                    logging.error("Erreur lors de l'execution du script %(label)s"% {'label': label.encode('utf-8')})
                    raise Exception
            
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Impossible d'exécuter un script du job %(label)s"% {'label': label.encode('utf-8')})
            raise Exception
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
                raise Exception
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
        try:
            source= u"%s/%s.%s"%(srcdir,filer,ext)
            dest=   u"%s/%s.%s"%(destpath,filer,ext)
            logging.debug('copy resource %s -> %s'%(source, dest))
            self.copyFile(source,dest)
        except:
            import traceback
            logging.error("Impossible de copier la ressource %s"%source)
            logging.debug(traceback.format_exc())
            raise Exception
        
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
            raise Exception







                    
class DraftPublisher(Publisher):
    def __init__(self, *args, **kwargs):
        super(DraftPublisher, self).__init__(*args, **kwargs)
        self._draft = True

    def assembly_dir(self, xjob):
        assembly_dir = self.substitute_variables(xjob.xpath('string(/job/dir/@value)'),xjob)
        assembly_dir = self.substitute_criteria(assembly_dir, xjob)
        assembly_dir = "/drafts/" + assembly_dir
        if assembly_dir[-1] != "/":
            assembly_dir += "/"
        return assembly_dir

    def cleanup_assembly_dir(self, xjob):
        assembly_dir = self.assembly_dir(xjob)
        self.rmtree(assembly_dir + "/sources")
        self.rmtree(assembly_dir + "/kolekti")
        

    # publishes a list of jobs
    
    def publish_draft(self, toc, jobs=None):
        """ publishes a kolekti toc, using the profiles sets present in jobs list"""
        
        # toc = xjob.xpath('string(/*/*[self::toc]/@value)')
        # toc = self.get_base_toc(toc) + ".html"
        logging.debug("publish toc %s",toc)
        if isinstance(toc,ET._ElementTree):
            xtoc = toc
        else:
            xtoc = self.parse(toc)
        publications = []
        
        for job in jobs:
            # path = self.get_base_job(job) + ".xml"
            if isinstance(job,ET._ElementTree):
                xjob = job
            else:
                xjob = self.parse(job)
            # assembly
            logging.debug('********************************** CREATE ASSEMBLY')
            assembly, assembly_dir, pubname = self.publish_assemble(xtoc, xjob.getroot())

            logging.debug('********************************** PUBLISH ASSEMBLY')
            pubres = self.publish_job(assembly, xjob.getroot())

            publications.append({"job":xjob.getroot().get('id'), "publications":pubres})
            try:
                pass
                #self.cleanup_assembly_dir(xjob.getroot())
            except:
                logging.debug('Warning: could not remove tmp dir')
        # self.write(json.dumps(publications), assembly_dir+'/kolekti/'+ pubname +'_publications.json')
        return publications
    
class Releaser(Publisher):
    def __init__(self, *args, **kwargs):
        super(Releaser, self).__init__(*args, **kwargs)
        
    def assembly_dir(self, xjob):
        assembly_dir = self.substitute_variables(xjob.xpath('string(/job/dir/@value)'),xjob)
        assembly_dir = self.substitute_criteria(assembly_dir, xjob)
        assembly_dir = "/releases/" + assembly_dir
        return assembly_dir

    def make_release(self, toc, jobs):
        """ releases a kolekti toc, using the profiles sets present in jobs list"""
        # toc = xjob.xpath('string(/*/*[self::toc]/@value)')
        res = []
        # toc = self.get_base_toc(toc) + ".html"
        logging.debug("release toc %s",toc)
        if isinstance(toc,ET._ElementTree):
            xtoc = toc
        else:
            xtoc = self.parse(toc)
        for job in jobs:
            # path = self.get_base_job(job) + ".xml"
            if isinstance(job,ET._ElementTree):
                xjob = job
            else:
                xjob = self.parse(job)
            # assembly
            logging.debug('********************************** CREATE ASSEMBLY')
            assembly, assembly_dir, pubname = self.publish_assemble(xtoc, xjob.getroot())
            res.append({"assembly_dir":assembly_dir,
                        "pubname":pubname,
                        "datetime":time.time(), #datetime.now(),
                        "job":unicode(xjob.getroot().get('id')),
                        "toc":xtoc.xpath('/html:html/html:head/html:title/text()',namespaces={"html":"http://www.w3.org/1999/xhtml"})
                })

        self.write('<publication type="release"/>', assembly_dir+"/.manifest")
        self.write(json.dumps(res), assembly_dir+"/kolekti/publication-parameters/"+pubname+"_"+self._publang+"_parameters.json")
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
    def __init__(self, *args, **kwargs):
        super(ReleasePublisher, self).__init__(*args, **kwargs)

    def assembly_dir(self, xjob):
        assembly_dir = self.substitute_variables(xjob.xpath('string(/job/dir/@value)'),xjob)
        assembly_dir = self.substitute_criteria(assembly_dir, xjob)
        assembly_dir = "/releases/" + assembly_dir
        return assembly_dir

    def cleanup_assembly_dir(self, xjob):
        pass

    def publish_assembly(self, release, assembly):
        """ publish an assembly"""
        assembly_dir = 'releases/' + release
        try:
            xassembly = self.parse('releases/' + release + '/sources/' + self._publang + '/assembly/'+ assembly + '.html')
        except:
            logging.error("unable to read assembly %s"%assembly)
            import traceback
            logging.debug(traceback.format_exc())
            
        xjob = self.parse('releases/' + release + '/kolekti/publication-parameters/'+ assembly +'.xml')
        xjob=xjob.getroot()
        publications = self.publish_job(xassembly,xjob)
        self.write(json.dumps(publications), assembly_dir+'/kolekti/publication-parameters/'+ assembly + '_' + self._publang + '_publications.json')
        return [{"job":xjob.get('id'), "publications":publications}]
