@echo off
REM Script para hacer push a GitHub automáticamente

git add .
git commit -m "Actualización automática"
git push

pause 