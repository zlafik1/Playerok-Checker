@echo off
chcp 65001 > nul
title PlayerOk Token Checker v2.1
color 0A
cls

echo ════════════════════════════════════════════════
echo        PLAYEROK TOKEN CHECKER v2.1
echo        Разработано ZLF Team
echo ════════════════════════════════════════════════
echo.

echo [i] Проверка Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo [-] Ошибка: Python не найден!
    echo [i] Установите Python 3.8+ с python.org
    pause
    exit
)

echo [i] Проверка зависимостей...
python -c "import curl_cffi" 2>nul
if errorlevel 1 (
    echo [i] Установка curl-cffi...
    pip install curl-cffi --quiet --disable-pip-version-check
    echo [+] Зависимости установлены
)

echo [+] Все готово!
echo [i] Запуск программы...
echo.

python bot.py

echo.
echo ════════════════════════════════════════════════
pause
