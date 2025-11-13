@echo off
echo ========================================
echo Starting Local Scraping Test
echo ========================================
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
echo.
echo Running test_local_scraping.py...
echo Browser will open in a few seconds...
echo.
python test_local_scraping.py
echo.
echo ========================================
echo Test completed!
echo ========================================
pause
