@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "VENV_PYTHON=%SCRIPT_DIR%.venv\Scripts\python.exe"
set "CLI_SCRIPT=%SCRIPT_DIR%word2md_cli.py"

REM 检查参数
if "%~1"=="" goto :show_usage
if "%~2"=="" goto :show_usage

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
echo Word2MD - Word 转 Markdown 命令行工具
echo.
echo 用法:
echo     word2md.bat input.docx output.md
echo.
echo 参数:
echo     input   输入的 Word 文件路径 (.docx/.doc)
echo     output  输出的 Markdown 文件路径 (.md)
echo.
echo 选项:
echo     --no-pandoc  禁用 Pandoc，使用 Mammoth 转换
echo.
echo 示例:
echo     word2md.bat document.docx output.md
echo     word2md.bat "我的文档.docx" "输出.md"
echo.
exit /b 1
