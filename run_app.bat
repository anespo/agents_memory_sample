@echo off
REM Agent Memory Management Application Launcher for Windows
REM This script checks dependencies and launches the Streamlit application

echo.
echo 🧠 Amazon Bedrock Agent Core Memory Management
echo ==============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.10 or higher.
    pause
    exit /b 1
)

echo ✅ Python detected
echo.

REM Check if uv is available
where uv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ uv package manager detected
    echo.
    echo 📦 Syncing dependencies with uv...
    uv sync
    echo.
    echo 🚀 Launching Streamlit application...
    uv run streamlit run app.py
) else (
    REM Check if streamlit is installed
    python -c "import streamlit" >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Streamlit not found. Installing dependencies...
        pip install -r requirements.txt
    ) else (
        echo ✅ Dependencies already installed
    )
    
    echo.
    echo 🚀 Launching Streamlit application...
    streamlit run app.py
)

pause
