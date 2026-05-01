# 🚀 Guia de Deploy na Vercel – VôleiPro

A Vercel é excelente para hospedar o frontend e o backend (Flask), mas ela tem uma característica importante: **o sistema de arquivos é "read-only" (apenas leitura)** e temporário. 

Isso significa que se o seu sistema salvar um novo usuário no arquivo `users.json`, esse dado **será perdido** assim que a Vercel reiniciar o servidor (o que acontece várias vezes ao dia).

---

## 🛠️ Como resolver a persistência de dados?

Para um sistema real na Vercel com menos de 1000 acessos, você tem duas opções principais:

### Opção 1: Usar o sistema atual (Ideal para Testes)
Se você apenas subir o código como está, o site vai funcionar, mas os dados não serão salvos permanentemente. Útil apenas para mostrar o design.

### Opção 2: Conectar a um Banco de Dados Gratuito (Recomendado)
Para que os dados não sumam, o ideal é trocar o salvamento em arquivo JSON por um banco de dados na nuvem.
- **Sugestão:** Use o **Vercel Postgres** ou **MongoDB Atlas** (ambos têm planos gratuitos excelentes).

---

## 📦 Passo a Passo para Subir na Vercel

### 1. Preparar o Repositório
1. Crie uma conta no [GitHub](https://github.com) se não tiver.
2. Crie um novo repositório (ex: `voleipro-valentim`).
3. Suba todos os arquivos da pasta `volei_campeonatos` para lá.

### 2. Conectar à Vercel
1. Vá para [vercel.com](https://vercel.com) e faça login com seu GitHub.
2. Clique em **"Add New"** > **"Project"**.
3. Importe o repositório que você acabou de criar.
4. A Vercel vai detectar automaticamente o arquivo `vercel.json` e o `requirements.txt`.
5. Clique em **Deploy**.

---

## 🛡️ Como Garantir que os Dados não Sumam (MongoDB)

Eu atualizei o código para suportar o **MongoDB Atlas** (que é gratuito). Siga estes passos para configurar:

1.  Crie uma conta gratuita em [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas).
2.  Crie um Cluster (Shared/Free) e um usuário de banco de dados.
3.  Pegue a sua **Connection String** (algo como `mongodb+srv://usuario:senha@cluster.mongodb.net/...`).
4.  No painel da **Vercel**, vá em **Settings** > **Environment Variables**.
5.  Adicione uma variável com o nome `MONGO_URI` e cole o seu link lá.
6.  Clique em **Save** e faça o **Redeploy**.

**Pronto!** Agora seus usuários e campeonatos ficarão salvos para sempre na nuvem.

### Se você quiser continuar na Vercel:
Eu posso te ajudar a converter o código para usar o **Vercel KV (Redis)** ou **Postgres**, que são as ferramentas da própria Vercel para salvar dados de forma permanente e gratuita para o seu volume de acessos.

---

## 🔗 Links Úteis
- [Dashboard Vercel](https://vercel.com/dashboard)
- [Documentação Vercel Python](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
