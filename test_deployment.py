#!/usr/bin/env python3
"""
IndexTTS Enhanced 部署测试脚本
验证部署是否成功，所有组件是否正常工作

使用方法: python3 test_deployment.py
"""

import os
import sys
import time
import requests
from pathlib import Path

def test_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    
    try:
        import torch
        print(f"  ✅ PyTorch: {torch.__version__}")
        print(f"  🚀 CUDA可用: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"  🎮 GPU: {torch.cuda.get_device_name(0)}")
    except ImportError as e:
        print(f"  ❌ PyTorch导入失败: {e}")
        return False
    
    try:
        import torchaudio
        print(f"  ✅ TorchAudio: {torchaudio.__version__}")
    except ImportError as e:
        print(f"  ❌ TorchAudio导入失败: {e}")
        return False
    
    try:
        import gradio
        print(f"  ✅ Gradio: {gradio.__version__}")
    except ImportError as e:
        print(f"  ❌ Gradio导入失败: {e}")
        return False
    
    try:
        import fastapi
        print(f"  ✅ FastAPI: {fastapi.__version__}")
    except ImportError as e:
        print(f"  ❌ FastAPI导入失败: {e}")
        return False
    
    print("✅ 基础导入测试通过")
    return True

def test_project_structure():
    """测试项目结构"""
    print("🔍 测试项目结构...")
    
    required_files = [
        "checkpoints/config.yaml",
        "checkpoints/gpt.pth", 
        "checkpoints/dvae.pth",
        "indextts/infer.py",
        "indextts/voice_manager.py",
        "webui_enhanced.py",
        "api_server.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            size_mb = os.path.getsize(file_path) / (1024*1024)
            print(f"  ✅ {file_path}: {size_mb:.1f} MB")
    
    if missing_files:
        print("  ❌ 缺少文件:")
        for file_path in missing_files:
            print(f"    - {file_path}")
        return False
    
    print("✅ 项目结构测试通过")
    return True

def test_model_loading():
    """测试模型加载"""
    print("🔍 测试模型加载...")
    
    try:
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from indextts.infer import IndexTTS
        
        print("  🔧 初始化IndexTTS...")
        tts = IndexTTS(model_dir="checkpoints", cfg_path="checkpoints/config.yaml")
        print("  ✅ 模型加载成功")
        
        # 测试音色管理器
        from indextts.voice_manager import VoiceManager
        voice_manager = VoiceManager()
        print("  ✅ 音色管理器初始化成功")
        
        return True
        
    except Exception as e:
        print(f"  ❌ 模型加载失败: {e}")
        return False

def test_api_server(host="localhost", port=8000, timeout=30):
    """测试API服务器"""
    print(f"🔍 测试API服务器 (http://{host}:{port})...")
    
    # 等待服务启动
    print(f"  ⏳ 等待API服务启动 (最多{timeout}秒)...")
    for i in range(timeout):
        try:
            response = requests.get(f"http://{host}:{port}/", timeout=5)
            if response.status_code in [200, 404]:  # 404也表示服务在运行
                print("  ✅ API服务响应正常")
                break
        except requests.exceptions.RequestException:
            if i == timeout - 1:
                print("  ❌ API服务无响应")
                return False
            time.sleep(1)
            print(f"    等待中... ({i+1}/{timeout})")
    
    # 测试API端点
    try:
        # 测试音色列表
        response = requests.get(f"http://{host}:{port}/api/voices", timeout=10)
        if response.status_code == 200:
            voices = response.json()
            print(f"  ✅ 音色列表获取成功: {len(voices.get('voices', []))} 个音色")
        else:
            print(f"  ⚠️  音色列表API返回状态码: {response.status_code}")
        
        # 测试TTS API（如果有音色）
        if voices.get('voices'):
            test_voice = voices['voices'][0]['name']
            tts_data = {
                "text": "这是一个测试",
                "voice_name": test_voice
            }
            response = requests.post(f"http://{host}:{port}/api/tts", 
                                   json=tts_data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                if result.get('success'):
                    print("  ✅ TTS API测试成功")
                else:
                    print(f"  ⚠️  TTS API返回错误: {result.get('message')}")
            else:
                print(f"  ⚠️  TTS API返回状态码: {response.status_code}")
        else:
            print("  ℹ️  跳过TTS测试（无可用音色）")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API测试失败: {e}")
        return False

def test_webui_server(host="localhost", port=7860, timeout=30):
    """测试WebUI服务器"""
    print(f"🔍 测试WebUI服务器 (http://{host}:{port})...")
    
    # 等待服务启动
    print(f"  ⏳ 等待WebUI服务启动 (最多{timeout}秒)...")
    for i in range(timeout):
        try:
            response = requests.get(f"http://{host}:{port}/", timeout=5)
            if response.status_code == 200:
                print("  ✅ WebUI服务响应正常")
                return True
        except requests.exceptions.RequestException:
            if i == timeout - 1:
                print("  ❌ WebUI服务无响应")
                return False
            time.sleep(1)
            print(f"    等待中... ({i+1}/{timeout})")
    
    return False

def run_full_test():
    """运行完整测试"""
    print("🚀 IndexTTS Enhanced 部署测试开始")
    print("=" * 50)
    
    tests = [
        ("基础导入", test_imports),
        ("项目结构", test_project_structure), 
        ("模型加载", test_model_loading),
    ]
    
    # 运行基础测试
    failed_tests = []
    for test_name, test_func in tests:
        print(f"\n📍 {test_name}测试")
        print("-" * 30)
        
        try:
            if not test_func():
                failed_tests.append(test_name)
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            failed_tests.append(test_name)
    
    # 服务测试需要手动启动服务
    print(f"\n📍 服务测试")
    print("-" * 30)
    print("ℹ️  服务测试需要手动启动服务后运行:")
    print("  启动API服务: ./start_api.sh")
    print("  测试API: python3 test_deployment.py --api")
    print("  启动WebUI: ./start_webui.sh") 
    print("  测试WebUI: python3 test_deployment.py --webui")
    
    # 总结
    print(f"\n" + "=" * 50)
    if failed_tests:
        print(f"⚠️  测试完成，{len(failed_tests)}个测试失败:")
        for test in failed_tests:
            print(f"  - {test}")
        print("\n💡 建议:")
        print("  1. 检查上述输出的错误信息")
        print("  2. 确保模型文件完整下载")
        print("  3. 检查依赖包是否正确安装")
        return False
    else:
        print("✅ 所有基础测试通过！")
        print("\n🎉 部署验证成功！")
        print("💡 接下来可以:")
        print("  1. 启动服务: ./start_webui.sh")
        print("  2. 访问Web界面: http://localhost:7860")
        print("  3. 上传音色文件开始使用")
        return True

def main():
    """主函数"""
    import argparse
    parser = argparse.ArgumentParser(description="IndexTTS Enhanced 部署测试")
    parser.add_argument("--api", action="store_true", help="仅测试API服务")
    parser.add_argument("--webui", action="store_true", help="仅测试WebUI服务")
    parser.add_argument("--host", default="localhost", help="服务器地址")
    parser.add_argument("--api-port", type=int, default=8000, help="API端口")
    parser.add_argument("--webui-port", type=int, default=7860, help="WebUI端口")
    
    args = parser.parse_args()
    
    if args.api:
        success = test_api_server(args.host, args.api_port)
        sys.exit(0 if success else 1)
    elif args.webui:
        success = test_webui_server(args.host, args.webui_port)
        sys.exit(0 if success else 1)
    else:
        success = run_full_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 