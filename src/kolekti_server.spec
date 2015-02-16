# -*- mode: python -*-
a = Analysis(['kolekti_server\\server.py'],
             pathex=['C:\\Users\\waloo\\Desktop\\kolekti\\kolekti\\src'],
             hiddenimports=['htmlentitydefs','HTMLParser','markupbase','django.contrib.sessions.serializers'],
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

data_files = [('LICENSE','LICENCE','DATA'),
              ('kolekti.ico','kolekti.ico','DATA')
              ]

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               data_files,
               strip=None,
               upx=True,
               name='kolekti_server')
