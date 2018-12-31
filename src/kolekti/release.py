# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2019 Stéphane Bonhomme (stephane@exselt.com)

""" Release utilities"""

import os
import copy
import logging
from lxml import etree as ET


logger = logging.getLogger("kolekti." + __name__)


class Release(object):
    """ Release releative functions
    - Copying release
    - Renaming
    - filtering assemblies
    """
    def __init__(self, user, project, release):
        self._basepath = basepath
        self._release = release
        self._xmlparser = ET.XMLParser(load_dtd = True)

        
    def __pathchars(self, s):
        intab = """?'"<>\/|"""
        outtab = "!_______"
        for i,o in zip(intab, outtab):
            s = s.replace(i,o)
        return s
        
    def _syspath(self, path):
        # returns os absolute path from relative path
        pathparts = [self.__pathchars(p) for p in path.split('/') if p!='']
        return os.path.join(self._basepath, *pathparts)

        
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
            print '{} [{}] modified'.format(self._release, lang)
            self.xwrite(assembly, '/sources/{}/assembly/{}_asm.html'.format(lang, self._release))

    def apply_filters_element(self, elt, profile_filter=True, assembly_filter=False, setPI = False, remove_conditional_elements = ['div', 'span']):
#        assert(not elt.get('class') is None)

        logger.debug('condition')
        logger.debug(elt.get('class'))
        tag = elt.xpath('string(local-name())')
        logger.debug(tag)
        logger.debug(self.job_criteria())
        
        if assembly_filter:
            evalc = self.eval_condition(self.job_criteria(), elt.get('class'))
            if evalc in [True, None]:
                if evalc and tag in remove_conditional_elements:
                    self.unwrap(elt)
                return False
            
        if profile_filter:
            for profile in self.profiles_criteria():
                evalc = self.eval_condition(profile, elt.get('class'))
                if evalc in [True, None]:
                    if evalc and tag in remove_conditional_elements:
                        self.unwrap(elt)
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
        
