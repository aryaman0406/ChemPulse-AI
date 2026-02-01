@echo off
REM Windows build script for Render deployment
REM This file ensures build.sh has correct permissions

echo Making build.sh executable...
git update-index --chmod=+x backend/build.sh

echo Adding changes...
git add backend/build.sh

echo Committing...
git commit -m "Make build.sh executable for Render deployment"

echo Pushing to GitHub...
git push

echo Done! Build.sh is now executable on Render.
pause
