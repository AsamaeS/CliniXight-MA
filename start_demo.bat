@echo off
echo =========================================================
echo    🚀 LANCEMENT CLINI-VIEW MA+ (FRONTEND + BACKEND) 🚀
echo =========================================================
echo.

echo [1/3] Installation des dependances (peut prendre 1 min la premiere fois)...
cd backend
python -m pip install -q -r requirements.txt
cd ../frontend
call npm install --silent
cd ..

echo.
echo [2/3] Demarrage du Backend FastAPI (Port 8000)...
start "CliniVIEW - Backend (FastAPI)" cmd /k "cd backend && uvicorn main:app --reload --port 8000"

echo.
echo [3/3] Demarrage du Frontend Next.js (Port 3000)...
start "CliniVIEW - Frontend (Next.js)" cmd /k "cd frontend && npm run dev"

echo.
echo =========================================================
echo ✅ L'application est en cours de demarrage !
echo 🌍 Le tableau de bord s'ouvrira sur : http://localhost:3000
echo =========================================================
echo Ne fermez pas les deux nouvelles fenetres noires (serveurs).
pause
