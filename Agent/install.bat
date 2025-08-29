@echo off
echo ===============================================
echo    Agentic AI Flight Scanner Setup
echo ===============================================
echo.

echo Installing Python dependencies...
pip install -r requirements.txt

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✓ Installation completed successfully!
    echo.
    echo You can now run the flight scanner:
    echo   python flight_scanner_agent.py
    echo.
    echo To test with demo data:
    echo   python demo_scraper.py
    echo.
    echo Configure your search in config.json before running.
) else (
    echo.
    echo ✗ Installation failed. Please check the error messages above.
    echo.
    echo Make sure you have Python and pip installed.
)

pause
