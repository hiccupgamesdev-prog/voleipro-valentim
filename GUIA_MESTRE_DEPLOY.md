# 🏆 Guia Mestre de Deploy: VôleiPro (Vercel + MongoDB)

Jhony, este guia foi feito para quem nunca mexeu com isso. Siga cada passo e seu site ficará perfeito e profissional.

---

## 1. Configurando o Banco de Dados (MongoDB Atlas)

*O banco de dados é onde as informações ficam salvas para sempre.*

1. Acesse [mongodb.com/atlas](https://www.mongodb.com/cloud/atlas) e crie uma conta grátis.

1. **Crie o Cluster:** Clique em "Create" e escolha a opção **M0 (Free)**. Escolha qualquer servidor (AWS/GCP) e clique em "Create Deployment".

1. **Segurança (Usuário):** Ele vai pedir para criar um usuário.
  - Escolha um nome (ex: `admin`) e uma senha (ex: `volei2026`).
  - **IMPORTANTE:** Anote essa senha, vamos usar ela já já. Clique em "Create Database User".

1. **Segurança (IP):** Em "IP Access List", clique em "Add My Current IP Address" e também adicione o IP `0.0.0.0/0` (isso permite que a Vercel acesse o banco). Clique em "Finish and Close".

1. **Pegar o Link de Conexão:**
  - No seu painel (Dashboard), clique no botão azul **"Connect"**.
  - Escolha **"Drivers"**.
  - Copie o link que aparecer (ex: `mongodb+srv://admin:<password>@cluster0.xxxx.mongodb.net/?retryWrites=true&w=majority`).
  - **O SEGREDO:** Onde está escrito `<password>`, você deve apagar isso e colocar a senha que você criou no passo 3. O link final deve ser algo como: `mongodb+srv://admin:volei2026@cluster0...`

---

## 2. Configurando a Vercel

*Onde o site ganha vida e o design aparece.*

1. Suba os arquivos para o GitHub (como você já fez).

1. No painel da Vercel, clique no seu projeto.

1. Vá na aba **"Settings"** (no topo) e depois em **"Environment Variables"** (na lateral esquerda).

1. Adicione a variável que faz o banco funcionar:
  - **Key:** `MONGO_URI`
  - **Value:** Cole aquele link completo do MongoDB que você preparou no passo anterior.
  - Clique em **"Add"**.

1. **DICA PARA O DESIGN:** Vá na aba **"Deployments"**, clique nos três pontinhos do seu último deploy e escolha **"Redeploy"**. Isso vai forçar a Vercel a ler as novas configurações de pastas que eu fiz para o CSS não sumir.

---

## 3. Seu Acesso de Administrador

Eu já deixei configurado no código:

- **E-mail:** `jhonybrandoborges@gmail.com`

- **Senha:** `Bakuman12345`

**O que fazer:** Assim que o site subir, vá em **"Cadastrar"** e crie sua conta com esse e-mail exato. O sistema vai reconhecer automaticamente que você é o **Dono (Admin)** e vai liberar o botão "Painel Admin" no menu para você criar os campeonatos.

---

## 4. Por que o design sumiu antes?

A Vercel às vezes se confunde com onde estão os arquivos de estilo. Eu ajustei o arquivo `app.py` para dizer explicitamente: *"Vercel, o CSS está na pasta /static"*. Agora, ao fazer o **Redeploy**, o visual dark deve aparecer perfeitamente.

---

### Checklist de Sucesso:

- [x] Criei o banco no MongoDB.

- [x] Coloquei o link `MONGO_URI` nas "Environment Variables" da Vercel.

- [x] Fiz o "Redeploy" na Vercel.

- [x] Cadastrei meu e-mail `jhonybrandoborges@gmail.com` no site.

- [x] Vi o botão "Painel Admin" aparecer.

**Agora é só mandar o link para a galera de Valentim Gentil!** 🏐🐉

