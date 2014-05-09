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




""" Modules model class """

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''

import re
import urllib2
import mimetypes
import os

from lxml import etree as ET

from kolekti.exceptions import exceptions as EXC
from kolekti.logger import dbgexc,debug
from kolekti.utils.i18n.i18n import tr

from kolektiserver.models.ProjectModel import ProjectModel

#from kolektiserver.models.sql.models import Usecase

class ModulesModel(ProjectModel):
    __localNS={"kolekti:browser":"ka",
               "kolekti:modules":"km",
               "kolekti:viewer":"kv"}
    _KEEPMETA=False

    def __init__(self, *args,**kwargs):
        ''' Init namespaces '''
        try:
            kwargs['ns'].update(self.__localNS)
        except KeyError:
            kwargs['ns']=self.__localNS
        super(ModulesModel,self).__init__(*args,**kwargs)

    ###############################################
    # DAV Methods
    ###############################################

    def getResource(self, id):
        ''' Get resource '''
        try:
            rev=self.http.params.get('rev',None)
            data=self.abstractIO.getFile(id,rev)
            return (data, mimetypes.guess_type(id),self._etag(id))
        except:
            dbgexc()
            raise EXC.NotFound

    def delete(self, id):
        ''' Override default delete method '''
        super(ModulesModel,self).delete(id)
        # Remove in DB usecase
        sql = self.http.dbbackend
        Usecase = sql.get_model('Usecase')
        norm_id=self.abstractIO.normalize_id(id)
        res = sql.select(Usecase, "resid='%s'" %norm_id)
        sql.delete(res)

    def move(self, id, newid):
        ''' Override default move method '''
        super(ModulesModel,self).move(id, newid)
        # Replace in DB Usecase
        sql = self.http.dbbackend
        Usecase = sql.get_model('Usecase')
        modid=self.abstractIO.normalize_id(id)
        res = sql.select(Usecase, "resid='%s'" %modid)
        if res != []:
            newmodid=self.abstractIO.normalize_id(newid)
            for r in res:
                r.resid = newmodid
            sql.commit()

    def copy(self, id, copyid):
        ''' Override default copy method '''
        copyid = '@modules/%s' %copyid
        super(ModulesModel,self).copy(id, copyid)
        # Duplicate in DB Usecase
        sql = self.http.dbbackend
        Usecase = sql.get_model('Usecase')
        norm_id=self.abstractIO.normalize_id(id)
        res = sql.select(Usecase, "resid='%s'" %norm_id)
        if res != []:
            newcopyid=self.abstractIO.normalize_id(copyid)
            mods = []
            #print res
            for mod in res:
                mods.append(Usecase(mod.project_id, newcopyid, mod.ref))
            #print mods
            sql.insert(mods)

    def put(self, id):
        ''' Override default put method '''
        # Get data of module before saving
        data = self.http.body
        logmsg=self.http.headers.get('KOLEKTICOMMIMSG','').decode('utf-8',"replace")
        if not isinstance(logmsg,unicode):
            logmsg = logmsg.decode('utf-8', 'ignore')
        # logmsg is an unicode

        if data is None:
            data=""
        try:
            if self.http.params.get("fixed"):
                data = self.abstractIO.getFile(id)
                xml = ET.HTML(data)
                # Fixed namespaces
                html = xml.xpath('/html')[0]
                html.set("xmlns", "http://www.w3.org/1999/xhtml")
                data = ET.tostring(xml, encoding="utf-8", method="xml", xml_declaration=True, pretty_print=True)
            # Save module
            self.abstractIO.putFile(id, data, logmsg)
            self.abstractIO.prop_del(id, "kolekti_validmod", "0")
        except:
            dbgexc()
            raise EXC.FailedDependency

        # Remove all existing usecases of current id
        sql = self.http.dbbackend
        Usecase = sql.get_model('Usecase')
        norm_id=self.abstractIO.normalize_id(id)
        res = sql.select(Usecase, "resid='%s'" %norm_id)
        sql.delete(res)

        try:
            # Get medias of new module
            parser = ET.XMLParser(load_dtd=True)
            listmed = self.__getMedias(ET.XML(data,parser))

            # Save usage for each media on module
            for med in listmed:
                norm_medresid=self.abstractIO.normalize_id(med)
                sql.insert(Usecase(self.project.get('id'), norm_id,norm_medresid))
            #super(ModulesModel, self).log_save(id)
        except:
            self.abstractIO.prop_set(id, "kolekti_validmod", "0")

    def isValid(self, resid):
        # if module doesn't exist, not try validate it
        if not self.abstractIO.exists(resid):
            return True
        return len(self.abstractIO.prop_get(resid, "kolekti_validmod")) == 0

    def __getMedias(self, xml):
        return [unicode(med.get('src')) for med in xml.xpath('/h:html/h:body//h:img', namespaces={"h":"http://www.w3.org/1999/xhtml"})]

    _history_filter=lambda self,p:os.path.splitext(p)[1]=='.xht'

    # DAV properties

    def _prop_dav_displayname(self, resid):
        #Example collection
        p = self._xmlprop('displayname')
        #p.text = uri.objname
        if self.__is_root_modules(resid):
            s = tr(u"[0022]Modules")
            p.text = s.i18n(self.http.translation)
        else:
            name= resid.split('/')[-1]
            p.text = name.rsplit('.',1)[0]
        return p

    # Browser
    def _prop_ka_mainbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('mainbrowseractions','kolekti:browser')
        ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newmodule'})
        return p

    def _prop_ka_rootdirbrowseractions(self, resid):
        ''' Define main actions of browser '''
        p = self._xmlprop('rootdirbrowseractions','kolekti:browser')
        ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newdir'})
        return p

    def _prop_ka_browseractions(self, resid):
        ''' Define action for each item of browser '''
        p = self._xmlprop('browseractions','kolekti:browser')
        if not self.__is_root_modules(resid) and self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'browsereditmodule'})
        if self.isCollection(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'delete'})
            ET.SubElement(p, '{kolekti:browser}action', attrib={'id':'newdir'})
        return p

    def _prop_ka_browserbehavior(self, resid):
        ''' Event to notify for each item of browser '''
        p = self._xmlprop('browserbehavior','kolekti:browser')
        if self.isResource(resid):
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'addtotrame'})
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'displaymodule'})
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'previewmodule'})
        elif self.isCollection(resid) and self.http.headers.get('Kolektibrowser', '') != '':
            ET.SubElement(p, '{kolekti:browser}behavior', attrib={'id':'selectdir'})
        return p

    def _prop_ka_browsericon(self, resid):
        ''' Change icon of browser items '''
        p = self._xmlprop('browsericon','kolekti:browser')
        if self.isResource(resid) and not self.isValid(resid):
            ET.SubElement(p, '{kolekti:browser}icon', attrib={'src':'browser_error'})
        return p

    # Modules properties
    def _prop_km_version(self, resid):
        ''' Get module version '''
        p = self._xmlprop('version','kolekti:modules')
        versioninfo=self.abstractIO.svnlog(resid,limit=1)[0]
        p.text=str(versioninfo.get('number'))
        return p

    def _prop_km_versions(self, resid):
        ''' Get module version history '''
        p = self._xmlprop('versions','kolekti:modules')
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

    def _prop_km_heading(self, resid):
        ''' Get module heading sidebar view '''
        p = self._xmlprop('heading','kolekti:modules')
        return p

    def _prop_km_usage(self, resid):
        ''' Get module trames usage '''
        p = self._xmlprop('usage','kolekti:modules')
        sql = self.http.dbbackend
        Usecase = sql.get_model('Usecase')
        modresid=self.abstractIO.normalize_id(resid)
        res = sql.select(Usecase, "ref='%s'" %(modresid,))
        for r in res:
            tresid = r.resid
            if tresid[len(self.abstractIO.uprojectpart)+1:].startswith('/trames'):
                turl = self.abstractIO.normalize_id(tresid)
                e = ET.SubElement(p, "{kolekti:modules}trame", {'resid': tresid, 'url': turl, 'urlid': self._urihash(turl)})
                tramemodel=self._loadMVCobject_('TramesModel')
                e.text = tramemodel._prop_dav_displayname(tresid).text
        return p

    def _prop_km_filterview(self, resid):
        ''' Get module filter view '''
        p = self._xmlprop('filterview','kolekti:modules')
        configmodel=self._loadMVCobject_('ConfigurationModel')
        criterias = configmodel.getCriterias()
        for crit in criterias.xpath("criteria[@type='enum']"):
            p.append(crit)
        return p

    def _prop_km_diagnostic(self, resid):
        ''' Get module diagnostic view '''
        p = self._xmlprop('diagnostic','kolekti:modules')
        if self.isResource(resid):
            try:
                configmodel=self._loadMVCobject_('ConfigurationModel')
                criterias = configmodel.getCriterias()
                parser = ET.XMLParser(load_dtd=True)
                mod = ET.XML(self.abstractIO.getFile(resid), parser)
                # Check links
                links = mod.xpath("//html:a", namespaces={"html":"http://www.w3.org/1999/xhtml"})
                self.__checkModuleLink(resid, p, links, "href", "a", criterias)
                # Check pictures
                img = mod.xpath("//html:img", namespaces={"html":"http://www.w3.org/1999/xhtml"})
                self.__checkLink(p, img, "src", "img", criterias)
                # Check flash animations
                anim = mod.xpath("//html:object/html:embed", namespaces={"html":"http://www.w3.org/1999/xhtml"})
                self.__checkLink(p, anim, "src", "embed", criterias)
                self.__checkCriterias(p, mod, criterias)

                prjdir = self.project.get('directory')
                if len(mod.xpath("/h:html/h:head/h:link[@rel='stylesheet' and @href='/projects/%s/design/edition/styles/criterias.css']"%prjdir,
                                 namespaces={'h':'http://www.w3.org/1999/xhtml'})) == 0:
                    ET.SubElement(p, "warning", {"criteriascss": "1"})
            except:
                ET.SubElement(p, "error", {"module": "1"})
        return p

    def __checkCriterias(self, p, mod, criterias):
        ''' Check all criterias are corrects '''
        # Check if conditions use existing criterias
        try:
            # Get all class attributes containing "=", parse the expression and check :
            conditions = mod.xpath("//html:*[contains(@class, '=')]", namespaces={"html":"http://www.w3.org/1999/xhtml"})
            for cond in conditions:
                filtercrit = self.__get_mod_conditions(cond.get('class'))
                for (code, values) in filtercrit.iteritems():
                    if code == "LANG":
                        continue
                    # Check if the criteria name exists
                    crit = criterias.xpath("/criterias/criteria[@code='%s']" %code)
                    if crit == []:
                        ET.SubElement(p, "criteriaerror", {"code": code})
                    else:
                        # Check if the value(s) specified conform to the type of the criteria
                        type= crit[0].get('type')
                        if type == "enum":
                            for value in values.iterkeys():
                                val = criterias.xpath("/criterias/criteria[@code='%s']/value[@code='%s']" %(code, value))
                                if val == []:
                                    ET.SubElement(p, "criteria_valueerror", {"code": code, "value": value})
                        elif type == "int":
                            range = criterias.xpath("/criterias/criteria[@code='%s']/range" %code)
                            val = values.keys()[0]
                            min = range[0].get('min', '0')
                            max = range[0].get('max', '')
                            if range == [] or not (val >= int(min) and (max == '' or val <= int(max))):
                                ET.SubElement(p, "criteria_valueerror", {"code": code, "value": value})
                        else:
                            pass
        except:
            dbgexc()

    def _prop_km_notes(self, resid):
        ''' Get module notes view '''
        p = self._xmlprop('notes','kolekti:modules')
        versioninfo=self.abstractIO.svnlog(resid,limit=1)[0]
        p.text=versioninfo.get('msg')
        return p

    def _prop_km_valid(self, resid):
        ''' Get if module is valid '''
        p = self._xmlprop('valid','kolekti:modules')
        if self.isValid(resid):
            p.text = "1";
        return p

    # Viewer
    def _prop_kv_views(self, resid):
        ''' Define viewers '''
        p = self._xmlprop('views', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'moduleviewer'})
        ET.SubElement(p, '{kolekti:viewer}view', attrib={'id':'moduleeditor'})
        return p

    def _prop_kv_vieweractions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('vieweractions', 'kolekti:viewer')
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'deleteresource'})
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'editmodule'})
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'duplicatemodule'})
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'renamemodule'})
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'movemodule'})
        ET.SubElement(p, '{kolekti:viewer}action', attrib={'id':'displaymodule'})
        return p

    def _prop_kv_clientactions(self, resid):
        ''' Define actions of viewers '''
        p = self._xmlprop('clientactions', 'kolekti:viewer')
        return p

    #
    # END PROPERTIES
    #

    def __is_root_modules(self, id):
        r=self.abstractIO.normalize_id(id)
        splitId = r.split('/')
        return len(splitId) == 4

    def __parse(self, data):
        ''' Parse file with dtd and replace html entities '''
        data = data.replace('&nbsp;', ' ')
        try:
            parser = ET.XMLParser(load_dtd=True)
            return ET.XML(data,parser)
        except:
            parser = ET.HTMLParser()
            return ET.XML(data,parser)

    def __checkModuleLink(self, resid, p, links, src, type, criterias):
        ''' Check if resource link exist '''
        for link in links:
            ref = unicode(link.get(src))
            if not ref.startswith('http://'):
                if not(ref.startswith('@') or ref.startswith('/') or ref.startswith('../')):
                    ref = '%s/%s' %(resid.rsplit('/', 1)[0], ref)
                crit = self.__contain_criteria(ref)
                if not crit and not self.abstractIO.exists(ref):
                    e = ET.SubElement(p, "error", {"src": ref, "type": type})
                    e.text = ref.split('/')[-1]
                elif not crit is None:
                    path = '/'.join(ref.split('/')[:-1])
                    self.__check_exist_criteria(p, path, criterias)

    def __checkLink(self, p, links, src, type, criterias):
        ''' Check if resource link exist '''
        for link in links:
            ref = unicode(link.get(src))
            if not ref.startswith('http://'):
                crit = self.__contain_criteria(ref)
                if not crit and not self.abstractIO.exists(ref):
                    e = ET.SubElement(p, "error", {"src": ref, "type": type})
                    e.text = ref.split('/')[-1]
                elif not crit is None:
                    path = '/'.join(ref.split('/')[:-1])
                    self.__check_exist_criteria(p, path, criterias)

    def __contain_criteria(self, path):
        ''' Return boolean if path contain criteria '''
        # remove file name in path
        path = '/'.join(path.split('/')[:-1])
        # return result of search criteria
        return not re.search('_[a-zA-Z0-9]+_', path) is None

    def __check_exist_criteria(self, p, path, criterias):
        ''' Check if criteria name exist '''
        res = re.search('_[a-zA-Z0-9]+_', path)
        if res is None:
            return
        else:
            code = path[res.start()+1:res.end()-1]
            crit = criterias.xpath("/criterias/criteria[@code='%s']" %code)
            if crit == []:
                ET.SubElement(p, "criteriaerror", {"code": code})
            return self.__check_exist_criteria(p, path[res.end():], criterias)

    def __get_mod_conditions(self, crit):
        ''' Generate dict with each criteria and values '''
        filtercrit = {}
        try:
            splitCond = crit.split('=')
            (name, values, cond) = self.__get_condition_criteriavalues(splitCond[:2], filtercrit, len(splitCond) == 2)

            while len(splitCond) > 2:
                splitCond[1] = splitCond[1][-len(cond):]
                splitCond = splitCond[1:]
                (name, values, cond) = self.__get_condition_criteriavalues(splitCond[:2], filtercrit, len(splitCond) == 2)
        except:
            pass
        return filtercrit

    def __get_condition_criteriavalues(self, tabs, filtercrit, last=True):
        ''' Get condition name and values '''
        cond = ''
        name = tabs[0].strip()
        # Create new dict if doesn't already exist
        if not filtercrit.has_key('name'):
            filtercrit[name] = {}
        # split values
        splitValues = re.split('[,;]*', tabs[1])
        if last:
            values = splitValues
        else:
            values = splitValues[:-1]
            cond = splitValues[-1]

        # set all values for current criteria
        for val in values:
            val = val.strip()
            if val[0] == '\\':
                val = val[1:].strip()
            # Append value if doesn't already exist
            if not filtercrit[name].has_key(val):
                filtercrit[name][val] = 1
        return (name, values, cond)

