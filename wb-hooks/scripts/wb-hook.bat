@echo off
REM wb-hook CLI 入口（Windows）
REM 用法: wb-hook init / add / list / remove / test

python "%~dp0wb-hook.py" %*
