# VôleiPro – Sistema de Gerenciamento de Campeonatos

Uma plataforma moderna para gerenciar campeonatos de vôlei em Valentim Gentil, com autenticação de usuários, inscrições em eventos e painel administrativo.

## 🚀 Características

- **Autenticação de Usuários**: Registro e login seguro com hashing de senhas
- **Gerenciamento de Campeonatos**: Criar, editar e deletar campeonatos
- **Inscrições**: Usuários podem se inscrever em campeonatos com sistema de fila de espera
- **Painel Administrativo**: Dashboard completo para admins gerenciarem eventos e usuários
- **Design Moderno**: Interface dark mode com glassmorphism e animações suaves
- **Responsivo**: Funciona perfeitamente em desktop e mobile

## 🛠️ Stack Tecnológico

- **Backend**: Flask 3.0+
- **Banco de Dados**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Animações**: AOS (Animate On Scroll)
- **Ícones**: Font Awesome 6.4
- **Deploy**: Vercel

## 📋 Pré-requisitos

- Python 3.8+
- MongoDB Atlas (ou MongoDB local)
- Git

## 🔧 Instalação Local

1. **Clone o repositório**
   ```bash
   git clone <seu-repositorio>
   cd volei_campeonatos
   ```

2. **Crie um ambiente virtual**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure as variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Edite .env com suas credenciais do MongoDB
   ```

5. **Execute a aplicação**
   ```bash
   python3 app.py
   ```

A aplicação estará disponível em `http://localhost:5000`

## 🚀 Deploy na Vercel

### Pré-requisitos
- Conta na Vercel
- Repositório Git (GitHub, GitLab ou Bitbucket)
- Banco de dados MongoDB Atlas

### Passos para Deploy

1. **Faça push do código para seu repositório Git**
   ```bash
   git add .
   git commit -m "Preparado para deploy na Vercel"
   git push origin main
   ```

2. **Conecte seu repositório à Vercel**
   - Acesse [vercel.com](https://vercel.com)
   - Clique em "New Project"
   - Selecione seu repositório
   - Clique em "Import"

3. **Configure as variáveis de ambiente**
   - Na página de configuração do projeto, vá para "Environment Variables"
   - Adicione as seguintes variáveis:
     - `MONGO_URI`: Sua string de conexão MongoDB Atlas
     - `SECRET_KEY`: Uma chave secreta forte (gere com: `python -c "import secrets; print(secrets.token_hex(32))"`)

4. **Deploy**
   - Clique em "Deploy"
   - Aguarde a conclusão do deploy

## 📊 Estrutura do Projeto

```
volei_campeonatos/
├── app.py                 # Aplicação principal Flask
├── requirements.txt       # Dependências Python
├── vercel.json           # Configuração Vercel
├── static/
│   ├── css/
│   │   └── style.css     # Estilos CSS
│   ├── js/               # JavaScript (se houver)
│   └── img/
│       └── logo_hiccup.png
└── templates/
    ├── base.html         # Template base
    ├── index.html        # Página inicial
    ├── login.html        # Página de login
    ├── cadastro.html     # Página de cadastro
    ├── perfil.html       # Página de perfil
    ├── campeonatos.html  # Lista de campeonatos
    ├── detalhe.html      # Detalhes do campeonato
    └── admin/
        ├── dashboard.html
        ├── usuarios.html
        ├── form_campeonato.html
        └── _sidebar.html
```

## 🔐 Autenticação

### Admin Padrão
Ao criar a primeira conta, o usuário com email `jhonybrandoborges@gmail.com` será automaticamente promovido a admin.

### Criando Admins Adicionais
1. Faça login como admin
2. Vá para "Painel Admin" → "Gerenciar Usuários"
3. Clique em "Promover" ao lado do usuário desejado

## 🗄️ Banco de Dados

### Coleções MongoDB

**users**
```json
{
  "_id": ObjectId,
  "id": "uuid",
  "nome": "string",
  "email": "string",
  "telefone": "string",
  "senha": "hashed_password",
  "role": "user|admin",
  "data_cadastro": "ISO datetime"
}
```

**campeonatos**
```json
{
  "_id": ObjectId,
  "id": "uuid",
  "nome": "string",
  "data_evento": "YYYY-MM-DD",
  "hora_evento": "HH:MM",
  "local": "string",
  "categoria": "string",
  "max_participantes": "number",
  "regras": "string",
  "inscritos": ["user_id"],
  "lista_espera": ["user_id"]
}
```

## 🐛 Troubleshooting

### Erro: "Banco de Dados Offline"
- Verifique se a variável `MONGO_URI` está configurada corretamente
- Confirme que seu IP está adicionado ao IP Whitelist no MongoDB Atlas
- Teste a conexão com: `python -c "from pymongo import MongoClient; MongoClient('<sua-mongo-uri>').admin.command('ping')"`

### Erro: "Acesso restrito"
- Apenas usuários com role `admin` podem acessar o painel administrativo
- Promova um usuário a admin através do painel (ou manualmente no banco de dados)

### Rotas retornam 404
- Certifique-se de que o `vercel.json` está configurado corretamente
- Verifique se todos os templates estão na pasta `templates/`

## 📝 Rotas Disponíveis

| Rota | Método | Descrição |
|------|--------|-----------|
| `/` | GET | Página inicial |
| `/login` | GET, POST | Login de usuário |
| `/cadastro` | GET, POST | Registro de novo usuário |
| `/logout` | GET | Logout |
| `/campeonatos` | GET | Lista todos os campeonatos |
| `/campeonato/<id>` | GET | Detalhes de um campeonato |
| `/inscrever/<id>` | GET | Inscrever em um campeonato |
| `/cancelar_inscricao/<id>` | GET | Cancelar inscrição |
| `/perfil` | GET, POST | Perfil do usuário |
| `/admin` | GET | Dashboard admin |
| `/admin/usuarios` | GET | Gerenciar usuários |
| `/admin/campeonatos/novo` | GET, POST | Criar campeonato |
| `/admin/campeonatos/editar/<id>` | GET, POST | Editar campeonato |
| `/admin/campeonatos/excluir/<id>` | GET | Excluir campeonato |

## 🤝 Contribuindo

Sinta-se livre para abrir issues e pull requests!

## 📄 Licença

Este projeto está sob a licença MIT.

## 👨‍💻 Desenvolvido por

**Jhony Brando** - Hiccup Games © 2026
