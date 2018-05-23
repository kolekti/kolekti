import sys
import os
from lxml import etree as ET

ns = {'namespaces':{'xsl':'http://www.w3.org/1999/XSL/Transform'}}

parser = ET.XMLParser(remove_blank_text=True)

def add_label(path, variable, label, lang):
#    print "addlabel", path, variable, label, lang    
    try:
        labels = ET.parse(path, parser)
    except IOError:
        labels = ET.ElementTree(ET.XML('<variables><critlist>:LANG</critlist></variables>'))
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
    try:
        varelt = labels.xpath('//variable[@code="%s"]'%variable)[0]
    except IndexError:
        varelt = ET.SubElement(labels.getroot(), "variable")
        varelt.set('code', variable)

    try:
        value = varelt.xpath('value[crit[@name="LANG"][@value="%s"]]/content'%lang)[0]
        if value.text != label:
            print(path)
            print('replacing var %s; lang %s : %s -> %s'%(variable, lang, value.text, label))
        
    except IndexError:
        valelt = ET.SubElement(varelt, 'value')
        ET.SubElement(valelt,'crit',  attrib={'name': 'LANG', 'value':lang})
        value = ET.SubElement(valelt,'content')
    value.text = label

    labels.write(path, encoding="utf-8", pretty_print=True)
        
def convert_webhelp_custom(path):
    genpath = os.path.join(path, "kolekti","publication-templates", "WebHelp5", "xsl", "generate.xsl")
    try:
        generate = ET.parse(genpath)
    except IOError:
#        print("no custom WebHelp generator")
        return
    except:
        print('could not parse %s'%genpath)
        return
    try:
        trfile = generate.xpath("//xsl:variable[@name='translationfile']", **ns)[0]
    except IndexError:
        return
    
    for e in trfile :
        trfile.remove(e)
    trfile.text = None
    ET.SubElement(trfile, '{%s}text'%(ns['namespaces']['xsl'],)).text = "/kolekti/publication-templates/share/labels"
    generate.write(genpath, encoding = 'utf-8')
    
def convert_webhelp_labels(path):
    if not os.path.exists(os.path.join(path, "sources")):
        return
    for lang in os.listdir(os.path.join(path, "sources")):    
        labelspathes = [
            os.path.join(path, "sources", lang, "variables", "WebHelp5_labels.xml"),
            os.path.join(path, "kolekti", "publication-templates", "WebHelp5", "variables", "labels.xml"),
            ]
        for labelspath in labelspathes:
            try:
    #            print labelspath
                xvar = ET.parse(labelspath)
                for var in xvar.xpath('/variables/variable/value'):
                    varlang = var.xpath('string(crit[@name="LANG"]/@value)').lower()
                    if varlang == "":
                        varlang = lang
                    lblpath = os.path.join(path, "kolekti","publication-templates", "share", "labels.xml")
                    varname = var.xpath('string(ancestor::variable/@code)')
                    label = var.xpath('string(content)')
                    add_label(lblpath, varname, label, varlang)
            except IOError:
                pass
#            print("no WebHelp labels")
            
def convert_labels(path):
    labelspath = os.path.join(path, "kolekti", "publication-templates", "share", "variables", "labels.xml")
    try:
        xvar = ET.parse(labelspath)
        for var in xvar.xpath('/variables/variable/value'):
            varlang = var.xpath('string(crit[@name="LANG"]/@value)')
            lblpath = os.path.join(path, "kolekti","publication-templates", "share", "labels.xml")
            varname = var.xpath('string(ancestor::variable/@code)')
            label = var.xpath('string(content)')
            add_label(lblpath, varname, label, varlang)
    except IOError:
        pass
#        print("no shared labels variable file")
        

if __name__ == "__main__":

    project_path = sys.argv[1]
    releases = os.listdir(os.path.join(project_path, 'releases'))
    for release in releases:
        release_path = os.path.join(project_path, 'releases', release)
        
#        print release_path
        convert_webhelp_custom(release_path)
        convert_webhelp_labels(release_path)
        convert_labels(release_path)
    convert_webhelp_custom(project_path)        
    convert_webhelp_labels(project_path)
    convert_labels(project_path)
