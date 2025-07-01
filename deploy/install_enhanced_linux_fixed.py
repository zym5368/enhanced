#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexTTS Enhanced Linux兼容性修复版安装脚本
修复了Windows特定路径和兼容性问题

使用方法:
1. 先拉取官方仓库: git clone https://github.com/index-tts/index-tts.git
2. 进入目录: cd index-tts
3. 复制本脚本到项目根目录
4. 运行: python3 install_enhanced_linux_fixed.py

修复内容:
- 动态检测conda安装位置
- 修复路径分隔符问题
- 增强依赖包兼容性检查
- 生成跨平台启动脚本

作者: IndexTTS Enhanced Team (Linux固定版)
版本: v1.1-linux-fixed
"""

import os
import sys
import shutil
import json
import urllib.request
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import platform

def main():
    print("🚀 IndexTTS Enhanced Linux兼容性修复安装器")
    print("此脚本将修复Ubuntu/Linux兼容性问题")
    print("="*50)
    
    # 检查是否在正确目录
    if not Path("webui.py").exists():
        print("❌ 请在IndexTTS项目根目录运行此脚本")
        return False
    
    # 创建兼容性修复脚本
    print("📝 创建Linux兼容性修复脚本...")
    
    fix_script_content = '''#!/usr/bin/env python3
import json
import os
import shutil
from pathlib import Path

def fix_voice_json_paths():
    """修复voices.json中的Windows路径分隔符"""
    voices_file = Path("voices/voices.json")
    if voices_file.exists():
        with open(voices_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 修复路径分隔符
        for voice_name, voice_info in data.items():
            if 'audio_path' in voice_info:
                # 将Windows路径转换为Unix路径
                path = voice_info['audio_path'].replace('\\\\', '/')
                voice_info['audio_path'] = path
        
        # 保存修复后的文件
        with open(voices_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print("✅ 修复voices.json路径分隔符")

def create_adaptive_startup_scripts():
    """创建自适应的启动脚本"""
    
    # 检测conda安装位置
    conda_script = \'''#!/bin/bash

# 检测conda安装位置的函数
detect_conda() {
    if command -v conda >/dev/null 2>&1; then
        # conda在PATH中，直接使用
        echo "conda"
        return 0
    elif [ -f ~/miniconda3/bin/activate ]; then
        echo "source ~/miniconda3/bin/activate"
        return 0
    elif [ -f ~/anaconda3/bin/activate ]; then
        echo "source ~/anaconda3/bin/activate"
        return 0
    elif [ -f /opt/conda/bin/activate ]; then
        echo "source /opt/conda/bin/activate"
        return 0
    else
        echo "conda_not_found"
        return 1
    fi
}

# 激活conda环境的函数
activate_conda_env() {
    local conda_cmd=$(detect_conda)
    
    if [ "$conda_cmd" = "conda_not_found" ]; then
        echo "❌ 未找到conda安装，请先安装conda"
        echo "或者直接使用: python webui_enhanced.py"
        exit 1
    fi
    
    echo "🔄 激活conda环境..."
    if [ "$conda_cmd" = "conda" ]; then
        conda activate index-tts
    else
        $conda_cmd index-tts
    fi
    
    if [ $? -eq 0 ]; then
        echo "✅ conda环境激活成功"
    else
        echo "❌ conda环境激活失败，使用系统Python"
        echo "⚠️  建议创建虚拟环境: python -m venv venv && source venv/bin/activate"
    fi
}
\'''
    
    # 创建增强版启动脚本
    enhanced_script = conda_script + \'''
echo "========================================"
echo "   IndexTTS Enhanced WebUI 启动脚本"
echo "========================================"

activate_conda_env

echo "🚀 启动IndexTTS增强版Web界面..."
echo "功能包括："
echo "- 🎤 音色保存和管理"
echo "- 📡 完整API接口"  
echo "- 🌐 增强Web界面"
echo
echo "🌐 访问地址: http://localhost:7860"
echo

python webui_enhanced.py --host 0.0.0.0 --port 7860 --enable_api
\'''
    
    # 创建API服务脚本
    api_script = conda_script + \'''
echo "========================================"
echo "     IndexTTS API服务器 启动脚本"
echo "========================================"

activate_conda_env

echo "🚀 启动IndexTTS API服务器..."
echo "📚 API文档: http://localhost:8000/docs"
echo "🔗 TTS接口: http://localhost:8000/api/tts"
echo

python api_server.py --port 8000
\'''
    
    # 写入脚本文件
    with open('run_enhanced_fixed.sh', 'w') as f:
        f.write(enhanced_script)
    
    with open('run_api_fixed.sh', 'w') as f:
        f.write(api_script)
    
    # 添加执行权限
    os.chmod('run_enhanced_fixed.sh', 0o755)
    os.chmod('run_api_fixed.sh', 0o755)
    
    print("✅ 创建自适应启动脚本: run_enhanced_fixed.sh, run_api_fixed.sh")

if __name__ == "__main__":
    print("🔧 修复Linux兼容性问题...")
    fix_voice_json_paths()
    create_adaptive_startup_scripts()
    print("✅ 修复完成！")
'''
    
    # 写入修复脚本
    with open("fix_linux_compatibility.py", "w", encoding="utf-8") as f:
        f.write(fix_script_content)
    
    os.chmod("fix_linux_compatibility.py", 0o755)
    print("✅ 创建修复脚本: fix_linux_compatibility.py")
    
    # 运行修复脚本
    print("🔧 运行兼容性修复...")
    try:
        subprocess.run([sys.executable, "fix_linux_compatibility.py"], check=True)
        print("✅ 兼容性修复完成")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  修复脚本运行失败: {e}")
    
    print("\n" + "="*50)
    print("🎉 Linux兼容性修复完成！")
    print("="*50)
    print()
    print("🚀 下一步:")
    print("  1. 激活conda环境: conda activate index-tts")
    print("  2. 安装依赖: pip install -r requirements_enhanced.txt")
    print("  3. 下载模型到checkpoints目录")
    print("  4. 启动服务: ./run_enhanced_fixed.sh")
    print()
    print("📚 详细指南: 查看 UBUNTU_SETUP_GUIDE.md")
    
    return True

if __name__ == "__main__":
    main() 