@echo off
echo Smart Thermostat Backend - GitHub Automation
echo ==========================================

REM Check if git is installed
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

REM Check if this is a git repository
if not exist ".git" (
    echo Initializing Git repository...
    git init
    
    echo Setting up remote repository...
    echo Using repository: https://github.com/jbkeenan/smartstatback.git
    git remote add origin https://github.com/jbkeenan/smartstatback.git
) else (
    echo Git repository already initialized.
    
    REM Update remote URL to ensure it's correct
    git remote set-url origin https://github.com/jbkeenan/smartstatback.git
    echo Remote URL set to: https://github.com/jbkeenan/smartstatback.git
)

REM Add all files
echo Adding all files to git...
git add .

REM Get commit message
set /p commit_msg="Enter commit message (or press Enter for default message): "
if "%commit_msg%"=="" set commit_msg=Update Smart Thermostat Backend

REM Commit changes
echo Committing changes...
git commit -m "%commit_msg%"

REM Push to GitHub
echo Pushing to GitHub...
git push -u origin main

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Push failed. Trying with master branch instead...
    git push -u origin master
    
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo Push failed. You might need to:
        echo 1. Check your internet connection
        echo 2. Verify your GitHub credentials
        echo 3. Create the repository on GitHub if it doesn't exist
        echo 4. Set the correct branch name (main or master)
    )
)

echo.
if %ERRORLEVEL% EQU 0 (
    echo Success! Your code has been pushed to GitHub.
) else (
    echo There were some issues. Please check the error messages above.
)

pause
