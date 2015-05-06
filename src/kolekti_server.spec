# -*- mode: python -*-
from glob import glob

a = Analysis(['kolekti_server\\server.py'],
             pathex=['C:\\Users\\waloo\\Desktop\\kolekti\\kolekti\\src'],
             hiddenimports=['htmlentitydefs',
                            'HTMLParser',
                            'markupbase',
                            'django.contrib.sessions.serializers',
                            'kserver.templatetags.ostags',
                            'kserver.templatetags.difftags',
                            'kserver.templatetags.timetags',
                            'kolekti',
                            'kolekti.plugins',
                            'kolekti.plugins.pluginBase',
                            'kolekti.plugins.WebHelp5',
                            ],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='kolekti_server.exe',
          debug=False,
          strip=None,
          upx=True,
          console=False, 
          icon='kolekti.ico')


#def extra_plugins():
#    for f on os.listdir('kolekti/plugins'):
#        if os.path.isfile(f):
#            if os.path.splitext(f) == ".pyc"

def extra_datas(mydir):
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append(d)
            rec_glob("%s/*" % d, files)
    files = []
    rec_glob("%s/*" % mydir, files)
    extra_datas = []
    for f in files:
        extra_datas.append((f, f, 'DATA'))
    return extra_datas

def extra_plugins():
    myplugins = ['WebHelp5','pluginBase']
    def rec_glob(p, files):
        import os
        import glob
        for d in glob.glob(p):
            if os.path.isfile(d):
                files.append((d,d,'DATA'))
            rec_glob("%s/*" % d, files)

    res = []
    for plugin in myplugins:
        f = os.path.join('kolekti','plugins', plugin)
        res.append((f+'.py', f+'.py','DATA'))
        res.append((f+'.pyc', f+'.pyc','DATA'))
        if os.path.exists(os.path.join('kolekti','plugins', "_%s" % plugin)):

            rec_glob("kolekti/plugins/_%s/*"%plugin, res)  
    return res


data_files = [('LICENSE','LICENCE','DATA'),
              ('kolekti.ico','kolekti.ico','DATA'),
              ('db.sqlite3',os.path.join('kolekti_server','db.sqlite3.ref'),'DATA'),
              (os.path.join('kolekti','pubscripts.xml'),os.path.join('kolekti','pubscripts.xml'),'DATA'),
              ] + extra_datas('kolekti/xsl') + extra_plugins()

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               data_files,
               strip=None,
               upx=True,
               name='kolekti_server')
