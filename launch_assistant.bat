@echo off
title Stacey's AI Assistant - Starting...

:: Start Ollama silently in the background
echo Starting Ollama model...
start "" /min cmd /c "ollama run llama3.2:3b"

:: Wait 8 seconds for model to load into memory
echo Warming up AI model (this takes about 8 seconds)...
timeout /t 8 /nobreak > nul

:: Launch the assistant GUI
echo Launching Stacey's AI Assistant...
cd C:\Users\Bizec\Desktop\School_General\Ollama-Projects
python stacey_assistant.py

:: If there's an error, pause so you can read it
if %errorlevel% neq 0 (
    echo.
    echo Something went wrong. Press any key to close.
    pause
)
