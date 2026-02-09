@echo off
echo Restarting RabbitMQ Service...
echo.

REM Method 1: Using sc command
sc stop RabbitMQ
timeout /t 3 /nobreak >nul
sc start RabbitMQ

echo.
echo Checking RabbitMQ status...
sc query RabbitMQ

echo.
echo RabbitMQ service restarted!
echo.
echo Management interface: http://localhost:15672
echo Username: guest
echo Password: guest
echo.
pause