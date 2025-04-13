@echo off
echo Setting up backend...
cd backend
call pip install -r requirements.txt
start cmd /k python Main.py

echo Setting up frontend...
cd ../frontend
call npm install
start cmd /k npm start

echo All services started! 🎉
