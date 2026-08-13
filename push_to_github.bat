@echo off
echo ===================================================
echo 🎬 PUSHING SHOWTIME PROJECT TO GITHUB
echo Repository: https://github.com/71382502139saieeswar-tony/showtime
echo ===================================================
echo.

set GIT_CMD="%~dp0portable_git\cmd\git.exe"

%GIT_CMD% init
%GIT_CMD% config user.name "71382502139saieeswar-tony"
%GIT_CMD% config user.email "saieeswar-tony@users.noreply.github.com"
%GIT_CMD% add .
%GIT_CMD% commit -m "Deploy ShowTime Streamlit Application & FastAPI Backend"
%GIT_CMD% branch -M main
%GIT_CMD% remote remove origin 2>nul
%GIT_CMD% remote add origin https://github.com/71382502139saieeswar-tony/showtime.git
%GIT_CMD% push -u origin main

echo.
echo ===================================================
echo DONE! If prompted for credentials, log in with your GitHub account!
echo ===================================================
pause
