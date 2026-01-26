@echo off
echo ====================================
echo RESEARCH DIGEST GENERATOR
echo ====================================
echo.

REM Ask user for number of papers
set /p NUM_PAPERS="How many papers? (press Enter for 3): "
if "%NUM_PAPERS%"=="" set NUM_PAPERS=3

echo.
echo Configuration:
echo - Papers to fetch: %NUM_PAPERS%
echo - Year filter: 2024+
echo.

echo [1/3] Cleaning old outputs...
if exist data\raw_papers.json del /q data\raw_papers.json
if exist data\normalized_papers.json del /q data\normalized_papers.json
if exist data\enhanced_papers.json del /q data\enhanced_papers.json
if exist visualizations\*.png del /q visualizations\*.png
if exist output\*.pdf del /q output\*.pdf
if exist output\*.html del /q output\*.html
echo Cleaned.
echo.

echo [2/3] Generating digest with %NUM_PAPERS% papers...
python main_pipeline.py --max-papers %NUM_PAPERS% --start-year 2024
echo.

echo [3/3] Complete!
echo Check output\ folder for your PDF
echo.
pause