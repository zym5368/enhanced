import json
import os
import sys
import threading
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional

import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
sys.path.append(os.path.join(current_dir, "indextts"))

import argparse
import pandas as pd
import gradio as gr
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from indextts.infer import IndexTTS
from indextts.voice_manager import VoiceManager
from tools.i18n.i18n import I18nAuto
import traceback

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
    filename: Optional[str] = None  # 自定义文件名（不包含扩展名）

class TTSResponse(BaseModel):
    success: bool
    message: str
    audio_url: Optional[str] = None
    task_id: Optional[str] = None

# 解析命令行参数
parser = argparse.ArgumentParser(description="IndexTTS Enhanced WebUI with API")
parser.add_argument("--verbose", action="store_true", default=False, help="Enable verbose mode")
parser.add_argument("--port", type=int, default=7860, help="Port to run the web UI on")
parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the web UI on")
parser.add_argument("--model_dir", type=str, default="checkpoints", help="Model checkpoints directory")
parser.add_argument("--enable_api", action="store_true", default=True, help="Enable API endpoints")
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
i18n = I18nAuto(language="zh_CN")
tts = IndexTTS(model_dir=cmd_args.model_dir, cfg_path=os.path.join(cmd_args.model_dir, "config.yaml"))
voice_manager = VoiceManager()

# 创建必要目录
os.makedirs("outputs/tasks", exist_ok=True)
os.makedirs("outputs/api", exist_ok=True)
os.makedirs("prompts", exist_ok=True)

# 加载示例
with open("tests/cases.jsonl", "r", encoding="utf-8") as f:
    example_cases = []
    for line in f:
        line = line.strip()
        if not line:
            continue
        example = json.loads(line)
        example_cases.append([os.path.join("tests", example.get("prompt_audio", "sample_prompt.wav")),
                              example.get("text"), ["普通推理", "批次推理"][example.get("infer_mode", 0)]])

def generate_tts_internal(prompt_audio_path, text, infer_mode, max_text_tokens_per_sentence=120, 
                         sentences_bucket_max_size=4, custom_filename=None, **generation_kwargs):
    """内部TTS生成函数"""
    if not prompt_audio_path:
        return None, "请提供参考音频"
    
    if not text or not text.strip():
        return None, "请输入文本内容"
    
    # 生成输出路径
    task_id = str(uuid.uuid4())
    
    # 支持自定义文件名
    if custom_filename:
        # 清理文件名，移除非法字符
        import re
        safe_filename = re.sub(r'[<>:"/\\|?*]', '_', custom_filename)
        filename = f"{safe_filename}.wav"
    else:
        filename = f"tts_{task_id}.wav"
    
    output_path = os.path.join("outputs", "api", filename)
    
    # 如果文件已存在，添加时间戳
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_part = filename.replace('.wav', '')
        filename = f"{name_part}_{timestamp}.wav"
        output_path = os.path.join("outputs", "api", filename)
    
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
        
        if result and os.path.exists(output_path):
            return output_path, "生成成功"
        else:
            return None, "生成失败"
            
    except Exception as e:
        tb = traceback.format_exc()
        return None, f"生成失败: {str(e)}\n{tb}"

def gen_single(prompt, text, infer_mode, max_text_tokens_per_sentence=120, sentences_bucket_max_size=4,
               *args, progress=gr.Progress()):
    """单个音频生成"""
    if not prompt:
        return gr.update(value=None), "请先上传参考音频"
    
    output_path = os.path.join("outputs", f"spk_{int(time.time())}.wav")
    tts.gr_progress = progress
    
    do_sample, top_p, top_k, temperature, \
        length_penalty, num_beams, repetition_penalty, max_mel_tokens = args
    
    kwargs = {
        "do_sample": bool(do_sample),
        "top_p": float(top_p),
        "top_k": int(top_k) if int(top_k) > 0 else None,
        "temperature": float(temperature),
        "length_penalty": float(length_penalty),
        "num_beams": num_beams,
        "repetition_penalty": float(repetition_penalty),
        "max_mel_tokens": int(max_mel_tokens),
    }
    
    try:
        if infer_mode == "普通推理":
            output = tts.infer(prompt, text, output_path, verbose=cmd_args.verbose,
                              max_text_tokens_per_sentence=int(max_text_tokens_per_sentence),
                              **kwargs)
        else:
            output = tts.infer_fast(prompt, text, output_path, verbose=cmd_args.verbose,
                                   max_text_tokens_per_sentence=int(max_text_tokens_per_sentence),
                                   sentences_bucket_max_size=int(sentences_bucket_max_size),
                                   **kwargs)
        return gr.update(value=output, visible=True), "生成成功"
    except Exception as e:
        return gr.update(value=None), f"生成失败: {str(e)}"

def save_voice_action(prompt_audio, voice_name, voice_description):
    """保存音色动作"""
    if not prompt_audio:
        return "请先上传音频文件", gr.update(), gr.update()
    
    if not voice_name or not voice_name.strip():
        return "请输入音色名称", gr.update(), gr.update()
    
    voice_name = voice_name.strip()
    result = voice_manager.save_voice(prompt_audio, voice_name, voice_description or "")
    
    if result["success"]:
        # 更新音色列表
        voices_list = get_voices_list()
        new_value = voices_list[0] if voices_list else None
        return result["message"], gr.update(choices=voices_list, value=new_value), gr.update(choices=voices_list, value=new_value)
    else:
        return result["message"], gr.update(), gr.update()

def delete_voice_action(voice_name):
    """删除音色动作"""
    if not voice_name or voice_name is None:
        return "请选择要删除的音色", gr.update(), gr.update()
    
    result = voice_manager.delete_voice(voice_name)
    
    if result["success"]:
        voices_list = get_voices_list()
        new_value = voices_list[0] if voices_list else None
        return result["message"], gr.update(choices=voices_list, value=new_value), gr.update(choices=voices_list, value=new_value)
    else:
        return result["message"], gr.update(), gr.update()

def get_voices_list():
    """获取音色列表"""
    voices = voice_manager.list_voices()
    return [voice["name"] for voice in voices]

def load_voice_action(voice_name):
    """加载选中的音色"""
    if not voice_name or voice_name is None:
        return gr.update(), "请选择音色"
    
    audio_path = voice_manager.get_voice_audio_path(voice_name)
    if audio_path:
        return gr.update(value=audio_path), f"已加载音色: {voice_name}"
    else:
        return gr.update(), f"音色文件不存在: {voice_name}"

def get_voices_table():
    """获取音色表格数据"""
    voices = voice_manager.list_voices()
    if not voices:
        return []
    
    data = []
    for voice in voices:
        data.append([
            voice["name"],
            voice.get("description", ""),
            f"{voice.get('duration', 0):.1f}s",
            datetime.fromtimestamp(voice.get("created_time", 0)).strftime("%Y-%m-%d %H:%M:%S"),
            f"{voice.get('file_size', 0) / 1024:.1f}KB"
        ])
    return data

def update_prompt_audio():
    """更新音频上传状态"""
    return gr.update(interactive=True)

def on_input_text_change(text, max_tokens_per_sentence):
    """文本变化时预览分句"""
    if text and len(text) > 0:
        text_tokens_list = tts.tokenizer.tokenize(text)
        sentences = tts.tokenizer.split_sentences(text_tokens_list, max_tokens_per_sentence=int(max_tokens_per_sentence))
        data = []
        for i, s in enumerate(sentences):
            sentence_str = ''.join(s)
            tokens_count = len(s)
            data.append([i, sentence_str, tokens_count])
        
        return gr.update(value=data, visible=True, type="array")
    else:
        return gr.update(value=[])

# 创建Gradio界面
with gr.Blocks(title="IndexTTS Enhanced Demo") as demo:
    mutex = threading.Lock()
    
    gr.HTML('''
    <h2><center>IndexTTS Enhanced: 音色保存功能 + API接口</h2>
    <h2><center>(Enhanced IndexTTS with Voice Management & API)</h2>
    <p align="center">
    <a href='https://arxiv.org/abs/2502.05512'><img src='https://img.shields.io/badge/ArXiv-2502.05512-red'></a>
    </p>
    ''')
    
    with gr.Tab("🎤 音频生成"):
        with gr.Row():
            with gr.Column(scale=1):
                prompt_audio = gr.Audio(label="参考音频", sources=["upload", "microphone"], type="filepath")
                
                # 音色保存功能
                with gr.Group():
                    gr.Markdown("### 💾 保存音色")
                    voice_name_input = gr.Textbox(label="音色名称", placeholder="给这个音色起个名字...")
                    voice_description_input = gr.Textbox(label="音色描述", placeholder="描述这个音色的特点（可选）")
                    save_voice_btn = gr.Button("保存音色", variant="secondary")
                
                # 加载已保存音色
                with gr.Group():
                    gr.Markdown("### 📂 加载音色")
                    voices_choices = get_voices_list()
                    saved_voices_dropdown = gr.Dropdown(
                        label="选择音色", 
                        choices=voices_choices,
                        value=voices_choices[0] if voices_choices else None,
                        interactive=True
                    )
                    load_voice_btn = gr.Button("加载音色", variant="secondary")
                
            with gr.Column(scale=2):
                input_text_single = gr.TextArea(
                    label="文本", 
                    placeholder="请输入目标文本", 
                    info=f"当前模型版本{tts.model_version or '1.0'}"
                )
                infer_mode = gr.Radio(
                    choices=["普通推理", "批次推理"], 
                    label="推理模式",
                    info="批次推理：更适合长句，性能翻倍",
                    value="普通推理"
                )
                gen_button = gr.Button("🎵 生成语音", variant="primary")
                
                status_text = gr.Textbox(label="状态", interactive=False)
                output_audio = gr.Audio(label="生成结果", visible=True)
        
        # 高级参数设置
        with gr.Accordion("⚙️ 高级生成参数设置", open=False):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("**GPT2 采样设置**")
                    with gr.Row():
                        do_sample = gr.Checkbox(label="do_sample", value=True, info="是否进行采样")
                        temperature = gr.Slider(label="temperature", minimum=0.1, maximum=2.0, value=1.0, step=0.1)
                    with gr.Row():
                        top_p = gr.Slider(label="top_p", minimum=0.0, maximum=1.0, value=0.8, step=0.01)
                        top_k = gr.Slider(label="top_k", minimum=0, maximum=100, value=30, step=1)
                        num_beams = gr.Slider(label="num_beams", value=3, minimum=1, maximum=10, step=1)
                    with gr.Row():
                        repetition_penalty = gr.Number(label="repetition_penalty", value=10.0, minimum=0.1, maximum=20.0, step=0.1)
                        length_penalty = gr.Number(label="length_penalty", value=0.0, minimum=-2.0, maximum=2.0, step=0.1)
                    max_mel_tokens = gr.Slider(
                        label="max_mel_tokens", 
                        value=600, 
                        minimum=50, 
                        maximum=tts.cfg.gpt.max_mel_tokens, 
                        step=10, 
                        info="生成Token最大数量"
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("**分句设置**")
                    with gr.Row():
                        max_text_tokens_per_sentence = gr.Slider(
                            label="分句最大Token数", 
                            value=120, 
                            minimum=20, 
                            maximum=tts.cfg.gpt.max_text_tokens, 
                            step=2,
                            info="建议80~200之间"
                        )
                        sentences_bucket_max_size = gr.Slider(
                            label="分句分桶的最大容量（批次推理生效）", 
                            value=4, 
                            minimum=1, 
                            maximum=16, 
                            step=1,
                            info="建议2-8之间"
                        )
                    
                    with gr.Accordion("预览分句结果", open=True):
                        sentences_preview = gr.Dataframe(
                            headers=["序号", "分句内容", "Token数"],
                            wrap=True
                        )
        
        advanced_params = [
            do_sample, top_p, top_k, temperature,
            length_penalty, num_beams, repetition_penalty, max_mel_tokens
        ]
        
        # 示例
        if len(example_cases) > 0:
            gr.Examples(
                examples=example_cases,
                inputs=[prompt_audio, input_text_single, infer_mode]
            )
    
    with gr.Tab("📚 音色管理"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("### 已保存的音色")
                voices_table = gr.Dataframe(
                    headers=["音色名称", "描述", "时长", "创建时间", "文件大小"],
                    value=get_voices_table(),
                    interactive=False
                )
                refresh_btn = gr.Button("🔄 刷新列表")
                
            with gr.Column():
                gr.Markdown("### 音色操作")
                delete_voices_choices = get_voices_list()
                delete_voice_dropdown = gr.Dropdown(
                    label="选择要删除的音色",
                    choices=delete_voices_choices,
                    value=delete_voices_choices[0] if delete_voices_choices else None
                )
                delete_voice_btn = gr.Button("🗑️ 删除音色", variant="stop")
                delete_status = gr.Textbox(label="操作状态", interactive=False)
    
    with gr.Tab("🔌 API说明"):
        gr.Markdown("""
        ### API接口使用说明
        
        本系统提供RESTful API接口，可以通过HTTP请求调用TTS功能，适合集成到dify工作流中。
        
        #### 1. 生成语音 API
        **支持两种接口和两种响应格式**
        
        **接口1: POST /api/tts (返回JSON响应)**
        - 返回包含音频URL的JSON响应
        
        **接口2: POST /api/tts/file (直接返回音频文件)**
        - 直接返回音频文件，无需二次请求
        
        **参数传递方式:**
        
        **方式1: JSON Body (推荐)**
        ```json
        {
            "text": "要转换的文本",
            "voice_name": "音色名称",
            "infer_mode": "普通推理",
            "max_text_tokens_per_sentence": 120,
            "temperature": 1.0,
            "top_p": 0.8,
            "top_k": 30,
            "return_file": false
        }
        ```
        
        **方式2: URL参数**
        ```
        POST /api/tts?text=要转换的文本&voice_name=音色名称&return_file=true
        ```
        
        **响应:**
        - `/api/tts`: JSON格式 `{"success": true, "audio_url": "/api/audio/xxx.wav"}`
        - `/api/tts/file`: 直接返回wav音频文件
        - 或在任意接口中添加 `return_file=true` 参数直接返回音频文件
        
        #### 2. 获取音色列表 API
        - **URL**: `GET /api/voices`
        - **响应**: 返回所有可用音色列表
        
        #### 3. 下载音频文件
        - **URL**: `GET /api/audio/{filename}`
        - **响应**: 返回音频文件
        
        #### Dify工作流集成示例
        在dify工作流中，您可以使用HTTP节点调用API：
        1. 设置请求URL为: `http://your-server:7860/api/tts`
        2. 设置请求方法为: `POST`
        3. 设置Content-Type为: `application/json`
        4. 在请求体中传入文本和音色名称
        5. 从响应中获取audio_url进行后续处理
        """)
    
    # 事件绑定
    prompt_audio.upload(update_prompt_audio, outputs=[gen_button])
    
    # 生成语音
    gen_button.click(
        gen_single,
        inputs=[prompt_audio, input_text_single, infer_mode,
                max_text_tokens_per_sentence, sentences_bucket_max_size] + advanced_params,
        outputs=[output_audio, status_text]
    )
    
    # 保存音色
    save_voice_btn.click(
        save_voice_action,
        inputs=[prompt_audio, voice_name_input, voice_description_input],
        outputs=[status_text, saved_voices_dropdown, delete_voice_dropdown]
    )
    
    # 加载音色
    load_voice_btn.click(
        load_voice_action,
        inputs=[saved_voices_dropdown],
        outputs=[prompt_audio, status_text]
    )
    
    # 删除音色
    delete_voice_btn.click(
        delete_voice_action,
        inputs=[delete_voice_dropdown],
        outputs=[delete_status, saved_voices_dropdown, delete_voice_dropdown]
    )
    
    # 刷新音色列表
    def refresh_voices():
        voices_list = get_voices_list()
        table_data = get_voices_table()
        new_value = voices_list[0] if voices_list else None
        return table_data, gr.update(choices=voices_list, value=new_value), gr.update(choices=voices_list, value=new_value)
    
    refresh_btn.click(
        refresh_voices,
        outputs=[voices_table, saved_voices_dropdown, delete_voice_dropdown]
    )
    
    # 文本变化预览
    input_text_single.change(
        on_input_text_change,
        inputs=[input_text_single, max_text_tokens_per_sentence],
        outputs=[sentences_preview]
    )
    max_text_tokens_per_sentence.change(
        on_input_text_change,
        inputs=[input_text_single, max_text_tokens_per_sentence],
        outputs=[sentences_preview]
    )

# 创建FastAPI应用
if cmd_args.enable_api:
    from fastapi import Request
    app = FastAPI(title="IndexTTS API", description="IndexTTS API for dify workflow integration")

    async def _process_tts_request(request: TTSRequest):
        """处理TTS请求的共用函数"""
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
            output_path, message = generate_tts_internal(
                audio_path,
                request.text,
                request.infer_mode,
                request.max_text_tokens_per_sentence,
                request.sentences_bucket_max_size,
                custom_filename=request.filename,
                **generation_kwargs
            )
            
            if output_path:
                # 生成音频URL
                filename = os.path.basename(output_path)
                audio_url = f"/api/audio/{filename}"
                
                # 正确计算task_id
                if filename.startswith("tts_") and filename.endswith(".wav"):
                    task_id = filename.replace("tts_", "").replace(".wav", "")
                else:
                    task_id = filename.replace(".wav", "")
                
                return TTSResponse(
                    success=True,
                    message=message,
                    audio_url=audio_url,
                    task_id=task_id
                )
            else:
                return TTSResponse(success=False, message=message)
                
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/api/tts", response_model=TTSResponse)
    async def api_tts(request: Request):
        """TTS API接口 - 返回JSON响应（包含音频URL）"""
        return await _handle_tts_request(request, return_file=False)
    
    @app.post("/api/tts/file")
    async def api_tts_file(request: Request):
        """TTS API接口 - 直接返回音频文件"""
        return await _handle_tts_request(request, return_file=True)
    
    async def _handle_tts_request(request: Request, return_file: bool = False):
        """处理TTS请求的统一函数"""
        try:
            content_type = request.headers.get("content-type", "")
            
            # 检查是否有return_file参数
            params = dict(request.query_params)
            if params.get("return_file", "false").lower() == "true":
                return_file = True
            
            if "application/json" in content_type:
                # JSON body
                body = await request.json()
                return_file = body.pop("return_file", return_file)  # 从body中提取return_file参数
                tts_request = TTSRequest(**body)
            else:
                # URL参数 (适用于GET风格的POST请求)
                if not params.get("text") or not params.get("voice_name"):
                    raise HTTPException(status_code=400, detail="缺少必需参数: text 和 voice_name")
                
                # 转换参数类型
                tts_request = TTSRequest(
                    text=params.get("text"),
                    voice_name=params.get("voice_name"),
                    infer_mode=params.get("infer_mode", "普通推理"),
                    max_text_tokens_per_sentence=int(params.get("max_text_tokens_per_sentence", 120)),
                    sentences_bucket_max_size=int(params.get("sentences_bucket_max_size", 4)),
                    do_sample=params.get("do_sample", "true").lower() == "true",
                    top_p=float(params.get("top_p", 0.8)),
                    top_k=int(params.get("top_k", 30)),
                    temperature=float(params.get("temperature", 1.0)),
                    length_penalty=float(params.get("length_penalty", 0.0)),
                    num_beams=int(params.get("num_beams", 3)),
                    repetition_penalty=float(params.get("repetition_penalty", 10.0)),
                    max_mel_tokens=int(params.get("max_mel_tokens", 600)),
                    filename=params.get("filename")
                )
            
            # 处理TTS请求
            result = await _process_tts_request(tts_request)
            
            if return_file and result.success and result.audio_url:
                # 直接返回音频文件
                filename = result.audio_url.split("/")[-1]
                file_path = os.path.join("outputs", "api", filename)
                if os.path.exists(file_path):
                    return FileResponse(
                        file_path, 
                        media_type="audio/wav", 
                        filename=f"tts_{tts_request.voice_name}_{result.task_id}.wav"
                    )
                else:
                    raise HTTPException(status_code=404, detail="音频文件未找到")
            else:
                # 返回JSON响应
                return result
            
        except ValueError as e:
            tb = traceback.format_exc()
            return {"success": False, "message": f"参数格式错误: {str(e)}\n{tb}"}
        except Exception as e:
            tb = traceback.format_exc()
            return {"success": False, "message": f"生成失败: {str(e)}\n{tb}"}

    @app.get("/api/voices")
    async def api_get_voices():
        """获取音色列表API"""
        try:
            voices = voice_manager.list_voices()
            return {"success": True, "voices": voices}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/audio/{filename}")
    async def api_get_audio(filename: str):
        """获取音频文件API"""
        file_path = os.path.join("outputs", "api", filename)
        if os.path.exists(file_path):
            return FileResponse(file_path, media_type="audio/wav", filename=filename)
        else:
            raise HTTPException(status_code=404, detail="音频文件不存在")

    # 将FastAPI应用挂载到Gradio
    demo = gr.mount_gradio_app(app, demo, path="")

if __name__ == "__main__":
    if cmd_args.enable_api:
        print(f"🚀 启动IndexTTS Enhanced WebUI + API服务")
        print(f"🌐 Web界面: http://{cmd_args.host}:{cmd_args.port}")
        print(f"📡 API文档: http://{cmd_args.host}:{cmd_args.port}/docs")
        print(f"🎵 TTS API: http://{cmd_args.host}:{cmd_args.port}/api/tts")
        print(f"📚 音色列表: http://{cmd_args.host}:{cmd_args.port}/api/voices")
        
        import uvicorn
        uvicorn.run(app, host=cmd_args.host, port=cmd_args.port)
    else:
        print(f"🚀 启动IndexTTS Enhanced WebUI (仅Web界面)")
        print(f"🌐 Web界面: http://{cmd_args.host}:{cmd_args.port}")
        demo.queue(20)
        demo.launch(server_name=cmd_args.host, server_port=cmd_args.port) 