@rem svn export --force --username=waloo http://beta.kolekti.net/svn/Exemple_PDFs dist\Exemple_PDF
@rem svn export --force --username=waloo http://beta.kolekti.net/svn/Exemple_WebhelpPersonnalisable dist\Exemple_Webhelp
@rem svn export --force --username=waloo http://beta.kolekti.net/svn/quickstart07 dist\Project_template

@set DJANGO_SETTINGS_MODULE=kolekti_server.settings
@pyinstaller -y -w --log-level DEBUG kolekti_server.spec 2>build.log 
@"C:\Program Files\Inno Setup 5\ISCC.exe" %BUILDPATH%\setup.iss

@for /f "tokens=1-4 delims=/ " %%G in ('date /t') do set mmddyyyy=%%I_%%H_%%G


@copy %BUILDPATH%\Output\setup-kolekti_0.7.3.exe F:\kolekti\setup-kolekti_0.7.3.exe
pause

