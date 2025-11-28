#!/bin/bash
# RedInk 服务器部署脚本

set -e

echo "=========================================="
echo "RedInk 项目部署脚本"
echo "=========================================="

# 服务器配置
SERVER_HOST="212.64.57.87"
SERVER_USER="root"
SERVER_PASS="Agenticseek1121"
DEPLOY_DIR="/opt/redink"
SERVICE_NAME="redink"

echo "1. 连接到服务器并创建部署目录..."
sshpass -p "$SERVER_PASS" ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'ENDSSH'
    mkdir -p /opt/redink
    mkdir -p /opt/redink/output
    mkdir -p /opt/redink/history
ENDSSH

echo "2. 上传项目文件..."
sshpass -p "$SERVER_PASS" rsync -avz --exclude='.git' --exclude='.venv' --exclude='node_modules' --exclude='frontend/node_modules' --exclude='frontend/dist' \
    /Users/weixiaogang/AI/redink/ "$SERVER_USER@$SERVER_HOST:$DEPLOY_DIR/"

echo "3. 在服务器上安装依赖和构建..."
sshpass -p "$SERVER_PASS" ssh "$SERVER_USER@$SERVER_HOST" << ENDSSH
    cd $DEPLOY_DIR
    
    # 检查 Python 版本
    if ! command -v python3.11 &> /dev/null; then
        echo "安装 Python 3.11..."
        # 这里需要根据服务器系统安装 Python 3.11
        # Ubuntu/Debian: apt-get install python3.11 python3.11-venv
        # CentOS/RHEL: yum install python311
    fi
    
    # 检查 uv
    if ! command -v uv &> /dev/null; then
        echo "安装 uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="\$HOME/.cargo/bin:\$PATH"
    fi
    
    # 安装后端依赖
    echo "安装后端依赖..."
    uv sync
    
    # 检查 Node.js 和 pnpm
    if ! command -v node &> /dev/null; then
        echo "安装 Node.js..."
        # 这里需要根据服务器系统安装 Node.js
    fi
    
    if ! command -v pnpm &> /dev/null; then
        echo "安装 pnpm..."
        npm install -g pnpm
    fi
    
    # 构建前端
    echo "构建前端..."
    cd frontend
    pnpm install
    pnpm build
    cd ..
    
    echo "✅ 依赖安装和构建完成"
ENDSSH

echo "4. 创建 systemd 服务..."
sshpass -p "$SERVER_PASS" ssh "$SERVER_USER@$SERVER_HOST" << ENDSSH
    cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=RedInk 小红书图文生成器
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$DEPLOY_DIR
Environment="PATH=/root/.cargo/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/root/.cargo/bin/uv run python -m backend.app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable ${SERVICE_NAME}
    systemctl restart ${SERVICE_NAME}
    
    echo "✅ 服务已启动"
    systemctl status ${SERVICE_NAME} --no-pager
ENDSSH

echo "=========================================="
echo "✅ 部署完成！"
echo "=========================================="
echo "服务地址: http://$SERVER_HOST:12398"
echo "查看日志: ssh $SERVER_USER@$SERVER_HOST 'journalctl -u $SERVICE_NAME -f'"
echo "停止服务: ssh $SERVER_USER@$SERVER_HOST 'systemctl stop $SERVICE_NAME'"
echo "启动服务: ssh $SERVER_USER@$SERVER_HOST 'systemctl start $SERVICE_NAME'"

