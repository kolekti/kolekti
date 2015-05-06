@set PYTHONPATH=C:\Users\waloo\Desktop\kolekti\kolekti\src\kolekti_server;C:\Users\waloo\Desktop\kolekti\kolekti\src
@rd build /s /q
@rd dist /s /q
@svn export --force --username=waloo http://beta.kolekti.net/svn/Exemple_PDFs dist\Exemple_PDFs
@svn export --force --username=waloo http://beta.kolekti.net/svn/Exemple_WebhelpPersonnalisable dist\Exemple_WebhelpPersonnalisable
@rem pyinstaller -w --name kolekti_server kolekti_server\server.py
@pyinstaller -y -w  kolekti_server.spec
@"C:\Program Files\Inno Setup 5\ISCC.exe" C:\Users\waloo\Desktop\kolekti\kolekti\src\setup.iss

@for /f "tokens=1-4 delims=/ " %%G in ('date /t') do set mmddyyyy=%%I_%%H_%%G

@copy C:\Users\waloo\Desktop\kolekti\kolekti\src\Output\setup-kolekti_0.7.exe F:\kolekti\setup-kolekti_0.7_%mmddyyyy%.exe
