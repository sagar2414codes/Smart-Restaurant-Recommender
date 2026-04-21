@echo off
REM Smart Restaurant Recommender - Quick Start Script
REM This script sets up and runs the application

echo.
echo ========================================
echo  Smart Restaurant Recommender 🍽️
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo ✅ Python found

REM Navigate to project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🚀 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt -q
echo ✅ Dependencies installed

REM Run the Streamlit app
echo.
echo ✨ Starting Smart Restaurant Recommender...
echo 🌐 Opening browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py

pause
