@echo off
chcp 65001 >nul
title SoundCloud App — Сборка

echo.
echo  ================================
echo   SoundCloud Desktop — Сборка
echo  ================================
echo.

:: Проверяем Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python не найден. Скачиваем и устанавливаем...
    powershell -Command "Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile 'python_installer.exe'"
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_pip=1
    del python_installer.exe
    echo [+] Python установлен. Перезапустите скрипт!
    pause
    exit
)

echo [+] Python найден
echo.


echo [*] Устанавливаем библиотеки...
pip install PyQt6 PyQt6-WebEngine pyinstaller --quiet
echo [+] Библиотеки установлены
echo.


echo [*] Собираем SoundCloud.exe...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "SoundCloud" ^
    --icon "icon.ico" ^
    --add-data "icon.ico;." ^
    soundcloud_app.py

if errorlevel 1 (
    echo.
    echo [!] Сборка без иконки (файл icon.ico не найден)
    pyinstaller ^
        --onefile ^
        --windowed ^
        --name "SoundCloud" ^
        soundcloud_app.py
)

echo.
echo [+] Готово! Файл: dist\SoundCloud.exe
echo.

set INNO="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if exist %INNO% (
    echo [*] Собираем установщик через Inno Setup...
    %INNO% installer.iss
    echo [+] Установщик: Output\SoundCloud_Setup.exe
) else (
    echo [i] Inno Setup не найден — только dist\SoundCloud.exe
    echo [i] Скачать Inno Setup: https://jrsoftware.org/isdl.php
)

echo.
pause
