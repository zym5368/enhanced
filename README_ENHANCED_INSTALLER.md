# IndexTTS Enhanced 一键安装器

## 📋 概述

本安装器用于在官方IndexTTS基础上快速部署增强功能，包括音色管理、API接口和增强Web界面。

## 🎯 功能特点

- ✅ **一键安装**: 自动克隆官方仓库并安装增强功能
- ✅ **完全兼容**: 基于官方IndexTTS，无侵入式修改
- ✅ **跨平台支持**: Windows和Linux系统
- ✅ **智能检测**: 自动检测文件存在情况
- ✅ **依赖管理**: 自动安装所需依赖包

## 🚀 使用方法

### 方式一：完全自动安装（推荐）

#### Windows用户
```bash
# 双击运行或在命令行执行
一键安装增强版.bat
```

#### Linux用户
```bash
# 添加执行权限并运行
chmod +x install_enhanced.sh
./install_enhanced.sh
```

### 方式二：手动分步安装

#### 1. 克隆官方仓库
```bash
git clone https://github.com/index-tts/index-tts.git index-tts-enhanced
```

#### 2. 运行简化版安装器
```bash
python install_enhanced_simple.py index-tts-enhanced
```

#### 3. 进入目录安装依赖
```bash
cd index-tts-enhanced
pip install -e .
pip install -r requirements_enhanced.txt
```

## 📁 安装器文件说明

| 文件名 | 用途 | 平台 |
|--------|------|------|
| `install_enhanced.py` | 完整版安装器（支持网络下载） | 通用 |
| `install_enhanced_simple.py` | 简化版安装器（本地文件复制） | 通用 |
| `一键安装增强版.bat` | Windows一键安装脚本 | Windows |
| `install_enhanced.sh` | Linux一键安装脚本 | Linux |

## 🔧 安装内容

### 增强文件
- `webui_enhanced.py` - 增强版Web界面
- `api_server.py` - 独立API服务器
- `indextts/voice_manager.py` - 音色管理模块
- `requirements_enhanced.txt` - 增强版依赖
- `test_api.py` - API测试脚本

### 启动脚本
- `run_enhanced.bat/sh` - 增强版启动脚本
- `run_api.bat/sh` - API服务器启动脚本

### 文档
- `USER_GUIDE.md` - 用户使用指南
- `VOICE_MANAGEMENT_GUIDE.md` - 音色管理指南
- `DEPLOYMENT_GUIDE.md` - 部署指南

### 目录结构
```
index-tts-enhanced/
├── webui_enhanced.py          # 增强版Web界面
├── api_server.py              # API服务器
├── indextts/voice_manager.py  # 音色管理
├── voices/                    # 音色存储目录
├── outputs/api/               # API输出目录
├── run_enhanced.bat          # Windows启动脚本
├── run_enhanced.sh           # Linux启动脚本
└── requirements_enhanced.txt  # 增强版依赖
```

## ⚙️ 配置说明

### 自动创建的配置
安装器会自动创建以下配置：

#### `checkpoints/config.yaml`
```yaml
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
```

#### `voices/voices.json`
```json
{
  "voices": [],
  "version": "1.0",
  "created_at": "2025-06-27"
}
```

## 📦 依赖说明

### 官方依赖
安装器会自动运行 `pip install -e .` 安装官方依赖。

### 增强版依赖
```
fastapi>=0.104.1
uvicorn>=0.24.0
python-multipart>=0.0.6
aiofiles>=23.2.1
jinja2>=3.1.2
requests>=2.31.0
pydantic>=2.5.0
psutil>=5.9.6
```

## 🏃‍♂️ 启动服务

### 下载模型文件
```bash
cd index-tts-enhanced

# 安装huggingface-cli
pip install huggingface-hub

# 下载IndexTTS-1.5模型
huggingface-cli download IndexTeam/IndexTTS-1.5 \
  config.yaml bigvgan_discriminator.pth bigvgan_generator.pth \
  bpe.model dvae.pth gpt.pth unigram_12000.vocab \
  --local-dir checkpoints
```

### 启动增强版
```bash
# Windows
run_enhanced.bat

# Linux
./run_enhanced.sh

# 手动启动
python webui_enhanced.py --host 0.0.0.0 --port 7860 --enable_api
```

### 访问服务
- **Web界面**: http://localhost:7860
- **API文档**: http://localhost:7860/docs
- **TTS接口**: http://localhost:7860/api/tts

## 🔍 故障排除

### 常见问题

#### 1. 克隆仓库失败
```bash
# 错误：fatal: unable to access
# 解决：检查网络连接，或使用代理
git config --global http.proxy http://proxy-server:port
```

#### 2. Python模块找不到
```bash
# 错误：ModuleNotFoundError
# 解决：检查Python环境和依赖安装
pip install -r requirements_enhanced.txt
```

#### 3. 端口占用
```bash
# 错误：Address already in use
# 解决：更改端口或关闭占用进程
python webui_enhanced.py --port 7861
```

#### 4. 模型文件缺失
```bash
# 错误：FileNotFoundError: checkpoints/gpt.pth
# 解决：下载模型文件到checkpoints目录
huggingface-cli download IndexTeam/IndexTTS-1.5 --local-dir checkpoints
```

### 检查安装结果
```bash
# 检查文件是否存在
ls -la webui_enhanced.py
ls -la indextts/voice_manager.py
ls -la voices/voices.json

# 检查Python依赖
pip list | grep fastapi
pip list | grep uvicorn

# 测试导入
python -c "from indextts.voice_manager import VoiceManager; print('OK')"
```

## 🆚 版本对比

| 功能 | 官方版本 | 增强版本 |
|------|----------|----------|
| Web界面 | ✅ 基础界面 | ✅ 增强界面 + 音色管理 |
| API接口 | ❌ 无 | ✅ 完整RESTful API |
| 音色保存 | ❌ 无 | ✅ 永久保存管理 |
| 音色搜索 | ❌ 无 | ✅ 按名称描述搜索 |
| 自定义文件名 | ❌ 无 | ✅ 支持 |
| dify集成 | ❌ 无 | ✅ 原生支持 |
| 部署支持 | ❌ 基础 | ✅ Docker/systemd |

## 🔄 更新和维护

### 更新增强功能
```bash
# 重新运行安装器
python install_enhanced_simple.py index-tts-enhanced
```

### 更新官方代码
```bash
cd index-tts-enhanced
git pull origin main
pip install -e .
```

### 备份音色数据
```bash
# 备份音色文件
cp -r voices/ voices_backup_$(date +%Y%m%d)/
```

## 📞 支持和反馈

- **文档**: 查看 `USER_GUIDE.md` 详细使用说明
- **Issues**: 提交问题到项目仓库
- **社区**: 参与官方IndexTTS讨论

## 📄 许可证

本增强版本遵循原项目的Apache-2.0许可证。

---

*安装器版本: v1.0 | 兼容IndexTTS v1.5 | 最后更新: 2025年6月* 