# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)

import urllib
import re
import sys
import os

from lxml import etree as ET

from common import kolektiBase, XSLExtensions
LOCAL_ENCODING=sys.getfilesystemencoding()

class PublishExtensions(XSLExtensions):
    ens = "kolekti:extensions:functions:publication"
    nsmap={"h":"http://www.w3.org/1999/xhtml"}

    def __init__(self, *args, **kwargs):
        if kwargs.has_key('profile'):
            self.profile = kwargs.get('profile')
            kwargs.pop('profile')
        if kwargs.has_key('lang'):
            self.publang = kwargs.get('lang')
            kwargs.pop('lang')
        super(PublishExtensions,self).__init__(*args, **kwargs)
        
    def getmodule(self, _, *args):
        modid = args[0]
        urlf = urllib.pathname2url(modid[1:].encode('utf-8'))
        if self.config['version'] == "0.6":
            url =  'file://'+urllib.pathname2url(self.path)+'/'+urlf
        else:
            url =  'file://'+urllib.pathname2url(self.path)+"/sources/"+self.publang+"/"+urlf
        return url
    
    def criterias(self, _, *args):
        return self.profile.xpath("criterias/criteria[@checked='1']")

    def lang(self, _, *args):
        return self.publang
    
    def replace_crit(self,_,*args):
        srcstr=args[0]
        crits=self.profile.xpath("criterias/criteria[@checked='1']")
        critdict={}
        for c in crits:
            critdict.update({c.get('code'):c.get('value')})
        critdict.update({'LANG':self.publang})

        for crit,val in critdict.iteritems():
            srcstr=srcstr.replace('_%s_'%crit,val)
        srcstr=srcstr.replace("_LANG_", self.publang)
        return srcstr

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
        srcstr = args[0]
        for variab in re.findall('\[var[ a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+\]', srcstr):
            splitVar = variab[4:-1].split(':')
            sheet = splitVar[0].strip()
            v = splitVar[1].strip()
            val = self.variable(None, sheet, v)
            srcstr=srcstr.replace(variab, val)
        return srcstr

    def variable(self, _, *args):
        varfile = args[0]
        name = args[1]
        if self.kolektiversion == "0.6":
            fvar = 'sheets/xml/'+varfile+'.xml'
        else:
            fvar = 'sources/share/xml/'+varfile+'.xml'
        xvar = ET.parse(os.path.join(self.path, fvar))
        var = xvar.xpath('string(//h:variable[@code="%s"]/h:value[crit[@name="lang"][@value="%s"]]/h:content)'%(name,self.publang),
                         namespaces=self.nsmap)
        return unicode(var)




class Publisher(kolektiBase):
    nsmap={"h":"http://www.w3.org/1999/xhtml"}

    def __init__(self, *args,**kwargs):
        self.publang = None
        if kwargs.has_key('lang'):
            self.publang = kwargs.get('lang')
            kwargs.pop('lang')
        super(Publisher, self).__init__(*args, **kwargs)
        if self.publang is None:
            self.publang = self.config.get("sourcelang","en")
        
        self.scriptdefs = ET.parse(os.path.join(self.appdir,'pubscripts.xml')).getroot()

        
    def _variable(self, varfile, name):
        if self.config['version'] == "0.6":
            fvar = '/sheets/xml/'+varfile+'.xml'
        else:
            fvar = '/sources/share/xml/'+varfile+'.xml'
        xvar = self.parse(fvar)
        var = xvar.xpath('string(//h:variable[@code="%s"]/h:value[crit[@name="lang"][@value="%s"]]/h:content)'%(name,self.publang),
                         namespaces=self.nsmap)
        return unicode(var)

    def substvar(self, srcstr):
        for variab in re.findall('\[var[ a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+\]', srcstr):
            splitVar = variab[4:-1].split(':')
            sheet = splitVar[0].strip()
            v = splitVar[1].strip()
            val = self._variable(sheet, v)
            srcstr=srcstr.replace(variab, val)
        return srcstr

    def substcrit(self,srcstr, profile):
        crits=profile.xpath("criterias/criteria[@checked='1']")
        critdict={}
        for c in crits:
            critdict.update({c.get('code'):c.get('value')})
        critdict.update({'LANG':self.publang})

        for crit,val in critdict.iteritems():
            srcstr=srcstr.replace('_%s_'%crit,val)
        srcstr=srcstr.replace("_LANG_", self.publang)
        return srcstr



    def publish(self, orders):        
        for order in orders:
            xorder = self.get_order(order)
            self.publish_order(xorder)

    def publication_init(self, path, pubtitle):
        try:
            pubref='/publications/'+path
            self.makedirs(pubref)
        except:
            # import traceback
            # print traceback.format_exc()
            print "Warning: publication path", path, "already exists"
        try:
            pubref_c='/publications/'+path + '_c'
            self.makedirs(pubref_c)
        except:
            pass
        return pubref
    
    def get_order(self, order):
        if self.config['version'] == "0.6":
            order = "configuration/orders/" + order + ".xml"
        else:
            order = "kolekti/orders/" + order + ".xml"
        xorder = self.parse(order)
        return xorder

    def publish_order(self, xorder):
        
        pubdir = self.substvar(xorder.xpath('string(/order/pubdir/@value)'))
        pubtitle = self.substvar(xorder.xpath('string(/order/pubtitle/@value)'))
        trame = xorder.xpath('string(/order/trame/@value)')
        if self.version == "0.6":
            trame = trame[1:]
        else:
            trame = '/sources/' + self.publang + '/' + trame[1:]
            
        pubdir = self.publication_init(pubdir, pubtitle)
        xtrame = self.parse(trame)
        assembly = self.publish_assemble(pubdir, pubtitle, xtrame)
        print "publishing profiles"
        for profile in xorder.xpath('/order/profiles/profile'):
            if profile.get('enabled',False):
                pivot = self.publish_profile(profile, pubdir, assembly)
                for script in xorder.xpath("/order/scripts/script[@enabled = 1]"):
                    print "Starting",script.get('name')
                    try:
                        self.publish_script(script, profile, pubdir, pivot)
                    except:
                        print "Error with",script.get('name')
                        import traceback
                        print traceback.format_exc()
                
    def publish_assemble(self, pubdir, pubtitle, trame):
        xsassembly = self.get_xsl('assembly', PublishExtensions, lang=self.publang)
        assembly = xsassembly(trame, lang=self.publang, title="'%s'"%pubtitle)
        assfile = pubdir + "_c/content.xhtml"
        self.write(str(assembly), assfile)
        return assembly
    
    def publish_profile(self, profile, pubdir, assembly):
        print "publish profile",profile.xpath('string(label)')
        pubdirprofile = pubdir + "/" + profile.xpath('string(label)')
        pubdirprofile_c = pubdir + "/" + profile.xpath('string(label)') + '_c'
        try:
            self.makedirs(pubdirprofile)
        except OSError:
            pass
        try:
            self.makedirs(pubdirprofile_c)
        except OSError:
            pass
        try:
            # criterias
            s = self.get_xsl('criterias', PublishExtensions, profile=profile, lang=self.publang)
            assembly = s(assembly)
            # filter
            s = self.get_xsl('filter', PublishExtensions, profile=profile, lang=self.publang)
            assembly = s(assembly)
            s = self.get_xsl('filter-empty-sections')
            assembly = s(assembly)
            # substvars
            s = self.get_xsl('variables', PublishExtensions, profile = profile, lang=self.publang)
            assembly = s(assembly)
            # process links
            s = self.get_xsl('links', PublishExtensions, profile = profile, lang=self.publang)
            assembly = s(assembly)
            # make index
            if assembly.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap):
                s = self.get_xsl('index')
                assembly = s(assembly)
            # make toc
            if assembly.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap):
                s = self.get_xsl('tdm')
                assembly = s(assembly)
            
            # revision notes
            # s = self.get_xsl('csv-revnotes')
            # assembly = s(assembly)
        except ET.XSLTApplyError, e:
            print s.error_log

        # media
        for med in assembly.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):
            ref = med.get('src')
            ref = self.getPathFromUrl(self.substcrit(ref, profile))
            try:
                self.makedirs(pubdirprofile_c +'/'+'/'.join(ref.split('/')[:-1]))
            except OSError:
                pass
            self.copyFile(ref, pubdirprofile_c + "/" + ref)
            
        # write pivot
        pivot = assembly
        pivfile = pubdirprofile_c + "/document.xhtml"
        self.write(str(pivot), pivfile)
        return pivot

    def publish_script(self, script, profile, pubdir, pivot):
        print
        print "script", script, profile, pubdir
        pubdirprofile = pubdir + "/" + profile.xpath('string(label)')
        pubdirprofile_c = pubdir + "/" + profile.xpath('string(label)') + '_c'
        suffix = self.substvar(self.substcrit(unicode(script.xpath("string(suffix[@enabled='1'])")),profile))
        name=script.get('name')
        params = {}
        for p in script.xpath('parameters/parameter'):
            params.update({p.get('name'):p.get('value')})
        label=name + suffix

        try:
            scrdef=self.scriptdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
        except IndexError:
            print "Impossible de trouver le script: %s" %label
            return
        
        try:
            # copy when parameters says to copy
            for pname,pval in params.iteritems():
                pdef=scrdef.xpath("parameters/parameter[@name='%s']"%pname)[0]
                if pdef.get('type')=='filelist' and pdef.get('copyto') is not None: 
                    if pdef.get('ext') == "less":
                        self.script_lesscompile(pval,
                                                unicode(pdef.get('dir')),
                                                pubdirprofile,
                                                '%s/%s'%(label,pdef.get('copyto')))
                            
                    else:
                        self.script_copy(pval,
                                         unicode(pdef.get('dir')),
                                         pubdirprofile,
                                         '%s/%s'%(label,pdef.get('copyto')),
                                         pdef.get('ext'))
                        self.script_copy(pval,
                                         unicode(pdef.get('dir')),
                                         pubdirprofile_c,
                                         'stylesheets/%s/%s'%(label,pdef.get('copyto')),
                                         pdef.get('ext'))

            stype=scrdef.get('type')
        except:
            import traceback
            print traceback.format_exc()
            print "[Script %s] Erreur lors de la copie des ressources"%label
            return
        try:
            if stype=="plugin":
                from kolekti.plugins import getPlugin
                
                plugname=scrdef.find("plugin").text
                try:
                    plugin = self.get_script(plugname)
                except:
                    import traceback
                    print traceback.format_exc()
                    print "Impossible de charger le script %(label)s", {'label': label.encode('utf-8')}
                    return

                for msg in plugin(script, profile, pubdir, pivot, self.publang):
                    print msg

                print "Exécution du script %(label)s réussie"% {'label': label.encode('utf-8')}
                


        except:
            print "Impossible d'exécuter le script %(label)s"% {'label': label.encode('utf-8')}
            import traceback
            print traceback.format_exc()
        




    def foo(self):
        try:
            if stype=="shell":
                cmd=scrdef.find("cmd").text
                # if get file with local url
                if cmd.find("_PIVLOCAL_") >= 0:
                    localdocument = pivot
                    for media in pivot.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
                        localsrc = self.model.abstractIO.local2unicode(self.model.url2local(str(media.get('src'))))
                        media.set('src', localsrc)
                    #save the pivot file
                    self.model.pubsavepivot(ET.tostring(pivot, xml_declaration=True, encoding="UTF-8"),
                                            '%s-local.xml'%self.pivname,
                                            False,
                                            profilename=self.pivname)

                cmd=self.__substscript(cmd, label, params)
                cmd=cmd.encode(LOCAL_ENCODING)
                debug(cmd)

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
                            print "Attention %(warn)s", {'warn': line}
                        elif re.search('error', line) or re.search('not found', line):
                            print "Erreur lors de l'exécution de la commande : %(cmd)s:\n  %(error)s"%{'cmd': cmd.decode(LOCAL_ENCODING).encode('utf-8'),
                                                                                                       'error': line.encode('utf-8')}
                            has_error = True

                    # if no error display link
                    
                    if not has_error:
                        xl=scrdef.find('link')
                        outfile=self.__substscript(xl.get('name'), label, params)
                        outref=self.__substscript(xl.get('ref'), label, params)
                        print "Exécution du script %(label)s réussie", {'label': label.encode('utf-8')}
                except:
                    print "Erreur lors de l'execution du script %(label)s", {'label': label.encode('utf-8')}
                    return
                    

            if stype=="xslt":
                try:
                    sxsl=scrdef.find("stylesheet").text
                    xslt_doc=ET.parse(os.path.join(conf.get('appdir'),'publication','xsl','plugins',sxsl))
                    xslt=ET.XSLT(xslt_doc)
                    sout=scrdef.find("output").text
                    debug(sout)
                    sout=self.__substscript(sout, label, params)

                    xparams={}
                    for n,v in params.iteritems():
                        xparams[n]="'%s'"%v

                    xparams['LANG']="'%s'"%self.lang
                    xparams['ZONE']="'%s'"%self.critdict.get('zone','')
                    xparams['DOCNAME']="'%s'"%self.docname
                    xparams['PUBDIR']="'%s'"%self.model.pubpath.decode(LOCAL_ENCODING)

                    docf=xslt(self.pivdocument,**xparams)
                    try:
                        self.model.pubsave(str(docf),'/'.join((label,sout)))
                    except:
                        yield(self.view.error(self.setmessage(u"[0058]Impossible d'exécuter le script %(label)s", {'label': label.encode('utf-8')})))
                        return
                    errors = set()
                    for err in xslt.error_log:
                        if not err.message in errors:
                            yield(self.view.error(err.message))
                            errors.add(err.message)
                    yield(self.view.success(self.setmessage(u"[0057]Exécution du script %(label)s réussie", {'label': label.encode('utf-8')})))

                    # output link to result of transformation
                    yield (self.view.publink(sout.split('/')[-1],
                                             label,
                                             '/'.join((self.model.local2url(self.model.pubpath), label, sout))))

                    # copy medias
                    try:
                        msrc = self.model.abstractIO.getid(os.path.join(self.model.pubpath, 'medias'))
                        dsrc = self.model.abstractIO.getid(os.path.join(self.model.pubpath, str(label), 'medias'))
                        self.model.abstractIO.copyDirs(msrc, dsrc)
                    except OSError:
                        pass
                    # make a zip with label directory
                    zipname=label+".zip"
                    zippy = self.model._loadMVCobject_('ZipFileIO')
                    zippy.open(os.path.join(self.model.pubpath,zipname), 'w')
                    top=os.path.join(self.model.pubpath,label)
                    for root, dirs, files in os.walk(top):
                        for name in files:
                            rt=root[len(top) + 1:]
                            zippy.write(str(os.path.join(root, name)),arcname=str(os.path.join(rt, name)))
                    zippy.close()

                    # link to the zip
                    yield (self.view.publink('Zip',
                                             label,
                                             '/'.join((self.model.local2url(self.model.pubpath), zipname))))

                except:
                    dbgexc()
        except:
            dbgexc()




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
            


    def script_copy(self, value, dirname, pubdir, copyto, ext):
        print "script copy",value, dirname, pubdir, copyto, ext
        if self.version == "0.6":        
            srcpath = u'design/publication/%s' %dirname
        else:
            srcpath = u'kolekti/stylesheets/%s' %dirname
        destcd = unicode(pubdir+'/'+copyto)

        print "script copy to",destcd
        try:
            self.makedirs(destcd)
        except OSError:
            pass
        try:
            source= u"%s/%s.%s"%(srcpath,value,ext)
            dest=   u"%s/%s.%s"%(destcd,value,ext)
            self.copyFile(source,dest)
        except:
            import traceback
            print traceback.format_exc()
        try:
            source=u"%s/%s.parts"%(srcpath,value)
            if self.exists(source):
                target=u"%s/%s.parts"%(destcd,value)
                try:
                    self.rmdir(target)
                except:
                    pass
                self.copyDirs(source,target)
        except:
            import traceback
            print traceback.format_exc()

