#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexTTS Enhanced 简化版一键安装脚本
直接从当前目录复制增强文件到官方IndexTTS仓库

使用方法:
1. 在当前目录运行: git clone https://github.com/index-tts/index-tts.git official_repo
2. 运行安装脚本: python install_enhanced_simple.py official_repo
3. 进入目录启动: cd official_repo && python webui_enhanced.py

作者: IndexTTS Enhanced Team
版本: v1.0
"""

import os
import sys
import shutil
import json
from pathlib import Path

def main():
    """主安装函数"""
    print("🚀 IndexTTS Enhanced 简化版安装器")
    print("="*50)
    
    # 检查命令行参数
    if len(sys.argv) != 2:
        print("❌ 使用方法: python install_enhanced_simple.py <目标目录>")
        print("例如: python install_enhanced_simple.py official_repo")
        sys.exit(1)
    
    target_dir = Path(sys.argv[1])
    current_dir = Path.cwd()
    
    # 检查目标目录是否为官方仓库
    if not (target_dir / "webui.py").exists():
        print(f"❌ 目标目录 '{target_dir}' 不是有效的IndexTTS仓库")
        print("请先克隆官方仓库: git clone https://github.com/index-tts/index-tts.git")
        sys.exit(1)
    
    print(f"✅ 检测到官方IndexTTS仓库: {target_dir}")
    
    # 需要复制的文件列表
    files_to_copy = [
        "webui_enhanced.py",
        "api_server.py", 
        "requirements_enhanced.txt",
        "test_api.py",
        "USER_GUIDE.md",
        "VOICE_MANAGEMENT_GUIDE.md", 
        "DEPLOYMENT_GUIDE.md",
        "indextts/voice_manager.py"
    ]
    
    # 创建目录结构
    print("📁 创建目录结构...")
    directories = ["voices", "outputs/api", "outputs/webui", "logs"]
    for dir_path in directories:
        (target_dir / dir_path).mkdir(parents=True, exist_ok=True)
        print(f"📂 创建: {dir_path}")
    
    # 复制文件
    print("\n📦 复制增强文件...")
    success_count = 0
    
    for file_path in files_to_copy:
        src = current_dir / file_path
        dst = target_dir / file_path
        
        if src.exists():
            # 确保目标目录存在
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"✅ 复制: {file_path}")
            success_count += 1
        else:
            print(f"⚠️  跳过: {file_path} (源文件不存在)")
    
    # 创建启动脚本
    print("\n📜 创建启动脚本...")
    
    # Windows批处理文件
    run_enhanced_bat = """@echo off
chcp 65001 > nul
echo ========================================
echo    IndexTTS Enhanced WebUI 启动脚本
echo ========================================

echo 正在激活conda环境 [index-tts]...
call conda activate index-tts
if errorlevel 1 (
    echo ❌ conda环境激活失败，请检查环境名称
    pause
    exit /b 1
)

echo ✅ conda环境激活成功
python --version

echo 正在启动IndexTTS增强版Web界面...
echo 功能包括：
echo - 音色保存和管理
echo - 完整API接口
echo - 增强Web界面

python webui_enhanced.py --host 0.0.0.0 --port 7860 --enable_api

pause
"""
    
    run_api_bat = """@echo off
chcp 65001 > nul
echo ========================================
echo     IndexTTS API服务器 启动脚本
echo ========================================

echo 正在激活conda环境 [index-tts]...
call conda activate index-tts
if errorlevel 1 (
    echo ❌ conda环境激活失败，请检查环境名称
    pause
    exit /b 1
)

echo ✅ conda环境激活成功
python --version

echo 正在启动IndexTTS API服务器...
echo API文档: http://localhost:7860/docs
echo TTS接口: http://localhost:7860/api/tts

python api_server.py

pause
"""
    
    # Linux shell脚本
    run_enhanced_sh = """#!/bin/bash
echo "========================================"
echo "   IndexTTS Enhanced WebUI 启动脚本"
echo "========================================"

# 激活conda环境
echo "正在激活conda环境 [index-tts]..."
source ~/miniconda3/bin/activate index-tts || {
    echo "❌ conda环境激活失败，请检查环境名称"
    exit 1
}

echo "✅ conda环境激活成功"
python --version

echo "正在启动IndexTTS增强版Web界面..."
echo "功能包括："
echo "- 音色保存和管理"
echo "- 完整API接口"  
echo "- 增强Web界面"

python webui_enhanced.py --host 0.0.0.0 --port 7860 --enable_api
"""
    
    run_api_sh = """#!/bin/bash
echo "========================================"
echo "     IndexTTS API服务器 启动脚本"
echo "========================================"

# 激活conda环境
echo "正在激活conda环境 [index-tts]..."
source ~/miniconda3/bin/activate index-tts || {
    echo "❌ conda环境激活失败，请检查环境名称"
    exit 1
}

echo "✅ conda环境激活成功"
python --version

echo "正在启动IndexTTS API服务器..."
echo "API文档: http://localhost:7860/docs"
echo "TTS接口: http://localhost:7860/api/tts"

python api_server.py
"""
    
    # 写入启动脚本
    scripts = {
        "run_enhanced.bat": run_enhanced_bat,
        "run_api.bat": run_api_bat,
        "run_enhanced.sh": run_enhanced_sh,
        "run_api.sh": run_api_sh
    }
    
    for script_name, content in scripts.items():
        script_path = target_dir / script_name
        script_path.write_text(content, encoding='utf-8')
        
        # 为shell脚本添加执行权限
        if script_name.endswith('.sh'):
            try:
                os.chmod(script_path, 0o755)
            except:
                pass
        
        print(f"✅ 创建: {script_name}")
    
    # 创建音色数据库文件
    print("\n📊 创建音色数据库...")
    voices_json = target_dir / "voices" / "voices.json"
    if not voices_json.exists():
        default_voices = {
            "voices": [],
            "version": "1.0",
            "created_at": "2025-06-27"
        }
        voices_json.write_text(json.dumps(default_voices, ensure_ascii=False, indent=2), 
                             encoding='utf-8')
        print("✅ 创建音色数据库文件")
    
    # 更新配置文件
    print("\n⚙️  配置文件...")
    config_path = target_dir / "checkpoints" / "config.yaml"
    
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        default_config = """# IndexTTS Enhanced Configuration
server:
  host: "0.0.0.0"
  port: 7860
  enable_api: true

model:
  device: "cuda"  # 或 "cpu"
  cache_size: 3

voice_management:
  storage_path: "voices/"
  max_voices: 100
  
api:
  max_text_length: 500
  output_dir: "outputs/api/"
  cors_enabled: true

generation:
  default_temperature: 1.0
  default_top_p: 0.8
  max_length: 500
"""
        config_path.write_text(default_config, encoding='utf-8')
        print("✅ 创建默认配置文件")
    else:
        print("✅ 配置文件已存在")
    
    # 显示安装结果
    print("\n" + "="*60)
    print("🎉 IndexTTS Enhanced 安装完成！")
    print("="*60)
    print()
    print("📋 安装内容:")
    print(f"  ✅ 复制文件: {success_count}/{len(files_to_copy)}")
    print("  ✅ 启动脚本: run_enhanced.bat/sh")
    print("  ✅ 音色管理系统")
    print("  ✅ API接口支持")
    print()
    print("🚀 下一步操作:")
    print(f"  1. cd {target_dir}")
    print("  2. 安装依赖: pip install -r requirements_enhanced.txt")
    print("  3. 下载模型文件到checkpoints/目录")
    print("  4. 启动服务:")
    print("     Windows: run_enhanced.bat")
    print("     Linux:   ./run_enhanced.sh")
    print("     手动:    python webui_enhanced.py")
    print()
    print("🌐 访问地址:")
    print("  Web界面: http://localhost:7860")
    print("  API文档: http://localhost:7860/docs")
    print()
    print("📚 查看文档:")
    print("  用户指南: USER_GUIDE.md")
    print("  音色管理: VOICE_MANAGEMENT_GUIDE.md")
    print("  部署指南: DEPLOYMENT_GUIDE.md")
    print("="*60)
    
    print(f"\n✅ 安装完成！现在可以进入 '{target_dir}' 目录启动服务了。")

if __name__ == "__main__":
    main()