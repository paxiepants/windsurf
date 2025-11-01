@echo off
REM Batch file to run ollama_chat.py with proper terminal
REM Double-click this file to run the interactive menu

echo.
echo ============================================================
echo Starting Ollama Chat Interactive Menu
echo ============================================================
echo.
echo Make sure Ollama is running in another window!
echo If not, open a new terminal and run: ollama serve
echo.
pause

REM Change to the script directory
cd /d "%~dp0"

REM Run the Python script
python ollama_chat.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ============================================================
    echo An error occurred. Press any key to exit...
    echo ============================================================
    pause > nul
)
