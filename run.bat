@echo off
chcp 65001 >nul
setlocal

REM ============================================================
REM 配置说明：
REM 请根据你的实际情况修改下面的虚拟环境路径
REM 
REM 方式1：使用系统Python（推荐新手）
REM set VENV_PYTHON=python
REM 
REM 方式2：使用指定的Python路径
REM set VENV_PYTHON=C:\Python\python.exe
REM 
REM 方式3：使用虚拟环境（推荐）
REM set VENV_PYTHON=你的虚拟环境路径\Scripts\python.exe
REM ============================================================

REM 请根据你的实际情况选择以下一种方式：
REM 默认使用系统Python
set VENV_PYTHON=python

REM 如果使用虚拟环境，请取消下面的注释并修改路径
REM set VENV_PYTHON=D:\Python\.venv\Scripts\python.exe

REM 检查Python是否可用
%VENV_PYTHON% --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python不可用: %VENV_PYTHON%
    echo 💡 请检查Python是否已安装或修改上面的VENV_PYTHON路径
    pause
    exit /b 1
)

REM 进入项目目录
cd /d "%~dp0"

echo ============================================================
echo 🚀 座位预约系统 Selenium V2 - 启动
echo ============================================================
echo.
echo 📂 项目目录: %CD%
echo 🐍 Python路径: %VENV_PYTHON%
echo.
echo ============================================================
echo.

REM 运行主程序
"%VENV_PYTHON%" main.py

REM 检查运行结果
if %errorlevel% neq 0 (
    echo.
    echo ❌ 程序运行出错，错误码: %errorlevel%
    pause
    exit /b %errorlevel%
)

echo.
echo ============================================================
echo ✅ 程序运行完成
echo ============================================================
pause

