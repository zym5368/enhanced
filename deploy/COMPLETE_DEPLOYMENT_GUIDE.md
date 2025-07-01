# IndexTTS Enhanced 完整部署指南

## 🎯 概述

这是一个一键部署脚本，能够在Ubuntu服务器上自动完成IndexTTS Enhanced的完整安装，包括：

- ✅ 系统依赖安装（FFmpeg、开发工具等）
- ✅ Miniconda环境配置
- ✅ PyTorch安装（自动检测CUDA版本）
- ✅ 项目依赖安装
- ✅ 模型文件下载（3GB+）
- ✅ 增强功能安装（API、Web界面、音色管理）
- ✅ 启动脚本创建
- ✅ 目录结构初始化

**🇨🇳 特别优化**：针对中国大陆服务器进行了优化，使用国内镜像源，大幅提升下载速度！

## 🚀 一键部署

### 准备工作

1. **服务器要求**
   - Ubuntu 18.04+ / Debian 10+
   - 至少20GB可用磁盘空间
   - 推荐16GB+内存
   - 稳定的网络连接（国内镜像源，速度较快）

2. **权限要求**
   - sudo权限（安装系统依赖需要）

### 部署步骤

1. **下载部署脚本**
```bash
# 从你的GitHub仓库下载
git clone https://github.com/zym5368/enhanced.git
cd index-tts-enhanced
```

2. **执行一键部署**
```bash
# 需要sudo权限安装系统依赖
sudo python3 deploy/complete_deploy.py
```

3. **等待部署完成**
   - 系统依赖安装：~3分钟（国内服务器）
   - Miniconda下载安装：~2分钟（清华镜像）
   - PyTorch安装：~5分钟（清华PyPI镜像）
   - 项目依赖安装：~3分钟（清华PyPI镜像）
   - 模型下载：~5-15分钟（HF-Mirror国内镜像）
   - **总耗时：~20-30分钟**（相比国外镜像节省50%+时间）

## 🇨🇳 国内镜像源优化

### 使用的镜像源

1. **Miniconda安装**
   - 🥇 清华大学镜像：`mirrors.tuna.tsinghua.edu.cn`
   - 🥈 北京外国语大学镜像：`mirrors.bfsu.edu.cn`
   - 🥉 官方源（备用）：`repo.anaconda.com`

2. **Python包安装（PyPI）**
   - 🥇 清华大学镜像：`pypi.tuna.tsinghua.edu.cn`
   - 自动配置pip.conf全局使用

3. **模型文件下载**
   - 🥇 HF-Mirror镜像：`hf-mirror.com`
   - 🥈 ModelScope：`modelscope.cn`
   - 🥉 HuggingFace官方（备用）：`huggingface.co`

4. **PyTorch安装**
   - 清华PyPI镜像 + PyTorch官方源混合

### 下载速度对比

| 项目 | 国外源 | 国内镜像 | 提升倍数 |
|------|--------|----------|----------|
| Miniconda | 30MB/s | 100MB/s | 3.3x |
| PyPI包 | 5MB/s | 50MB/s | 10x |
| 模型文件 | 2MB/s | 20MB/s | 10x |
| **总体** | **40-60分钟** | **20-30分钟** | **2x** |

## 📂 部署后的目录结构

```
~/index-tts-enhanced/
├── checkpoints/                 # 模型文件
│   ├── config.yaml
│   ├── gpt.pth
│   ├── dvae.pth
│   ├── bigvgan_generator.pth
│   └── ...
├── indextts/                    # 核心代码
│   ├── infer.py
│   ├── voice_manager.py
│   └── ...
├── outputs/                     # 输出目录
│   ├── api/                     # API输出
│   └── webui/                   # Web界面输出
├── voices/                      # 音色库
│   └── voices.json
├── webui_enhanced.py            # 增强版Web界面
├── api_server.py                # API服务器
├── requirements_enhanced.txt    # 增强版依赖
├── start_webui.sh              # Web界面启动脚本
├── start_api.sh                # API服务启动脚本
└── test_api.py                 # API测试脚本
```

## 🌟 启动服务

部署完成后，切换到项目目录：

```bash
cd ~/index-tts-enhanced
```

### 启动Web界面（推荐）

```bash
# 启动增强版Web界面（包含API）
./start_webui.sh

# 或者手动启动
~/miniconda3/envs/index-tts/bin/python webui_enhanced.py --host 0.0.0.0 --port 7860
```

**访问地址**: http://你的服务器IP:7860

### 启动独立API服务

```bash
# 启动独立API服务器
./start_api.sh

# 或者手动启动
~/miniconda3/envs/index-tts/bin/python api_server.py --host 0.0.0.0 --port 8000
```

**API文档**: http://你的服务器IP:8000/docs

## 🧪 测试验证

### 1. 基础功能测试

```bash
cd ~/index-tts-enhanced

# 测试模型加载
~/miniconda3/envs/index-tts/bin/python -c "
from indextts.infer import IndexTTS
tts = IndexTTS(model_dir='checkpoints', cfg_path='checkpoints/config.yaml')
print('✅ 模型加载成功')
"
```

### 2. API测试

```bash
# 启动Web界面后，测试API
python3 test_api.py
```

### 3. 手动测试API

```bash
# 获取音色列表
curl http://localhost:7860/api/voices

# 测试TTS（需要先添加音色）
curl -X POST http://localhost:7860/api/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是测试",
    "voice_name": "测试音色"
  }'
```

## 🔧 故障排除

### 常见问题

1. **模型下载失败**
```bash
cd ~/index-tts-enhanced

# 方法1：使用HF-Mirror镜像
export HF_ENDPOINT=https://hf-mirror.com
~/miniconda3/envs/index-tts/bin/python -c "
from huggingface_hub import snapshot_download
snapshot_download('IndexTeam/IndexTTS-1.5', local_dir='checkpoints')
"

# 方法2：使用ModelScope
~/miniconda3/envs/index-tts/bin/python -c "
from modelscope import snapshot_download
snapshot_download('IndexTeam/IndexTTS-1.5', cache_dir='checkpoints')
"

# 方法3：手动下载
# 访问 https://hf-mirror.com/IndexTeam/IndexTTS-1.5
# 或访问 https://modelscope.cn/models/IndexTeam/IndexTTS-1.5
```

2. **PyTorch CUDA版本不匹配**
```bash
# 检查CUDA版本
nvidia-smi

# 重新安装对应PyTorch（使用清华镜像）
pip_path=~/miniconda3/envs/index-tts/bin/pip
$pip_path uninstall torch torchaudio -y
$pip_path install torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://download.pytorch.org/whl/cu118
```

3. **网络连接问题**
```bash
# 测试国内镜像连通性
curl -I https://pypi.tuna.tsinghua.edu.cn/simple/
curl -I https://hf-mirror.com/
curl -I https://mirrors.tuna.tsinghua.edu.cn/

# 如果清华镜像不可用，尝试其他镜像
export HF_ENDPOINT=https://huggingface.co  # 使用官方源
pip install -i https://pypi.python.org/simple/  # 使用官方PyPI
```

4. **依赖包安装失败**
```bash
# 清理pip缓存
~/miniconda3/envs/index-tts/bin/pip cache purge

# 重新安装，指定镜像源
~/miniconda3/envs/index-tts/bin/pip install -r requirements_enhanced.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple \
  --trusted-host pypi.tuna.tsinghua.edu.cn
```

### 镜像源切换

如果默认镜像源不可用，可以手动切换：

```bash
# 切换PyPI镜像源
~/.pip/pip.conf

[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
trusted-host = mirrors.aliyun.com

# 切换HuggingFace镜像
export HF_ENDPOINT=https://huggingface.co

# 切换Conda镜像
conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/pkgs/free/
```

## 🚀 手动下载模型

如果自动下载失败，可以手动下载：

### 方法1：HF-Mirror（推荐）

```bash
# 访问镜像站下载
wget https://hf-mirror.com/IndexTeam/IndexTTS-1.5/resolve/main/config.yaml
wget https://hf-mirror.com/IndexTeam/IndexTTS-1.5/resolve/main/gpt.pth
wget https://hf-mirror.com/IndexTeam/IndexTTS-1.5/resolve/main/dvae.pth
# ... 下载其他模型文件
```

### 方法2：ModelScope

```bash
# 使用git lfs下载
git clone https://www.modelscope.cn/IndexTeam/IndexTTS-1.5.git checkpoints
```

### 方法3：百度网盘（如果有分享）

某些社区可能会提供百度网盘分享链接，可以关注相关社区获取。

## 🔒 安全配置

### 防火墙设置

```bash
# 开放Web界面端口
sudo ufw allow 7860

# 开放API端口
sudo ufw allow 8000

# 如果只允许特定IP访问
sudo ufw allow from 192.168.1.0/24 to any port 7860
```

## 📊 性能优化

### 国内网络优化

```bash
# 设置DNS服务器（提升域名解析速度）
echo "nameserver 223.5.5.5" | sudo tee /etc/resolv.conf
echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf

# 永久配置pip镜像源
mkdir -p ~/.pip
cat > ~/.pip/pip.conf << EOF
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
timeout = 60
EOF
```

### GPU优化

```bash
# 设置CUDA内存优化
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4
```

## 🎉 部署成功示例

成功部署后，你将看到类似的输出：

```
🎉 IndexTTS Enhanced 部署完成！
==================================================
📂 项目目录: /home/user/index-tts-enhanced
🐍 Python路径: /home/user/miniconda3/envs/index-tts/bin/python

🚀 启动命令:
  cd /home/user/index-tts-enhanced
  ./start_webui.sh     # Web界面
  ./start_api.sh       # API服务

🌐 访问地址:
  Web界面: http://localhost:7860
  API服务: http://localhost:8000

💡 使用了以下国内镜像源:
  - 清华大学 PyPI 镜像
  - 清华大学 Conda 镜像
  - HF-Mirror HuggingFace 镜像
  - ModelScope 备用模型源
==================================================
```

## 🆘 获取帮助

- **GitHub Issues**: 项目仓库的Issues页面
- **镜像源问题**: 如果某个镜像源不可用，脚本会自动尝试备用源
- **模型下载问题**: 提供了多种下载方式，包括手动下载选项

按照这个输出的信息进行后续操作即可！国内服务器的部署速度将大大提升！🚀 