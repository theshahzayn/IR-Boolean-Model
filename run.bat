@echo off
echo Setting up backend...
cd backend
start cmd /k python Main.py

echo Setting up frontend...
cd ../frontend
start cmd /k npm start

echo All services started! 🎉
