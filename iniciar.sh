#!/bin/bash
# Script de inicialização do VôleiPro
# Uso: bash iniciar.sh

echo "🏐 VôleiPro – Iniciando sistema..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale com: sudo apt install python3 python3-pip"
    exit 1
fi

# Instalar dependências se necessário
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Instalando dependências..."
    pip3 install -r requirements.txt
fi

# Criar pasta data se não existir
mkdir -p data

# Criar arquivo de usuários se não existir
if [ ! -f data/users.json ]; then
    echo '[{"id":"1","nome":"Administrador","email":"admin@volei.com","telefone":"(17) 99999-9999","senha":"admin123","role":"admin","criado_em":"2026-01-01T00:00:00"}]' > data/users.json
    echo "✅ Arquivo de usuários criado (admin@volei.com / admin123)"
fi

# Criar arquivo de campeonatos se não existir
if [ ! -f data/campeonatos.json ]; then
    echo '[]' > data/campeonatos.json
    echo "✅ Arquivo de campeonatos criado"
fi

echo ""
echo "🚀 Iniciando servidor em http://0.0.0.0:5000"
echo "   Acesse: http://localhost:5000"
echo "   Admin:  admin@volei.com / admin123"
echo ""
echo "   Pressione Ctrl+C para parar"
echo ""

# Verificar se gunicorn está disponível (produção) ou usar Flask dev server
if command -v gunicorn &> /dev/null; then
    gunicorn -w 2 -b 0.0.0.0:5000 app:app
else
    python3 app.py
fi
