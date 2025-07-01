#!/usr/bin/env python3
"""
IndexTTS Enhanced API 使用示例

演示如何使用IndexTTS Enhanced的API接口进行文本转语音

使用前请确保：
1. 已经部署并启动了IndexTTS Enhanced服务
2. 已经上传了至少一个音色
3. 服务正在运行（http://localhost:7860 或你的服务器地址）
"""

import requests
import json
import time
import os
from typing import List, Dict, Optional

class IndexTTSClient:
    """IndexTTS Enhanced API客户端"""
    
    def __init__(self, base_url: str = "http://localhost:7860"):
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api"
    
    def get_voices(self) -> List[Dict]:
        """获取所有可用音色"""
        try:
            response = requests.get(f"{self.api_base}/voices", timeout=10)
            response.raise_for_status()
            data = response.json()
            return data.get('voices', [])
        except Exception as e:
            print(f"获取音色列表失败: {e}")
            return []
    
    def text_to_speech(self, text: str, voice_name: str, output_path: Optional[str] = None) -> Optional[str]:
        """文本转语音"""
        try:
            payload = {
                "text": text,
                "voice_name": voice_name
            }
            
            response = requests.post(
                f"{self.api_base}/tts",
                json=payload,
                timeout=60  # TTS可能需要较长时间
            )
            response.raise_for_status()
            
            result = response.json()
            if result.get('success'):
                audio_path = result.get('audio_path')
                if output_path and audio_path:
                    # 如果指定了输出路径，下载音频文件
                    self.download_audio(audio_path, output_path)
                    return output_path
                return audio_path
            else:
                print(f"TTS失败: {result.get('message')}")
                return None
                
        except Exception as e:
            print(f"文本转语音失败: {e}")
            return None
    
    def download_audio(self, audio_path: str, output_path: str):
        """下载音频文件"""
        try:
            # 构建下载URL
            download_url = f"{self.base_url}/file={audio_path}"
            
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"音频文件已下载到: {output_path}")
            
        except Exception as e:
            print(f"下载音频文件失败: {e}")
    
    def test_connection(self) -> bool:
        """测试连接"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except:
            return False

def example_basic_usage():
    """基础使用示例"""
    print("=" * 50)
    print("🎤 IndexTTS Enhanced API 基础使用示例")
    print("=" * 50)
    
    # 初始化客户端
    client = IndexTTSClient("http://localhost:7860")
    
    # 测试连接
    print("🔍 测试连接...")
    if not client.test_connection():
        print("❌ 无法连接到IndexTTS服务，请确保服务已启动")
        return
    print("✅ 连接成功")
    
    # 获取音色列表
    print("\n📋 获取音色列表...")
    voices = client.get_voices()
    if not voices:
        print("❌ 没有可用的音色，请先上传音色文件")
        return
    
    print(f"✅ 找到 {len(voices)} 个音色:")
    for i, voice in enumerate(voices):
        print(f"  {i+1}. {voice['name']} - {voice.get('description', '无描述')}")
    
    # 选择第一个音色进行测试
    test_voice = voices[0]['name']
    print(f"\n🎯 使用音色: {test_voice}")
    
    # 文本转语音
    test_texts = [
        "你好，这是IndexTTS Enhanced的测试。",
        "今天天气真不错，适合出去走走。",
        "科技改变生活，人工智能让世界更美好。"
    ]
    
    print("\n🎵 开始文本转语音测试...")
    for i, text in enumerate(test_texts):
        print(f"\n测试 {i+1}/3: {text}")
        
        start_time = time.time()
        audio_path = client.text_to_speech(text, test_voice)
        end_time = time.time()
        
        if audio_path:
            print(f"✅ 生成成功! 耗时: {end_time - start_time:.2f}秒")
            print(f"📁 音频文件: {audio_path}")
        else:
            print("❌ 生成失败")
        
        time.sleep(1)  # 避免请求过于频繁

def example_batch_processing():
    """批量处理示例"""
    print("\n" + "=" * 50)
    print("🔄 批量处理示例")
    print("=" * 50)
    
    client = IndexTTSClient("http://localhost:7860")
    
    # 获取音色列表
    voices = client.get_voices()
    if not voices:
        print("❌ 没有可用的音色")
        return
    
    # 批量文本
    batch_texts = [
        "欢迎使用IndexTTS Enhanced",
        "这是一个强大的文本转语音系统",
        "支持多种音色和语言",
        "生成高质量的语音输出",
        "感谢您的使用"
    ]
    
    voice_name = voices[0]['name']
    print(f"🎯 使用音色: {voice_name}")
    print(f"📝 处理 {len(batch_texts)} 段文本...")
    
    results = []
    total_start = time.time()
    
    for i, text in enumerate(batch_texts):
        print(f"\n处理 {i+1}/{len(batch_texts)}: {text[:20]}...")
        
        start_time = time.time()
        audio_path = client.text_to_speech(text, voice_name)
        end_time = time.time()
        
        result = {
            "text": text,
            "audio_path": audio_path,
            "duration": end_time - start_time,
            "success": audio_path is not None
        }
        results.append(result)
        
        if result["success"]:
            print(f"✅ 成功 ({result['duration']:.2f}s)")
        else:
            print("❌ 失败")
    
    total_time = time.time() - total_start
    success_count = sum(1 for r in results if r["success"])
    
    print(f"\n📊 批处理完成:")
    print(f"  总耗时: {total_time:.2f}秒")
    print(f"  成功率: {success_count}/{len(batch_texts)} ({success_count/len(batch_texts)*100:.1f}%)")
    print(f"  平均每段: {total_time/len(batch_texts):.2f}秒")

def example_voice_comparison():
    """多音色对比示例"""
    print("\n" + "=" * 50)
    print("🎭 多音色对比示例")
    print("=" * 50)
    
    client = IndexTTSClient("http://localhost:7860")
    
    # 获取音色列表
    voices = client.get_voices()
    if len(voices) < 2:
        print("❌ 需要至少2个音色进行对比测试")
        return
    
    test_text = "这是一段用于测试不同音色效果的文本。"
    print(f"📝 测试文本: {test_text}")
    
    print(f"\n🎯 使用 {min(3, len(voices))} 个音色进行对比:")
    
    for i, voice in enumerate(voices[:3]):  # 最多测试3个音色
        print(f"\n音色 {i+1}: {voice['name']}")
        print(f"描述: {voice.get('description', '无描述')}")
        
        start_time = time.time()
        audio_path = client.text_to_speech(test_text, voice['name'])
        end_time = time.time()
        
        if audio_path:
            print(f"✅ 生成成功 ({end_time - start_time:.2f}s)")
            print(f"📁 文件: {audio_path}")
        else:
            print("❌ 生成失败")

def example_error_handling():
    """错误处理示例"""
    print("\n" + "=" * 50)
    print("🛠️ 错误处理示例")
    print("=" * 50)
    
    client = IndexTTSClient("http://localhost:7860")
    
    # 测试不存在的音色
    print("🧪 测试不存在的音色...")
    result = client.text_to_speech("测试文本", "不存在的音色")
    if result is None:
        print("✅ 正确处理了不存在的音色错误")
    
    # 测试空文本
    voices = client.get_voices()
    if voices:
        print("\n🧪 测试空文本...")
        result = client.text_to_speech("", voices[0]['name'])
        if result is None:
            print("✅ 正确处理了空文本错误")
    
    # 测试过长文本
    print("\n🧪 测试过长文本...")
    long_text = "这是一段很长的文本。" * 100  # 创建很长的文本
    if voices:
        result = client.text_to_speech(long_text[:500], voices[0]['name'])  # 截断到合理长度
        if result:
            print("✅ 成功处理较长文本")
        else:
            print("⚠️ 长文本处理失败")

def main():
    """主函数"""
    print("🚀 IndexTTS Enhanced API 使用示例")
    print("请确保IndexTTS Enhanced服务正在运行...")
    
    # 运行所有示例
    example_basic_usage()
    
    input("\n按回车键继续批量处理示例...")
    example_batch_processing()
    
    input("\n按回车键继续多音色对比示例...")
    example_voice_comparison()
    
    input("\n按回车键继续错误处理示例...")
    example_error_handling()
    
    print("\n🎉 所有示例完成!")
    print("💡 更多用法请参考API文档: http://localhost:7860/docs")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 示例已停止")
    except Exception as e:
        print(f"\n❌ 运行示例时出错: {e}")
        import traceback
        traceback.print_exc() 