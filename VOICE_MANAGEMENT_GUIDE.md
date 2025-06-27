# IndexTTS 音色管理和API使用指南

## 📋 概述

本指南介绍如何使用IndexTTS的音色保存功能和API接口，特别是如何与dify工作流集成。

## 🚀 快速启动

### 1. 启动增强版Web界面

```bash
# Windows
run_enhanced.bat

# Linux/Mac
python webui_enhanced.py --host 0.0.0.0 --port 7860
```

### 2. 启动API服务器

```bash
# Windows
run_api.bat

# Linux/Mac
python api_server.py --host 0.0.0.0 --port 8000
```

## 💾 音色保存功能

### 在Web界面中保存音色

1. **上传参考音频**
   - 点击"参考音频"区域上传音频文件
   - 支持wav、mp3等格式
   - 建议音频长度3-10秒，音质清晰

2. **保存音色**
   - 输入音色名称（必填）
   - 输入音色描述（可选）
   - 点击"保存音色"按钮

3. **使用保存的音色**
   - 在"加载音色"下拉框中选择已保存的音色
   - 点击"加载音色"按钮
   - 系统会自动加载对应的音频文件

### 音色管理

在"音色管理"标签页中，您可以：
- 查看所有已保存的音色列表
- 查看音色的详细信息（时长、创建时间、文件大小）
- 删除不需要的音色
- 刷新音色列表

## 🔌 API接口使用

### 基本信息

- **Web界面**: http://localhost:7860
- **API服务**: http://localhost:8000
- **API文档**: http://localhost:8000/docs

### 主要API端点

#### 1. 文本转语音 API

**请求**:
```http
POST /api/tts
Content-Type: application/json

{
    "text": "要转换的文本内容",
    "voice_name": "音色名称",
    "infer_mode": "普通推理",
    "temperature": 1.0,
    "top_p": 0.8,
    "top_k": 30
}
```

**响应**:
```json
{
    "success": true,
    "message": "生成成功",
    "audio_url": "/api/audio/tts_uuid.wav",
    "task_id": "uuid",
    "duration": 2.5
}
```

#### 2. 获取音色列表 API

**请求**:
```http
GET /api/voices
```

**响应**:
```json
{
    "success": true,
    "voices": [
        {
            "name": "女声温柔",
            "description": "温柔的女性声音",
            "duration": 5.2,
            "created_time": 1640995200,
            "file_size": 524288
        }
    ]
}
```

#### 3. 下载音频文件 API

**请求**:
```http
GET /api/audio/{filename}
```

**响应**: 返回音频文件（WAV格式）

#### 4. 服务状态 API

**请求**:
```http
GET /api/status
```

**响应**:
```json
{
    "status": "running",
    "model_version": "1.5",
    "voices_count": 5,
    "model_dir": "checkpoints"
}
```

## 🔧 Dify工作流集成

### 在Dify中配置HTTP节点

1. **添加HTTP节点**
   - 在dify工作流中添加HTTP节点
   - 设置请求方法为 `POST`

2. **配置请求参数**
   ```
   URL: http://your-server-ip:8000/api/tts
   Method: POST
   Headers: 
     Content-Type: application/json
   Body:
   {
       "text": "{{input_text}}",
       "voice_name": "{{voice_name}}",
       "infer_mode": "普通推理"
   }
   ```

3. **处理响应**
   - 从响应中提取 `audio_url` 字段
   - 使用 `http://your-server-ip:8000{{audio_url}}` 获取完整音频URL

### 工作流示例

```mermaid
graph LR
    A[用户输入文本] --> B[HTTP节点调用TTS API]
    B --> C[获取音频URL]
    C --> D[后续处理/返回给用户]
```

### Python代码示例

```python
import requests

# TTS API调用
def call_tts_api(text, voice_name, server_url="http://localhost:8000"):
    url = f"{server_url}/api/tts"
    
    payload = {
        "text": text,
        "voice_name": voice_name,
        "infer_mode": "普通推理",
        "temperature": 1.0
    }
    
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        result = response.json()
        if result["success"]:
            audio_url = f"{server_url}{result['audio_url']}"
            return audio_url
    
    return None

# 使用示例
audio_url = call_tts_api("大家好，欢迎使用IndexTTS！", "女声温柔")
if audio_url:
    print(f"生成的音频URL: {audio_url}")
```

## ⚙️ 高级配置

### 自定义生成参数

在API请求中，您可以调整以下参数来控制音频生成：

- `infer_mode`: 推理模式（"普通推理" 或 "批次推理"）
- `temperature`: 控制随机性（0.1-2.0）
- `top_p`: 采样策略（0.0-1.0）
- `top_k`: 候选词数量（1-100）
- `max_text_tokens_per_sentence`: 分句最大Token数
- `repetition_penalty`: 重复惩罚（0.1-20.0）

### 性能优化建议

1. **批次推理**: 对于长文本，使用"批次推理"模式可提升速度
2. **音色缓存**: 重复使用相同音色时，系统会自动利用缓存提升速度
3. **文件清理**: 定期调用 `/api/cleanup` 清理临时文件
4. **并发限制**: API服务器支持并发请求，但建议控制在合理范围内

## 🛠️ 故障排除

### 常见问题

1. **音色不存在错误**
   - 检查音色名称是否正确
   - 使用 `/api/voices` 接口获取可用音色列表

2. **音频生成失败**
   - 检查文本内容是否为空
   - 确认模型文件完整
   - 查看服务器日志

3. **文件访问错误**
   - 确认音频文件存在
   - 检查文件权限设置

### 日志查看

启动服务时添加 `--verbose` 参数可以看到详细日志：

```bash
python api_server.py --verbose
```

## 📝 注意事项

1. **音色文件管理**: 音色文件存储在 `voices/` 目录下，请定期备份
2. **临时文件**: API生成的音频文件存储在 `outputs/api/` 目录下
3. **端口配置**: 确保7860和8000端口未被占用
4. **网络访问**: 在生产环境中请配置适当的防火墙规则
5. **音频格式**: 生成的音频为WAV格式，采样率24kHz

## 📞 技术支持

如果遇到问题，请：
1. 查看API文档：http://localhost:8000/docs
2. 检查服务状态：http://localhost:8000/api/status
3. 查看项目GitHub仓库获取最新信息 