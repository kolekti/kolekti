from lxml import etree as ET
import logging

class ConditionsError(Exception):
    pass

class ConditionParseError(Exception):
    pass

class ConditionsParser(object):
    def __init__(self, condstring):
        try:
            condstring = condstring.replace(' ','')
            self.condexps = condstring.split(';')
            self.parsed = {}
            for ce in self.condexps:
                crit, valexp = ce.split('=')
                isexc =  valexp[0] == '\\'
                if isexc:
                    valexp = valexp[1:]

                self.parsed.update({crit:{
                    'vals':valexp.split(','),
                    'exc': isexc
                }})
        except:
            raise ConditionParseError
        
    def validate(self, settings):
        for crit, critdef in self.parsed.iteritems():
            if not settings.xpath('/settings/criteria/criterion[@name="%s"]'%crit):
                logging.error('undefined criteria %s'%crit)
                raise ConditionsError
            for val in critdef.get('vals'):
                if not settings.xpath('/settings/criteria/criterion[@name="%s"]/value[.="%s"]'%(crit, val)):
                    logging.error('undefined value %s for criteria %s'%(val,crit))
                    raise ConditionsError


    def evaluate(self, xcriteria):
        for criterion in xcriteria:
            cd = self.parsed.get(criterion.get('name'), None)
            if cd is not None:
                if criterion.get('value') in cd.get('vals'):
                    if cd.get('exc'):
                        return False
                else:
                    if not cd.get('exc'):
                        return False

        return True

import unittest
class TestConditions(unittest.TestCase):
    settings = ET.XML("""<settings><criteria><criterion name="A"><value>A1</value><value>A2</value></criterion><criterion name="B"><value>B1</value><value>B2</value></criterion></criteria></settings>""")
    profile = ET.XML("""<criteria><criterion name="A" value="A1"/><criterion name="B" value="B1"/></criteria>""")
    exp_true= ["A=A1","A=A1;B=B1","A=\A2","A=A1;B=\B2"]
    exp_false= ["A=A2","A=A1;B=B2","A=\A1","A=A1;B=\B1"]
    exp_err = ["C=C1","A=A1,A2;C=C1","A=A3"]
    exp_syntaxerr = ["C=C1","A=A1,A2;C=C1","A=A3"]

    def test_true_expressions(self):
        for e in self.exp_true:
            p = ConditionsParser(e)
            self.assertTrue(p.evaluate(self.profile))

    def test_false_expressions(self):
        for e in self.exp_false:
            p = ConditionsParser(e)
            self.assertFalse(p.evaluate(self.profile))

    def test_error_expressions(self):
        for e in self.exp_err:
            with self.assertRaises(ConditionsError):
                p = ConditionsParser(e)
                p.validate(self.settings)
                
if __name__ == "__main__":
    unittest.main()
