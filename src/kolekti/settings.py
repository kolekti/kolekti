import os
import logging
import ConfigParser

userdir = os.path.expanduser("~")

if os.sys.platform[:3] == "win":
    appdatadir = os.path.join(os.getenv("APPDATA"),'kolekti')
    usercfgfile = "kolekti.ini"
else:
    appdatadir = userdir
    usercfgfile = ".kolekti"

default_settings ={
    "InstallSettings":{
        "projectspath":os.path.join(userdir,'kolekti-projects'),
        "kolektiversion":"0.7",
        },
}


def settings(settings_file=""):
    config = ConfigParser.SafeConfigParser(dict_type=dict)

    config_files =[
        settings_file,
        'kolekti.ini',
        os.path.join(appdatadir,usercfgfile),
        '/etc/kolekti.ini',
        ]

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


