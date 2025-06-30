#!/bin/bash

echo "========================================"
echo "   IndexTTS Enhanced 一键安装脚本"
echo "========================================"
echo

echo "🚀 激活conda环境..."
# 创建Python环境
conda create -n index-tts python=3.10 -y
conda activate index-tts

echo "🚀 开始安装IndexTTS Enhanced..."
echo

echo "1️⃣ 克隆官方IndexTTS仓库..."
git clone https://github.com/index-tts/index-tts.git index-tts-enhanced
if [ $? -ne 0 ]; then
    echo "❌ 克隆官方仓库失败，请检查网络连接和git安装"
    exit 1
fi
echo "✅ 官方仓库克隆完成"
echo

echo "2️⃣ 安装增强功能..."
python3 install_enhanced_simple.py index-tts-enhanced
if [ $? -ne 0 ]; then
    echo "❌ 增强功能安装失败"
    exit 1
fi
echo

echo "3️⃣ 进入项目目录..."
cd index-tts-enhanced

echo "4️⃣ 安装官方依赖..."
pip install -e .
if [ $? -ne 0 ]; then
    echo "⚠️  官方依赖安装失败，请手动安装"
fi

echo "5️⃣ 安装增强版依赖..."
pip install -r requirements_enhanced.txt
if [ $? -ne 0 ]; then
    echo "⚠️  增强版依赖安装失败，请手动安装"
fi

echo
echo "========================================"
echo "🎉 IndexTTS Enhanced 安装完成！"
echo "========================================"
echo
echo "📋 安装位置: index-tts-enhanced/"
echo
echo "🚀 下一步操作:"
echo "  1. 下载模型文件到 index-tts-enhanced/checkpoints/ 目录"
echo "  2. 启动服务: ./run_enhanced.sh"
echo
echo "💡 模型下载命令:"
echo "  pip install huggingface-hub"
echo "  huggingface-cli download IndexTeam/IndexTTS-1.5 config.yaml bigvgan_discriminator.pth bigvgan_generator.pth bpe.model dvae.pth gpt.pth unigram_12000.vocab --local-dir checkpoints"
echo
echo "🌐 启动后访问: http://localhost:7860"
echo 
