@echo off
chcp 65001
echo ========================================
echo      IndexTTS API 服务器启动脚本
echo ========================================
echo.

echo 正在激活conda环境 [index-tts]...
call D:\software\conda\Scripts\activate.bat index-tts

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 激活conda环境失败，使用系统Python...
    python --version
    echo.
    python api_server.py
) else (
    echo ✅ conda环境激活成功
    python --version
    echo.
    echo 正在启动IndexTTS API服务器...
    echo 这将启用以下API接口：
    echo - POST /api/tts          (文本转语音)
    echo - GET  /api/voices       (获取音色列表)
    echo - GET  /api/audio/{file} (下载音频文件)
    echo - GET  /api/status       (服务状态)
    echo.
    echo API服务器将运行在: http://localhost:8000
    echo Swagger文档地址: http://localhost:8000/docs
    echo.
    python api_server.py --host 0.0.0.0 --port 8000
)

echo.
echo 程序已退出，按任意键关闭窗口...
pause > nul 