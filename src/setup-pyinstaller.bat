@set PYTHONPATH=C:\Users\waloo\Desktop\kolekti\kolekti\src\kolekti_server;C:\Users\waloo\Desktop\kolekti\kolekti\src

@rem pyinstaller -w --name kolekti_server kolekti_server\server.py
@pyinstaller -y  kolekti_server.spec
@"C:\Program Files\Inno Setup 5\ISCC.exe" C:\Users\waloo\Desktop\kolekti\kolekti\src\setup.iss

@for /f "tokens=1-4 delims=/ " %%G in ('date /t') do set mmddyyyy=%%I_%%H_%%G

@copy C:\Users\waloo\Desktop\kolekti\kolekti\src\Output\setup-kolekti_0.7.exe F:\kolekti\setup-kolekti_0.7_%mmddyyyy%.exe