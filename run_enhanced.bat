@echo off
chcp 65001
echo ========================================
echo    IndexTTS Enhanced WebUI 启动脚本
echo ========================================
echo.

echo 正在激活conda环境 [index-tts]...
call D:\software\conda\Scripts\activate.bat index-tts

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 激活conda环境失败，使用系统Python...
    python --version
    echo.
    python webui_enhanced.py
) else (
    echo ✅ conda环境激活成功
    python --version
    echo.
    echo 正在启动IndexTTS增强版Web界面...
    echo 功能包括：
    echo - 🎤 音频生成
    echo - 💾 音色保存和管理
    echo - 📚 音色库浏览
    echo.
    python webui_enhanced.py --host 0.0.0.0 --port 7860
)

echo.
echo 程序已退出，按任意键关闭窗口...
pause > nul 