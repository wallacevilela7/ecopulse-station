#!/usr/bin/env bash
# ==============================================================
# Script de Provisionamento Automatizado para AWS EC2 (Ubuntu 24.04)
# EcoPulse Station - Projeto e Desenvolvimento II (UNIP)
# ==============================================================
set -euo pipefail

echo ">>> [1/5] Atualizando pacotes do sistema operacional..."
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y python3-pip python3-venv git nginx curl ufw postgresql-client

echo ">>> [2/5] Criando diretório de logs..."
sudo mkdir -p /var/log/ecopulse
sudo chown -R ubuntu:ubuntu /var/log/ecopulse

echo ">>> [3/5] Configurando ambiente virtual Python..."
cd /home/ubuntu/ecopulse-station/backend
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt gunicorn

echo ">>> [4/5] Instalando e habilitando serviço Systemd..."
sudo cp infra/deploy/ecopulse-backend.service /etc/systemd/system/ecopulse-backend.service
sudo systemctl daemon-reload
sudo systemctl enable ecopulse-backend.service

echo ">>> [5/5] Configurando Nginx Reverse Proxy..."
sudo cp infra/docker/nginx.conf /etc/nginx/sites-available/ecopulse
sudo ln -sf /etc/nginx/sites-available/ecopulse /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo ">>> Sucesso! Configure o arquivo .env e inicie com: sudo systemctl start ecopulse-backend"
