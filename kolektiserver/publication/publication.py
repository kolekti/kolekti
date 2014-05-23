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
import sys
import imp
import urllib2
import copy
import gc

from datetime import datetime
from babel.dates import format_date, format_datetime
from lxml import etree as ET

from kolekti.logger import dbgexc,debug
from kolekti.utils.i18n.i18n import tr

from kolektiserver.kolekticonf import conf

LOCAL_ENCODING=sys.getfilesystemencoding()


class PublisherExtensions(object):
    """
    Extensions functions for xslt that are applied during publishing process
    """
    ens = "kolekti:extensions:functions:publication"

    def __init__(self, publisher):
        super(PublisherExtensions,self).__init__()
        self.publisher=publisher
        self.__cache={}
        self._xmldocs = []

    def cleanup(self):
        print "ext cleanup"
        self.publisher=None
        self._cache={}
        print "cleaning %d documents"%len(self._xmldocs)
        for d in self._xmldocs:
            del(d)

    def criterias(self,_,*args):
        """Get the list of criterias node as defined in the project configuration"""
        return self.publisher.profile.xpath("criterias/criteria[@checked='1']")

    def title(self, _, *args):
        return self.publisher.pubparams["pubtitle"]

    def lang(self, _, *args):
        return self.publisher.model.lang

    def variables(self,_,*args):
        """
        Returns the variables' definition xml file,
        """
        filename=args[0]
        if self.__cache.has_key(filename):
            return self.__cache.get(filename)
        try:
            v=self.publisher.model.getvariables(filename)
        except:
            raise PublisherError(self.publisher.setmessage(u"[0026]Impossible de trouver le fichier tableur: %(sheet)s", {'sheet': filename}))
        self.__cache[filename]=v
        return v

    def variable(self,_,*args):
        sheet=args[0]
        variab=args[1]
        return self.publisher.get_variable(sheet,variab)

    def replace_strvar(self,_,*args):
        variab=args[0]
        return self.publisher.replace_strvar(variab)

    def replace_crit(self,_,*args):
        crit=args[0]
        return self.publisher.replace_crit(crit)

    def replace_mastercrit(self,_,*args):
        crit=args[0]
        return self.publisher.replace_mastercrit(crit)

    def solve_resid(self,_,*args):
        """
        Returns a kolekti url using the project:// url scheme
        """
        resid=args[0][1:]
        rurl=urllib2.quote(resid.encode('utf-8'))
        url=u'project://%s'%rurl
        return url

    def get_module(self,_,*args):
        """
        Parses and returns a module as a lxml element
        """
        resid=args[0]
        print "get module",resid
        try:
            srcmod=self.publisher.model.getResource(urllib2.unquote(resid).decode('utf-8'))
        except UnicodeEncodeError:
            try:
                srcmod=self.publisher.model.getResource(unicode(resid))
            except:
                dbgexc()
                raise PublisherError(self.publisher.setmessage(u"[0032]Impossible de trouver le module : %(resid)s", {'resid': resid}))
        except:
            dbgexc()
            raise PublisherError(self.publisher.setmessage(u"[0032]Impossible de trouver le module : %(resid)s", {'resid': resid}))
        try:
            parser = ET.XMLParser(load_dtd=True)
            mod=ET.XML(srcmod[0], parser)
        except ET.XMLSyntaxError, e:
            dbgexc()
            raise PublisherError(self.publisher.setmessage(u"[0033]Erreur lors de la lecture du module : %(resid)s %(error)s", {'resid': resid, 'error': e.error_log.filter_from_level(ET.ErrorLevels.FATAL)}))

        self._xmldocs.append(mod)
        return mod

    def get_revnotes(self,_,*args):
        """Returns svn revisions for the given ressource"""
        logs = ET.Element("logs")
        resid=unicode(args[0])
        if resid.startswith(u"project://"):
            resid = u"/projects/%s/%s" %(self.publisher.model.project.get('directory'), resid[10:])
        svnio=self.publisher.model._loadMVCobject_("svnIO")
        res = svnio.svnlog(resid)
        for r in res:
            attrib = {}
            for (n, v) in r.iteritems():
                if n == "date":
                    d = datetime.utcfromtimestamp(v)
                    v = d.strftime("%x %X")
                attrib[n] = unicode(v)
            ET.SubElement(logs, "log", attrib)
        return logs

    def modules_history(self,_,*args):
        try:
            return self.publisher.modhistory.getroot()
        except:
            return []

    def modname(self,_,*args):
        """Returns module name"""
        resid = args[0]
        return resid.split('/')[-1]

    def username(self,_,*args):
        """Gets user name from given id"""
        uid = args[0]
        if uid == "None":
            uid = "0"
        return self.publisher.model.getUsername(int(uid))

    def resid2url(self,_,*args):
        """ returns a kolekti url from resid"""
        return self.publisher.model.id2url(unicode(args[0]))

    def url2resid(self,_,*args):
        """ returns a kolekti resid from url"""
        return self.publisher.model.url2id(args[0])

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

    def setmessage(self, _, *args):
        """Returns formated message, according to linguistic settings"""
        msg = args[0].strip()
        params = {}
        i = 1
        for p in re.findall("%\([^)]+\)s", msg):
            code = p[2:-2]
            params[code] = args[i]
            i += 1

        return self.publisher.setmessage(msg, params)

class PublisherError(Exception):
    """
    Exceptions raised during Publication Phase
    """

    def __init__(self,msg):
        self.err=msg

    def __str__(self):
        return self.err

class PublisherPrefixResolver(ET.Resolver):
    """
    lxml url resolver for kolekti:// url
    """
    def __init__(self,model):
        self.model=model
        super(PublisherPrefixResolver,self).__init__()

    def resolve(self, url, pubid, context):
        """Resolves wether it's a kolekti, kolektiapp, or project url scheme"""
        if url.startswith('kolekti://'):
            localpath=url.split('/')[2:]
            return self.resolve_filename(os.path.join(conf.get('fmkdir'), *localpath),context)
        if url.startswith('kolektiapp://'):
            localpath=url.split('/')[2:]
            return self.resolve_filename(os.path.join(conf.get('appdir'), *localpath),context)
        if url.startswith('project://'):
            localpath=url.split('/')[2:]
            return self.resolve_filename(os.path.join(self.model.projectpath, *localpath),context)

class Publisher(object):
    """
    Generic publisher class
    Provides instanciators and context setting for publication
    """
    nsmap = {"h": "http://www.w3.org/1999/xhtml"}

    def __init__(self, view, model):
        self.view=view
        self.model=model
        self.extensions = {}
        self.cachevarfile = {}
        self.extf_obj = None
        self.__loadextensions()

    def setmessage(self, msg, params={}):
        """Returns formated message, according to linguistic settings"""
        s = tr(msg, params)
        return s.i18n(self.model.http.translation)

    def __loadextensions(self):
        """Loads xslt Extension Class """
        self.extf_obj = PublisherExtensions(self)
        exts = (n for n in dir(PublisherExtensions) if not(n.startswith('_')))
        self.extensions.update(ET.Extension(self.extf_obj, exts, ns=self.extf_obj.ens))

    def get_xsl(self,xslfile):
        """
        Instanciante an xsl processor with the extensions registered
        and using the custom url resolver
        """
        parser = ET.XMLParser()
        parser.resolvers.add(PublisherPrefixResolver(self.model))
        xsldoc  = ET.parse(xslfile,parser)
        xsl = ET.XSLT(xsldoc, extensions=self.extensions)
        return xsl

    def cleanup(self):
        self.extf_obj.cleanup()
        print gc.get_referrers(self.extf_obj)
        self.extf_obj = None
        self.view = None
        self.model = None
        self.extensions = None
        self.cachevarfile = None

class TramePublisher(Publisher):
    """
    The publisher class
    is responsible for performing all publications of a trame :
    - aggregation
    - variable substitutions
    - calling publication backend plugins
    """

    @property
    def profilename(self):
        return self.pivname

    @property
    def document(self):
        return copy.deepcopy(self.pivdocument)

    def _assemble(self):
        """
        performs the assembly of a trame into the masterdocument
        independently from profile
        """

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','aggreg.xsl'))
        try:
            self.masterdocument=xsl(self.trame)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0034]Une erreur est survenue au cours de l'assemblage")))
            raise PublisherError(xsl.error_log)
        except IOError, e:
            yield(self.view.error(self.setmessage(u"[0034]Une erreur est survenue au cours de l'assemblage")))
            raise PublisherError(e)
        except PublisherError, e:
            raise PublisherError(e)
        except:
            dbgexc()
        # create directory and put pivot file into it
        #self.model.make_pubdir(self.pubparams.get('pub_directory'))
        #self.model.pubsave(ET.tostring(self.masterdocument),'pivot-assembly.xml')
        #yield self.view.details("assembly done!")

    def _modules_history(self):
        """
        generate svn logs for trame modules
        """
        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','modules-history.xsl'))
        try:
            self.modhistory=xsl(self.masterdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0339]Une erreur est survenue au cours de la génération de l'historique des versions")))
            raise PublisherError(xsl.error_log)
        except IOError, e:
            yield(self.view.error(self.setmessage(u"[0339]Une erreur est survenue au cours de la génération de l'historique des versions")))
            raise PublisherError(e)
        except PublisherError, e:
            raise PublisherError(e)
        except:
            dbgexc()
        
    def settrame(self, trame, pubparams):
        """
        Associates a trame to the publisher
        Associates the publication parameters
        Assembles the composite doc
        """
        self.trame=trame
        self.pubparams=pubparams
        try:
            # assemble the trame
            debug("assemble")
            for msg in self._assemble():
                yield msg
            debug("modules history")
            for msg in self._modules_history():
                yield msg
        except PublisherError as e:
            debug(e.err)
            yield self.view.error(unicode(e.err))
        except:
            dbgexc()

    def publish(self):
        """
        Starts publication of the assembled masterdocument
        """
        yield self.view.start_section("infos")
        dt = datetime.utcfromtimestamp(self.model.pubtime)
        v = format_datetime(dt, tzinfo=self.model.tzinfo, locale=self.model.locale_lang)
        yield self.view.info(self.setmessage(u"[0231]Date de publication"), v)
        trameurl = "%s?open=%s" %(self.model.id2url(u"@trames"), self.pubparams['trame'][8:])
        yield self.view.labellink(trameurl, self.setmessage(u"[0171]Trame"), self.pubparams['trame'].split('/')[-1], {"class": "trame"})
        yield self.view.info(self.setmessage(u"[0170]Langue"), unicode(self.model.lang))
        yield self.view.finalize()

        yield self.view.start_section("publication_log")

        for profile in self.pubparams['profiles']:
            logs = ''
            for msg in self.publish_profile(profile):
                logs += msg
                yield msg

            self.model.pubsave("<logs>%s</logs>" %logs, '_logs.xml')

        yield self.view.finalize()

    ### The following may be externallized in a specific class if we want to use different publishing
    ### Classes, selected in the publication profile.

    def replace_crit(self, crit):
        ''' Replaces criterias '''
        return self._substcrit(crit)

    def replace_mastercrit(self, crit):
        ''' Replaces criterias of master'''
        return self.__substmastercrit(crit)

    def replace_strvar(self, var):
        ''' Replaces var sheet '''
        return self._subststrvar(var)

    def _prepare(self):
        """
        Creates the publication directory for a given profile
        @publication/profile.pub_directory/datetime.profile.id
        """
        pubdir=''
        try:
            pubdir=self._subststrvar(self._substcrit(self.pubparams['pubdir']))
        except:
            pass
        self.model.make_pubdir(pubdir,self.pivname,self.pubparams['trame'])
        self.model.pubsave(ET.tostring(self.modhistory, xml_declaration=True, encoding="UTF-8"),'modules-history.xml')
        yield(self.view.details(self.setmessage(u"[0035]Dossier de publication créé")))

    def _criterias(self):
        """
        This adds criterias to the header of the pivot file
        """
        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','criterias.xsl'))
        try:
            self.pivdocument=xsl(self.pivdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0036]Une erreur est survenue au cours de l'ajout des critères")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()
        self.model.pubsavepivot(ET.tostring(self.masterdocument, xml_declaration=True, encoding="UTF-8"),'pivot-assembly.xml')
        yield(self.view.details(self.setmessage(u"[0037]Assemblage terminé!")))

    def _filter(self):
        """
        This performs the filtering of the pivot
        """

        #xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','filter-exclusive.xsl'))
        #try:
        #    self.pivdocument=xsl(self.pivdocument)
        #except ET.XSLTApplyError, e:
        #    yield(self.view.error(u"une erreur est survenue au cours du filtrage"))
        #    debug(xsl.error_log)
        #except:
        #    dbgexc()
        #yield self.view.details(u"Exclusive conditions done!")

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','filter.xsl'))
        try:
            self.pivdocument=xsl(self.pivdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0038]Une erreur est survenue au cours du filtrage")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','filter-empty-sections.xsl'))
        try:
            self.pivdocument=xsl(self.pivdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0325]Une erreur est survenue au cours du filtrage des sections vides")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()
        self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),
                                'pivot-filtered.xml')
        yield(self.view.details(self.setmessage(u"[0039]Filtrage des conditions terminé!")))

    def _filtermaster(self):
        """
        This performs the filtering of the master file
        """

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','filter-master.xsl'))
        try:
            self.masterdocument=xsl(self.masterdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0038]Une erreur est survenue au cours du filtrage")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','filter-empty-sections.xsl'))
        try:
            self.masterdocument=xsl(self.masterdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0325]Une erreur est survenue au cours du filtrage des sections vides")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()
        yield(self.view.details(self.setmessage(u"[0039]Filtrage des conditions terminé!")))

    def _substituteVars(self):
        """
        This substitutes variables in the pivot document
        """

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','variables.xsl'))
        try:
            self.pivdocument=xsl(self.pivdocument)
            errors = set()
            for err in xsl.error_log:
                if not err.message in errors:
                    yield(self.view.error(err.message))
                    errors.add(err.message)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0040]Une erreur est survenue au cours de la substitution des variables")))
            raise PublisherError(xsl.error_log)
        except PublisherError, e:
            dbgexc()
            yield(self.view.error(self.setmessage(u"[0040]Une erreur est survenue au cours de la substitution des variables")))
            raise e

        self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),'pivot-variables.xml')
        yield(self.view.details(self.setmessage(u"[0041]Substitution des variables terminée!")))

    def _processLinks(self, master=False):
        """
        This step translates links (module to module) into internal links in the pivot document
        """
        # Replace internal http links
        host = self.model.http.url.split('/projects/')[0]
        for link in self.pivdocument.xpath("//h:a[starts-with(@href, '%s')]"%host, namespaces=self.nsmap):
            link.set('href', link.get('href')[len(host):])

        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','links.xsl'))
        try:
            if master:
                self.masterdocument=xsl(self.masterdocument)
            else:
                self.pivdocument=xsl(self.pivdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0042]Une erreur est survenue au cours du traitement des liens")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()
        if not master:
            self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),'pivot-links.xml')
        yield(self.view.details(self.setmessage(u"[0043]Résolution des liens terminée!")))

    def _checkLinks(self):
        """
        This step verify if links they are broken in the pivot document
        """
        xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','check-links.xsl'))
        try:
            self.pivdocument=xsl(self.pivdocument)
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0042]Une erreur est survenue au cours du traitement des liens")))
            raise PublisherError(xsl.error_log)
        except:
            dbgexc()
        self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),'pivot-links.xml')
        yield(self.view.details(self.setmessage(u"[0043]Résolution des liens terminée!")))

    def _makeTOC(self):
        """
        This step builds the toc in the pivot document
        """
        if len(self.pivdocument.xpath("//h:div[@class='TDM']", namespaces=self.nsmap)) > 0:
            xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','tdm.xsl'))
            try:
                self.pivdocument=xsl(self.pivdocument)
            except ET.XSLTApplyError, e:
                yield(self.view.error(self.setmessage(u"[0044]Une erreur est survenue lors de la génération de la table des matière")))
                debug(xsl.error_log)
            except:
                dbgexc()
            self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),'pivot-with-tdm.xml')
            yield(self.view.details(self.setmessage(u"[0045]Génération de la table des matières terminée!")))

    def _makeINDEX(self):
        """
        This step builds the index in the pivot document
        """
        # TODO : test if index virtual module is there
        if len(self.pivdocument.xpath("//h:div[@class='INDEX']", namespaces=self.nsmap)) > 0:
            xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','index.xsl'))
            try:
                self.pivdocument=xsl(self.pivdocument)
            except ET.XSLTApplyError, e:
                yield(self.view.error(self.setmessage(u"[0046]Une erreur est survenue lors de la génération de l'index")))
                debug(xsl.error_log)
            except:
                dbgexc()
            self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),'pivot-with-index.xml')
            yield(self.view.details(self.setmessage(u"[0047]Génération de l'index terminée!")))

    def _makeREVNOTES(self):
        """
        This step builds the Revision Notes Table in the pivot document
        """

        try:
            xslcsv=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','csv-revnotes.xsl'))
            csvdoc=xslcsv(self.pivdocument)
            if not csvdoc is None:
                self.model.pubsave(str(csvdoc),'modules-history.csv')
        except ET.XSLTApplyError, e:
            yield(self.view.error(self.setmessage(u"[0339]Une erreur est survenue au cours de la génération de l'historique des versions")))
            debug(xsl.error_log)
        except:
            dbgexc()

        if len(self.pivdocument.xpath("//h:div[@class='REVNOTES']", namespaces=self.nsmap)) > 0:
            xsl=self.get_xsl(os.path.join(conf.get('appdir'),'publication','xsl','revnotes.xsl'))
            try:
                self.pivdocument=xsl(self.pivdocument)
            except ET.XSLTApplyError, e:
                yield(self.view.error(self.setmessage(u"[0048]Une erreur est survenue lors de la génération de la table des modifications")))
                debug(xsl.error_log)
            except:
                dbgexc()
            self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),'pivot-with-revnotes.xml')
            yield(self.view.details(self.setmessage(u"[0049]Génération de la table des modifications terminée!")))

    def _processMedia(self):
        """
        This one copies media from project space into publication space
        """
        precmed = {}
        for med in self.pivdocument.xpath('//h:img[@src]|//h:embed[@src]', namespaces=self.nsmap):
            src = self.model.url2id(med.get('src'))
            if src.startswith('http://') or src.startswith('https://'):
                newsrc = src
            else:
                try:
                    if not precmed.has_key(src):
                        newsrc = self.model.id2url(self.model.medias_copy(src))
                    else:
                        newsrc = precmed[src]
                except (IOError, KeyError):
                    misssrc = u"/_lib/kolekti/icons/missing_media.png"
                    if not precmed.has_key(misssrc):
                        newsrc = self.model.id2url(self.model.medias_copy(misssrc, "icons"))
                        precmed[misssrc] = newsrc
                    else:
                        newsrc = precmed[misssrc]
                    yield(self.view.error(self.setmessage(u"[0050]Echec lors de la copie du média %(src)s", {'src': str(med.get('src'))})))
                except:
                    dbgexc()
                    continue
                med.set('src', newsrc)
                precmed.update({src:newsrc})
        yield(self.view.details(self.setmessage(u"[0051]Copie des médias terminée!")))

    def _scripts(self, scripts):
        """
        This steps starts the publication scripts declared in the publication profile
        - shell scripts
        - plugins
        - xslt scripts
        """
        # get the declaration of publication scripts (declared in config)
        scrdefs=self.model.getPubscripts()

        for defs in scripts:
            label=defs.get("label")
            name=defs.get('name')
            suffix=defs.get('suffix')
            params=defs.get('params')
            try:
                scrdef=scrdefs.xpath('/scripts/pubscript[@id="%s"]'%name)[0]
            except IndexError:
                debug("Impossible de trouver le script: %s" %name)
                continue
            try:
                # copy when parameters says to copy
                for pname,pval in params.iteritems():
                    pdef=scrdef.xpath("parameters/parameter[@name='%s']"%pname)[0]
                    if pdef.get('type')=='filelist' and pdef.get('copyto') is not None: 
                        if pdef.get('ext') == "less":
                            self.model.script_lesscompile(pval,
                                                          unicode(pdef.get('dir')),
                                                          '%s/%s'%(label,pdef.get('copyto')))
                            
                        else:
                            self.model.script_copy(pval,
                                                   unicode(pdef.get('dir')),
                                                   '%s/%s'%(label,pdef.get('copyto')), pdef.get('ext'))
                stype=scrdef.get('type')
            except:
                dbgexc()
                yield(self.view.error(self.setmessage(u"[0052]Erreur lors de la copie des ressources")))
                return
            try:
                if stype=="shell":
                    cmd=scrdef.find("cmd").text
                    # if get file with local url
                    if cmd.find("_PIVLOCAL_") >= 0:
                        localdocument = self.document
                        for media in localdocument.xpath("//h:img[@src]|//h:embed[@src]", namespaces=self.nsmap):
                            localsrc = self.model.abstractIO.local2unicode(self.model.url2local(str(media.get('src'))))
                            media.set('src', localsrc)
                        #save the pivot file
                        self.model.pubsavepivot(ET.tostring(localdocument, xml_declaration=True, encoding="UTF-8"),
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
                                yield(self.view.error(self.setmessage(u"[0053]Attention %(warn)s", {'warn': line})))
                            elif re.search('error', line) or re.search('not found', line):
                                yield(self.view.error(self.setmessage(u"[0054]Erreur lors de l'exécution de la commande : %(cmd)s (%(error)s)",
                                                                      {'cmd': cmd.decode(LOCAL_ENCODING).encode('utf-8'), 'error': line.encode('utf-8')})))
                                has_error = True

                        # if no error display link
                        if not has_error:
                            xl=scrdef.find('link')
                            outfile=self.__substscript(xl.get('name'), label, params)
                            outref=self.__substscript(xl.get('ref'), label, params)
                            yield (self.view.publink(outfile,
                                                     label,
                                                     outref))
                            yield (self.view.success(self.setmessage(u"[0055]Exécution du script %(label)s réussie", {'label': label.encode('utf-8')})))
                    except:
                        dbgexc()
                        os.system(cmd.encode('utf-8'))

                if stype=="plugin":
                    try:
                        plugname=scrdef.find("plugin").text
                        try:
                            module=sys.modules[plugname]
                        except KeyError:
                            pluginpath=os.path.join(conf.get('appdir'),"publication","plugins")
                            if not pluginpath in sys.path:
                                sys.path.append(pluginpath)
                            fp, pathname, description = imp.find_module(plugname)
                            try:
                                module = imp.load_module(name, fp, pathname, description)
                            except:
                                dbgexc()
                                yield(self.view.error(self.setmessage(u"[0056]Impossible de charger le script %(label)s", {'label': label.encode('utf-8')})))
                                return
                        debug("###### Calling plugin %s"%str(module))
                        plugin=getattr(module,'plugin')(self,label,suffix,params)
                        for msg in plugin.postpub():
                            yield msg

                        yield(self.view.success(self.setmessage(u"[0057]Exécution du script %(label)s réussie", {'label': label.encode('utf-8')})))
                    except:
                        dbgexc()
                        yield(self.view.error(self.setmessage(u"[0058]Impossible d'exécuter le script %(label)s", {'label': label.encode('utf-8')})))

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

                        xparams['LANG']="'%s'"%self.model.lang
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

    def __substscript(self,srcstr,label,params):
        """
        Substitutes, in srcstr, all
        - variables values
        - criterias by their value
        - publication parameters
        """
        srcstr=srcstr.replace("_LABEL_", label)
        #substitue les critères et l'environnement
        srcstr=self.__substall(srcstr)

        #substitue les parametres
        for n,v in params.iteritems():
            srcstr=srcstr.replace("_%s_"%n,v)
        return srcstr

    def __substall(self,srcstr):
        """
        Substitutes, in srcstr, all
        - variables values
        - criterias by their value
        """
        #substitue les critères
        srcstr=self._substcrit(srcstr)

        #substitue l'environnement
        srcstr=srcstr.replace("_PIV_", os.path.join("_PUBDIR_", "_pivots", "%s.xml" %self.pivname))
        srcstr=srcstr.replace("_PIVLOCAL_", os.path.join("_PUBDIR_", "_pivots", "%s-local.xml" %self.pivname))
        srcstr=srcstr.replace("_LANG_", self.model.lang)
        srcstr=srcstr.replace("_DOCNAME_", self.docname)
        srcstr=srcstr.replace("_PUBDIR_", self.model.pubpath.decode(LOCAL_ENCODING))
        srcstr=srcstr.replace("_PUBURL_", self.model.pubdirurl)
        srcstr=srcstr.replace("_BASEDIR_", self.model.basepath.decode(LOCAL_ENCODING))

        return srcstr

    def _substcrit(self,srcstr):
        for crit,val in self.critdict.iteritems():
            srcstr=srcstr.replace('_%s_'%crit,val)
        srcstr=srcstr.replace("_LANG_", self.model.lang)
        return srcstr

    def __substmastercrit(self,srcstr):
        for crit,val in self.filtercrit.iteritems():
            srcstr=srcstr.replace('_%s_'%crit,val)
        return srcstr
    
    def _subststrvar(self,srcstr):
        '''Replaces kolekti variable with a string'''
        for variab in re.findall('\[var[ a-zA-Z0-9_]+:[a-zA-Z0-9_ ]+\]', srcstr):
            splitVar = variab[4:-1].split(':')
            sheet = splitVar[0].strip()
            v = splitVar[1].strip()
            try:
                if self.cachevarfile.has_key(sheet):
                    varxml = self.cachevarfile.get(sheet)
                else:
                    varxml=self.model.getvariables(sheet)
                    self.cachevarfile[sheet]=varxml
            except:
                debug(u'Unable to read sheet : %s'%sheet)
                continue
            # Generate xpath to select content of var
            xsearch = "/h:variables/h:variable[@code='%s']/h:value" %v
            critlist = varxml.xpath('string(/h:variables/h:critlist)', namespaces=self.nsmap)
            critcond = ''
            for crit in critlist.split(':'):
                if crit != '':
                    try:
                        critcond += " and h:crit[@name='%s']/@value = '%s'" %(crit, self.critdict[crit])
                    except:
                        pass
            if critcond != '':
                xsearch += "[%s]" %critcond[5:]
            xsearch += "/h:content"
            val = varxml.xpath('string(%s)' %xsearch, namespaces=self.nsmap)
            srcstr=srcstr.replace(variab, val)
        return srcstr

    def get_variable(self,sheet,var):
        try:
            if self.cachevarfile.has_key(sheet):
                varxml = self.cachevarfile.get(sheet)
            else:
                varxml=self.model.getvariables(sheet)
                self.cachevarfile[sheet]=varxml
        except:
            dbgexc()
            debug(u'Unable to read sheet : %s'%sheet)
            raise PublisherError, self.setmessage(u"[0026]Impossible de trouver le fichier tableur: %(sheet)s", {'sheet': sheet})
        # Generate xpath to select content of var
        xsearch = "/h:variables/h:variable[@code='%s']/h:value" %var
        critlist = varxml.xpath('string(/h:variables/h:critlist)', namespaces=self.nsmap)
        critcond = ''
        for crit in critlist.split(':'):
            if crit != '':
                try:
                    critcond += " and h:crit[@name='%s']/@value = '%s'" %(crit, self.critdict[crit])
                except:
                    pass
        if critcond != '':
            xsearch += "[%s]" %critcond[5:]
        xsearch += "/h:content"
        val = varxml.xpath('string(%s)' %xsearch, namespaces=self.nsmap)
        return val

    def __master(self):
        yield self.view.details(u"Dummy master generation!")

    def publish_profile(self, profile):
        """
        Publish the masterdocument for given profile
        """
        self.profile=profile

        #init dictionnary
        try:
            #create the dictionnary of criterias
            self.critdict={}
            crits=self.profile.xpath("criterias/criteria[@checked='1']")
            for c in crits:
                debug(ET.tostring(c))
                self.critdict.update({c.get('code'):c.get('value')})
            self.critdict.update({'LANG':self.model.lang})

            # get the lists of scripts to perform as post publication
            scripts=[]
            for s in self.pubparams['scripts']:
                suffix = self._subststrvar(self._substcrit(unicode(s.xpath("string(suffix[@enabled='1'])"))))
                name = unicode(s.get('name'))
                label = name+suffix
                debug(label)
                params={}
                for p in s.xpath('parameters/parameter'):
                    params.update({p.get('name'):p.get('value')})
                scripts.append({'label':label,'name':name,'suffix': suffix, 'params':params})
        except:
            dbgexc()
            yield(self.view.error(self.setmessage(u"[0059]Echec lors de l'initialisation des critères et des scripts.")))
            return

            # replace criterias _FOO_ with their values in the pivot filename
        self.pivname = self._subststrvar(self._substcrit(unicode(self.profile.xpath("string(label)"))))

        yield(self.view.start_section("profile"))
        yield(self.view.profile(self.pivname))

        self.pivdocument=self.masterdocument

        try:
            if self.pivname == "pivot":
                self.docname = "document"
            else:
                self.docname = self.pivname

            yield(self.view.start_section("result"))

            # create the publication directory
            for msg in self._prepare():
                yield msg

            # filtering
            for msg in self._criterias():
                yield msg

            # filtering
            for msg in self._filter():
                yield msg

            # variables substitution
            for msg in self._substituteVars():
                yield msg

            for msg in self._processLinks():
                yield msg

            # build the index
            for msg in self._makeINDEX():
                yield msg

            # build the toc of the document
            for msg in self._makeTOC():
                yield msg

            # build the revision notes table
            for msg in self._makeREVNOTES():
                yield msg

            # contrôle et copie des illustrations des modules
            for msg in self._processMedia():
                yield msg

            #save the pivot file
            self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),
                                    '%s.xml'%self.pivname,
                                    True,
                                    profilename=self.pivname)

            # appel des scripts post-publication
            for msg in self._scripts(scripts):
                yield msg

        except PublisherError as e:
            debug(e.err)
            yield self.view.details(unicode(e.err))
        except:
            dbgexc()
            yield(self.view.error(self.setmessage(u"[0059]Une erreur inconnue s'est produite pendant le processus de publication")))
        yield(self.view.finalize())
        yield(self.view.finalize())

    def genmaster(self, trame):
        """
        Generates a master document : zip bundled contains everything
        needed for a defferred publication
        """

        yield self.view.start_section("master")
        yield(self.view.details(self.setmessage(u"[0060]Génération de l'enveloppe")))
        try:
            if not self.pubparams.get('filter_master') == '0':
                self.model.add_db_master_criteria(self.pubparams.get('filter_master'))
                self.filtercrit={}
                self.__mastercriterias(self.pubparams.get('filter_master'))
                head = self.masterdocument.xpath('/h:html/h:head', namespaces={'h': 'http://www.w3.org/1999/xhtml'})[0]
                for (code, value) in self.filtercrit.iteritems():
                    ET.SubElement(head, '{%s}meta' %self.nsmap['h'], {'scheme':'condition', 'name':code.strip(),'content':value.strip()})

                for msg in self._filtermaster():
                    yield msg

            for msg in self._processLinks(master=True):
                yield msg

            # extract moduleinfos
            self._module_info_out()

            for msg in self.model.genmaster(self, trame):
                yield msg

            yield(self.view.details(self.setmessage(u"[0061]Génération de l'enveloppe terminée")))
        except:
            dbgexc()
            yield(self.view.error(self.setmessage(u"[0062]Erreur lors de la génération de l'enveloppe")))
        yield(self.view.finalize())

    def _module_info_out(self):
        ''' extract moduleinfos '''
        self.moduleinfos = ET.Element("{%s}moduleinfos" %self.nsmap['h'])
        for minfo in self.masterdocument.xpath("//h:div[@class='moduleinfo']", namespaces=self.nsmap):
            mod = minfo.getparent()
            minfo.set('modid', mod.get('id'))
            self.moduleinfos.append(minfo)

    def _module_info_in(self):
        ''' import moduleinfos '''
        for minfo in self.model.module_infos:
            try:
                modinfo = self.masterdocument.xpath("//h:div[@class='module'][@id='%s']" %minfo.get('modid'), namespaces=self.nsmap)[0]
                minfo.attrib.pop("modid")
                modinfo.append(minfo)
            except IndexError:
                debug("id %s not found" %minfo.get('modid'))

    def __mastercriterias(self, crit):
        try:
            cpos = re.search(',|;', crit)
            c = crit.split('=')
            if cpos is None:
                self.filtercrit.update({c[0]: c[1]})
            else:
                climit = re.search(',|;', c[1])
                self.filtercrit.update({c[0]: c[1][:climit.start()]})
                self.__mastercriterias(crit[cpos.end():])
        except:
            pass

class MasterPublisher(TramePublisher):
    """ Publish a translated master"""

    def setpubparams(self, pubparams):
        """
        Associates publication parameters
        """
        self.pubparams=pubparams
        try:
            # assemble the trame
            debug("assemble")
            for msg in self._assemble():
                yield msg
            debug("modules history")
            self._modules_history()
        except PublisherError as e:
            debug(e.err)
            yield self.view.error(unicode(e.err))
        except:
            dbgexc()

    def _assemble(self):
        """
        Performs the assembly of a trame into the masterdocument
        independently from profile
        """
        try:
            self.masterdocument=self.model.pivot
            self._module_info_in()
        except:
            dbgexc()
            yield(self.view.error(self.setmessage(u"[0063]Une erreur est survenue lors de la récupération du document enveloppe")))

    def _modules_history(self):
        """
        generate svn logs for trame modules
        """
        self.modhistory = self.model.modules_history

    def publish_profile(self, profile):
        """
        Publish the masterdocument for given profile
        """
        if self.model.masterversion == 1:
            super(MasterPublisher, self).publish_profile(profile)
        else:
            self.profile=profile
    
            #init dictionnary
            try:
                #create the dictionnary of criterias
                self.critdict={}
                crits=self.profile.xpath("criterias/criteria[@checked='1']")
                for c in crits:
                    debug(ET.tostring(c))
                    self.critdict.update({c.get('code'):c.get('value')})
                self.critdict.update({'LANG':self.model.lang})
    
                # get the lists of scripts to perform as post publication
                scripts=[]
                for s in self.pubparams['scripts']:
                    suffix = self._subststrvar(self._substcrit(unicode(s.xpath("string(suffix[@enabled='1'])"))))
                    name = unicode(s.get('name'))
                    label = name+suffix
                    debug(label)
                    params={}
                    for p in s.xpath('parameters/parameter'):
                        params.update({p.get('name'):p.get('value')})
                    scripts.append({'label':label,'name':name,'suffix': suffix, 'params':params})
            except:
                dbgexc()
                yield(self.view.error(self.setmessage(u"[0059]Echec lors de l'initialisation des critères et des scripts.")))
                return
    
                # replace criterias _FOO_ with their values in the pivot filename
            self.pivname = self._subststrvar(self._substcrit(unicode(self.profile.xpath("string(label)"))))
    
            yield(self.view.start_section("profile"))
            yield(self.view.profile(self.pivname))
    
            self.pivdocument=self.masterdocument
    
            try:
                if self.pivname == "pivot":
                    self.docname = "document"
                else:
                    self.docname = self.pivname
    
                yield(self.view.start_section("result"))
    
                # create the publication directory
                for msg in self._prepare():
                    yield msg
    
                # filtering
                for msg in self._criterias():
                    yield msg
    
                # filtering
                for msg in self._filter():
                    yield msg
    
                # variables substitution
                for msg in self._substituteVars():
                    yield msg
    
                for msg in self._checkLinks():
                    yield msg
    
                # build the index
                for msg in self._makeINDEX():
                    yield msg
    
                # build the toc of the document
                for msg in self._makeTOC():
                    yield msg
    
                # build the revision notes table
                for msg in self._makeREVNOTES():
                    yield msg
    
                # contrôle et copie des illustrations des modules
                for msg in self._processMedia():
                    yield msg
    
                #save the pivot file
                self.model.pubsavepivot(ET.tostring(self.pivdocument, xml_declaration=True, encoding="UTF-8"),
                                        '%s.xml'%self.pivname,
                                        True,
                                        profilename=self.pivname)
    
                # appel des scripts post-publication
                for msg in self._scripts(scripts):
                    yield msg
    
            except PublisherError as e:
                debug(e.err)
                yield self.view.details(unicode(e.err))
            except:
                dbgexc()
                yield(self.view.error(self.setmessage(u"[0059]Une erreur inconnue s'est produite pendant le processus de publication")))
            yield(self.view.finalize())
            yield(self.view.finalize())
