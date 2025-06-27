#!/usr/bin/env python3
"""
IndexTTS API 测试脚本
用于测试音色保存功能和API接口
"""

import requests
import json
import time
import os

# 配置
API_BASE_URL = "http://localhost:8000"
TEST_TEXT = "大家好，我是IndexTTS语音合成系统，很高兴为您服务！"

def test_api_status():
    """测试API状态"""
    print("🔍 测试API状态...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ API服务正常运行")
            print(f"   - 模型版本: {data.get('model_version', '未知')}")
            print(f"   - 音色数量: {data.get('voices_count', 0)}")
            print(f"   - 模型目录: {data.get('model_dir', '未知')}")
            return True
        else:
            print(f"❌ API状态检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API连接失败: {e}")
        return False

def test_get_voices():
    """测试获取音色列表"""
    print("\n📚 测试获取音色列表...")
    try:
        response = requests.get(f"{API_BASE_URL}/api/voices")
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                voices = data["voices"]
                print(f"✅ 成功获取音色列表 ({len(voices)}个音色)")
                for voice in voices:
                    print(f"   - {voice['name']}: {voice.get('description', '无描述')}")
                return voices
            else:
                print("❌ 获取音色列表失败")
                return []
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return []

def test_tts_generation(voice_name):
    """测试TTS生成"""
    print(f"\n🎵 测试TTS生成 (音色: {voice_name})...")
    
    payload = {
        "text": TEST_TEXT,
        "voice_name": voice_name,
        "infer_mode": "普通推理",
        "temperature": 1.0,
        "top_p": 0.8,
        "top_k": 30
    }
    
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE_URL}/api/tts", 
            json=payload,
            timeout=60  # 60秒超时
        )
        duration = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                print(f"✅ TTS生成成功")
                print(f"   - 音频URL: {data['audio_url']}")
                print(f"   - 任务ID: {data['task_id']}")
                print(f"   - 生成耗时: {data.get('duration', 0):.2f}秒")
                print(f"   - 请求总耗时: {duration:.2f}秒")
                return data["audio_url"]
            else:
                print(f"❌ TTS生成失败: {data['message']}")
                return None
        else:
            print(f"❌ 请求失败: {response.status_code}")
            if response.headers.get('content-type', '').startswith('application/json'):
                error_data = response.json()
                print(f"   错误详情: {error_data.get('detail', '未知错误')}")
            return None
    except requests.exceptions.Timeout:
        print(f"❌ 请求超时 (>{60}秒)")
        return None
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return None

def test_audio_download(audio_url):
    """测试音频下载"""
    print(f"\n📥 测试音频下载...")
    try:
        full_url = f"{API_BASE_URL}{audio_url}"
        response = requests.get(full_url)
        
        if response.status_code == 200:
            print(f"✅ 音频下载成功")
            print(f"   - 文件大小: {len(response.content)} 字节")
            print(f"   - 内容类型: {response.headers.get('content-type', '未知')}")
            
            # 保存到本地测试
            test_file = "test_output.wav"
            with open(test_file, "wb") as f:
                f.write(response.content)
            print(f"   - 已保存到: {test_file}")
            return True
        else:
            print(f"❌ 音频下载失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载异常: {e}")
        return False

def test_api_performance(voice_name, test_count=3):
    """测试API性能"""
    print(f"\n⚡ 性能测试 (运行{test_count}次)...")
    
    times = []
    for i in range(test_count):
        print(f"  第{i+1}次测试...", end=" ")
        
        payload = {
            "text": f"这是第{i+1}次性能测试，{TEST_TEXT}",
            "voice_name": voice_name,
            "infer_mode": "普通推理"
        }
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_BASE_URL}/api/tts", json=payload)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data["success"]:
                    times.append(duration)
                    print(f"✅ {duration:.2f}秒")
                else:
                    print(f"❌ 失败: {data['message']}")
            else:
                print(f"❌ HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ 异常: {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        print(f"\n📊 性能统计:")
        print(f"   - 平均耗时: {avg_time:.2f}秒")
        print(f"   - 最快耗时: {min_time:.2f}秒")
        print(f"   - 最慢耗时: {max_time:.2f}秒")

def main():
    """主测试函数"""
    print("=" * 50)
    print("      IndexTTS API 测试脚本")
    print("=" * 50)
    
    # 1. 测试API状态
    if not test_api_status():
        print("\n❌ API服务不可用，请先启动API服务器")
        print("   运行命令: python api_server.py")
        return
    
    # 2. 获取音色列表
    voices = test_get_voices()
    if not voices:
        print("\n⚠️  没有可用的音色，请先在Web界面中保存音色")
        print("   访问地址: http://localhost:7860")
        return
    
    # 选择第一个音色进行测试
    test_voice = voices[0]["name"]
    print(f"\n🎯 使用音色 '{test_voice}' 进行测试")
    
    # 3. 测试TTS生成
    audio_url = test_tts_generation(test_voice)
    if not audio_url:
        print("\n❌ TTS生成失败，测试终止")
        return
    
    # 4. 测试音频下载
    test_audio_download(audio_url)
    
    # 5. 性能测试
    test_api_performance(test_voice)
    
    print("\n" + "=" * 50)
    print("🎉 API测试完成！")
    print("=" * 50)

if __name__ == "__main__":
    main() 