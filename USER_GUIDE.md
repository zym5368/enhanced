# IndexTTS Enhanced 完整使用指南

## 📋 目录

- [项目概述](#项目概述)
- [功能特性](#功能特性)
- [环境要求](#环境要求)
- [安装启动](#安装启动)
- [Web界面使用](#web界面使用)
- [API使用指南](#api使用指南)
- [音色管理](#音色管理)
- [配置说明](#配置说明)
- [故障排除](#故障排除)

---

## 项目概述

IndexTTS Enhanced 是一个增强版的文本转语音(TTS)系统，基于原版 IndexTTS 扩展了音色管理和API功能。支持高质量的中英文语音合成，提供友好的Web界面和完整的RESTful API。

### 主要改进

- ✅ **音色保存管理** - 上传音频后可保存为音色，支持描述和搜索
- ✅ **完整API接口** - 提供RESTful API，支持dify等工作流集成
- ✅ **自定义文件名** - API支持指定生成音频的文件名
- ✅ **双重访问方式** - 同时支持Web界面和API调用
- ✅ **音色缓存优化** - 重复使用相同音色时性能更佳

---

## 功能特性

### 🎤 语音合成功能
- **高质量TTS**: 支持中英文混合语音合成
- **两种推理模式**: 普通推理(快速)和批次推理(高质量)
- **音色克隆**: 支持任意音频作为参考音色
- **参数可调**: 支持温度、top-p、top-k等生成参数调节

### 💾 音色管理系统
- **音色保存**: 上传音频后可保存为可重用的音色
- **音色描述**: 为每个音色添加描述信息便于管理
- **音色列表**: 查看所有已保存音色的详细信息
- **音色删除**: 支持删除不需要的音色
- **音色搜索**: 快速查找特定音色

### 🌐 API接口服务
- **RESTful API**: 标准HTTP API，易于集成
- **多种调用方式**: 支持JSON body和URL参数
- **自定义文件名**: 可指定生成音频的文件名
- **双重响应模式**: 支持JSON响应和直接文件下载
- **dify集成友好**: 专为工作流集成设计

---

## 环境要求

### 系统要求
- **操作系统**: Windows 10/11 (推荐)
- **Python版本**: 3.10.x
- **内存**: 8GB+ (推荐16GB+)
- **存储**: 10GB+ 可用空间
- **GPU**: 可选，支持CUDA加速

### 依赖环境
- **Conda**: 用于Python环境管理
- **PyTorch**: 深度学习框架
- **Gradio**: Web界面框架
- **FastAPI**: API服务框架

---

## 安装启动

### 1. 环境准备

确保已安装Conda，然后创建并激活环境：

```bash
# 创建conda环境
conda create -n index-tts python=3.10
conda activate index-tts
```

### 2. 安装依赖

```bash
# 安装基础依赖
pip install -r requirements.txt

# 安装增强功能依赖
pip install -r requirements_enhanced.txt
```

### 3. 模型下载

确保在 `checkpoints/` 目录下有以下文件：
- `gpt.pth` - GPT模型权重
- `bigvgan_generator.pth` - BigVGAN生成器
- `bpe.model` - BPE分词模型
- `config.yaml` - 配置文件

### 4. 启动服务

#### 方式一：增强版Web界面+API (推荐)
```bash
# Windows
run_enhanced.bat

# 手动启动
python webui_enhanced.py --enable_api --port 7860
```

#### 方式二：仅API服务
```bash
# Windows
run_api.bat

# 手动启动
python api_server.py --port 7860
```

#### 方式三：仅Web界面
```bash
# Windows
run.bat

# 手动启动
python webui.py --port 7860
```

### 5. 访问服务

启动成功后访问：
- **Web界面**: http://localhost:7860
- **API文档**: http://localhost:7860/docs
- **音色列表API**: http://localhost:7860/api/voices

---

## Web界面使用

### 音频生成页面

1. **上传参考音频**
   - 点击"参考音频"区域上传WAV/MP3文件
   - 或使用麦克风录制音频
   - 音频长度建议5-15秒

2. **保存音色**
   - 上传音频后，在"保存音色"区域
   - 输入音色名称(必填)和描述(可选)
   - 点击"保存音色"按钮

3. **加载已保存音色**
   - 在"加载音色"下拉菜单选择音色
   - 点击"加载音色"按钮

4. **输入文本并生成**
   - 在"文本"区域输入要合成的文字
   - 选择推理模式(普通推理/批次推理)
   - 调整生成参数(可选)
   - 点击"生成"按钮

### 音色管理页面

1. **查看音色列表**
   - 显示所有已保存音色的详细信息
   - 包括名称、描述、时长、创建时间、文件大小

2. **删除音色**
   - 在删除区域选择要删除的音色
   - 点击"删除选中音色"按钮
   - 确认删除操作

3. **刷新音色列表**
   - 点击"刷新音色列表"按钮更新显示

---

## API使用指南

### API端点概览

| 端点 | 方法 | 功能 | 响应类型 |
|------|------|------|----------|
| `/api/tts` | POST | 文本转语音 | JSON |
| `/api/tts/file` | POST | 文本转语音 | 音频文件 |
| `/api/voices` | GET | 获取音色列表 | JSON |
| `/api/audio/{filename}` | GET | 下载音频文件 | 音频文件 |

### 1. 文本转语音 API

#### 基本调用 (JSON响应)

```bash
curl -X POST "http://localhost:7860/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "你好，这是一个测试",
    "voice_name": "冰姐"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "生成成功",
  "audio_url": "/api/audio/tts_123e4567-e89b-12d3-a456-426614174000.wav",
  "task_id": "123e4567-e89b-12d3-a456-426614174000"
}
```

#### 自定义文件名

```bash
curl -X POST "http://localhost:7860/api/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "自定义文件名测试",
    "voice_name": "冰姐",
    "filename": "my_custom_audio"
  }'
```

**响应示例**:
```json
{
  "success": true,
  "message": "生成成功",
  "audio_url": "/api/audio/my_custom_audio.wav",
  "task_id": "my_custom_audio"
}
```

#### 直接下载音频文件

```bash
curl -X POST "http://localhost:7860/api/tts/file" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "直接下载音频",
    "voice_name": "冰姐",
    "filename": "download_test"
  }' \
  --output "output.wav"
```

#### URL参数方式

```bash
curl -X POST "http://localhost:7860/api/tts?text=URL参数测试&voice_name=冰姐&filename=url_test"
```

### 2. 完整参数列表

```json
{
  "text": "要合成的文本内容",
  "voice_name": "音色名称",
  "filename": "自定义文件名(可选)",
  "infer_mode": "普通推理",
  "max_text_tokens_per_sentence": 120,
  "sentences_bucket_max_size": 4,
  "do_sample": true,
  "top_p": 0.8,
  "top_k": 30,
  "temperature": 1.0,
  "length_penalty": 0.0,
  "num_beams": 3,
  "repetition_penalty": 10.0,
  "max_mel_tokens": 600
}
```

### 3. 获取音色列表

```bash
curl "http://localhost:7860/api/voices"
```

**响应示例**:
```json
{
  "success": true,
  "voices": [
    {
      "name": "冰姐",
      "description": "清晰女声",
      "duration": 10.97,
      "created_time": 1751022397.98,
      "file_size": 175174
    }
  ]
}
```

### 4. Python调用示例

```python
import requests
import json

# 基本调用
def tts_generate(text, voice_name, filename=None):
    url = "http://localhost:7860/api/tts"
    data = {
        "text": text,
        "voice_name": voice_name
    }
    if filename:
        data["filename"] = filename
    
    response = requests.post(url, json=data)
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            # 下载音频文件
            audio_url = f"http://localhost:7860{result['audio_url']}"
            audio_response = requests.get(audio_url)
            with open(f"{filename or 'output'}.wav", "wb") as f:
                f.write(audio_response.content)
            print(f"音频已保存: {filename or 'output'}.wav")
        else:
            print(f"生成失败: {result['message']}")
    else:
        print(f"请求失败: {response.text}")

# 使用示例
tts_generate("你好世界", "冰姐", "hello_world")
```

### 5. dify工作流集成

在dify中创建HTTP请求节点：

```yaml
# 请求配置
Method: POST
URL: http://your-server:7860/api/tts
Headers:
  Content-Type: application/json

# 请求体
{
  "text": "{{input_text}}",
  "voice_name": "{{voice_name}}",
  "filename": "{{custom_filename}}"
}

# 输出处理
audio_url: {{response.audio_url}}
```

---

## 音色管理

### 音色文件结构

```
voices/
├── voices.json          # 音色元数据
└── voice_xxx_x.MP3     # 音色音频文件
```

### 音色数据格式

```json
{
  "音色名称": {
    "id": "voice_1234567890_0",
    "name": "音色名称",
    "description": "音色描述",
    "audio_path": "voices\\voice_1234567890_0.MP3",
    "created_time": 1751022397.98,
    "duration": 10.973537414965987,
    "sample_rate": 44100,
    "file_size": 175174
  }
}
```

### 音色管理最佳实践

1. **音频质量要求**
   - 推荐使用清晰、无噪音的音频
   - 音频长度5-15秒最佳
   - 支持WAV、MP3格式

2. **命名规范**
   - 使用有意义的音色名称
   - 避免使用特殊字符
   - 添加描述信息便于管理

3. **存储管理**
   - 定期清理不需要的音色
   - 备份重要音色文件
   - 监控存储空间使用

---

## 配置说明

### 启动参数

```bash
python webui_enhanced.py \
  --port 7860 \              # 服务端口
  --host 0.0.0.0 \          # 绑定地址
  --model_dir checkpoints \ # 模型目录
  --enable_api \            # 启用API
  --verbose                 # 详细日志
```

### 配置文件 (checkpoints/config.yaml)

```yaml
# 模型配置
model:
  gpt_path: "checkpoints/gpt.pth"
  bigvgan_path: "checkpoints/bigvgan_generator.pth"
  bpe_path: "checkpoints/bpe.model"

# 生成参数
generation:
  default_temperature: 1.0
  default_top_p: 0.8
  default_top_k: 30
  max_text_tokens: 120
```

### 环境变量

```bash
# CUDA配置
export CUDA_HOME="/path/to/cuda"
export CUDA_PATH="/path/to/cuda"

# 模型缓存
export TORCH_HOME="/path/to/torch/cache"
```

---

## 故障排除

### 常见问题

#### 1. 服务启动失败

**问题**: 模型文件不存在
```
Required file checkpoints/gpt.pth does not exist
```

**解决**: 
- 检查模型文件是否完整下载
- 确认文件路径正确
- 重新下载缺失的模型文件

#### 2. 音色不存在错误

**问题**: API调用返回音色不存在
```json
{"detail": "音色 'xxx' 不存在"}
```

**解决**:
- 检查音色名称是否正确
- 调用 `/api/voices` 查看可用音色
- 确认音色已正确保存

#### 3. 内存不足

**问题**: 生成过程中内存溢出
```
RuntimeError: CUDA out of memory
```

**解决**:
- 减少批次大小参数
- 关闭其他占用内存的程序
- 使用CPU模式(性能较慢)

#### 4. 文件名特殊字符问题

**问题**: 自定义文件名包含非法字符

**解决**:
- 系统会自动清理特殊字符 `<>:"/\|?*`
- 替换为下划线 `_`
- 建议使用字母、数字、下划线

### 日志调试

启用详细日志模式：
```bash
python webui_enhanced.py --verbose
```

查看生成过程日志：
```
[DEBUG] generate_tts_internal called with custom_filename: test
[DEBUG] Using custom filename: test.wav
>> start inference...
>> Reference audio length: 10.95 seconds
>> gpt_gen_time: 1.96 seconds
>> bigvgan_time: 0.15 seconds
>> Total inference time: 2.16 seconds
```

### 性能优化

1. **GPU加速**
   - 安装CUDA支持的PyTorch版本
   - 确保CUDA环境变量配置正确

2. **模型缓存**
   - 首次加载较慢，后续会利用缓存
   - 避免频繁重启服务

3. **并发限制**
   - API支持并发调用
   - 建议根据硬件性能限制并发数

---

## 技术支持

### 项目信息
- **版本**: Enhanced v1.0
- **基于**: IndexTTS开源项目
- **许可**: 遵循原项目许可证

### 获取帮助
- 查看项目README文档
- 检查issue列表寻找类似问题
- 查看API文档: http://localhost:7860/docs

### 贡献指南
- 欢迎提交bug报告和功能建议
- 遵循代码规范和提交规范
- 确保充分测试后提交PR

---

*最后更新: 2025年6月* 