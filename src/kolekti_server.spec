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
          console=True )


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

data_files = [('LICENSE','LICENCE','DATA'),
              ('kolekti.ico','kolekti.ico','DATA'),
              (os.path.join('kolekti','pubscripts.xml'),os.path.join('kolekti','pubscripts.xml'),'DATA'),
              ] + extra_datas('kolekti/xsl') + extra_datas('kolekti/plugins/_WebHelp5')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               data_files,
               strip=None,
               upx=True,
               name='kolekti_server')
