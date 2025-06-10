@echo off
echo Setting up Invoice OCR Processing environment...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python first.
    pause
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file template...
    echo GOOGLE_API_KEY=your_api_key_here > .env
    echo Please edit the .env file and add your Google API key
)

echo Setup complete! Running the script...
python local.py

pause 