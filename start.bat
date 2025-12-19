@echo off
chcp 65001 >nul
title ZLF PlayerOk Checker

echo.
echo     ZLF PLAYEROK CHECKER v1.0
echo.
echo     playerokapi от: alleexxeeyy
echo     Портфолио: https://zlafik1.github.io/zlafikbio/
echo.
timeout /t 1 /nobreak >nul

python bot.py

echo.
echo     Программа завершена
pause