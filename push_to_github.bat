@echo off
echo ===================================================
echo 🎬 PUSHING SHOWTIME PROJECT TO GITHUB
echo Repository: https://github.com/71382502139saieeswar-tony/showtime
echo ===================================================
echo.

git init
git add .
git commit -m "Deploy ShowTime Streamlit Application & FastAPI Backend"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/71382502139saieeswar-tony/showtime.git
git push -u origin main --force

echo.
echo ===================================================
echo SUCCESS! Your project is pushed to GitHub!
echo Now go to https://share.streamlit.io to deploy!
echo ===================================================
pause
