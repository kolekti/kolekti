import os
import logging
import ConfigParser

userdir = os.path.expanduser("~")

default_settings ={
    "InstallSettings":{
        "projectspath":os.path.join(userdir,'kolekti','projects'),
#        "base":os.path.join(userdir,'kolekti','projects','quickstart'),
        "active_project":'quickstart'
        },
}


def settings(settings_file=""):
    config = ConfigParser.SafeConfigParser(dict_type=dict)

    config_files =[    
        settings_file,
        os.path.join(userdir,".kolekti.ini"),
        '/etc/kolekti.ini',
        'kolekti.ini']

    read_files = config.read(config_files)

    for section in default_settings:
        if not config.has_section(section):
            config.add_section(section)
        for option, value in default_settings.get(section).iteritems():
            if not config.has_option(section,option):
                config.set(section,option,value)
    settings_dict = {}
    for section in config.sections():  
        settings_dict.update({section:dict(config.items(section))})

    return settings_dict


