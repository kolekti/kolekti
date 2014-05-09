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


import os
import re
import urllib2
import copy
import subprocess

from StringIO import StringIO
from datetime import datetime
from lxml import etree as ET

from kolektiserver.models.ProjectModel import ProjectModel
from kolektiserver.kolekticonf import conf

from kolekti.logger import dbgexc,debug
from kolekti.utils.i18n.i18n import tr

class PublishModel(ProjectModel):
    __pubdir = u'@'+conf.get('dirPUB')

    def __init__(self, *args, **kargs):
        super(PublishModel, self).__init__( *args, **kargs)

        self.__ntime = self._get_time()
        self.__publicationid = unicode(self.__ntime)
        self.userinfomodel=self._loadMVCobject_('UserAccountModel')

    @property
    def locale_lang(self):
        return self.lang
    
    @property
    def pubdir(self):
        return self.__pubdir

    @property
    def pubdirurl(self):
        return self.id2url(self.__pubdir)

    @property
    def pubtime(self):
        return self.__ntime

    @property
    def pivname(self):
        return self.__publicationid

    @property
    def projectpath(self):
        return self.abstractIO.getpath(u'@')

    @property
    def basepath(self):
        return self.abstractIO.getpath(u'/')

    @property
    def pubpath(self):
        return self.abstractIO.getpath(self.__pubdir)

    def getdata(self, data):
        try:
            return ET.XML(data)
        except:
            return None

    def trame(self, resid):
        return self.abstractIO.parse(resid)

    def make_pubdir(self, pubdir, profile="",trame=""):
        debug(('make pubdir',pubdir,profile,trame))
        p=u"/".join((u'@'+conf.get('dirPUB'), pubdir, profile, self.lang, self.__publicationid))
        self.__pubdir=p

        self.abstractIO.makedirs(u"%s/%s"%(p,u"_pivots"))
        p=u"/".join((u'@'+conf.get('dirPUB'), pubdir, profile, "__manifest.xml"))
        try:
            mf=self.abstractIO.parse(p).getroot()
        except:
            mf=ET.XML("<manifest/>")
        author = '%s %s' %(self.userinfomodel._prop_kui_firstname(self.http.path).text,self.userinfomodel._prop_kui_lastname(self.http.path).text)
        ET.SubElement(mf, 'publication', {'author': author, 'time': self.__publicationid, 'profile':profile, 'trame':trame})
        self.abstractIO.putFile(p,ET.tostring(mf))

    def pubsave(self, data, filename):
        p='/'.join((self.__pubdir,filename))
        self.abstractIO.putFile(p,data)

    def pubsavepivot(self, data, filename, last=False, profilename=""):
        p=u'/'.join((self.__pubdir,u"_pivots",filename))

        # if last pivot file: update manifest file
        if last:
            profilepath = self.__pubdir.rsplit('/', 2)[0]
            mfid=u"/".join((profilepath, "__manifest.xml"))
            mf=self.abstractIO.parse(mfid)
            pub =  mf.xpath("/manifest/publication[@time = '%s' and @profile = '%s']" %(self.__publicationid, profilename))[0]
            pub.set('pivname', filename)
            self.abstractIO.putFile('%s/__manifest.xml' %profilepath,ET.tostring(mf))

        self.abstractIO.putFile(p,data)

    def getvariables(self, filename):
        ods_resid=u"/".join((u'@'+conf.get('dirSHEETS'), u'sources','%s.ods'%filename))
        xml_resid=u"/".join((u'@'+conf.get('dirSHEETS'), u'xml','%s.xml'%filename))

        if not self.abstractIO.exists(xml_resid) or self.abstractIO.isNewer(ods_resid,xml_resid):
            sheetsmodel=self._loadMVCobject_('SheetsModel')
            xml=sheetsmodel.genVarFile(ods_resid,xml_resid,'ods')
        else:
            xml=self.abstractIO.parse(xml_resid)
        return xml.getroot()

    def medias_copy(self, source, srcdir="medias"):
        dest = u"/".join((self.__pubdir, u'medias', source.split("/%s/" %srcdir)[1]))
        realcd = u"/".join(dest.split('/')[:-1])
        if not(self.abstractIO.exists(realcd)):
            self.abstractIO.makedirs(dest)
        self.abstractIO.copyFile(source,dest)
        return dest

    def script_copy(self, value, dirname, copyto, ext):
        srcpath = u'@design/publication/%s' %dirname
        destcd = unicode(self.__pubdir+'/'+copyto)
        dummycd = unicode(destcd+'/dummy')

        debug(("script copy to",destcd))
        if not(self.abstractIO.exists(destcd)):
            debug('make the dir')
            self.abstractIO.makedirs(dummycd)
        try:
            source= u"%s/%s.%s"%(srcpath,value,ext)
            dest=   u"%s/%s.%s"%(destcd,value,ext)
            self.abstractIO.copyFile(source,dest)
        except:
            dbgexc()
        try:
            source=u"%s/%s.parts"%(srcpath,value)
            if self.abstractIO.exists(source):
                target=u"%s/%s.parts"%(destcd,value)
                try:
                    self.abstractIO.rmdir(target)
                except:
                    pass
                self.abstractIO.copyDirs(source,target)
        except:
            dbgexc()

    def script_lesscompile(self, lessfile, srcdir, dstdir):
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
            

    def add_orders_history(self):
        ''' Add current order in db history '''
        pid = int(self.project.get('id'))
        resid = self.http.path

        sql = self.http.dbbackend
        OrdersHistory = sql.get_model('OrdersHistory')
        res = sql.select(OrdersHistory, "pid = %d and resid = '%s'" %(pid,resid))
        if res == []:
            sql.insert(OrdersHistory(pid, resid, self.http.userId, self.__publicationid))
        else:
            try:
                oh = res[0]
                oh.uid = self.http.userId
                oh.time = self.__ntime
                sql.commit()
            except:
                sql.rollback()
                dbgexc()

    def genmaster(self, publisher, trame):
        ''' Generate master '''
        xhtmlns={'h':'http://www.w3.org/1999/xhtml'}
        zip = self.get_zip_object()
        zip.open(data="", mode='w')
        manifest = ET.Element("master", {"version": '2'})
        zip.writestr('assembly.xhtml', ET.tostring(publisher.masterdocument, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
        ET.SubElement(manifest, "file", {"ref": "assembly.xhtml"})
        zip.writestr('config/moduleinfos.xml', ET.tostring(publisher.moduleinfos, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
        ET.SubElement(manifest, "file", {"ref": "config/moduleinfos.xml"})

        profilecrit = {}
        for profile in publisher.pubparams['profiles']:
            lbl = profile.xpath("string(label)")
            criterias = profile.xpath("criterias/criteria[@checked='1']")
            profilecrit[lbl] = []
            for crit in criterias:
                profilecrit[lbl].append((crit.xpath('string(@code)'),crit.xpath('string(@value)')))

        # Copy media
        medcopy = {}
        for med in publisher.masterdocument.xpath('/h:html/h:body//h:img|/h:html/h:body//h:embed', namespaces=xhtmlns):
            src = unicode(med.get('src'))
            if not(src[:7] == "http://" or src[:8] == "https://" or src[:4] == "www."):
                if not self.abstractIO.exists(src):
                    crit = re.findall('_[a-zA-Z0-9]+_', src)
                    for c in crit:
                        for pcrit in profilecrit:
                            critval = profile.xpath("string(criterias/criteria[@checked='1' and @code='%s']/@value)" %c[1:-1])
                            if critval != '':
                                src = src.replace(c, critval)
                medsrc = self.abstractIO.getpath(src)
                try:
                    if not medcopy.has_key(medsrc):
                        arcname = '/'.join(self.abstractIO.getid(medsrc).split('/')[3:]).encode('utf-8')
                        zip.write(medsrc, arcname)
                        ET.SubElement(manifest, "file", {"ref": arcname})
                        medcopy[medsrc] = True
                except:
                    dbgexc()
                    yield(publisher.view.error(publisher.setmessage(u"[0050]Echec lors de la copie du média %(src)s", {'src': str(src)})))

        # Copy sheets
        sheets = {}
        for var in publisher.masterdocument.xpath("/h:html//h:var[contains(@class,':')]", namespaces=xhtmlns):
            v = var.get('class')
            name = '%s.ods' %v.split(':')[0]
            sheets.update({name:'1'})

        for sheet in sheets:
            sheet = publisher.replace_crit(sheet)
            resid = '/'.join((('@'+conf.get('dirSHEETS')), 'sources', sheet))
            foff = self.abstractIO.getpath(resid)
            # read sheet and remove unused lang
            try:
                zip.write(foff, resid[1:])
                ET.SubElement(manifest, "file", {"ref": resid[1:]})
            except:
                s = tr(u"[0026]Impossible de trouver le fichier tableur: %(sheet)s", {'sheet': sheet})
                yield publisher.view.error(s.i18n(self.http.translation))

        # generate csv revnotes
#        self.csv_revnotes(publisher, zip, trame)
        ET.SubElement(manifest, "file", {"ref": "config/manifest.xml"})

        zip.writestr('config/config.xml', self.configmaster(trame, publisher.pubparams))
        ET.SubElement(manifest, "file", {"ref": "config/config.xml"})
        zip.writestr('modules-history.xml', ET.tostring(publisher.modhistory, xml_declaration=True, encoding="UTF-8"))
        ET.SubElement(manifest, "file", {"ref": "modules-history.xml"})
        zip.writestr('lang', self.lang.encode('utf-8'))
        ET.SubElement(manifest, "file", {"ref": "lang"})

        # Write manifest file
        ET.SubElement(manifest, "file", {"ref": "revnotes.csv"})
        zip.writestr('config/manifest.xml', ET.tostring(manifest, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
        zip.close()

        # save the generated zip
        mastername = publisher.pubparams.get('master_name', '')
        if  mastername == '':
            mastername = self.http.path.split('/')[-1][:-4]

        masterid = u"@masters/%s.zip"%mastername
        self.putdata(masterid, zip.zipfile.getvalue())

        yield publisher.view.labellink(self.id2url(masterid), publisher.setmessage(u"[0301]Enveloppe"), masterid.split('/')[-1], {"class": "masterlink"})

    def csv_revnotes(self, publisher, zip, trame):
        xmltrame = self.abstractIO.parse(trame)
        svnio=publisher.model._loadMVCobject_("svnProjectsIO")
        legend = []
        buf = "%s;%s;%s;%s;%s;%s\r\n" %(publisher.replace_strvar('[var kolektitext:NomMod]'),
                                        publisher.replace_strvar('[var kolektitext:Location]'),
                                        publisher.replace_strvar('[var kolektitext:RevInd]'),
                                        publisher.replace_strvar('[var kolektitext:Author]'),
                                        publisher.replace_strvar('[var kolektitext:Date]'),
                                        publisher.replace_strvar('[var kolektitext:Comments]'))
        for mod in xmltrame.xpath('/kt:trame//kt:module', namespaces={"kt": "kolekti:trames"}):
            resid = unicode(mod.get('resid'))
            if resid[:10] != "kolekti://":
                logs = svnio.svnlog(resid, 1)
                for log in logs:
                    d = datetime.utcfromtimestamp(log['date'])
                    fd = d.strftime("%x %X")
                    author = log['uid']
                    if author == "None" or author == "-1":
                        author = ""
                    else:
                        author = self.getUsername(int(log['uid']))
                    splitResid = resid.split('/')
                    l = ';'.join((splitResid[-1],'/'.join(splitResid[:-1]),str(log['number']),author,fd,log['msg']))
                    buf += "%s\r\n" %l
        zip.writestr('revnotes.csv', buf.encode('iso-8859-15'))

    def configmaster(self, trame, pubparams):
        ''' Generate config.xml file include in master '''
        d = ET.Element('data')
        ET.SubElement(d, 'field', {'name': 'trame', 'value': trame})
        ET.SubElement(d, 'field', {'name': 'pubdir', 'value': pubparams.get('pubdir', '')})
        ET.SubElement(d, 'field', {'name': 'pubtitle', 'value': pubparams.get('pubtitle', '')})
        ET.SubElement(d, 'field', {'name': 'filtermaster', 'value': pubparams.get('filter_master', '')})
        ET.SubElement(d, 'field', {'name': 'mastername', 'value': pubparams.get('master_name', '')})
        author = '%s %s' %(self.userinfomodel._prop_kui_firstname(self.http.path).text,self.userinfomodel._prop_kui_lastname(self.http.path).text)
        ET.SubElement(d, 'field', {'name': 'author', 'value': author})
        ET.SubElement(d, 'field', {'name': 'creation_date', 'value': self.__publicationid})
        profiles = ET.SubElement(d, 'profiles')
        for p in pubparams['profiles']:
            profiles.append(p)
        scripts = ET.SubElement(d, 'scripts')
        for s in pubparams['scripts']:
            scripts.append(s)

        return ET.tostring(d, pretty_print=True)

    def get_zip_object(self):
        ''' Get a copy of zip object '''
        return copy.copy(self._loadMVCobject_('ZipFileIO'))

    def add_db_master_criteria(self, filtermaster):
        ''' Add value of filter criteria for master in DB '''
        if filtermaster != '':
            sql = self.http.dbbackend
            MasterFilter = sql.get_model('MasterFilter')
            try:
                sql.insert(MasterFilter(self.project.get('id'), filtermaster))
            except:
                sql.rollback()
            sql.close()

    ###############################################
    # DAV Methods
    ###############################################

    def _prop_k_history(self, resid):
        """history of a resource or collection"""
        p = self._xmlprop('history','kolekti')
        pid = int(self.project.get('id'))
        sql = self.http.dbbackend
        OrdersHistory = sql.get_model('OrdersHistory')
        res = sql.select(OrdersHistory, "pid = %d" %pid)
        lfiles = ET.SubElement(p, "listfiles")
        for oh in res:
            ET.SubElement(lfiles, "ordershistory", {"pid": str(oh.pid), "resid": oh.resid, "uid": str(oh.uid), "time": oh.time})
        return p
