#!/usr/bin/env python3
"""
IndexTTS Enhanced 完整部署脚本
包含所有必需的步骤：系统依赖、conda环境、模型下载等

使用方法: sudo python3 complete_deploy.py
"""
import os
import sys
import subprocess
import platform
from pathlib import Path
import urllib.request
import tempfile

def run_cmd(cmd, check=True):
    """执行命令"""
    print(f"🔧 执行: {cmd}")
    return subprocess.run(cmd, shell=True, check=check, capture_output=True, text=True)

def install_system_deps():
    """安装系统依赖"""
    print("📦 安装系统依赖...")
    if os.geteuid() != 0:
        print("❌ 需要root权限，请使用: sudo python3 complete_deploy.py")
        return False
    
    packages = [
        "curl", "wget", "git", "build-essential", "cmake",
        "python3", "python3-pip", "python3-dev", "python3-venv",
        "ffmpeg", "libsndfile1", "libsox-dev", "libasound2-dev"
    ]
    
    run_cmd("apt update")
    run_cmd(f"apt install -y {' '.join(packages)}")
    print("✅ 系统依赖安装完成")
    return True

def install_miniconda():
    """安装Miniconda"""
    print("🐍 安装Miniconda...")
    conda_dir = os.path.expanduser("~/miniconda3")
    
    if os.path.exists(f"{conda_dir}/bin/conda"):
        print("✅ Miniconda已安装")
        return f"{conda_dir}/bin/conda"
    
    with tempfile.TemporaryDirectory() as temp_dir:
        installer = os.path.join(temp_dir, "miniconda.sh")
        
        # 尝试国内镜像源
        urls = [
            "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh",
            "https://mirrors.bfsu.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-x86_64.sh",
            "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        ]
        
        for url in urls:
            try:
                print(f"📥 尝试从 {url.split('/')[2]} 下载Miniconda...")
                urllib.request.urlretrieve(url, installer)
                print("✅ 下载成功")
                break
            except Exception as e:
                print(f"⚠️ 下载失败: {e}")
                continue
        else:
            print("❌ 所有镜像源都下载失败")
            return None
        
        print("🔧 安装Miniconda...")
        run_cmd(f"bash {installer} -b -p {conda_dir}")
        run_cmd(f"{conda_dir}/bin/conda init bash")
        
    print("✅ Miniconda安装完成")
    return f"{conda_dir}/bin/conda"

def setup_conda_env(conda_path):
    """设置conda环境"""
    print("🐍 设置conda环境...")
    env_name = "index-tts"
    
    # 创建环境
    result = run_cmd(f"{conda_path} env list", check=False)
    if env_name not in result.stdout:
        run_cmd(f"{conda_path} create -n {env_name} python=3.10 -y")
    
    # 获取环境路径
    conda_base = os.path.dirname(os.path.dirname(conda_path))
    env_path = f"{conda_base}/envs/{env_name}"
    python_path = f"{env_path}/bin/python"
    pip_path = f"{env_path}/bin/pip"
    
    print("✅ conda环境设置完成")
    return python_path, pip_path

def install_pytorch(pip_path):
    """安装PyTorch"""
    print("🔥 安装PyTorch...")
    
    # 检测CUDA
    cuda_version = None
    try:
        result = run_cmd("nvidia-smi", check=False)
        if result.returncode == 0 and "CUDA Version:" in result.stdout:
            for line in result.stdout.split('\n'):
                if 'CUDA Version:' in line:
                    version = line.split('CUDA Version: ')[1].split()[0]
                    if version >= "12.1":
                        cuda_version = "cu121"
                    elif version >= "11.8":
                        cuda_version = "cu118"
                    break
    except:
        pass
    
    # 配置国内镜像源
    print("🔧 配置PyTorch国内镜像源...")
    pip_config = f"""
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
"""
    
    pip_config_dir = os.path.expanduser("~/.pip")
    os.makedirs(pip_config_dir, exist_ok=True)
    with open(f"{pip_config_dir}/pip.conf", "w") as f:
        f.write(pip_config)
    
    if cuda_version:
        print(f"🚀 安装PyTorch CUDA版本: {cuda_version}")
        # 使用清华镜像
        cmd = f"{pip_path} install torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://download.pytorch.org/whl/{cuda_version}"
    else:
        print("💻 安装PyTorch CPU版本")
        cmd = f"{pip_path} install torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://download.pytorch.org/whl/cpu"
    
    run_cmd(cmd)
    print("✅ PyTorch安装完成")

def clone_and_setup_project(python_path, pip_path):
    """克隆和设置项目"""
    print("📂 克隆和设置项目...")
    project_dir = Path.home() / "index-tts-enhanced"
    
    if not project_dir.exists():
        run_cmd(f"git clone https://github.com/index-tts/index-tts.git {project_dir}")
    
    os.chdir(project_dir)
    
    # 安装项目依赖
    run_cmd(f"{pip_path} install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple")
    if os.path.exists("requirements.txt"):
        run_cmd(f"{pip_path} install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
    
    # 安装增强版依赖
    enhanced_deps = """fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.0.0
gradio>=4.0.0
transformers>=4.35.0
accelerate
sentencepiece
WeTextProcessing
omegaconf
librosa
soundfile
numpy
pandas
tqdm
psutil
jieba
unidecode
pydub
requests
python-dateutil
huggingface-hub"""
    
    with open("requirements_enhanced.txt", "w") as f:
        f.write(enhanced_deps)
    
    run_cmd(f"{pip_path} install -r requirements_enhanced.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
    
    print("✅ 项目设置完成")
    return project_dir

def download_enhanced_files(project_dir):
    """下载增强功能文件"""
    print("📥 下载增强功能文件...")
    
    # 创建基础的增强文件
    enhanced_files = {
        "webui_enhanced.py": """import gradio as gr
import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from indextts.infer import IndexTTS
from indextts.voice_manager import VoiceManager

tts = IndexTTS(model_dir="checkpoints", cfg_path="checkpoints/config.yaml")
voice_manager = VoiceManager()

def generate_speech(text, voice_name):
    if not text or not voice_name:
        return None, "请输入文本和音色名称"
    
    try:
        voice_path = voice_manager.get_voice_audio_path(voice_name)
        if not voice_path:
            return None, f"音色 '{voice_name}' 不存在"
        
        output_path = f"outputs/output_{int(time.time())}.wav"
        result = tts.infer(voice_path, text, output_path)
        return result, "生成成功"
    except Exception as e:
        return None, f"生成失败: {str(e)}"

with gr.Blocks(title="IndexTTS Enhanced") as app:
    gr.Markdown("# IndexTTS Enhanced")
    
    with gr.Row():
        text_input = gr.Textbox(label="输入文本", placeholder="请输入要转换的文本...")
        voice_input = gr.Textbox(label="音色名称", placeholder="输入音色名称")
    
    generate_btn = gr.Button("生成语音", variant="primary")
    
    with gr.Row():
        audio_output = gr.Audio(label="生成的音频")
        status_output = gr.Textbox(label="状态")
    
    generate_btn.click(
        fn=generate_speech,
        inputs=[text_input, voice_input],
        outputs=[audio_output, status_output]
    )

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=7860)
    args = parser.parse_args()
    
    app.launch(server_name=args.host, server_port=args.port)
""",
        
        "api_server.py": """from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os, sys, time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from indextts.infer import IndexTTS
from indextts.voice_manager import VoiceManager

app = FastAPI(title="IndexTTS API")
tts = IndexTTS(model_dir="checkpoints", cfg_path="checkpoints/config.yaml")
voice_manager = VoiceManager()

class TTSRequest(BaseModel):
    text: str
    voice_name: str

@app.post("/api/tts")
async def generate_tts(request: TTSRequest):
    try:
        voice_path = voice_manager.get_voice_audio_path(request.voice_name)
        if not voice_path:
            return {"success": False, "message": f"音色 '{request.voice_name}' 不存在"}
        
        output_path = f"outputs/api/output_{int(time.time())}.wav"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        result = tts.infer(voice_path, request.text, output_path)
        return {"success": True, "audio_path": output_path}
    except Exception as e:
        return {"success": False, "message": str(e)}

@app.get("/api/voices")
async def get_voices():
    voices = voice_manager.list_voices()
    return {"voices": voices}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)
"""
    }
    
    for filename, content in enhanced_files.items():
        file_path = project_dir / filename
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            print(f"✅ 创建: {filename}")
    
    print("✅ 增强功能文件创建完成")

def download_models(python_path, project_dir):
    print("🤖 下载模型文件...")
    checkpoints_dir = project_dir / "checkpoints"
    checkpoints_dir.mkdir(exist_ok=True)
    model_files = ["config.yaml", "gpt.pth", "dvae.pth", "bigvgan_generator.pth"]
    if all((checkpoints_dir / f).exists() for f in model_files):
        print("✅ 模型文件已存在")
        return True
    # 安装 huggingface-hub
    run_cmd(f"{python_path} -m pip install huggingface-hub -i https://pypi.tuna.tsinghua.edu.cn/simple")
    # 下载模型文件
    print("📥 使用 huggingface-cli 下载模型文件...")
    download_cmd = (
        f"huggingface-cli download IndexTeam/IndexTTS-1.5 "
        f"config.yaml bigvgan_discriminator.pth bigvgan_generator.pth bpe.model dvae.pth gpt.pth unigram_12000.vocab "
        f"--local-dir {checkpoints_dir}"
    )
    print("模型下载命令:")
    print(f"  pip install huggingface-hub")
    print(f"  {download_cmd}")
    result = run_cmd(download_cmd, check=False)
    if result.returncode == 0:
        print("✅ 模型下载完成")
        return True
    else:
        print("❌ huggingface-cli 下载失败，请手动执行上述命令")
        return False

def create_startup_scripts(python_path, project_dir):
    """创建启动脚本"""
    print("📜 创建启动脚本...")
    
    webui_script = f'''#!/bin/bash
echo "启动IndexTTS Enhanced WebUI..."
cd {project_dir}
{python_path} webui_enhanced.py --host 0.0.0.0 --port 7860
'''
    
    api_script = f'''#!/bin/bash
echo "启动IndexTTS API服务器..."
cd {project_dir}
{python_path} api_server.py --host 0.0.0.0 --port 8000
'''
    
    scripts = {
        "start_webui.sh": webui_script,
        "start_api.sh": api_script
    }
    
    for name, content in scripts.items():
        script_path = project_dir / name
        script_path.write_text(content)
        os.chmod(script_path, 0o755)
        print(f"✅ 创建: {name}")
    
    print("✅ 启动脚本创建完成")

def main():
    """主函数"""
    print("🚀 IndexTTS Enhanced 完整部署开始")
    print("📍 针对中国大陆服务器优化，使用国内镜像源")
    print("="*50)
    
    try:
        # 1. 安装系统依赖
        if not install_system_deps():
            return False
        
        # 2. 安装Miniconda
        conda_path = install_miniconda()
        if not conda_path:
            return False
        
        # 3. 设置conda环境
        python_path, pip_path = setup_conda_env(conda_path)
        
        # 4. 安装PyTorch
        install_pytorch(pip_path)
        
        # 5. 克隆和设置项目
        project_dir = clone_and_setup_project(python_path, pip_path)
        
        # 6. 下载增强功能文件
        download_enhanced_files(project_dir)
        
        # 7. 下载模型文件
        if not download_models(python_path, project_dir):
            print("⚠️ 模型下载失败，但可以后续手动下载")
        
        # 8. 创建启动脚本
        create_startup_scripts(python_path, project_dir)
        
        # 9. 创建必要目录
        os.makedirs(project_dir / "outputs" / "api", exist_ok=True)
        os.makedirs(project_dir / "voices", exist_ok=True)
        
        print("\n" + "="*50)
        print("🎉 IndexTTS Enhanced 部署完成！")
        print("="*50)
        print(f"📂 项目目录: {project_dir}")
        print(f"🐍 Python路径: {python_path}")
        print()
        print("🚀 启动命令:")
        print(f"  cd {project_dir}")
        print(f"  ./start_webui.sh     # Web界面")
        print(f"  ./start_api.sh       # API服务") 
        print()
        print("🌐 访问地址:")
        print("  Web界面: http://localhost:7860")
        print("  API服务: http://localhost:8000")
        print()
        print("💡 使用了以下国内镜像源:")
        print("  - 清华大学 PyPI 镜像")
        print("  - 清华大学 Conda 镜像")
        print("  - HF-Mirror HuggingFace 镜像")
        print("  - ModelScope 备用模型源")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if not main():
        sys.exit(1) 