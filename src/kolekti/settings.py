import os
import logging
import ConfigParser

userdir = os.path.expanduser("~")

default_setting ={
    "InstallSettings":{
        "projects_dir":os.path.join(userdir,'kolekti','projects'),
        "base":os.path.join(userdir,'kolekti','projects','quickstart'),
        "active_project":'quickstart'
        },
    "draft":{},
    "release":{},
    "publish":{},
    "varods":{},
    "varxml":{},
    "index":{},
    "search":{},
    "sync":{},
}


def settings(settings_file=None):
    config = ConfigParser.SafeConfigParser()
    try:
        # get config from argument (command line)
        config.read(settings_file)
    except:
        # get config from userdir
        settings_file = os.path.join(userdir,".kolekti.ini")
        try:
            config.read(settings_path)
        except:
            # get config from /etc/koleti.ini
            try:
                config.read('/etc/kolekti.ini')
            except:
                # get config from execution directory
                try:
                    config.read("kolekti.ini")
                except:
                    return default_settings
    
    settings_dict = {}
    for section in default_settings:
        setings_dict.update({section:{}})
        try:
            entries = dict(config.items(section))
        except ConfigParser.NoSectionError:
            entries = {}
        for entry in default_settings.get(section):
            settings_dict.get(section).update({entry:entries.get(entry, default_settings.get(entry))})

    return settings_dict


