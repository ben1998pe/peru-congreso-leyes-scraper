@echo off
echo Configurando automatizacion del scraper...

REM Crear tarea programada para ejecutar diariamente
schtasks /create /tn "Scraper Congreso Peru" /tr "python \"%~dp0..\scripts\auto_scraper.py\"" /sc daily /st 06:00 /f

echo Tarea programada creada exitosamente!
echo La tarea se ejecutara todos los dias a las 6:00 AM
echo Para ver la tarea: schtasks /query /tn "Scraper Congreso Peru"
echo Para eliminar la tarea: schtasks /delete /tn "Scraper Congreso Peru" /f

pause
