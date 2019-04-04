# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2019 Stéphane Bonhomme (stephane@exselt.com)

""" Release utilities"""

import os
import copy
import logging
import shutil
import time
import json
from lxml import etree as ET

from synchro import SynchroManager

logger = logging.getLogger("kolekti." + __name__)

release_info = {
    "assembly_dir" : None,
    "lang" : None,
    "datetime" : 0,
    "toc" : None,
    "releaseindex" : None,
    "releasename" : None,
    "pubname" : None,
    "job" : None,
    "releasedir" : None,
    "releaseprev" : None
}

namespaces = {"h":"http://www.w3.org/1999/xhtml"}
ns = {"namespaces":namespaces}


class Release(object):
    """ Release releative functions
    - Copying release
    - Renaming
    - filtering assemblies
    """
    def __init__(self, basepath, username, project, release):
        self._basepath = basepath
        self._username = username
        self._project = project
        self._release = release
        self._xmlparser = ET.XMLParser(load_dtd = True)

    @property
    def args(self):
        return [self._basepath, self._username, self._project]
        
    def __pathchars(self, s):
        intab = """?'"<>\/|"""
        outtab = "!_______"
        for i,o in zip(intab, outtab):
            s = s.replace(i,o)
        return s
        
    def _syspath(self, path):
        # returns os absolute path from relative path
        pathparts = [self.__pathchars(p) for p in path.split('/') if p!='']
        return os.path.join(self._basepath, self._username, self._project, *pathparts)

        
    def __makepath(self, path):
        return self._syspath('/releases/{}{}'.format(self._release, path))

    def xwrite(self, xml, filename, encoding = "utf-8", pretty_print=True, xml_declaration=True):

        ospath = self.__makepath(filename)
        with open(ospath, "w") as f:
            f.write(ET.tostring(xml, encoding = encoding, pretty_print = pretty_print,xml_declaration=xml_declaration))
            
    def parse(self, filename):
        src = self.__makepath(filename)
        return ET.parse(src,self._xmlparser)
    
    def assembly(self, lang):
        return self.parse('/sources/{}/assembly/{}_asm.html'.format(lang, self._release))
        
    def job(self):
        return self.parse('/kolekti/publication-parameters/{}_asm.xml'.format(self._release))
        
    def profiles(self, enabled=True):
        job = self.job()
        xp = '/job/profiles/profile'
        if enabled:
            xp = xp + '[@enabled = "1"]'
        for profile in job.xpath(xp):
            yield profile
            
    def profiles_criteria(self):
        job_criteria = self.job_criteria()
        for profile in self.profiles():
            crits = copy.copy(job_criteria)
            for c in profile.xpath('criteria/criterion'):
                crits.update({c.get('code'):c.get('value')})
            yield crits

        
    def job_criteria(self):
        job = self.job()
        crits = {}
        for c in job.xpath('/job/criteria/criterion'):
            crits.update({c.get('code'):c.get('value')})
        return crits


    def noneCat(self, *args):
        """
        Concatenate arguments. Treats None as the empty string, though it returns
        the None object if all the args are None. That might not seem sensible, but
        it works well for managing lxml text components.
        """
        for ritem in args:
            if ritem is not None:
                break
        else:
            # Executed only if loop terminates through normal exhaustion, not via break
            return None
        
        # Otherwise, grab their string representations (empty string for None)
        return ''.join((unicode(v) if v is not None else "") for v in args)
    
    def unwrap(self, elt):
        """
        Unwrap the element. The element is deleted and all of its children
        are pasted in its place.
        """
#        logger.debug('unwrap')
        parent = elt.getparent()
        prev = elt.getprevious()
        kids = list(elt)
        siblings = list(parent)
        # parent inherits children, if any
        sibnum = siblings.index(elt)

        if kids:
            parent[sibnum:sibnum+1] = kids
        else:
            parent.remove(elt)
        if prev is not None:
            prev.tail = self.noneCat(prev.tail, elt.text)
        else:
            parent.text = self.noneCat(parent.text, elt.text)
        if kids:
            last_child = kids[-1]
            last_child.tail = self.noneCat(last_child.tail, elt.tail)
        elif prev is not None:
            prev.tail = self.noneCat(prev.tail, elt.tail)
        else:
            parent.text = self.noneCat(parent.text, elt.tail)
        return elt
        
    def remove(self, elt):
        """
        Remove the element. The element is deleted with all of its children
        """
        parent = elt.getparent()
        prev = elt.getprevious()
        parent.remove(elt)
        if prev is not None:
            prev.tail = self.noneCat(prev.tail, elt.tail)
        else:
            parent.text = self.noneCat(parent.text, elt.tail)
        return elt
        
    def apply_filters(self, lang):
        assembly = self.assembly(lang)
        do_save = False
        for elt in assembly.xpath('//*[contains(@class, "=")]'):
            do_save = self.apply_filters_element(elt) or do_save
            
        if do_save:
            # elimine les topics dont le contenu est vide
            exp = '//h:div[@class="topic"][not(node()[not(self::h:div[@class="topicinfo"])][not(normalize-space()="")])]'           
            for elt in assembly.xpath(exp, **ns):
                self.remove(elt)
                
            # elimine les sections dont le contenu est vide
            exp = '//h:div[@class="section"][not(.//h:div/@class="topic")]'
            for elt in assembly.xpath(exp, **ns):
                self.remove(elt)
                
            logger.debug('{} [{}] modified'.format(self._release, lang))
            self.xwrite(assembly, '/sources/{}/assembly/{}_asm.html'.format(lang, self._release))

    def apply_filters_element(self, elt, profile_filter=True, assembly_filter=False, setPI = False, remove_conditional_elements = ['div', 'span']):
#        assert(not elt.get('class') is None)

#        logger.debug('condition')
#        logger.debug(elt.get('class'))
        tag = elt.xpath('string(local-name())')
#        logger.debug(tag)
#        logger.debug(self.job_criteria())
        
        if assembly_filter:
            evalc = self.eval_condition(self.job_criteria(), elt.get('class'))
            if evalc in [True, None]:
                if evalc and tag in remove_conditional_elements:
                    self.unwrap(elt)
                    return True
                return False
            
        if profile_filter:
            for profile in self.profiles_criteria():
                evalc = self.eval_condition(profile, elt.get('class'))
                if evalc in [True, None]:
                    logger.debug("found " + str(profile))
                    return False
        if setPI:
            elt.addprevious(ET.ProcessingInstruction("filter", "[{} {}]".format(tag, elt.get('class'))))
            
        self.remove(elt)
        return True

            
    def eval_condition(self, criteria_values, cond_string):
        class EvalExceptionTrue(Exception):
            pass
        
        class EvalExceptionNotFound(Exception):
            pass
        
        result = None
        
        cond_string = cond_string.replace(' ','')
        conditions = cond_string.split(";")
        for condition in conditions:
            try:
                exclude = False
                if "\\" in condition:
                    exclude = True
                    
                condition = condition.replace('\\','')
                criterion, values = condition.split('=')
                
                if not criteria_values.has_key(criterion):
                    raise EvalExceptionNotFound()
                    
                for value in values.split(','):
                    if value == criteria_values[criterion]:
                        if exclude:
                            return False
                        else:
                            raise EvalExceptionTrue()
                        
                # la valeur du profil non trouvée
                if not exclude:
                    return False
                
            except EvalExceptionTrue:
                result = True
                
            except EvalExceptionNotFound:
                pass
            
        return result

    # rename release
    
    def rename(self, newname, newindex):

        newrelease = newname + '_' + newindex
        src = '/releases/%s'%(self._release,)
        dst = '/releases/%s'%(newrelease,)
        try:
            syncMgr = SynchroManager(*self.args)
            os.makedirs(os.path.join(self._basepath, self._username, self._project) + dst)
            syncMgr.add_resource(dst)
            syncMgr.move_resource(src +'/sources', dst+ '/sources' )
            syncMgr.move_resource(src +'/kolekti', dst + '/kolekti')
            syncMgr.move_resource(src +'/release_info.json', dst +'/release_info.json')
            syncMgr.delete_resource(src)
        except:
            logger.exception('unable to get sync')
            raise
            shutil.move(
                self._syspath(src),
                self._syspath(dst)
                )
            
#        logger.debug(os.listdir(self._syspath('{}/sources'.format(dst))))
        for lang in os.listdir(self._syspath('{}/sources'.format(dst))):
            src_assembly_path = '/sources/%s/assembly/%s_asm.html'%(lang,self._release)
            if os.path.exists(self._syspath("%s%s"%(dst, src_assembly_path))):
                assembly_path = ('/sources/%s/assembly/%s_asm.html'%(lang, newrelease))

                try:
                    syncMgr.move_resource(
                        "%s%s"%(dst, src_assembly_path),
                        "%s%s"%(dst, assembly_path)
                    )
                except:
                    shutil.move(
                        self._syspath("%s%s"%(dst, src_assembly_path)),
                        self._syspath("%s%s"%(dst, assembly_path))
                    )

                ospath = self._syspath("%s%s"%(dst, assembly_path))
                assembly = ET.parse(ospath, self._xmlparser)
                head = assembly.xpath('/h:html/h:head', **ns)[0]
                self._set_meta(head, "kolekti.project", self._project)
                self._set_meta(head, "kolekti.releasedir", newrelease)
                self._set_meta(head, "kolekti.releasename", newname)
                self._set_meta(head, "kolekti.releaseindex", newindex)

                with open(ospath, "w") as f:
                    f.write(ET.tostring(
                        assembly,
                        encoding = "utf-8",
                        pretty_print = True,
                        xml_declaration = True
                        ))

        # handle publication parameters
        src_job_path = '/kolekti/publication-parameters/%s_asm.xml'%(self._release)
        job_path = '/kolekti/publication-parameters/%s_asm.xml'%(newrelease)
        try:
            syncMgr.move_resource(
                "%s%s"%(dst, src_job_path),
                "%s%s"%(dst, job_path)
            )
        except:
            shutil.move(
                self._syspath("%s%s"%(dst, src_job_path)),
                self._syspath("%s%s"%(dst, job_path))
            )

        # process publication parameters

        ospath = self._syspath("%s%s"%(dst, job_path))
        pp = ET.parse(ospath, self._xmlparser)
        job = pp.getroot()
        job.set('pubdir',newrelease)
        job.set('id',newrelease+"_asm")
        
        with open(ospath, "w") as f:
            f.write(ET.tostring(
                pp,
                encoding = "utf-8",
                pretty_print = True,
                xml_declaration = True
                ))


        # process json info file
        infofile = self._syspath('{}/release_info.json'.format(dst))
        try:
            mf = json.load(open(infofile))
        except:
            logger.exception('info unreadable')
            mf = copy.copy(release_info)

        date = int(time.time())
            
        mf.update({
            "assembly_dir" : '/releases/{}'.format(newrelease),
            "datetime" : date,
            "releaseindex" : newindex,
            "releasename" : newname,
            "releasedir" : newrelease,
        })
        json.dump(mf, open(infofile,'w'))

            

            
    def _set_meta(self, head, name, content):
        try:
            meta = head.xpath('h:meta[@name="{}"]'.format(name), **ns)[0]
            meta.set("content", content)
        except IndexError:
            meta = ET.SubElement(head, '{http://www.w3.org/1999/xhtml}meta', {"name":name, "content":content})

        
    
            
import unittest

class FilterTest(unittest.TestCase):
    def setUp(self):
        self.release=Release('/tmp', '')

    def test_eval_1(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_2(self):
        condstring = "M=A,B"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)

    def test_eval_3(self):
        condstring = "M=A"
        crits = {'M':'B'}
        val = self.release.eval_condition(crits, condstring)
        self.assertFalse(val)

    def test_eval_4(self):
        condstring = "N=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertEqual(val, None)

    def test_eval_5(self):
        condstring = "M=A,B"
        crits = {'M':'C'}
        val = self.release.eval_condition(crits, condstring)
        self.assertFalse(val)

    def test_eval_6(self):
        condstring = "M=A;N=B"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)

    def test_eval_7(self):
        condstring = "M=A; N=B"
        crits = {'M':'A', 'N':'B'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)

    def test_eval_8(self):
        condstring = "M=A; N=B"
        crits = {'M':'A', 'Z':'B'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_9(self):
        condstring = "M=A; N=B"
        crits = {'M':'A', 'N':'C'}
        val = self.release.eval_condition(crits, condstring)
        self.assertFalse(val)
        
    def test_eval_10(self):
        condstring = "M=A; N=B,C"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_11(self):
        condstring = "M=A; N=B,C"
        crits = {'M':'A','N':'C'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_12(self):
        condstring = "M=A; N=B,C"
        crits = {'M':'A','N':'D'}
        val = self.release.eval_condition(crits, condstring)
        self.assertFalse(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_eval_(self):
        condstring = "M=A"
        crits = {'M':'A'}
        val = self.release.eval_condition(crits, condstring)
        self.assertTrue(val)
        
    def test_zone(self):
        self.release.job_criteria = lambda:{'M':'A'}
        elt = ET.XML('<p>before<span class="M=A">keep</span><span class="M=B">remove</span>after</p>')
        for e in elt.xpath('//*[@class]'):
            self.release.apply_filters_element(e, False,True,False)
        val = ET.tostring(elt)
        self.assertEqual(val, '<p>beforekeepafter</p>')


    def test_unwrap(self):
        root = ET.XML('<p>before<span class="M=A">keep</span><span class="M=B">remove</span>after</p>')
        e=root.find('span')
        self.release.unwrap(e)
        val = ET.tostring(root)
        self.assertEqual(val, '<p>beforekeep<span class="M=B">remove</span>after</p>')
        
    def test_unwrap_2(self):
        root = ET.XML('<p>before<span class="M=A">keep</span><span class="M=B">remove</span>after</p>')
        e=root.findall('span')
        self.release.unwrap(e[1])
        val = ET.tostring(root)
        self.assertEqual(val, '<p>before<span class="M=A">keep</span>removeafter</p>')
        
    def test_unwrap_3(self):
        root = ET.XML('<p>before<s>in</s><s>in2</s>after</p>')
        e=root.find('s')
        self.release.unwrap(e)
        val = ET.tostring(root)
        self.assertEqual(val, '<p>beforein<s>in2</s>after</p>')
        
    def test_unwrap_4(self):
        root = ET.XML('<p>before<s>in</s><s>in2</s>after</p>')
        e=root.findall('s')
        self.release.unwrap(e[1])
        val = ET.tostring(root)
        self.assertEqual(val, '<p>before<s>in</s>in2after</p>')
        
    def test_unwrap_5(self):
        root = ET.XML('<p>before<s>in</s><s>in2</s>after</p>')
        for e in root.findall('s'):
            self.release.unwrap(e)
        val = ET.tostring(root)
        self.assertEqual(val, '<p>beforeinin2after</p>')
        
