# -*- coding: utf-8 -*-
import os
import sys
import argparse
import datetime
from lxml import etree as ET
import logging
import csv
import copy

ns = {'namespaces':{'h':'http://www.w3.org/1999/xhtml'}}


class Report(object):
    def __init__(self):
        self.report = {
            'topics':{},
            'variables':{},
            'errors':[]
            }

    def dump(self):
        return str(self.report)

    def add_topic(self, topic, release = None):
        try:
            self.report['topics'][topic]
        except KeyError:
            self.report['topics'].update({topic:{'variables':{}}})
            
    def add_variable(self, varfile, varname, topic=None, lang=None, release=None, toc=None):
        self.add_topic(topic)
        try:
            self.report['variables'][varfile].add(varname)
        except KeyError:
            self.report['variables'].update({varfile:set([varname])})

        try:
            self.report['topic'][topic]['variables'][varfile].add(varname)
        except KeyError:
            self.report['variables'].update({varfile:set([varname])})

    def error(self, message, **kwargs):
        error = kwargs
        error.update({'message':message})
        self.report['errors'].append(error)
        
class Checker(object):
    def __init__(self, path):
        self.path = path
        settings = os.path.join(self.path, 'kolekti', 'settings.xml')
        self.settings = ET.parse(settings)
        self.report = Report()
        self.parser = ET.XMLParser(load_dtd = True)
        
    def _get_criteria_dict(self, profile):
        criteria = profile.xpath("criteria/criterion|/job/criteria/criterion")
        criteria_dict={}
        for c in criteria:
            criteria_dict.update({c.get('code'):c.get('value',None)})
        return criteria_dict

    def get_report_file(self, name):
        return os.path.join(self.path, "reporting", "%s_%s.csv"%(name, datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')))
    
    def subst_criteria(self, string, criteria):
        for criterion, val in criteria.iteritems():
            if val is not None:
                string=string.replace('{%s}'%criterion, val)
        return string
    
    def dump(self):
        print self.report.dump()

    exclude_releases = [
        "BRADY_EU_IM_KORA100_KORA250_VEGA_VERSION_06_09_2016",
        "BRADY_Help_Pour_formation",
        "BRADY_US_HLP_REPLY_ESPRIT_REPLY200",
        "LEADS_EU_Vega_Belex_Manuals_TRANSLATION_11_05_2016",
        "RMS_PatientManual_HotspotGPRS_japan",
        "RMS_PatientManual_MonitorPSTN_japan",
    ]
        
    def check_project(self):
        logging.error('not implemented')
        
    def check_toc(self, toc, pubparams):
        logging.error('not implemented')
        
    def check_release(self, release):
        logging.info('checking release %s',release)
        release_path = os.path.join(self.path, 'releases', release)
        langs = os.listdir(os.path.join(release_path, 'sources'))
        job_path = os.path.join(release_path, 'kolekti', 'publication-parameters', release + '_asm.xml')
        job = ET.parse(job_path)

        for lang in langs:
            if lang == "share":
                continue
            logging.info('checking language %s',lang)
            assembly_path = os.path.join(release_path, 'sources', lang, 'assembly', release + '_asm.html')
            assembly = ET.parse(assembly_path, self.parser)


                            
    def collect_variables(self):
        def job_variables(label, job):
            pass
        # collect variables in jobs
        job_variables = {}
        for job in sorted(os.listdir(os.path.join(self.path, 'kolekti', 'publication-parameters'))):
            job_path = os.path.join(self.path, 'kolekti', 'publication-parameters', job)
            xjob = ET.parse(job_path)
            for profile in job.xpath('/job/profiles/profile', **ns):
                label = profile.find('label').text
                criteria = self._get_criteria_dict(profile)
                directory = profile.find('').get('value','')
                variables = re.findall()
                job_variables[varref].append((job_path, label))
                
        # collect variables in topics
        topic_variables = {}
        for root, dirs, files in os.walk(os.path.join(self.path, "sources","en","topics")):
            for f in files:
                topic_dir = root.replace(self.path + "/", '')
                try:
                    topic = ET.parse(os.path.join(root, f), self.parser)
                except :
                    print "XML error %s/%s"%(topic_dir, f)
                    continue
                for var in topic.xpath('//h:var',**ns):
                    try:
                        topic_variables[var.get('class')].append((topic_dir, f))
                    except KeyError:
                        topic_variables[var.get('class')] = [(topic_dir, f)]
        print topic_variables.keys()
        
        # collect variables in releases
        release_variables = {}
        for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
            if release in self.exclude_releases:
                continue
            release_path = os.path.join(self.path, 'releases', release)
            job_path = os.path.join(release_path, 'kolekti', 'publication-parameters', release + '_asm.xml')
            if not os.path.exists(job_path):
                continue
            release_variables.update({release: collect_release_variables(release)})

    def collect_release_variables(self, release):
        release_path = os.path.join(self.path, 'releases', release)
        job_path = os.path.join(release_path, 'kolekti', 'publication-parameters', release + '_asm.xml')

        job = ET.parse(job_path)
        langs = os.listdir(os.path.join(release_path, 'sources'))
        for profile in job.xpath("/job/profiles/profile"):
            criteria = self._get_criteria_dict(profile)
            criteria.update({'LANG':lang})

            for variable in assembly.xpath('//h:var', **ns):
                topic = variable.xpath("string(ancestor::h:div[@class='topic']/h:div[@class='topicinfo']/h:p[span[@class='infolabel'] = 'source']/h:span[@class='infovalue'])", **ns)
                logging.debug('variable: %s', ET.tostring(variable))
                    
                if ':' in variable.get('class'):
                    varfile, varname = variable.get('class').split(':')
                    
                    self.report.add_variable(self.subst_criteria(varfile, criteria), self.subst_criteria(varname, criteria), topic, lang)
                else:
                    if variable.get('class') in criteria.keys():
                        pass
                    else:
                        self.report.error('Var references undefined criteria', topic=topic, lang=lang, profile=profile, assembly=assembly)

        for profile in job.xpath("/job/profiles/profile"):
            pass
                            
    def check_releases_criteria(self):
        for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
            if release in self.exclude_releases:
                continue
            release_path = os.path.join(self.path, 'releases', release)
            job_path = os.path.join(release_path, 'kolekti', 'publication-parameters', release + '_asm.xml')
            if not os.path.exists(job_path):
                continue
            job = ET.parse(job_path)
            langs = os.listdir(os.path.join(release_path, 'sources'))
            
            for profile in job.xpath("/job/profiles/profile"):
                label = profile.find('label').text
                criteria = self._get_criteria_dict(profile)
                for key, val in criteria.iteritems():
                    if len(self.settings.xpath('/settings/criteria/criterion[@code=$code]/value[text()=$value]',code=key, value=val )) == 0:
                        print '\t'.join(["missing",release,label,key,val])

        
# ==================================================================================
# correction des identifiants dans les releases

    def fix_assemblies_id(self):
        with open(self.get_report_file("assemblies_id"), "wb") as csvfile:
            reswriter = csv.writer(csvfile, delimiter=',')
            for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
                if release in self.exclude_releases:
                    continue
                release_path = os.path.join(self.path, 'releases', release)  
                for lang in os.listdir(os.path.join(release_path, 'sources')):
                    modified = False
                    if lang == "share":
                        continue
                    assembly_path = os.path.join(release_path, 'sources', lang, 'assembly', release + '_asm.html')
                    try:
                        assembly = ET.parse(assembly_path, self.parser)
                    except:
                        # print "could not parse", assembly_path
                        continue
                    for elt in assembly.xpath('//ancestor::h:div[@class="topic"]//*[@id]', **ns):
                        elt_id = elt.get('id')
                        mod_id = elt.xpath('ancestor::h:div[@class="topic"]', **ns)[0].get('id')
                        if elt_id.split('_', 0) == mod_id:
                            continue
                        elt.set('id', mod_id + "_" + elt_id)
                        modified = True
                        print elt.get('id'), mod_id

                    if modified:
                        reswriter.writerow([release, lang])
                        with open(assembly_path, "wb") as f: 
                            f.write(ET.tostring(assembly, encoding = "utf-8"))
                            
# ==================================================================================
# correction des meta des topics inclus dans les assemblages
                
    def fix_assemblies_mod_sources(self):
        with open(self.get_report_file("assemblies_mod_sources"), "wb") as csvfile:
            reswriter = csv.writer(csvfile, delimiter=',')
            for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
                if release in self.exclude_releases:
                    continue
                release_path = os.path.join(self.path, 'releases', release)  
                for lang in os.listdir(os.path.join(release_path, 'sources')):
                    modified = False
                    if lang == "share":
                        continue
                    assembly_path = os.path.join(release_path, 'sources', lang, 'assembly', release + '_asm.html')
                    try:
                        assembly = ET.parse(assembly_path, self.parser)
                    except:
                        # print "could not parse", assembly_path
                        continue
            
                    for link in assembly.xpath('//h:div[@class="topicinfo"]//h:a', **ns):
                        metalist = link.xpath('ancestor::h:div[@class="topicinfo"]',**ns)[0]
                        metap = link.xpath('ancestor::h:p[1]',**ns)[0]
                        metaname = metap.xpath('h:span[@class="infolabel"]', **ns)[0]
                        if link.get('href')[:7] == 'file://' and metaname.text == "source":
                            newref = '/sources/' + link.get('href').split('/sources/')[1]
                            newmeta = copy.deepcopy(metap)
                            metalist.append(newmeta)
                            newmeta.xpath('.//h:a', **ns)[0].text = newref
                            newmeta.xpath('.//h:a', **ns)[0].set('href', newref)
                            metaname.text = "localsource"
                            modified = True
                    if modified:
                        reswriter.writerow([release, lang])
                        with open(assembly_path, "wb") as f: 
                            f.write(ET.tostring(assembly, encoding = "utf-8"))


# ===================================================================================
# controle des liens
                            
    def resolve_ref(self, sourcepath, ref):
        if '/' in ref:
            if ref[0] == "/":
                return os.path.join(self.path, *ref.split('/')[1:])
            else:
                return os.path.join(self.path, sourcepath, *ref.split('/'))
        else:
            return os.path.join(self.path, sourcepath, ref)

    mod_target_xpath = '//h:div[@class="topic"][h:div[@class="topicinfo"]/h:p[h:span[@class="infolabel"] = "source"]/h:span[@class="infovalue"]/h:a[@href=$href]]'
        
    def source_link_guess(self, source_dir, href):
        link = None
        if href[-4:] == '.xht':
            href = href[:-4] + '.html'
            if os.path.exists(self.resolve_ref(source_dir, href)):
                return href.replace('.xht','.html')

        if '_HLP_' in href:
            href = href.replace('_HLP_', '_HELP_TACHY_')
            if os.path.exists(self.resolve_ref(source_dir, href)):
                return href

        if '_PARAM_' in href:
            href = href.replace('_PARAM_', '_HELP_TACHY_')
            if os.path.exists(self.resolve_ref(source_dir, href)):
                return href
            

    def assembly_link_guess(self, assembly, href, lang):
        link = None
        
        if href[-4:] == '.xht':
            href = href[:-4] + '.html'
            if assembly.xpath(self.mod_target_xpath, href = href, **ns):
                return href
            
        if '{LANG}' in href:
            href = href.replace('{LANG}', 'en')
            if assembly.xpath(self.mod_target_xpath, href = href, **ns):
                return href
            
        if '_HLP_' in href:
            href = href.replace('_HLP_', '_HELP_TACHY_')
            if assembly.xpath(self.mod_target_xpath, href = href, **ns):
                return href

        if '_PARAM_' in href:
            href = href.replace('_PARAM_', '_HELP_TACHY_')
            if assembly.xpath(self.mod_target_xpath, href = href, **ns):
                return href
            
        if '/sources/'+lang in href:
            href = href.replace('/sources/'+lang, '/sources/en')
            if assembly.xpath(self.mod_target_xpath, href = href, **ns):
                return href

        return link

    def fix_links(self):
        self.fix_links_topics()
        self.fix_links_releases()

    def fix_links_topics(self):
        with open(self.get_report_file('links_topics'), "wb") as csvfile:
            reswriter = csv.writer(csvfile, delimiter=',')
            for root, dirs, files in os.walk(os.path.join(self.path, "sources","en","topics")):
                for f in files:
                    topic_dir = root.replace(self.path + "/", '')
                    statuses = self.fix_links_topic(root, f)
                    if len(statuses):
                        reswriter.writerow(['/'.join([topic_dir, f])])
                        for st in statuses:
                            reswriter.writerow([''] + st)

    def fix_links_releases(self):               
        with open(self.get_report_file("links_releases"), "wb") as csvfile:
            reswriter = csv.writer(csvfile, delimiter=',')
            for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
                if release in self.exclude_releases:
                    continue
                statuses = self.fix_links_release(release)
                reswriter.writerow([release])
                if len(statuses):
                    for st in statuses:
                        reswriter.writerow([''] + st)
            
    def fix_links_release(self, release):
        res = []
        release_path = os.path.join(self.path, 'releases', release)  
        for lang in os.listdir(os.path.join(release_path, 'sources')):
            lres = []
            if lang == "share":
                continue
            assembly_path = os.path.join(release_path, 'sources', lang, 'assembly', release + '_asm.html')
            try:
                assembly = ET.parse(assembly_path, self.parser)
            except:
#                print "could not parse", assembly_path
                lres.append([lang, 'E','parse error', assembly_path])
                continue
 #           print assembly_path
            assembly_modified = False
            for link in assembly.xpath('//h:a', **ns):
                link_modified = False
                fix_href = None
                if len(link.xpath('ancestor::h:div[@class="topicinfo"]', **ns)):
                    continue
                if link.get('rel',None) == 'kolekti:topic:error':
                    lres.append([lang, "E", "topic inclusion error", link.get('href')])
#                    print "topic inclusion error", link.get('href')
                    continue
                mod_src = link.xpath('ancestor::h:div[@class="topic"]/h:div[@class="topicinfo"]/h:p[h:span[@class="infolabel"] = "source"]/h:span[@class="infovalue"]/h:a', **ns)[0]
                src_ref = mod_src.get('href')
                href = link.get('href')

                if href.startswith('http://') or href.startswith('https://'):
                    continue
                
                try:
                    resource, idl = href.split('#')
                except ValueError:
                    resource = href
                    idl = None

                if resource == "":
                    resource = src_ref
                    newref = ""
                elif '/' in resource:
                    pass
                else:
                    newref = resource
                    resource = mod_src.get('href').rsplit('/', 1)[0] + "/" + resource
                    link_modified = True
                    
                mod_target = assembly.xpath(self.mod_target_xpath, href = resource, **ns)
                if len(mod_target) == 0:                    
                    fix_href = self.assembly_link_guess(assembly, resource, lang)
                    if fix_href is None:
                        lres.append([lang, "E", "unresolved link", href, "", src_ref])
                        continue
                    else:
                        if idl is None:
                            mod_target = assembly.xpath(self.mod_target_xpath, href = fix_href, **ns)
                            newref = resource = fix_href
                            link_modified = True
                        
                mod_target = assembly.xpath(self.mod_target_xpath, href = resource, **ns)                        
                if len(mod_target) == 1:
                    target_id = mod_target[0].get('id')
                    if idl is not None:
                        target_elt = mod_target[0].xpath('.//*[@id=$eid]', eid = idl)
                        if len(target_elt) == 0:
                            target_elt = mod_target[0].xpath('.//*[@id=$eid]', eid = target_id + '_' + idl)
                            if len(target_elt) == 0:
                                lres.append([lang, "E", "ID not found", href, "", src_ref])
                                continue
                            else:
                                idl = target_id + '_' + idl
                                link_modified = True            
                                
                if link_modified:
                    assembly_modified = True
                    if idl is None:
                        lres.append([lang, "F", "", href, fix_href, src_ref])
                        link.set('href', newref)
                    else:
                        lres.append([lang, "F", "", href, newref + "#" + idl, src_ref])
                        link.set('href', newref + "#" + idl)
                        
            if assembly_modified:
                with open(assembly_path, "wb") as afile:
                    afile.write(ET.tostring(assembly, encoding = "utf-8")) 
            res = res + lres
            displ = lres #[r for r in lres if r[1] == "E"]
            if len(displ):
                print assembly_path
                for l in displ:
                    print l
                
        return res
            
    def fix_links_topic(self, root, f):            
        res = []
        modified = False
        try:
            topic = os.path.join(root,f)
            topic_dir = root.replace(self.path + "/", '')
            xtopic = ET.parse(topic, self.parser)
            links = xtopic.xpath('//h:a', **ns)
        except:
            print "could not parse", topic_dir, topic
            return [['E','parse error']]
        
        for link in links:
            fix = None
            href = link.get('href')
            try:
                resource, idl = href.split('#')
            except ValueError:
                resource = href
                idl = None
                
            try:
                if resource == '':
                    target = topic
                    xtarget = xtopic
                elif resource.startswith("http://") or resource.startswith("https://"):
                    target = href
                    xtarget = None
                    continue
                else:
                    target = self.resolve_ref(topic_dir, resource)
                    xtarget = ET.parse(target, self.parser)
                           
            except IOError:
                fix = self.source_link_guess(topic_dir, resource)
                if fix is None:
                    res.append(['E', 'target topic not found', href])
                    continue
                xtarget = ET.parse(self.resolve_ref(topic_dir, fix), self.parser)
                if idl:
                    fix = fix + "#" + idl
            if idl is None:
                pass
            else:
                if len(xtarget.xpath('//@id[. = $idl]', idl = idl, **ns)) != 1:
                    res.append(['E', 'anchor not found', href])
                    continue
            
            if not fix is None:
                link.set('href',fix)
                res.append(['F', '', href, fix])
                modified = True
        if modified:
             with open(topic, "wb") as topicfile:
                 topicfile.write(ET.tostring(xtopic, encoding = "utf-8"))
        return res



#   ======================================================================================
#   Traitement des fichiers models (livanova)


    models_profiles = {
        "IM": {
            "IM_Rev":"INDICE",
            "IM_RadicalRef":None,
            "IM_Year":"ANNEE",
            "IM_Month":"MOIS",
            "ProductName":None,
            "ProductSHORTName":None,
            "ProductCode":None,
            },
        "HLP": {
            "HELP_Rev":"INDICE",
            "HELP_RadicalRef":None,
            "HELP_Year":"ANNEE",
            "HELP_Month":"MOIS",
            "ProductName":None,
            "ProductSHORTName":None,
            "ProductCode":None,
            "HLP_filename":None,
            "CHM_filename":None,
            }
        }
        
    models_variables = {
        "IM":[
            "ProductName",
            "ProductSHORTName",
            "ProductCode",
            "IM_Rev",
            "IM_RadicalRef",
            "IM_Year",
            "IM_Month",
            ],
        "HLP": [
            "ProductName",
            "ProductSHORTName",
            "ProductCode",
            "HELP_Rev",
            "HELP_RadicalRef",
            "HELP_Year",
            "HELP_Month",
            "HLP_filename",
            "CHM_filename",
            ]
        }

    def collect_product_names(self):
        for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
            if release in self.exclude_releases:
                continue
            release_path = os.path.join(self.path, 'releases', release)
            job_path = os.path.join(release_path, 'kolekti', 'publication-parameters', release + '_asm.xml')
            job = ET.parse(job_path)
            if not os.path.exists(job_path):
                continue
            print release
            langmodels = {}
            textes_auto_vars = {}
            for lang in os.listdir(os.path.join(release_path, 'sources')):
                if lang == "share":
                    continue
                try:
                    textes_auto_vars[lang] = ET.parse(os.path.join(release_path, 'sources', lang, 'variables', 'TextesAuto.xml'))
                except:
                    print('unable to parse TextesAuto for %s'%lang)
                    continue
            for profile in job.xpath("/job/profiles/profile"):
                label = profile.find('label').text
                criteria = self._get_criteria_dict(profile)
                statuses = []
                if "M" in criteria.keys():
                    model = criteria['M']
                    langmodels[model] = {}
                    for lang in os.listdir(os.path.join(release_path, 'sources')):
                        if lang == "share" or not (lang in textes_auto_vars.keys()) :
                            continue
                        productname = textes_auto_vars[lang].xpath('string(/variables/variable[@code=$code]/value[crit[@name="ZONE"][@value=$zone]]/content)',code = criteria['M'], zone = criteria['ZONE'])
                        try:
                            langmodels[model][productname].append(lang)
                        except KeyError:
                            langmodels[model][productname]=[lang]
                    if len(langmodels[model].keys()) != 1:
                        print "ERROR with profile %s, lang models are %s"%(label, str(langmodels[model]))

                else:
                    print "no model"
                

        
    def guess_kind(self, release):

        imlabels = ['_IM_', 'ImplantManual','Manuals','Vega_only','RMS_EUR_HotspotGPRS_Translation_060416']
        for p in imlabels :
            if p in release:
                return 'IM'
        return 'HLP'


    def get_models_value(self, criteria, code, release):
        if code == "ProductName":
            get_same_lang_variable("TextesAuto") 
    
    def check_releases_models(self):
       
        with open(self.get_report_file("release_models"), "wb") as csvfile:
            info = csv.writer(csvfile, delimiter=',')
            info.writerow([
                "release",
                "zone / profile",
                "kind / model",
                "model file in release",
                "model file in sources",
                "ProductName",
                "ProductSHORTName",
                "ProductCode",
                "HELP/IM_Rev",
                "HELP/IM_RadicalRef",
                "HELP/IM_Year",
                "HELP/IM_Month",
                "HLP_filename",
                "CHM_filename"
                ])
            for release in sorted(os.listdir(os.path.join(self.path, 'releases'))):
                if release in self.exclude_releases:
                    continue
                release_path = os.path.join(self.path, 'releases', release)
                job_path = os.path.join(release_path, 'kolekti', 'publication-parameters', release + '_asm.xml')
                if not os.path.exists(job_path):
                    continue
                
                job = ET.parse(job_path)
                kind = self.guess_kind(release)
                
                print release
                langs = os.listdir(os.path.join(release_path, 'sources'))
                zone = job.xpath('string(/job/criteria/criterion[@code="ZONE"]/@value)')
                info.writerow([release, zone, kind])
                for profile in job.xpath("/job/profiles/profile"):
                    label = profile.find('label').text
                    criteria = self._get_criteria_dict(profile)
                    statuses = []
                    if "M" in criteria.keys():
                        model = criteria['M']
                        statuses.append(model)
                        xmodel = srcxmodel = None
                        if os.path.exists(os.path.join(release_path, 'sources', 'share', 'variables', 'models', model+'.xml')):
                            statuses.append("Y")
                            xmodel = ET.parse(os.path.join(release_path, 'sources', 'share', 'variables', 'models', model+'.xml'))
                        else:
                            statuses.append("N")
                        if os.path.exists(os.path.join(self.path, 'sources', 'share', 'variables', 'models', model+'.xml')):
                            statuses.append("Y")
                            srcxmodel = ET.parse(os.path.join(self.path, 'sources', 'share', 'variables', 'models', model+'.xml'))
                        else:
                            statuses.append("N")

                                
                        for k in self.models_variables[kind]:
                            code = k
                            v = self.models_profiles[kind][k]
                            if xmodel is None :
                                mvv= ""
                            else:
                                mvv = xmodel.xpath('string(/variables/variable[@code=$code]/value[crit[@name = "ZONE"][@value = $zone]]/content)', code = code, zone = zone)
                            if mvv != "" and mvv !="xxNAxx" and mvv != "xxTBDxx":
                                statuses.append("%s [R]"%mvv)                                
                            elif (v is not None) and (v in criteria.keys()) and (criteria[v] != ''):
                                statuses.append("%s [C]"%criteria[v])
                            else:
                                if srcxmodel is None :
                                    smvv = ""
                                else:
                                    smvv = srcxmodel.xpath('string(/variables/variable[@code=$code]/value[crit[@name = "ZONE"][@value = $zone]]/content)', code = code, zone = zone)      
                                if smvv == "" or smvv == "xxNAxx" or smvv == "xxTBDxx":
                                    statuses.append("ERROR : not found")
                                    # val, where = self.get_models_value(criteria, code, release)
                                    # if val is None:
                                    #     statuses.append("not found")
                                    # else:
                                    #     statuses.append("%s [%s]"%val, where)
                                else:
                                    statuses.append("%s [S]"%smvv)
                    else:
                        statuses.append("Critere M non défini")

                    info.writerow(["",label]+ statuses)
            

                            
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Kolekti Analysis.')
    parser.add_argument('--project', help="project directory")
    parser.add_argument('--log', help="logging level")
    parser.add_argument('-c', "--custom",  help="run custom command")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--release', help="release to analyse")
    tocgroup = group.add_argument_group('tocs')
    tocgroup.add_argument('--toc', help="toc to analyse")
    tocgroup.add_argument('--pubparam', help="publication parameters to apply")

    args = parser.parse_args()

    if args.log:
        numeric_level = getattr(logging, args.log.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError('Invalid log level: %s' % loglevel)
        logging.basicConfig(level=numeric_level)
            
    
    if args.project is None:
        project = os.getcwd()
    else:
        project = args.project
    checker = Checker(project)

    if args.custom:
        try:
            cmd = getattr(checker, args.custom)
            cmd()
        finally:
            checker.dump()
        sys.exit(0)
        
    if args.release:
        try:
            checker.check_release(args.release)
        finally:
            checker.dump()
        sys.exit(0)
    if args.toc:
        checker.check_toc(args.toc, args.pubparam)
        sys.exit(0)

    checker.check_project()
        
