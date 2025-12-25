@echo off
chcp 65001 >nul
title 🚀 ZLF PlayerOk Checker v2.0

echo.
echo     ╔══════════════════════════════════════════════════════════╗
echo     ║                                                          ║
echo     ║                  🚀 ZLF PLAYEROK CHECKER                 ║
echo     ║                     Версия 2.0                           ║
echo     ║                                                          ║
echo     ╚══════════════════════════════════════════════════════════╝
echo.
echo        📦 playerokapi от: alleexxeeyy
echo        🌐 Портфолио: https://zlafik1.github.io/zlafikbio/
echo.
echo        📅 %date% %time%
echo.
timeout /t 2 /nobreak >nul

python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo    ❗ Python не найден! Установите Python 3.7+
    echo    📥 Скачать: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

python -c "import playerokapi" >nul 2>&1
if errorlevel 1 (
    echo.
    echo    ⚠  playerokapi не установлен
    echo    📦 Устанавливаю библиотеку...
    pip install playerokapi --quiet
    echo    ✅ playerokapi установлен
)

echo.
echo    🚀 Запуск программы...
echo.
timeout /t 1 /nobreak >nul

python bot.py

echo.
echo    📊 Программа завершена
echo    🕐 Время работы: %time%
echo.
pause