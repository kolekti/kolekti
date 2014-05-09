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


""" Configuration model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import os
import mimetypes
import hashlib
import time

from lxml import etree as ET

from kolekti.exceptions import exceptions as EXC
from kolekti.logger import dbgexc
from kolekti.utils.i18n.i18n import tr

from kolektiserver.models.ProjectModel import ProjectModel
#from kolektiserver.models.sql.models import Usecase, Criterias, CriteriaValues

class ConfigurationModel(ProjectModel):
    __localNS={"kolekti:browser":"ka",
               "kolekti:usersession":"ku",
               "kolekti:configuration":"kc",
               "kolekti:scripts":"ks",
               "kolekti:viewer":"kv"}

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(ConfigurationModel,self).__init__(*args,**kwargs)

    def listCollection(self, id):
        l = super(ConfigurationModel, self).listCollection(id)
        if id == "@configuration" or id.split('/')[-1] == "configuration":
            l.append(u"criterias.xml")
        l.reverse()
        return l

    def getResource(self, id):
        ''' Overload get resource '''
        try:
            filename = id.split('/')[-1]
            if filename == '_':
                return ('<order><profiles /><scripts /></order>', ('application/xml','utf-8'), self._etag(id))
            elif filename == "criterias.xml":
                return (self.__load_criterias(), ('application/xml','utf-8'), self._etag(id))
            else:
                return (self.abstractIO.getFile(id), mimetypes.guess_type(id),self._etag(id))
        except:
            dbgexc()
            raise EXC.NotFound

    def _etag(self, id):
        ''' Overload get etag methods '''
        try:
            return super(ConfigurationModel, self)._etag(id)
        except:
            m=hashlib.md5()
            m.update(self.abstractIO.getpath(id))
            return m.hexdigest()

    def isResource(self, id):
        ''' Overload verification of resource '''
        filename = id.split('/')[-1]
        if filename == '_' or filename == "criterias.xml":
            return True
        return self.abstractIO.isFile(id)

    def put(self, id):
        data = self.http.body
        if data is None:
            data = ""
        elif data == "":
            dirname = id.split('configuration/')[1]
            if dirname.startswith("orders"):
                data = '<order><profiles /><scripts /></order>'
            elif dirname.startswith("publication_profiles"):
                data = '<publicationprofile/>'

        try:
            if id.split('/')[-1] == "criterias.xml":
                self.__put_criterias(data)
            else:
                logmsg=self.http.headers.get('KOLEKTICOMMIMSG','').decode('utf-8',"replace")
                self.abstractIO.putFile(id, data, logmsg)
                if id.split('configuration/')[1].startswith("orders"):
                    d = ET.XML(data)
                    try:
                        tid =  unicode(d.xpath('.//trame')[0].get('value'))
                        norm_id = self.abstractIO.normalize_id(id)
                        norm_tid = self.abstractIO.normalize_id(tid)
                        sql = self.http.dbbackend
                        Usecase = sql.get_model('Usecase')
                        res = sql.select(Usecase, "resid='%s'" %norm_id)
                        if res == []:
                            sql.insert(Usecase(int(self.project.get('id')), norm_id,norm_tid))
                        else:
                            res[0].ref = norm_tid
                        sql.commit()
                        sql.close()
                    except IndexError:
                        pass
        except:
            dbgexc()
            raise EXC.FailedDependency

        if id.split('/')[-1] == "criterias.xml":
            self.__generateCriteriasCss(id, data)
        #elif id.split('configuration/')[1].startswith("publication_profiles") and id.split('/')[-1] != '_':
        #    self.log_save(id)

    def getCriterias(self):
        ''' Get criterias definition '''
        return ET.XML(self.__load_criterias())

    # def log_save(self, resid):
    #     logdir=self._normalize_id(resid).split(u'/')[:5]
    #     log = u'/'.join(logdir+[u'_manifest.xml'])
    #     if self.abstractIO.exists(log):
    #         d = self.abstractIO.parse(log)
    #         root = d.getroot()
    #     else:
    #         root = ET.Element('listfiles')
    #     ET.SubElement(root, 'file', {'date':str(time.time()),'uid':str(self.http.userId),'resid':resid})
    #     self.abstractIO.putFile(log,ET.tostring(root,pretty_print=True))

    def __load_criterias(self):
        ''' Load criterias from DB and generate xml '''
        criterias = ET.Element("criterias")
        sql = self.http.dbbackend
        Criterias = sql.get_model('Criterias')
        CriteriaValues = sql.get_model('CriteriaValues')
        for crit in sql.select(Criterias, "pid = '%s'" %self.project.get('id'), "code"):
            criteria = ET.SubElement(criterias, "criteria", {'code':crit.code,'name':crit.name,'type':crit.type})
            if crit.type == "enum" or crit.type == "int":
                for val in sql.select(CriteriaValues, "criteria_id = %d" %crit.id):
                    if crit.type == "int":
                        ET.SubElement(criteria, "range",{'min':val.value1,'max':val.value2})
                    else:
                        ET.SubElement(criteria, "value",{'code':val.value1, 'name':val.value2})
        sql.close()
        return ET.tostring(criterias)

    def __put_criterias(self, data):
        ''' Put criterias into DB '''
        criterias = ET.XML(data)
        listcrit = []
        sql = self.http.dbbackend
        Criterias = sql.get_model('Criterias')
        CriteriaValues = sql.get_model('CriteriaValues')
        try:
            pid = self.project.get('id')
            # Remove all existing records
            res = sql.select(Criterias, "pid = '%s'" %pid)
            res_values = []
            for r in res:
                res_values.extend(sql.select(CriteriaValues, "criteria_id = '%s'" %r.id))
            res.extend(res_values)
            sql.delete(res)
            # Set new records
            for criteria in criterias.xpath('criteria'):
                listcrit.append(Criterias(pid,criteria.get('name'),criteria.get('code'),criteria.get('type')))
            sql.insert(listcrit)
            # Generate values for criterias
            listvalues = []
            for crit in listcrit:
                for val in criterias.xpath("criteria[@code='%s']/value" %crit.code):
                    listvalues.append(CriteriaValues(crit.id,val.get('code'),val.get('name')))
                for intval in criterias.xpath("criteria[@code='%s']/range" %crit.code):
                    listvalues.append(CriteriaValues(crit.id,intval.get('min'),intval.get('max')))
            sql.insert(listvalues)
            sql.commit()
        except:
            sql.rollback()
            dbgexc()
        sql.close()

    def __generateCriteriasCss(self, id, data):
        ''' Generate criterias css file '''
        criterias = ET.XML(data)
        buf = '*[class~="="]  {}\n'
        crit = criterias.xpath("/criterias/criteria[@type='enum']/value")
        for c in crit:
            rule=u'*[class~="%s"]:before' %c.get('code')
            if not (crit[-1] == c):
                rule+=','
            buf += rule.encode('utf-8')
        buf += ''' {
            content : attr(class);
            color: blue;
            display:block;
            border-bottom: 1px solid #D0D0D0;
            padding: 2px;
            margin:0;
            background-color: #F0F0F0;
            font-family: sans-serif;
            font-size: 60%;
            }'''

        self.abstractIO.putFile(u"@design/edition/styles/criterias.css", buf)

    def __is_root_conf(self, id):
        r=self.abstractIO.normalize_id(id)
        splitId = r.split('/')
        return len(splitId) == 4

    def __get_pubprofiles(self, resid):
        try:
            xml = ET.XML(self.abstractIO.getFile(resid))
            dprof = {}
            for profile in xml.xpath('/order/profiles/profile'):
                dprof.update({profile.get('value'):True})
            return dprof
        except:
            return {}

    _history_filter=lambda self,p: (not p.split('/')[-1][0]=='_') and (os.path.splitext(p)[1]=='.xml')


    ###############################################
    # DAV Methods
    ###############################################

    def _prop_dav_creationdate(self, resid):
        try:
            return super(ConfigurationModel, self)._prop_dav_creationdate(resid)
        except:
            p = self._xmlprop('creationdate')
            p.text = "0"
            return p

    def _prop_dav_getcontentlength(self, resid):
        try:
            return super(ConfigurationModel, self)._prop_dav_getcontentlength(resid)
        except:
            p = self._xmlprop('getcontentlength')
            p.text = "0"
            return p

    def _prop_dav_getlastmodified(self, resid):
        try:
            return super(ConfigurationModel, self)._prop_dav_getlastmodified(resid)
        except:
            p = self._xmlprop('getlastmodified')
            p.text = "0"
            return p

    def _prop_dav_displayname(self, resid):
        ''' Change displayname '''
        p = self._xmlprop('displayname')
        if self.__is_root_conf(resid):
            s = tr(u"[0225]Configuration")
        else:
            dn = resid.split('/')[-1]
            if dn == "publication_profiles":
                s = tr(u"[0200]Profils de publication")
            elif dn == "orders":
                s = tr(u"[0217]Lancements")
            elif dn == "criterias.xml":
                s = tr(u"[0145]Critères")
            else:
                s = tr(dn.rsplit('.',1)[0])
        p.text = s.i18n(self.http.translation)
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if self.isResource(resid) and not resid.split('/')[-1] == 'criterias.xml':
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'delete'})
        if self.isCollection(resid) and not self.__is_root_conf(resid):
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newfile'})
            if resid.endswith('configuration/orders'):
                ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'neworder'})
            elif resid.endswith('configuration/publication_profiles'):
                ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newpublishprofile'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'display'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        res = resid.split('configuration/')[1]
        if res == "criterias.xml":
            ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'criteriaseditor'})
        elif res.startswith("publication_profiles/"):
            ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'publicationprofileseditor'})
        elif res.startswith("orders/"):
            ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'orderseditor'})
        else:
            ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'baseviewer'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        return p

    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        res = resid.split('configuration/')[1]
        if res.startswith("orders/"):
            ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'detachedview'})
            ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'publish'})
            ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'publishwithmaster'})            
        return p

    # Configuration
    def _prop_kc_versions(self, resid):
        ''' Get configuration files version history '''
        p = self._xmlprop('versions','kolekti:configuration')
        versioninfo=self.abstractIO.svnlog(resid, limit=10)
        for vi in versioninfo:
            rev=ET.SubElement(p,'rev')
            rev.set('revnum',str(vi.get('number')))
            rev.set('time',str(vi.get('date')))
            rev.set('uid',str(vi.get('uid')))
            rev.set('author',str(vi.get('author')))
            try:
                msg = vi.get('msg').strip()
                if msg == '':
                    s = tr(u"[0023]Pas de note")
                    msg = s.i18n(self.http.translation)
                rev.set('message', msg)
            except ValueError:
                dbgexc()
                s = tr(u"[0024]Erreur!")
                rev.set('message', s.i18n(self.http.translation))
        return p

    def _prop_kc_notes(self, resid):
        ''' Get configuration file notes view '''
        p = self._xmlprop('notes','kolekti:configuration')
        try:
            versioninfo=self.abstractIO.svnlog(resid,limit=1)[0]
            p.text=versioninfo.get('msg')
        except:
            p.text = ''
        return p

    def _prop_kc_criterias(self, resid):
        ''' Define criterias '''
        p = self._xmlprop('criterias', 'kolekti:configuration')
        p.append(self.getCriterias())
        return p

    def _prop_kc_profile(self, resid):
        ''' Define profile  '''
        p = self._xmlprop('profile', 'kolekti:configuration')
        data = self.http.headers.get('KolektiData', None)
        if data:
            if data != "":
                (file, mimetype, etag) = self.getResource(u"@configuration/publication_profiles/%s" %data)
                p.append(ET.XML(file))
        else:
            (file, mimetype, etag) = self.getResource(resid)
            p.append(ET.XML(file))
        return p

        # Scripts
    def _prop_ks_script(self, resid):
        ''' Get data for a script '''
        p = self._xmlprop('script', 'kolekti:scripts')
        if self.http.headers.get('KolektiData', None):
            pubscripts = self.getPubscripts()
            sc = pubscripts.xpath("/scripts/pubscript[@id='%s']" %self.http.headers['KolektiData'])[0]
            p.append(sc) 
        return p

    def __checkCriteria(self, pr, crit, code):
        ''' Check all values for one criteria '''
        for value in crit[code]:
            res = pr.xpath("/kc:profile/publication_profile/criterias/criteria[@code='%s' and @value='%s']" %(code.decode('utf-8'), value), namespaces={'kc': 'kolekti:configuration'})
            if len(res) > 0:
                return True
        return False

    def __checkScript(self, pr, scr, name):
        ''' Check all values for one profile '''
        for value in scr[name]:
            res = pr.xpath("/kc:profile/publication_profile/scripts/script[@label='%s']" %value, namespaces={'kc': 'kolekti:configuration'})
            if len(res) > 0:
                return True
        return False
