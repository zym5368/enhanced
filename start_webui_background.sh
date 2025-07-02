#!/bin/bash
# IndexTTS Enhanced WebUI 后台启动脚本
# 建议放到 /etc/rc.local 或 systemd 等自启目录

# 激活conda环境
source ~/miniconda3/etc/profile.d/conda.sh
conda activate index-tts

# 切换到项目根目录
cd /root/index-tts-official

# 设置PYTHONPATH，确保增强包可用
export PYTHONPATH=.

# 后台启动WebUI服务，日志输出到webui.log
nohup python enhanced/webui_enhanced.py --host 0.0.0.0 --port 80 > webui.log 2>&1 &

echo "IndexTTS Enhanced WebUI 已后台启动，日志见 webui.log" 