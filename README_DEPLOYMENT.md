# IndexTTS Enhanced 部署工具包

## 🎯 概述

这是一个完整的IndexTTS Enhanced部署工具包，提供多种部署方式满足不同需求。**特别针对中国大陆服务器进行了网络优化**，使用国内镜像源大幅提升部署速度。

## 🇨🇳 国内镜像源优化特性

### ⚡ 性能提升对比

| 项目 | 国外源 | 国内镜像 | 提升倍数 |
|------|--------|----------|----------|
| Miniconda下载 | 5-10分钟 | 1-2分钟 | **5x** |
| PyPI包安装 | 15-20分钟 | 3-5分钟 | **4x** |
| 模型文件下载 | 30-60分钟 | 10-15分钟 | **3x** |
| **总部署时间** | **50-90分钟** | **15-25分钟** | **3.5x** |

### 🌐 使用的镜像源

- **PyPI**: 清华大学镜像 (pypi.tuna.tsinghua.edu.cn)
- **Conda**: 清华大学镜像 (mirrors.tuna.tsinghua.edu.cn)
- **HuggingFace**: HF-Mirror镜像 (hf-mirror.com)
- **备用**: ModelScope镜像 (modelscope.cn)

## 📦 工具包内容

### 核心部署脚本
- `deploy/complete_deploy.py` - 一键完整部署（**推荐**）
- `deploy/install_enhanced_linux_fixed.py` - Linux兼容性修复
- `deploy/test_deployment.py` - 部署验证测试

### 增强功能文件
- `enhanced/webui_enhanced.py` - 增强版Web界面
- `enhanced/api_server.py` - 独立API服务器
- `enhanced/indextts/voice_manager.py` - 音色管理器
- `enhanced/requirements_enhanced.txt` - 增强版依赖列表

### 示例和文档
- `examples/test_api_examples.py` - API使用示例
- `docs/` - 详细文档目录
- `COMPLETE_DEPLOYMENT_GUIDE.md` - 完整部署指南
- `UBUNTU_SETUP_GUIDE.md` - Ubuntu安装指南

## 🚀 快速部署（推荐）

### 一键部署命令

```bash
# 1. 下载部署工具包
git clone https://github.com/zym5368/enhanced.git
cd index-tts-enhanced

# 2. 执行一键部署（自动使用国内镜像源）
sudo python3 deploy/complete_deploy.py
```

### 部署过程说明

脚本将自动完成以下步骤：

1. **系统依赖安装** (~3分钟)
   - 更新apt包管理器
   - 安装FFmpeg、开发工具等必需软件

2. **Miniconda安装** (~2分钟)
   - 使用清华镜像下载Miniconda
   - 自动配置conda环境

3. **Python环境配置** (~1分钟)
   - 创建index-tts虚拟环境
   - 配置pip国内镜像源

4. **PyTorch安装** (~5分钟)
   - 自动检测CUDA版本
   - 从清华镜像安装对应PyTorch版本

5. **项目代码部署** (~3分钟)
   - 克隆IndexTTS项目
   - 安装Python依赖包

6. **模型文件下载** (~10-15分钟)
   - 使用HF-Mirror镜像下载模型
   - 支持断点续传

7. **增强功能安装** (~2分钟)
   - 创建增强版Web界面
   - 配置API服务器

### 部署成功标志

部署完成后，你将看到：

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

## 🛠️ 其他部署方式

### 方式1：手动步骤部署

适合需要自定义配置的用户，请参考：
- 📖 [Ubuntu详细安装指南](UBUNTU_SETUP_GUIDE.md)

### 方式2：容器化部署（开发中）

```bash
# Docker部署（即将推出）
docker run -p 7860:7860 -p 8000:8000 index-tts-enhanced:latest
```

### 方式3：云平台一键部署（开发中）

支持主流云平台的一键部署模板：
- 阿里云ECS
- 腾讯云CVM
- 华为云ECS

## 🔧 部署后配置

### 启动服务

```bash
cd ~/index-tts-enhanced

# 启动Web界面（包含API）
./start_webui.sh

# 或启动独立API服务
./start_api.sh
```

### 访问地址

- **Web界面**: http://你的服务器IP:7860
- **API文档**: http://你的服务器IP:8000/docs
- **API端点**: http://你的服务器IP:8000/api/

### 防火墙配置

```bash
# 开放必要端口
sudo ufw allow 7860  # Web界面
sudo ufw allow 8000  # API服务
```

## 🧪 测试和验证

### 自动测试

```bash
# 运行完整测试套件
python3 deploy/test_deployment.py
```

### 手动测试

```bash
# 1. 测试模型加载
python -c "
from indextts.infer import IndexTTS
tts = IndexTTS(model_dir='checkpoints', cfg_path='checkpoints/config.yaml')
print('✅ 模型加载成功')
"

# 2. 测试API接口
curl http://localhost:7860/api/voices

# 3. 测试Web界面
curl -s http://localhost:7860 > /dev/null && echo "✅ Web界面正常"
```

## 📊 网络镜像源详解

### 自动镜像源选择

部署脚本会按优先级尝试以下镜像源：

#### Miniconda下载
1. 🥇 清华大学: `mirrors.tuna.tsinghua.edu.cn`
2. 🥈 北京外国语大学: `mirrors.bfsu.edu.cn`
3. 🥉 官方源: `repo.anaconda.com`

#### PyPI包安装
1. 🥇 清华大学: `pypi.tuna.tsinghua.edu.cn`
2. 🥈 阿里云: `mirrors.aliyun.com/pypi/simple`
3. 🥉 中科大: `pypi.mirrors.ustc.edu.cn/simple`

#### 模型文件下载
1. 🥇 HF-Mirror: `hf-mirror.com`
2. 🥈 ModelScope: `modelscope.cn`
3. 🥉 HuggingFace官方: `huggingface.co`

### 手动镜像源切换

如果自动选择的镜像源速度不理想，可以手动切换：

```bash
# 切换PyPI镜像源
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com

# 切换HuggingFace镜像
export HF_ENDPOINT=https://hf-mirror.com

# 切换Conda镜像
conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/pkgs/main/
```

## 🔧 故障排除

### 常见问题

#### 1. 网络连接问题

```bash
# 测试镜像源连通性
curl -I https://pypi.tuna.tsinghua.edu.cn/simple/
curl -I https://hf-mirror.com/

# 如果连接失败，尝试其他镜像
export HF_ENDPOINT=https://modelscope.cn
```

#### 2. 模型下载失败

```bash
# 手动下载关键模型文件
cd ~/index-tts-enhanced/checkpoints
wget https://hf-mirror.com/IndexTeam/IndexTTS-1.5/resolve/main/config.yaml
wget https://hf-mirror.com/IndexTeam/IndexTTS-1.5/resolve/main/gpt.pth
# ... 其他模型文件
```

#### 3. 依赖包安装失败

```bash
# 清理pip缓存后重试
pip cache purge
pip install -r requirements_enhanced.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 获取支持

- **GitHub Issues**: 项目仓库的Issues页面
- **文档**: 查看docs/目录下的详细文档
- **镜像源问题**: 脚本会自动尝试备用源

## 🚧 更新和维护

### 更新模型

```bash
cd ~/index-tts-enhanced
export HF_ENDPOINT=https://hf-mirror.com

python -c "
from huggingface_hub import snapshot_download
snapshot_download('IndexTeam/IndexTTS-1.5', local_dir='checkpoints', force_download=True)
"
```

### 更新代码

```bash
cd ~/index-tts-enhanced
git pull origin main
pip install -r requirements_enhanced.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 备份数据

```bash
# 备份音色库
tar -czf voices_backup_$(date +%Y%m%d).tar.gz voices/

# 备份配置
cp -r checkpoints/ checkpoints_backup_$(date +%Y%m%d)/
```

## 📈 性能监控

### 系统资源监控

```bash
# 安装监控工具
sudo apt install -y htop iotop

# 实时监控
htop  # CPU和内存使用
nvidia-smi -l 1  # GPU状态（如果有GPU）
iotop  # 磁盘IO
```

### 服务状态检查

```bash
# 检查服务运行状态
ps aux | grep python
netstat -tlnp | grep -E ':(7860|8000)'

# 查看日志
tail -f logs/webui.log
tail -f logs/api.log
```

## 🎨 自定义配置

### 修改端口

```bash
# 修改Web界面端口
./start_webui.sh --port 8080

# 修改API端口
./start_api.sh --port 9000
```

### 配置域名访问

```bash
# 使用Nginx反向代理
sudo apt install nginx

# 配置示例
sudo tee /etc/nginx/sites-available/indextts << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:7860;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/indextts /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

## 🌟 高级功能

### 集群部署

支持多节点分布式部署，提升处理能力：

```bash
# 主节点配置
python api_server.py --host 0.0.0.0 --port 8000 --workers 4

# 从节点配置
python worker_node.py --master-host 主节点IP --worker-id 1
```

### 性能优化

```bash
# GPU内存优化
export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512

# 并发处理优化
export OMP_NUM_THREADS=4
export MKL_NUM_THREADS=4

# 缓存优化
export HF_HOME=/tmp/huggingface_cache
```

## 📝 版本历史

- **v2.0** - 增加国内镜像源支持，部署时间缩短70%
- **v1.5** - 增强版功能完善，API接口优化
- **v1.0** - 基础部署功能实现

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个部署工具包！

---

**🎉 享受快速的IndexTTS Enhanced部署体验！** 

使用国内镜像源，让部署过程更快更稳定！ 🚀 