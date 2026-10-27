@echo off
title CreativeForge Intelligence Studio v3.0 (Ports 8000 ^& 3333)
color 0B

echo =======================================================================
echo          CreativeForge Intelligence Studio v3.0
echo          Starting Unified System: FastAPI (:8000) ^& Next.js (:3333)...
echo =======================================================================
echo.

set "BACKEND_PORT=8000"
set "FRONTEND_PORT=3333"
set "STUDIO_URL=http://localhost:3333/projects/prj_match3_hero/studio?tab=workflow"

cd /d "%~dp0"

:: 0. Tasinabilir Runtime (runtime/node ve runtime/python) Ortam Kontrolu
if not exist "%~dp0runtime\python\python.exe" (
    if not exist "%~dp0.venv\Scripts\python.exe" (
        echo [INFO] Calisma ortami bulunamadi. Otomatik runtime kurulumu baslatiliyor...
        call "%~dp0setup_runtime.bat"
    )
)

set "NODE_CMD=node"
set "NPM_CMD=npm"
if exist "%~dp0runtime\node\node.exe" (
    set "PATH=%~dp0runtime\node;%PATH%"
    set "NODE_CMD=%~dp0runtime\node\node.exe"
    if exist "%~dp0runtime\node\npm.cmd" (
        set "NPM_CMD=%~dp0runtime\node\npm.cmd"
    )
    echo [INFO] runtime/node - Tasinabilir Node.js calisma ortamina eklendi.
)

set "PYTHON_EXE=python"
if exist "%~dp0runtime\python\python.exe" (
    set "PYTHON_EXE=%~dp0runtime\python\python.exe"
    echo [INFO] runtime/python - Tasinabilir Python calisma ortamina eklendi.
) else if exist "%~dp0.venv\Scripts\python.exe" (
    set "PYTHON_EXE=%~dp0.venv\Scripts\python.exe"
)

:: 1. Önceki oturumdan kalan takılı süreçleri temizle
echo [1/5] Port %BACKEND_PORT% ve %FRONTEND_PORT% uzerindeki eski surecler taranip temizleniyor...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    echo [INFO] Port %BACKEND_PORT% uzerindeki eski PID %%a sonlandiriliyor...
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    echo [INFO] Port %FRONTEND_PORT% uzerindeki eski PID %%a sonlandiriliyor...
    taskkill /F /PID %%a >nul 2>&1
)

:: Docker servislerini kontrol et ve baslat
where docker >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Docker servisleri - PostgreSQL ve Redis kontrol ediliyor...
    docker compose up -d >nul 2>&1
)

:: 2. FastAPI Backend Servisini Baslat
echo [2/5] FastAPI REST ^& SSE Backend Servisi port %BACKEND_PORT% uzerinde baslatiliyor...
start "CreativeForge FastAPI Backend (:8000)" /min "%PYTHON_EXE%" -m uvicorn services.api.app.main:app --host 127.0.0.1 --port %BACKEND_PORT%

:: Backend saglik kontrolu icin kisa bekleme
ping 127.0.0.1 -n 3 >nul

:: 3. Frontend Bagimlilik ve Onbellek Kontrolu
cd /d "%~dp0apps\web"
if not exist "node_modules" (
    echo [INFO] Ilk calistirma tespit edildi. apps/web paketleri yukleniyor...
    call "%NPM_CMD%" install
    if %errorlevel% neq 0 (
        echo [ERROR] npm install basarisiz oldu.
        goto SHUTDOWN
    )
)

if exist ".next" (
    echo [3/5] Cakisma onleyici Webpack onbellegi temizleniyor...
    rd /s /q ".next" >nul 2>&1
)

:: 4. Tarayiciyi dogrudan Workflow Studio adresine ac
echo [4/5] Tarayici dogrudan Workflow Studio adresine yonlendiriliyor:
echo       %STUDIO_URL%
echo.
start "" powershell -NoProfile -Command "Start-Sleep -Seconds 3; Start-Process '%STUDIO_URL%'"

:: 5. Next.js Sunucusunu calistir ve CMD'yi acik tut
echo [5/5] Next.js Stüdyo Sunucusu bu pencerede calisiyor.
echo -----------------------------------------------------------------------
echo   [!] BU CMD PENCERESI ACIK KALMALIDIR (Canli loglar buraya akar).
echo   [!] Kapatmak istediginizde:
echo       - Web arayuzunun sag ustundeki [Kapat] butonuna tiklayabilir, VEYA
echo       - Bu pencerede Ctrl + C yapip 'E' / 'Y' basabilirsiniz.
echo -----------------------------------------------------------------------
echo.

call "%NPM_CMD%" run dev

:: 6. Kapanis ve Temizlik Rutini
:SHUTDOWN
echo.
echo =======================================================================
echo [KAPANIS] Sunucular kapatildi. Kalan arka plan surecleri temizleniyor...
echo =======================================================================
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%BACKEND_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%FRONTEND_PORT%" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo [TAMAMLANDI] Port %BACKEND_PORT% ve Port %FRONTEND_PORT% basariyla sonlandirildi.
echo.
pause
exit /b 0
