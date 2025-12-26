#!/bin/bash

# Mock Data API 快速测试脚本

echo "🚀 Veri-Train Mock Data API 测试"
echo "================================"
echo ""

# 检查Python版本
echo "📌 检查Python版本..."
python3 --version || { echo "❌ Python3未安装"; exit 1; }
echo ""

# 检查是否在正确目录
if [ ! -f "app/main.py" ]; then
    echo "❌ 请在 Veri-Train 目录下运行此脚本"
    exit 1
fi

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "🔧 激活虚拟环境..."
source venv/bin/activate

# 安装核心依赖 (仅测试需要的最小依赖)
echo "📥 安装核心依赖..."
pip install -q fastapi uvicorn pydantic sqlalchemy python-multipart || {
    echo "❌ 依赖安装失败"
    exit 1
}

echo ""
echo "✅ 环境准备完成！"
echo ""
echo "🌟 启动API服务器..."
echo "   - API文档: http://localhost:8000/api/v1/docs"
echo "   - 健康检查: http://localhost:8000/health"
echo ""
echo "💡 提示: 所有API都已使用假数据，无需数据库！"
echo ""
echo "按 Ctrl+C 停止服务器"
echo "================================"
echo ""

# 启动服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
