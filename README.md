# 🏐 VôleiPro – Sistema de Campeonatos de Vôlei

Sistema simples de gerenciamento de campeonatos de vôlei para Valentim Gentil.
Desenvolvido com **Python/Flask** e banco de dados em **arquivos JSON** — sem necessidade de instalar MySQL, PostgreSQL ou qualquer banco externo.

---

## 📁 Estrutura do Projeto

```
volei_campeonatos/
├── app.py                  # Aplicação principal Flask
├── requirements.txt        # Dependências Python
├── README.md               # Este arquivo
├── data/
│   ├── users.json          # Banco de dados de usuários
│   └── campeonatos.json    # Banco de dados de campeonatos
├── static/
│   └── css/
│       └── style.css       # Estilos do sistema
└── templates/
    ├── base.html           # Layout base (navbar, footer)
    ├── index.html          # Página inicial
    ├── login.html          # Tela de login
    ├── cadastro.html       # Tela de cadastro
    ├── campeonatos.html    # Lista de campeonatos
    ├── detalhe.html        # Detalhe do campeonato
    ├── perfil.html         # Perfil do usuário
    └── admin/
        ├── _sidebar.html       # Sidebar do admin
        ├── dashboard.html      # Painel admin
        ├── form_campeonato.html # Criar/editar campeonato
        ├── ver_campeonato.html  # Ver campeonato (admin)
        └── usuarios.html       # Gerenciar usuários
```

---

## ⚙️ Requisitos

- **Python 3.8+** instalado no servidor
- Acesso ao terminal (SSH ou painel de hospedagem)

---

## 🚀 Instalação Rápida

### 1. Copiar os arquivos para o servidor

Faça upload da pasta `volei_campeonatos/` para o seu servidor via FTP, SCP ou painel de controle.

### 2. Instalar as dependências

```bash
cd volei_campeonatos
pip3 install -r requirements.txt
```

### 3. Testar localmente

```bash
python3 app.py
```

Acesse: `http://localhost:5000`

---

## 🌐 Deploy em Produção

### Opção A: Usando Gunicorn (recomendado para VPS/Linux)

```bash
# Instalar gunicorn
pip3 install gunicorn

# Rodar em produção
gunicorn -w 2 -b 0.0.0.0:5000 app:app
```

### Opção B: Usando systemd (para manter rodando após reiniciar o servidor)

Crie o arquivo `/etc/systemd/system/voleipro.service`:

```ini
[Unit]
Description=VôleiPro – Sistema de Campeonatos
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/volei_campeonatos
ExecStart=/usr/local/bin/gunicorn -w 2 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Ative o serviço:

```bash
sudo systemctl daemon-reload
sudo systemctl enable voleipro
sudo systemctl start voleipro
```

### Opção C: Nginx como proxy reverso (porta 80/443)

Instale o Nginx e crie `/etc/nginx/sites-available/voleipro`:

```nginx
server {
    listen 80;
    server_name seudominio.com.br;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Ative:

```bash
sudo ln -s /etc/nginx/sites-available/voleipro /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## 🔐 Acesso Padrão (Admin)

| Campo  | Valor             |
|--------|-------------------|
| E-mail | admin@volei.com   |
| Senha  | admin123          |

> **IMPORTANTE:** Altere a senha do admin após o primeiro acesso em **Meu Perfil**.

---

## 🔑 Segurança

Antes de colocar em produção, altere a `secret_key` no arquivo `app.py`:

```python
app.secret_key = "coloque-aqui-uma-chave-secreta-longa-e-aleatoria"
```

Gere uma chave segura com:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 👤 Funcionalidades

### Área do Usuário
- Cadastro com nome, e-mail e telefone
- Login com e-mail e senha
- Visualizar campeonatos disponíveis
- Ver detalhes: data, local, regras, participantes
- Inscrever-se em campeonatos
- Entrar automaticamente na lista de espera quando lotado
- Cancelar inscrição (promove automaticamente o próximo da espera)
- Editar perfil e alterar senha

### Painel Administrativo
- Dashboard com estatísticas gerais
- Criar, editar e excluir campeonatos
- Definir data, local, regras, categoria e máximo de participantes
- Ver lista de inscritos e lista de espera com dados de contato
- Remover participantes individualmente
- Gerenciar usuários (promover para admin, excluir)

---

## 💾 Backup dos Dados

Os dados ficam nos arquivos JSON na pasta `data/`. Para fazer backup:

```bash
cp -r data/ backup_$(date +%Y%m%d)/
```

Recomenda-se configurar um cron job para backup automático diário:

```bash
# Editar crontab
crontab -e

# Adicionar linha (backup todo dia às 3h da manhã)
0 3 * * * cp -r /var/www/volei_campeonatos/data/ /backups/volei_$(date +\%Y\%m\%d)/
```

---

## 📞 Suporte

Sistema desenvolvido para a comunidade de vôlei de **Valentim Gentil – SP**.
