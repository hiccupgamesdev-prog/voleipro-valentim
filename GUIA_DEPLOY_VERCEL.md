# Guia Completo de Deploy na Vercel

## 📋 Checklist Pré-Deploy

- [ ] Código testado localmente
- [ ] Variáveis de ambiente configuradas em `.env`
- [ ] Repositório Git criado e sincronizado
- [ ] MongoDB Atlas configurado
- [ ] IP whitelist atualizado no MongoDB Atlas

## 🔑 Variáveis de Ambiente Necessárias

Na Vercel, configure as seguintes variáveis em **Settings → Environment Variables**:

### Obrigatórias
- **MONGO_URI**: String de conexão MongoDB Atlas
  - Formato: `mongodb+srv://usuario:senha@cluster.mongodb.net/voleipro?retryWrites=true&w=majority`
  - Obtenha em: MongoDB Atlas → Connect → Connect your application

- **SECRET_KEY**: Chave secreta para sessões Flask
  - Gere com: `python -c "import secrets; print(secrets.token_hex(32))"`
  - Mude em produção por segurança

### Opcionais
- **FLASK_ENV**: `production` (padrão)

## 🚀 Passos para Deploy

### 1. Preparar o Repositório

```bash
# Clone ou navegue para o diretório do projeto
cd volei_campeonatos

# Inicialize git se ainda não tiver
git init
git add .
git commit -m "Preparado para deploy na Vercel"

# Adicione seu repositório remoto
git remote add origin https://github.com/seu-usuario/seu-repositorio.git
git push -u origin main
```

### 2. Conectar à Vercel

**Opção A: Via Dashboard Vercel (Recomendado)**

1. Acesse [vercel.com](https://vercel.com)
2. Clique em **"New Project"**
3. Selecione seu repositório GitHub/GitLab/Bitbucket
4. Clique em **"Import"**
5. Na página de configuração:
   - **Framework Preset**: Python
   - **Root Directory**: `volei_campeonatos` (se o projeto estiver em subpasta)
   - Deixe outros campos com valores padrão
6. Clique em **"Environment Variables"** e adicione:
   - `MONGO_URI`: Sua string de conexão
   - `SECRET_KEY`: Sua chave secreta
7. Clique em **"Deploy"**

**Opção B: Via CLI Vercel**

```bash
# Instale o Vercel CLI
npm i -g vercel

# Faça login
vercel login

# Deploy
vercel --prod
```

### 3. Configurar MongoDB Atlas

1. Acesse [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Crie um cluster (Free tier é suficiente)
3. Vá para **Database Access** e crie um usuário
4. Vá para **Network Access** e adicione o IP `0.0.0.0/0` (ou o IP da Vercel)
5. Vá para **Connect** → **Connect your application**
6. Copie a string de conexão e substitua `<password>` pela senha do usuário
7. Cole em `MONGO_URI` na Vercel

## ✅ Verificar Deploy

1. Acesse a URL do seu projeto na Vercel
2. Teste as rotas principais:
   - `/` - Página inicial
   - `/login` - Página de login
   - `/cadastro` - Página de cadastro

## 🔍 Troubleshooting

### Erro: "Cannot find module 'flask'"
- **Solução**: Verifique se `requirements.txt` está no diretório raiz do projeto

### Erro: "MongoDB connection timeout"
- **Solução**: 
  - Verifique se `MONGO_URI` está correto
  - Adicione o IP da Vercel ao whitelist do MongoDB Atlas
  - Tente: `0.0.0.0/0` (menos seguro, mas funciona para testes)

### Erro: "Static files not loading"
- **Solução**: 
  - Verifique se a pasta `static/` existe
  - Confirme que `vercel.json` tem a rota `/static/(.*)`
  - Limpe o cache do navegador (Ctrl+Shift+Delete)

### Erro: "Acesso restrito" ao acessar `/admin`
- **Solução**: 
  - Crie uma conta com o email `jhonybrandoborges@gmail.com` para ser admin automaticamente
  - Ou promova um usuário existente no painel admin

### Erro: "Database Offline"
- **Solução**: 
  - Verifique a variável `MONGO_URI`
  - Teste a conexão localmente: `python -c "from pymongo import MongoClient; MongoClient('<sua-uri>').admin.command('ping')"`

## 🔐 Segurança

### Antes de ir para Produção

1. **Mude a SECRET_KEY**
   - Gere uma nova: `python -c "import secrets; print(secrets.token_hex(32))"`
   - Atualize em Vercel → Environment Variables

2. **Restrinja o IP do MongoDB**
   - Ao invés de `0.0.0.0/0`, adicione apenas o IP da Vercel
   - Vercel → Project Settings → Deployments para ver IPs

3. **Use variáveis de ambiente**
   - Nunca commite `.env` com dados reais
   - Use `.env.example` como template

4. **Ative HTTPS**
   - Vercel ativa automaticamente
   - Verifique em Project Settings → Domains

## 📊 Monitoramento

### Logs da Vercel

```bash
# Ver logs em tempo real
vercel logs seu-projeto.vercel.app --follow
```

### Métricas

- Acesse **Analytics** no dashboard da Vercel
- Monitore: Requests, Bandwidth, Serverless Function Duration

## 🔄 Atualizações

### Deploy de Novas Versões

```bash
# Faça as alterações localmente
git add .
git commit -m "Descrição das mudanças"

# Push para o repositório
git push origin main

# Vercel fará deploy automaticamente
```

## 📞 Suporte

- **Documentação Vercel**: https://vercel.com/docs
- **Documentação Flask**: https://flask.palletsprojects.com/
- **Documentação MongoDB**: https://docs.mongodb.com/
