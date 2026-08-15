#!/bin/bash
# TraceTempAI 一键初始化脚本（Ubuntu 22.04）
# 用法：先完成文件上传（backend/、frontend/、requirements.txt 至 /opt/tracetempai）
#       并配置好 /opt/tracetempai/backend/.env，然后执行：
#       chmod +x deploy_init.sh && sudo ./deploy_init.sh
set -e

APP_DIR=/opt/tracetempai

echo "==> [1/6] 安装基础软件"
apt update && apt install -y python3-venv python3-pip nginx

echo "==> [2/6] 安装 Node.js 18"
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

echo "==> [3/6] 后端虚拟环境与依赖"
cd $APP_DIR/backend
if [ ! -d venv ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r $APP_DIR/requirements.txt

echo "==> [4/6] 配置 systemd 服务"
cat > /etc/systemd/system/tracetempai.service <<'EOF'
[Unit]
Description=TraceTempAI FastAPI Backend
After=network.target

[Service]
Type=simple
User=root
Group=root
WorkingDirectory=/opt/tracetempai/backend
EnvironmentFile=/opt/tracetempai/backend/.env
ExecStart=/opt/tracetempai/backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now tracetempai

echo "==> [5/6] 前端构建"
cd $APP_DIR/frontend
if [ ! -d node_modules ]; then
    npm install
else
    npm install
fi
npm run build

echo "==> [6/6] 配置 Nginx"
cat > /etc/nginx/sites-available/tracetempai <<'EOF'
server {
    listen 80;
    server_name _;
    gzip on;
    gzip_types text/plain text/css application/json application/javascript application/xml;
    gzip_min_length 1k;
    client_max_body_size 20m;
    root /opt/tracetempai/frontend/dist;
    index index.html;
    location / { try_files $uri $uri/ /index.html; }
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 600s;
        proxy_send_timeout 600s;
    }
    location /assets/ {
        expires 7d;
        add_header Cache-Control "public";
    }
}
EOF
ln -sf /etc/nginx/sites-available/tracetempai /etc/nginx/sites-enabled/tracetempai
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl reload nginx

echo "==> 部署完成！访问 http://<公网IP>"
