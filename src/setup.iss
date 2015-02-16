; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define MyAppName "kolekti"
#define MyAppVersion "0.7"
#define MyAppPublisher "Exselt Services"
#define MyAppURL "http://www.kolekti.org/"
#define MyAppExeName "kolekti_server.exe"

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{8B4AEA7A-A156-49ED-8498-5DDAEF4A888F}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
;AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
LicenseFile=C:\Users\waloo\Desktop\kolekti\kolekti\src\LICENCE
OutputBaseFilename=setup-{#MyAppName}_{#MyAppVersion}
;OutputDir=F:\kolekti\
Compression=lzma
SolidCompression=yes

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "C:\Users\waloo\Desktop\kolekti\kolekti\src\dist\kolekti_server\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[INI]
Filename: "{app}\kolekti.ini"; Section: "InstallSettings"; Key: "projectsPath"; String: "{code:GetDataDir}"
Filename: "{app}\kolekti.ini"; Section: "InstallSettings"; Key: "installdir"; String: "{app}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent


[Code]
var
  DataDirPage: TInputDirWizardPage;
  
procedure InitializeWizard;
begin
  { Create the pages }
  
  DataDirPage := CreateInputDirPage(wpSelectDir,
    'Sélectionnez le dossier projets', 'les projets kolekti seront installés dans el dossier sélectionné',
    'Select the folder in which Setup should install personal data files, then click Next.',
    False, '');
  DataDirPage.Add('');

  { Set default values, using settings that were stored last time if possible }

  DataDirPage.Values[0] := GetPreviousData('DataDir', '');
end;

procedure RegisterPreviousData(PreviousDataKey: Integer);
var
  UsageMode: String;
begin
  { Store the settings so we can restore them next time }
  SetPreviousData(PreviousDataKey, 'DataDir', DataDirPage.Values[0]);
end;
      {
function ShouldSkipPage(PageID: Integer): Boolean;
begin
    Result := False;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  I: Integer;
begin
    Result := True;
end;
       }

function GetDataDir(Param: String): String;
begin
  { Return the selected DataDir }
  Result := DataDirPage.Values[0];
end;
