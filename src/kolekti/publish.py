# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import urllib
import re
import sys
import os
import copy
import logging

from lxml import etree as ET

from common import kolektiBase, XSLExtensions
LOCAL_ENCODING=sys.getfilesystemencoding()

class PublisherMixin(object):
    nsmap={"h":"http://www.w3.org/1999/xhtml"}
    def __init__(self, *args, **kwargs):
        self._publang = None
        if kwargs.has_key('lang'):
            self._publang = kwargs.get('lang')
            kwargs.pop('lang')
    
        super(PublisherMixin, self).__init__(*args, **kwargs)
        if self._publang is None:
            self._publang = self._config.get("sourcelang","en")

    def process_path(self, path):
        return self.substitute_criteria(path, ET.XML('<criteria/>'))

    def substitute_criteria(self,string, profile, extra={}):
        extra.update({"LANG":self._publang})
        return super(PublisherMixin, self).substitute_criteria(string, profile, extra=extra)




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
        logging.debug("get topic %s"%self.getUrlPath(path))
        return self.getUrlPath(path)
        
    def criteria(self, _, *args):
        return self._profile.xpath("criteria/criterion[@checked='1' or @user='1']")

    def lang(self, _, *args):
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
        
def test():
    testprofile = """
    <profile>
    </profile>"""
    profile = ET.XML(testprofile)
    pe = PublisherExtensions(profile)
    

class Publisher(PublisherMixin, kolektiBase):
    def __init__(self, *args,**kwargs):
        super(Publisher, self).__init__(*args, **kwargs)
        if self._publang is None:
            self._publang = self._config.get("sourcelang","en")
        
        self.scriptdefs = ET.parse(os.path.join(self._appdir,'pubscripts.xml')).getroot()
        logging.debug("kolekti %s"%self._version)
        
    def _variable(self, varfile, name):
        fvar = self.get_base_variable(varfile)
        xvar = self.parse(fvar)
        
        var = xvar.xpath('string(//h:variable[@code="%s"]/h:value[crit[@name="lang"][@value="%s"]]/h:content)'%(name,self._publang),
                         namespaces=self.nsmap)
        return unicode(var)

    def __substscript(self, s, subst, profile):
        for k,v in subst.iteritems():
            s = s.replace('_%s_'%k,v)
        return self.substitute_variables(self.substitute_criteria(s,profile),profile)


    # publishes a list of jobs
    
    def publish(self, jobs):
        for job in jobs:
            path = self.get_base_job(job) + ".xml"
            xjob = self.parse(path)
            self.publish_job(xjob)
            
    # publish a single job
    def publish_job(self, xjob):

        toc = xjob.xpath('string(/*/*[self::toc]/@value)')
        toc = self.process_path(toc)
        
        # parses and assembly the trame
        xtoc = self.parse(toc)
        assembly = self.publish_assemble(xtoc)

        for profile in xjob.xpath('/job/profiles/profile'):

            if profile.get('enabled','0') == '1':
                logging.info('publishing profile %s'%profile.find('label').text)
                # calculates and creates the publication directory 
                pubdir = self.substitute_variables(xjob.xpath('string(/*/pubdir/@value)'),profile)
                pubdir = self.substitute_criteria(pubdir, profile)
                pubdir = self.get_base_publication(pubdir)
                logging.debug('pubdir : %s'%pubdir)
                
                try:
                    self.makedirs(pubdir)
                except:
                    logging.info("publication path %s already exists"%pubdir)

                # creates the document (pivot) file
                pivot = self.publish_profile(profile, pubdir, assembly)

                # lunch scripts
                
                for script in xjob.xpath("/*/scripts/script[@enabled = 1]"):
                    try:
                        
                        self.copy_script_params(script, profile, pubdir)
                        self.start_script(script, profile, pubdir, pivot)
                        #print "--> Done script:",script.get('name')
                    except:
                        import traceback
                        logging.error("Script %s finished with errors"%script.get('name'))
                        logging.debug(traceback.format_exc())
                        raise Exception

    def publish_assemble(self, trame):
        xsassembly = self.get_xsl('assembly', PublisherExtensions, lang=self._publang)
        assembly = xsassembly(trame, lang="'%s'"%self._publang)
#        self.write(str(assembly), "/publications/ass.xml")
        return assembly
    
    def publish_profile(self, profile, pubdir, assembly):

        logging.info("* Publishing profile %s",profile.xpath('string(label)'))
        
        pubdirprofile = pubdir
        pubdirprofile_c = pubdir + "/" + self.substitute_criteria(profile.xpath('string(label)'), profile) + '_c'
        try:
            self.makedirs(pubdirprofile)
        except OSError:
            pass
        try:
            self.makedirs(pubdirprofile_c)
        except OSError:
            pass
        try:
            # criteria
            s = self.get_xsl('criteria', PublisherExtensions, profile=profile, lang=self._publang)
            assembly = s(assembly)
            # filter
            s = self.get_xsl('filter', PublisherExtensions, profile=profile, lang=self._publang)
            assembly = s(assembly)
            s = self.get_xsl('filter-empty-sections')
            assembly = s(assembly)
            # process title levels
            # s = self.get_xsl('titles', PublisherExtensions, profile = profile, lang=self._publang)
            # assembly = s(assembly)
            # substvars
            s = self.get_xsl('variables', PublisherExtensions, profile = profile, lang=self._publang)
            assembly = s(assembly)
            # process links
            s = self.get_xsl('links', PublisherExtensions, profile = profile, lang=self._publang)
            assembly = s(assembly)
            # make index
            if assembly.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap):
                s = self.get_xsl('index')
                assembly = s(assembly)
            # make toc
            # if assembly.xpath("//h:div[@class='TOC']", namespaces=self.nsmap):
            s = self.get_xsl('toc')
            assembly = s(assembly)
            
            # revision notes
            # s = self.get_xsl('csv-revnotes')
            # assembly = s(assembly)

            # cleanup title levels
            
            # s = self.get_xsl('titles', PublisherExtensions, profile = profile, lang=self._publang)
            # assembly = s(assembly)

        except ET.XSLTApplyError, e:
            logging.debug(s.error_log)
            logging.error("Error in publication prcess")
            raise Exception
        
        # copy media to _c, update src attributes in pivot
        
        for med in assembly.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):
            base = med.xpath("string(ancestor::h:div[@class='topic']/h:div[@class='topicinfo']/h:p[h:span/@class='infolabel' = 'source']/h:span[@class='infovalue'])", namespaces=self.nsmap)
            ref = med.get('src')
            ref = self.getPathFromSourceUrl(self.substitute_criteria(ref, profile))
            med.set('src',self.substitute_criteria(ref, profile)[1:])
            try:
                self.makedirs(pubdirprofile_c +'/'+'/'.join(ref.split('/')[:-1]))
            except OSError:
                pass
            self.copyFile(ref, pubdirprofile_c + ref)
            
        # write pivot
        pivot = assembly
        pivfile = pubdirprofile_c + "/document.xhtml"

        self.xwrite(pivot, pivfile)

        return pivot

    def copy_script_params(self, script, profile, pubdir):
        
        pubdirprofile_c = pubdir + "/" + self.substitute_criteria(profile.xpath('string(label)'), profile) + '_c'
        name=script.get('name')
        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            logging.error("Script %s not found" %name)
            raise Exception

        params = {}
        try:
            params = {}
            for p in script.xpath('parameters/parameter'):
                params.update({p.get('name'):p.get('value')})

            for pdef in scrdef.xpath('parameters/parameter'):
                pname = pdef.get('name')
                pval =  params.get(pname)
                print pname, pval
                if pval is not None and pdef.get('type')=='filelist':
                    if pdef.get('ext') == "less":
                        # TODO less compil
                        self.script_lesscompile(pval,
                                                unicode(pdef.get('dir')),
                                                pubdirprofile_c,
                                                '%s/%s'%(label,copyto))
                            
                    else:
                        self.script_copy(filer = pval,
                                         srcdir = unicode(pdef.get('dir')),
                                         targetroot = pubdirprofile_c,
                                         ext = pdef.get('ext'))
                if pdef.get('type')=='resource':
                    filer = unicode(pdef.get('file'))
                    srcdir = unicode(self.substitute_criteria(pdef.get('dir'), profile))
                    self.script_copy(filer = filer,
                                     srcdir = srcdir,
                                     targetroot = pubdirprofile_c,
                                     ext = pdef.get('ext'))

        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("[Script %s] could not copy resources"%name)
            raise Exception
        
        
        

    def start_script(self, script, profile, pubdir, pivot):
        label = profile.xpath('string(label)') 
        pubdirprofile = pubdir 
        pubdirprofile_c = pubdir + "/" + label + '_c'
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
            print "Impossible de trouver le script: %s" %label
            raise Exception

        
        # shall we filter the pivot before applying the script
        if 'pivot_filter' in params :
            xfilter = params['pivot_filter']
            xdir = scrdef.xpath("string(parameters/parameter[@name='pivot_filter']/@dir)")
            xf = self.get_xsl(xfilter, xsldir = self.get_base_layout(xdir))
            fpivot = xf(pivot)
            pivfile = pubdirprofile_c + "/filtered_" + pubname + ".xhtml"
            self.xwrite(fpivot, pivfile, pretty_print = False)
        else:
            fpivot = pivot
            pivfile = pubdirprofile_c + "/document.xhtml"

        subst = copy.copy(params)
        subst.update({
            "APPDIR":self._appdir,
            "PUBDIR":self.getOsPath(pubdirprofile),
            "SRCDIR":self.getOsPath(pubdirprofile_c),
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

                for msg in plugin(script, profile, pubdir, fpivot, self._publang):
                    print msg

                print "Exécution du script %(label)s réussie"% {'label': label.encode('utf-8')}

                
            elif stype=="shell":
                cmd=scrdef.find("cmd").text

                # if get file with local url                
                if cmd.find("_PIVLOCAL_") >= 0:
                    localdocument = fpivot
                    for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
                        localsrc = self.getOsPath(str(media.get('src')))
                        media.set('src', localsrc)

                cmd=self.__substscript(cmd, subst, profile)
                cmd=cmd.encode(LOCAL_ENCODING)
                print cmd

                try:
                    import subprocess
                    exccmd = subprocess.Popen(cmd, shell=True,
                                              stdin=subprocess.PIPE,
                                              stdout=subprocess.PIPE,
                                              stderr=subprocess.PIPE,
                                              close_fds=True)
                    err=exccmd.stderr.read()
                    out=exccmd.stdout.read()
                    err=err.decode(LOCAL_ENCODING)
                    out=out.decode(LOCAL_ENCODING)
                    has_error = False
                    for line in err.split('\n'):
                        # Doesn't display licence warning
                        if re.search('license.dat', line):
                            continue
                        # display warning or error
                        if re.search('warning', line):
                            print "Attention %(warn)s"% {'warn': line}
                        elif re.search('error', line) or re.search('not found', line):
                            print line
                            print "Erreur lors de l'exécution de la commande : %(cmd)s:\n  %(error)s"%{'cmd': cmd.decode(LOCAL_ENCODING).encode('utf-8'),
                                                                                                                  'error': line.encode('utf-8')}

                                                                                                                  
                        
                            has_error = True

                    # if no error display link
                    
                    if not has_error:
                        xl=scrdef.find('link')
                        outfile=self.__substscript(xl.get('name'), subst, profile)
                        outref=self.__substscript(xl.get('ref'), subst, profile)
                        print "Exécution du script %(label)s réussie"% {'label': label.encode('utf-8')}
                except:
                    import traceback
                    logging.debug(traceback.format_exc())
                    logging.error("Erreur lors de l'execution du script %(label)s"% {'label': label.encode('utf-8')})
                    raise Exception

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
                    xparams['PUBDIR']="'%s'"%self.model.pubpath.decode(LOCAL_ENCODING)

                    docf=xslt(self.pivdocument,**xparams)
                    try:
                        self.model.pubsave(str(docf),'/'.join((label,sout)))
                    except:
                        print "Impossible d'exécuter le script %(label)s"%{'label': label.encode('utf-8')}
                        return
                    errors = set()
                    for err in xslt.error_log:
                        if not err.message in errors:
                            print err.message
                            errors.add(err.message)
                    print "Exécution du script %(label)s réussie"%{'label': label.encode('utf-8')}

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
                    print "Erreur lors de l'execution du script %(label)s"% {'label': label.encode('utf-8')}
                    raise Exception
#            print "Script", label,"sucessful"
            
        except:
            import traceback
            logging.debug(traceback.format_exc())
            logging.error("Impossible d'exécuter un script du job %(label)s"% {'label': label.encode('utf-8')})
            raise Exception
        return




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

        debug(("script less compile to",destcd))
        
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
            if not exccmd.returncode == 0:
                err=exccmd.stderr.read()
                debug(err)
                raise Exception
        except:
            dbgexc()
            


    def script_copy(self, filer, srcdir, targetroot, ext):

        # copies file [srcdir]/[filer].[ext] to
        # [targetroot]/[srcdir]/[filer].[ext]
        # also copies recursively [filer].parts directory
        
        # print "script copy",value, dirname, pubdir, copyto, ext
        srcpath = self.get_base_layout(srcdir)
        destpath = unicode(targetroot + "/" + srcdir)
        
        try:
            self.makedirs(destpath)
        except OSError:
            pass
        try:
            source= u"%s/%s.%s"%(srcdir,filer,ext)
            dest=   u"%s/%s.%s"%(destpath,filer,ext)
            print source,'->', dest
            self.copyFile(source,dest)
        except:
            import traceback
            print traceback.format_exc()
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
            print traceback.format_exc()

            
