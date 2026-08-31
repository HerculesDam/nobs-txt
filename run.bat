@echo off
setlocal
chcp 65001 >nul
title nobs-txt - No bs TXT converter
cd /d "%~dp0"

rem ---- Prefer the project venv, otherwise any Python on PATH ----
set "PYCMD="
if exist ".venv\Scripts\python.exe" set "PYCMD=.venv\Scripts\python.exe"
if not defined PYCMD (
    py -3 --version >nul 2>nul
    if not errorlevel 1 set "PYCMD=py -3"
)
if not defined PYCMD (
    python --version >nul 2>nul
    if not errorlevel 1 set "PYCMD=python"
)
if not defined PYCMD (
    echo.
    echo   [x] Python not found. Install it from https://www.python.org/downloads/ and try again.
    echo.
    pause
    exit /b 1
)

echo   [i] Using: %PYCMD%
echo.
rem No arguments -> interactive wizard. Pass flags through with %*.
%PYCMD% -m nobs_txt %*
echo.
pause
endlocal
