@echo off
title CreativeForge - Tasinabilir Runtime Kurucusu (Zero-Config Portable Setup)
color 0A

echo =======================================================================
echo          CreativeForge Intelligence Studio v3.0
echo          Tasinabilir Runtime Kurulum Araci (Zero-Install Engine)
echo =======================================================================
echo.
echo Bu arac, sisteminize Node.js veya Python kurmaniza GEREK KALMADAN,
echo projenin icine izole 'runtime' klasorunu otomatik olarak indirip kurar.
echo.

cd /d "%~dp0"

if not exist "runtime" mkdir "runtime"
if not exist "runtime\downloads" mkdir "runtime\downloads"

:: 1. Node.js Portable
if not exist "runtime\node\node.exe" (
    echo [1/4] Tasinabilir Node.js (v20.18.0 LTS) indiriliyor...
    curl.exe -L -o "runtime\downloads\node.zip" "https://nodejs.org/dist/v20.18.0/node-v20.18.0-win-x64.zip"
    if %errorlevel% neq 0 (
        echo [HATA] Node.js indirilemedi. Lutfen internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
    echo [INFO] Node.js arsivi runtime/node klasorune cikartiliyor...
    powershell -NoProfile -Command "Expand-Archive -Path 'runtime\downloads\node.zip' -DestinationPath 'runtime\temp_node' -Force; Get-ChildItem 'runtime\temp_node\*' | Move-Item -Destination 'runtime\node' -Force; Remove-Item 'runtime\temp_node' -Recurse -Force"
) else (
    echo [INFO] runtime/node zaten mevcut, atlandi.
)

:: 2. Python Portable Embed
if not exist "runtime\python\python.exe" (
    echo [2/4] Tasinabilir Python 3.11 Embed indiriliyor...
    curl.exe -L -o "runtime\downloads\python-embed.zip" "https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    if %errorlevel% neq 0 (
        echo [HATA] Python indirilemedi. Lutfen internet baglantinizi kontrol edin.
        pause
        exit /b 1
    )
    echo [INFO] Python arsivi runtime/python klasorune cikartiliyor...
    powershell -NoProfile -Command "Expand-Archive -Path 'runtime\downloads\python-embed.zip' -DestinationPath 'runtime\python' -Force"

    :: python311._pth dosyasina site-packages ve relative import baglantisi ekle
    echo python311.zip> "runtime\python\python311._pth"
    echo .>> "runtime\python\python311._pth"
    echo Lib/site-packages>> "runtime\python\python311._pth"
    echo ../..>> "runtime\python\python311._pth"
    echo import site>> "runtime\python\python311._pth"
) else (
    echo [INFO] runtime/python zaten mevcut, atlandi.
)

:: 3. Pip Kurulumu
if not exist "runtime\python\Lib\site-packages\pip" (
    echo [3/4] Paket yoneticisi (pip) kuruluyor...
    curl.exe -L -o "runtime\downloads\get-pip.py" "https://bootstrap.pypa.io/get-pip.py"
    .\runtime\python\python.exe "runtime\downloads\get-pip.py" --no-warn-script-location
)

:: 4. Python Bagimliliklarini Kurma
echo [4/4] Proje Python paketleri kuruluyor...
.\runtime\python\python.exe -m pip install -e . "greenlet>=3.0.0" httpx aiohttp pillow

:: Gecici indirmeleri temizle
if exist "runtime\downloads" rd /s /q "runtime\downloads" >nul 2>&1

:: .env dosyasini kontrol et
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [INFO] .env dosyasi ornekten kopyalandi.
    )
)

echo.
echo =======================================================================
echo [TAMAMLANDI] Tasinabilir runtime ortami hazirlandi!
echo Artik hicbir kuruluma gerek olmadan dogrudan run.bat calistirabilirsiniz.
echo =======================================================================
echo.
pause
