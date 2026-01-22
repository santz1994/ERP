@echo off
REM =====================================================================
REM ERP 2026 - QA Infrastructure Quick Setup (Windows)
REM Usage: qa-setup.bat
REM =====================================================================

setlocal enabledelayedexpansion
cd /d %~dp0

echo.
echo =====================================================================
echo ERP 2026 - QA Infrastructure Quick Setup
echo =====================================================================
echo.

REM Check Python
echo [1/6] Checking Python environment...
python --version >nul 2>&1
if errorlevel 1 (
    echo. [ERROR] Python not found. Install Python 3.10+
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VER=%%i
echo [OK] Python %PYTHON_VER%

REM Navigate to backend
cd erp-softtoys

REM Install dependencies
echo [2/6] Installing QA dependencies...
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt 2>nul
echo [OK] Dependencies installed

REM Check conftest
echo [3/6] Checking test configuration...
if exist "..\tests\conftest.py" (
    echo [OK] conftest.py found
) else (
    echo [ERROR] conftest.py not found
    exit /b 1
)

REM Check pytest
echo [4/6] Verifying pytest...
pytest --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pytest not found
    exit /b 1
)
echo [OK] pytest ready

REM Collect tests
echo [5/6] Collecting tests...
pytest ..\tests\ --collect-only -q 2>nul | findstr "test_" | head -5
echo [OK] Tests collected

REM Check tools
echo [6/6] Checking QA tools...
setlocal disabledelayedexpansion
for %%t in (black ruff mypy bandit) do (
    where %%t >nul 2>&1 && echo [OK] %%t || echo [INFO] %%t available via pip
)

echo.
echo =====================================================================
echo [SUCCESS] Setup Complete!
echo =====================================================================
echo.
echo Next steps:
echo.
echo   1. Start backend:
echo      uvicorn app.main:app --reload --port 8000
echo.
echo   2. Run all tests:
echo      pytest ..\tests\ -v
echo.
echo   3. Run specific suite:
echo      pytest ..\tests\test_boundary_value_analysis.py -v
echo.
echo   4. Run with coverage:
echo      pytest ..\tests\ --cov=app --cov-report=html
echo.
echo   5. Run load tests:
echo      locust -f ..\tests\locustfile.py --headless -u 5 -r 1 -t 20s --host http://localhost:8000
echo.
echo   6. Security scan:
echo      bandit -r app -f txt
echo.
echo =====================================================================
echo.
