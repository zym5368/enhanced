#!/bin/bash
# 先激活conda环境，再启动WebUI
source ~/miniconda3/etc/profile.d/conda.sh
conda activate index-tts

# 切换到脚本所在目录（即项目根目录）
cd "$(dirname "$0")"

# 设置PYTHONPATH，确保tools等模块可被导入
export PYTHONPATH=.

# 启动WebUI
python enhanced/webui_enhanced.py --host 0.0.0.0 --port 7860
