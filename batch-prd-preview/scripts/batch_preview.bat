@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "CLI_SCRIPT=%SCRIPT_DIR%batch_preview.py"

REM 显示帮助信息
if "%~1"=="--help" goto :show_usage
if "%~1"=="-h" goto :show_usage
if "%~1"=="help" goto :show_usage

REM 检查虚拟环境 Python 是否存在
if exist "%VENV_PYTHON%" (
    "%VENV_PYTHON%" "%CLI_SCRIPT%" %*
) else (
    REM 尝试使用系统 Python
    python "%CLI_SCRIPT%" %*
)

exit /b %ERRORLEVEL%

:show_usage
echo.
echo Batch PRD Preview - 批量 Word 预览转换工具
echo.
echo 用法:
echo     batch_preview.bat [选项]
echo.
echo 选项:
echo     --input-dir DIR     输入目录路径（包含 Word 文件）
echo     --output-dir DIR    输出目录路径
echo     --file-pattern      文件匹配模式（默认 *.docx）
echo     --help, -h          显示帮助信息
echo.
echo 示例:
echo     batch_preview.bat --input-dir ./prds --output-dir ./output
echo     batch_preview.bat --input-dir D:/documents --output-dir D:/preview
echo     batch_preview.bat --file-pattern "*.doc"
echo     batch_preview.bat  # 使用默认路径（当前目录）
echo.
echo 输出结构:
echo     prd-preview-output/
echo     ├── preview-summary.md    # 汇总报告
echo     ├── 文件A/
echo     │   ├── assets/           # 图片目录
echo     │   └── preview.md        # 转换后的 Markdown
echo     └── 文件B/
echo         └── preview.md
echo.
exit /b 0