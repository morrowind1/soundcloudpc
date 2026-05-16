; ============================================================
;  SoundCloud Desktop — Inno Setup Script
;  Собирает полноценный установщик с ярлыками и удалением
; ============================================================

#define AppName      "SoundCloud"
#define AppVersion   "1.0"
#define AppPublisher "Личная разработка"
#define AppExeName   "SoundCloud.exe"
#define AppURL       "https://soundcloud.com"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=Output
OutputBaseFilename=SoundCloud_Setup
; SetupIconFile=icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
WizardResizable=no
PrivilegesRequired=admin
WizardImageFile=compiler:WizModernImage.bmp
WizardSmallImageFile=compiler:WizModernSmallImage.bmp

[Languages]
Name: "russian"; MessagesFile: "compiler:Languages\Russian.isl"

[Tasks]
Name: "desktopicon";    Description: "Создать ярлык на рабочем столе";    GroupDescription: "Дополнительные задачи:"
Name: "startmenuicon";  Description: "Добавить в меню Пуск";              GroupDescription: "Дополнительные задачи:"
Name: "startupicon";    Description: "Запускать при старте Windows";       GroupDescription: "Дополнительные задачи:"; Flags: unchecked

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion


[Icons]
Name: "{autodesktop}\{#AppName}";          Filename: "{app}\{#AppExeName}"; Tasks: desktopicon
Name: "{group}\{#AppName}";               Filename: "{app}\{#AppExeName}"; Tasks: startmenuicon
Name: "{group}\Удалить {#AppName}";       Filename: "{uninstallexe}";       Tasks: startmenuicon
Name: "{userstartup}\{#AppName}";         Filename: "{app}\{#AppExeName}"; Tasks: startupicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Запустить {#AppName}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}"

[Code]
procedure InitializeWizard();
begin
  WizardForm.WelcomeLabel2.Caption :=
    'Будет установлено приложение SoundCloud Desktop.' + #13#10 + #13#10 +
    'Это личная разработка — полноценное десктопное' + #13#10 +
    'приложение без браузера.' + #13#10 + #13#10 +
    'Нажмите «Далее» для продолжения.';
end;
