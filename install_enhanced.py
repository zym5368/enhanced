#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexTTS Enhanced 一键安装脚本
在官方IndexTTS基础上自动安装增强功能

使用方法:
1. 先拉取官方仓库: git clone https://github.com/index-tts/index-tts.git
2. 进入目录: cd index-tts
3. 运行本脚本: python install_enhanced.py

作者: IndexTTS Enhanced Team
版本: v1.0
"""

import os
import sys
import shutil
import json
import urllib.request
import subprocess
from pathlib import Path
from typing import List, Dict

class EnhancedInstaller:
    def __init__(self):
        self.base_dir = Path.cwd()
        self.enhanced_files = {
            # 增强版文件及其下载URL
            "webui_enhanced.py": "https://raw.githubusercontent.com/zym5368/enhanced/main/webui_enhanced.py",
            "api_server.py": "https://raw.githubusercontent.com/zym5368/enhanced/main/api_server.py", 
            "indextts/voice_manager.py": "https://raw.githubusercontent.com/zym5368/enhanced/main/voice_manager.py",
            "requirements_enhanced.txt": "https://raw.githubusercontent.com/zym5368/enhanced/main/requirements_enhanced.txt",
            "test_api.py": "https://raw.githubusercontent.com/zym5368/enhanced/main/test_api.py",
            "USER_GUIDE.md": "https://raw.githubusercontent.com/zym5368/enhanced/main/USER_GUIDE.md",
            "VOICE_MANAGEMENT_GUIDE.md": "https://raw.githubusercontent.com/zym5368/enhanced/main/VOICE_MANAGEMENT_GUIDE.md",
            "DEPLOYMENT_GUIDE.md": "https://raw.githubusercontent.com/zym5368/enhanced/main/DEPLOYMENT_GUIDE.md"
        }
        
        # Windows批处理文件
        self.bat_files = {
            "run_enhanced.bat": self._generate_run_enhanced_bat(),
            "run_api.bat": self._generate_run_api_bat()
        }
        
        # Linux shell脚本
        self.shell_files = {
            "run_enhanced.sh": self._generate_run_enhanced_sh(),
            "run_api.sh": self._generate_run_api_sh()
        }

    def check_official_repo(self) -> bool:
        """检查是否在官方IndexTTS仓库目录中"""
        required_files = ["webui.py", "indextts", "checkpoints", "requirements.txt"]
        missing_files = []
        
        for file in required_files:
            if not (self.base_dir / file).exists():
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ 错误: 未找到以下官方文件: {', '.join(missing_files)}")
            print("请确保在官方IndexTTS仓库根目录中运行此脚本")
            return False
        
        print("✅ 检测到官方IndexTTS仓库")
        return True

    def backup_original_files(self) -> None:
        """备份原始文件"""
        backup_dir = self.base_dir / "backup_original"
        backup_dir.mkdir(exist_ok=True)
        
        # 备份可能被修改的文件
        files_to_backup = ["webui.py", "checkpoints/config.yaml"]
        
        for file_path in files_to_backup:
            src = self.base_dir / file_path
            if src.exists():
                dst = backup_dir / file_path
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                print(f"📁 备份: {file_path} -> backup_original/{file_path}")

    def download_file(self, url: str, file_path: Path) -> bool:
        """下载文件"""
        try:
            print(f"📥 下载: {file_path.name}")
            
            # 如果是从本地文件复制（开发模式）
            if url.startswith("file://"):
                local_path = Path(url[7:])  # 移除 file:// 前缀
                if local_path.exists():
                    shutil.copy2(local_path, file_path)
                    return True
                else:
                    print(f"⚠️  本地文件不存在: {local_path}")
                    return False
            
            # 从网络下载
            urllib.request.urlretrieve(url, file_path)
            return True
        except Exception as e:
            print(f"❌ 下载失败 {file_path.name}: {e}")
            return False

    def create_enhanced_files_from_local(self) -> bool:
        """从当前目录的文件创建增强文件（开发模式）"""
        print("🔧 从本地文件创建增强版文件...")
        
        # 检查本地是否有增强文件
        local_enhanced_files = {
            "webui_enhanced.py": self.base_dir / "webui_enhanced.py",
            "api_server.py": self.base_dir / "api_server.py",
            "indextts/voice_manager.py": self.base_dir / "indextts" / "voice_manager.py",
            "requirements_enhanced.txt": self.base_dir / "requirements_enhanced.txt",
            "test_api.py": self.base_dir / "test_api.py",
            "USER_GUIDE.md": self.base_dir / "USER_GUIDE.md",
            "VOICE_MANAGEMENT_GUIDE.md": self.base_dir / "VOICE_MANAGEMENT_GUIDE.md",
            "DEPLOYMENT_GUIDE.md": self.base_dir / "DEPLOYMENT_GUIDE.md"
        }
        
        # 如果本地有这些文件，说明是开发模式
        local_files_exist = sum(1 for f in local_enhanced_files.values() if f.exists())
        
        if local_files_exist >= 4:  # 如果超过一半的文件存在
            print("✅ 检测到本地增强文件，使用本地版本")
            return True
        
        return False

    def install_enhanced_files(self) -> bool:
        """安装增强文件"""
        print("📦 安装IndexTTS增强功能...")
        
        # 检查是否使用本地文件
        use_local = self.create_enhanced_files_from_local()
        
        success_count = 0
        total_files = len(self.enhanced_files)
        
        for file_path, url in self.enhanced_files.items():
            target_path = self.base_dir / file_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            if use_local:
                # 如果文件已存在就跳过
                if target_path.exists():
                    print(f"✅ 已存在: {file_path}")
                    success_count += 1
                    continue
            
            # 下载或复制文件
            if self.download_file(url, target_path):
                success_count += 1
            else:
                # 如果下载失败，尝试创建默认版本
                if self._create_default_file(file_path, target_path):
                    success_count += 1
        
        print(f"📊 文件安装情况: {success_count}/{total_files} 成功")
        return success_count >= total_files * 0.8  # 80%成功率认为安装成功

    def _create_default_file(self, file_path: str, target_path: Path) -> bool:
        """创建默认文件内容"""
        try:
            if file_path == "requirements_enhanced.txt":
                content = self._generate_requirements_enhanced()
            elif file_path.endswith(".md"):
                content = f"# {file_path}\n\n增强功能文档，请参考官方仓库获取最新版本。\n"
            elif file_path == "test_api.py":
                content = self._generate_test_api_py()
            else:
                return False
            
            target_path.write_text(content, encoding='utf-8')
            print(f"📝 创建默认文件: {file_path}")
            return True
        except Exception as e:
            print(f"❌ 创建默认文件失败 {file_path}: {e}")
            return False

    def create_startup_scripts(self) -> None:
        """创建启动脚本"""
        print("📜 创建启动脚本...")
        
        # Windows批处理文件
        for filename, content in self.bat_files.items():
            file_path = self.base_dir / filename
            file_path.write_text(content, encoding='utf-8')
            print(f"✅ 创建: {filename}")
        
        # Linux shell脚本
        for filename, content in self.shell_files.items():
            file_path = self.base_dir / filename
            file_path.write_text(content, encoding='utf-8')
            # 添加执行权限
            try:
                os.chmod(file_path, 0o755)
            except:
                pass
            print(f"✅ 创建: {filename}")

    def create_directories(self) -> None:
        """创建必要目录"""
        print("📁 创建目录结构...")
        
        directories = [
            "voices",
            "outputs/api", 
            "outputs/webui",
            "logs"
        ]
        
        for dir_path in directories:
            (self.base_dir / dir_path).mkdir(parents=True, exist_ok=True)
            print(f"📂 创建目录: {dir_path}")

    def update_config_yaml(self) -> None:
        """更新配置文件"""
        config_path = self.base_dir / "checkpoints" / "config.yaml"
        
        if not config_path.exists():
            print("⚠️  配置文件不存在，创建默认配置")
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

    def install_dependencies(self) -> bool:
        """安装增强版依赖"""
        print("📦 安装增强版依赖...")
        
        requirements_file = self.base_dir / "requirements_enhanced.txt"
        if not requirements_file.exists():
            print("⚠️  requirements_enhanced.txt 不存在，跳过依赖安装")
            return False
        
        try:
            # 检查pip
            subprocess.run([sys.executable, "-m", "pip", "--version"], 
                         check=True, capture_output=True)
            
            # 安装依赖
            print("🔄 正在安装Python依赖包...")
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", 
                "-r", str(requirements_file)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ 依赖安装成功")
                return True
            else:
                print(f"❌ 依赖安装失败: {result.stderr}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ pip命令执行失败: {e}")
            return False
        except FileNotFoundError:
            print("❌ 未找到pip，请确保Python环境正确")
            return False

    def create_voices_json(self) -> None:
        """创建音色数据库文件"""
        voices_json = self.base_dir / "voices" / "voices.json"
        if not voices_json.exists():
            default_voices = {
                "voices": [],
                "version": "1.0",
                "created_at": "2025-06-27"
            }
            voices_json.write_text(json.dumps(default_voices, ensure_ascii=False, indent=2), 
                                 encoding='utf-8')
            print("✅ 创建音色数据库文件")

    def _generate_requirements_enhanced(self) -> str:
        """生成增强版依赖文件内容"""
        return """# IndexTTS Enhanced 额外依赖
fastapi>=0.104.1
uvicorn>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.2.1
jinja2>=3.1.2
python-jose>=3.3.0
passlib>=1.7.4
bcrypt>=4.1.2
redis>=5.0.1
celery>=5.3.4
psutil>=5.9.6
requests>=2.31.0
pydantic>=2.5.0
typing-extensions>=4.8.0
"""

    def _generate_test_api_py(self) -> str:
        """生成API测试文件内容"""
        return '''#!/usr/bin/env python3
"""
IndexTTS Enhanced API 测试脚本
"""
import requests
import json

def test_api():
    base_url = "http://localhost:7860"
    
    # 测试音色列表
    print("测试音色列表...")
    try:
        response = requests.get(f"{base_url}/api/voices")
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.json()}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    test_api()
'''

    def _generate_run_enhanced_bat(self) -> str:
        """生成Windows增强版启动脚本"""
        return """@echo off
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
echo - 🎤 音色保存和管理
echo - 📡 完整API接口
echo - 🌐 增强Web界面

python webui_enhanced.py --host 0.0.0.0 --port 7860 --enable_api

pause
"""

    def _generate_run_api_bat(self) -> str:
        """生成Windows API服务启动脚本"""
        return """@echo off
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

    def _generate_run_enhanced_sh(self) -> str:
        """生成Linux增强版启动脚本"""
        return """#!/bin/bash
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
echo "- 🎤 音色保存和管理"
echo "- 📡 完整API接口"  
echo "- 🌐 增强Web界面"

python webui_enhanced.py --host 0.0.0.0 --port 7860 --enable_api
"""

    def _generate_run_api_sh(self) -> str:
        """生成Linux API服务启动脚本"""
        return """#!/bin/bash
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

    def print_success_message(self) -> None:
        """打印安装成功信息"""
        print("\n" + "="*60)
        print("🎉 IndexTTS Enhanced 安装完成！")
        print("="*60)
        print()
        print("📋 安装内容:")
        print("  ✅ 增强版Web界面 (webui_enhanced.py)")
        print("  ✅ API服务器 (api_server.py)")
        print("  ✅ 音色管理系统 (indextts/voice_manager.py)")
        print("  ✅ 启动脚本 (run_enhanced.bat/sh)")
        print("  ✅ 使用文档 (USER_GUIDE.md)")
        print()
        print("🚀 启动方式:")
        print("  Windows: run_enhanced.bat")
        print("  Linux:   ./run_enhanced.sh")
        print("  手动:    python webui_enhanced.py")
        print()
        print("🌐 访问地址:")
        print("  Web界面: http://localhost:7860")
        print("  API文档: http://localhost:7860/docs")
        print()
        print("📚 文档:")
        print("  用户指南: USER_GUIDE.md")
        print("  音色管理: VOICE_MANAGEMENT_GUIDE.md")
        print("  部署指南: DEPLOYMENT_GUIDE.md")
        print()
        print("❓ 遇到问题？查看故障排除指南或提交Issue")
        print("="*60)

    def run(self) -> bool:
        """运行安装流程"""
        print("🚀 IndexTTS Enhanced 一键安装器 v1.0")
        print("="*50)
        
        # 1. 检查官方仓库
        if not self.check_official_repo():
            return False
        
        # 2. 备份原始文件
        self.backup_original_files()
        
        # 3. 创建目录结构
        self.create_directories()
        
        # 4. 安装增强文件
        if not self.install_enhanced_files():
            print("❌ 增强文件安装失败，但可以继续使用基础功能")
        
        # 5. 创建启动脚本
        self.create_startup_scripts()
        
        # 6. 更新配置文件
        self.update_config_yaml()
        
        # 7. 创建音色数据库
        self.create_voices_json()
        
        # 8. 安装依赖
        deps_success = self.install_dependencies()
        if not deps_success:
            print("⚠️  依赖安装失败，请手动运行: pip install -r requirements_enhanced.txt")
        
        # 9. 显示成功信息
        self.print_success_message()
        
        return True


def main():
    """主函数"""
    try:
        installer = EnhancedInstaller()
        success = installer.run()
        
        if success:
            print("\n✅ 安装完成！现在可以启动IndexTTS Enhanced了。")
            sys.exit(0)
        else:
            print("\n❌ 安装失败，请检查错误信息。")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️ 安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 安装过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 