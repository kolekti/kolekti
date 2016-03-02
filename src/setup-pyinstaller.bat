@set BUILDPATH=F:\Bureau\kolekti\sources\0.7\kolekti\src
@set PYTHONPATH=%BUILDPATH%\kolekti_server;%BUILDPATH%
@rem rd build /s /q
@rem rd dist /s /q
@rem svn export --force --username=waloo http://beta.kolekti.net/svn/Exemple_PDFs dist\Exemple_PDF
@rem svn export --force --username=waloo http://beta.kolekti.net/svn/Exemple_WebhelpPersonnalisable dist\Exemple_Webhelp
@rem svn export --force --username=waloo http://beta.kolekti.net/svn/quickstart07 dist\Project_template


@rem pyinstaller -w --name kolekti_server kolekti_server\server.py
@pyinstaller -y -w  kolekti_server.spec
@"C:\Program Files\Inno Setup 5\ISCC.exe" %BUILDPATH%\setup.iss

@for /f "tokens=1-4 delims=/ " %%G in ('date /t') do set mmddyyyy=%%I_%%H_%%G

@copy %BUILDPATH%\Output\setup-kolekti_0.7.1.exe F:\kolekti\setup-kolekti_0.7_%mmddyyyy%.exe

