import json
import os
import sys
import uuid
import time
from typing import Dict, List, Optional

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "indextts"))

import argparse
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from indextts.infer import IndexTTS
from indextts.voice_manager import VoiceManager

# API请求模型
class TTSRequest(BaseModel):
    text: str
    voice_name: str
    infer_mode: str = "普通推理"
    max_text_tokens_per_sentence: int = 120
    sentences_bucket_max_size: int = 4
    do_sample: bool = True
    top_p: float = 0.8
    top_k: int = 30
    temperature: float = 1.0
    length_penalty: float = 0.0
    num_beams: int = 3
    repetition_penalty: float = 10.0
    max_mel_tokens: int = 600

class TTSResponse(BaseModel):
    success: bool
    message: str
    audio_url: Optional[str] = None
    task_id: Optional[str] = None
    duration: Optional[float] = None

class VoiceListResponse(BaseModel):
    success: bool
    voices: List[Dict]

# 解析命令行参数
parser = argparse.ArgumentParser(description="IndexTTS API Server")
parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose mode")
parser.add_argument("--port", type=int, default=8000, help="Port to run the API server on")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the API server on")
parser.add_argument("--model_dir", type=str, default="checkpoints", help="Model checkpoints directory")
cmd_args = parser.parse_args()

# 检查模型文件
if not os.path.exists(cmd_args.model_dir):
    print(f"Model directory {cmd_args.model_dir} does not exist. Please download the model first.")
    sys.exit(1)

for file in [
    "bigvgan_generator.pth",
    "bpe.model", 
    "gpt.pth",
    "config.yaml",
]:
    file_path = os.path.join(cmd_args.model_dir, file)
    if not os.path.exists(file_path):
        print(f"Required file {file_path} does not exist. Please download it.")
        sys.exit(1)

# 初始化组件
print("正在加载模型...")
tts = IndexTTS(model_dir=cmd_args.model_dir, cfg_path=os.path.join(cmd_args.model_dir, "config.yaml"))
voice_manager = VoiceManager()
print("模型加载完成!")

# 创建必要目录
os.makedirs("outputs/api", exist_ok=True)

# 创建FastAPI应用
app = FastAPI(
    title="IndexTTS API",
    description="IndexTTS API for dify workflow integration",
    version="1.0.0"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_tts_internal(prompt_audio_path, text, infer_mode, max_text_tokens_per_sentence=120, 
                         sentences_bucket_max_size=4, **generation_kwargs):
    """内部TTS生成函数"""
    if not prompt_audio_path:
        return None, "请提供参考音频", 0
    
    if not text or not text.strip():
        return None, "请输入文本内容", 0
    
    # 生成输出路径
    task_id = str(uuid.uuid4())
    output_path = os.path.join("outputs", "api", f"tts_{task_id}.wav")
    
    start_time = time.time()
    
    try:
        if infer_mode == "普通推理":
            result = tts.infer(prompt_audio_path, text, output_path, verbose=cmd_args.verbose,
                              max_text_tokens_per_sentence=int(max_text_tokens_per_sentence),
                              **generation_kwargs)
        else:
            # 批次推理
            result = tts.infer_fast(prompt_audio_path, text, output_path, verbose=cmd_args.verbose,
                                   max_text_tokens_per_sentence=int(max_text_tokens_per_sentence),
                                   sentences_bucket_max_size=int(sentences_bucket_max_size),
                                   **generation_kwargs)
        
        duration = time.time() - start_time
        
        if result and os.path.exists(output_path):
            return output_path, "生成成功", duration
        else:
            return None, "生成失败", duration
            
    except Exception as e:
        duration = time.time() - start_time
        return None, f"生成失败: {str(e)}", duration

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "IndexTTS API Server", 
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "tts": "/api/tts",
            "voices": "/api/voices",
            "audio": "/api/audio/{filename}"
        }
    }

@app.post("/api/tts", response_model=TTSResponse)
async def api_tts(request: TTSRequest):
    """TTS API接口"""
    try:
        # 检查音色是否存在
        audio_path = voice_manager.get_voice_audio_path(request.voice_name)
        if not audio_path:
            raise HTTPException(status_code=400, detail=f"音色 '{request.voice_name}' 不存在")
        
        # 准备生成参数
        generation_kwargs = {
            "do_sample": request.do_sample,
            "top_p": request.top_p,
            "top_k": request.top_k,
            "temperature": request.temperature,
            "length_penalty": request.length_penalty,
            "num_beams": request.num_beams,
            "repetition_penalty": request.repetition_penalty,
            "max_mel_tokens": request.max_mel_tokens,
        }
        
        # 生成语音
        output_path, message, duration = generate_tts_internal(
            audio_path,
            request.text,
            request.infer_mode,
            request.max_text_tokens_per_sentence,
            request.sentences_bucket_max_size,
            **generation_kwargs
        )
        
        if output_path:
            # 生成音频URL
            filename = os.path.basename(output_path)
            audio_url = f"/api/audio/{filename}"
            
            return TTSResponse(
                success=True,
                message=message,
                audio_url=audio_url,
                task_id=filename.replace("tts_", "").replace(".wav", ""),
                duration=duration
            )
        else:
            return TTSResponse(success=False, message=message, duration=duration)
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/voices", response_model=VoiceListResponse)
async def api_get_voices():
    """获取音色列表API"""
    try:
        voices = voice_manager.list_voices()
        return VoiceListResponse(success=True, voices=voices)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
async def api_get_audio(filename: str):
    """获取音频文件API"""
    file_path = os.path.join("outputs", "api", filename)
    if os.path.exists(file_path):
        return FileResponse(
            file_path, 
            media_type="audio/wav", 
            filename=filename,
            headers={"Cache-Control": "max-age=3600"}  # 缓存1小时
        )
    else:
        raise HTTPException(status_code=404, detail="音频文件不存在")

@app.get("/api/status")
async def api_status():
    """获取服务状态"""
    voices_count = len(voice_manager.list_voices())
    return {
        "status": "running",
        "model_version": getattr(tts, 'model_version', '1.0'),
        "voices_count": voices_count,
        "model_dir": cmd_args.model_dir
    }

@app.delete("/api/cleanup")
async def api_cleanup():
    """清理临时文件"""
    try:
        import glob
        api_files = glob.glob("outputs/api/tts_*.wav")
        
        # 删除1小时前的文件
        current_time = time.time()
        deleted_count = 0
        
        for file_path in api_files:
            file_time = os.path.getctime(file_path)
            if current_time - file_time > 3600:  # 1小时
                os.remove(file_path)
                deleted_count += 1
        
        return {
            "success": True,
            "message": f"清理了 {deleted_count} 个临时文件"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    print(f"🚀 启动IndexTTS API服务器")
    print(f"📡 API地址: http://{cmd_args.host}:{cmd_args.port}")
    print(f"📖 API文档: http://{cmd_args.host}:{cmd_args.port}/docs")
    print(f"🎵 TTS接口: http://{cmd_args.host}:{cmd_args.port}/api/tts")
    print(f"📚 音色列表: http://{cmd_args.host}:{cmd_args.port}/api/voices")
    print("=" * 50)
    
    # 显示当前可用音色
    voices = voice_manager.list_voices()
    if voices:
        print(f"📋 当前可用音色 ({len(voices)}个):")
        for voice in voices[:5]:  # 只显示前5个
            print(f"  - {voice['name']}: {voice.get('description', '无描述')}")
        if len(voices) > 5:
            print(f"  ... 还有 {len(voices) - 5} 个音色")
    else:
        print("⚠️  暂无保存的音色，请先使用Web界面保存音色")
    
    print("=" * 50)
    
    uvicorn.run(
        app, 
        host=cmd_args.host, 
        port=cmd_args.port,
        log_level="info"
    ) 