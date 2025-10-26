@echo off
chcp 65001 > nul
echo ========================================
echo   小説コンバーター / Syosetu Converter
echo ========================================
echo.
echo [1/4] Starting the application...
echo Current directory: %CD%
REM バッチのあるディレクトリに移動
cd /d "%~dp0"
echo Working directory: %CD%
echo.

REM venvを有効化
echo [2/4] Activating virtual environment...
if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo Please create a virtual environment first:
    echo   python -m venv .venv
    pause
    exit /b 1
)
call .venv\Scripts\activate.bat
echo Virtual environment activated: OK
echo.

REM Pythonスクリプトを実行
echo [3/4] Installing dependencies...
echo Reading requirements from: app\requirements.txt
if not exist "app\requirements.txt" (
    echo [ERROR] requirements.txt not found!
    pause
    exit /b 1
)
pip install -r app\requirements.txt
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to install dependencies.
    echo Please check the error messages above.
    pause
    exit /b 1
)
echo Dependencies installed: OK
echo.

cls

echo [4/4] Running the application...
echo ========================================
echo.
python app\main.py
set EXIT_CODE=%errorlevel%
echo.
echo ========================================
if %EXIT_CODE% neq 0 (
    echo [ERROR] Application exited with error code: %EXIT_CODE%
    echo Please check the log file: syosetu_converter.log
    pause
    exit /b %EXIT_CODE%
)

REM 終了時に仮想環境を無効化
echo.
echo [SUCCESS] Application finished successfully.
echo Deactivating virtual environment...
deactivate
echo.
echo Press any key to exit...
pause > nul
