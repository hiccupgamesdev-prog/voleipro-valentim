# 🚀 Guia Iniciante: Como colocar seu site no ar (Vercel + GitHub)

Jhony, seguir este caminho é o melhor porque seu site terá um endereço oficial (ex: `voleipro.vercel.app`) e funcionará direto do celular dos seus amigos.

---

### 1º Passo: Criar uma conta no GitHub
O GitHub é onde guardamos o código.
1. Acesse [github.com](https://github.com/) e crie uma conta gratuita.
2. No canto superior direito, clique no botão **"+"** e depois em **"New repository"**.
3. Dê um nome para ele (ex: `voleipro-valentim`).
4. Deixe como **Public** e clique em **"Create repository"**.

### 2º Passo: Enviar os arquivos para o GitHub
Como você nunca fez isso, o jeito mais fácil é:
1. No seu computador, extraia o arquivo ZIP que te mandei.
2. No GitHub, na página do repositório que você criou, clique no link **"uploading an existing file"**.
3. Arraste **todos os arquivos de dentro da pasta** `volei_campeonatos` para lá.
4. Espere carregar, role para baixo e clique em **"Commit changes"**.

### 3º Passo: Conectar na Vercel (Onde o site ganha vida)
1. Acesse [vercel.com](https://vercel.com/) e clique em **"Signup"**.
2. Escolha **"Continue with GitHub"**. Isso vai conectar sua conta da Vercel com o código que você acabou de subir.
3. Após logar, você verá um botão azul escrito **"Add New..."** e depois **"Project"**.
4. Você verá o seu repositório `voleipro-valentim` na lista. Clique em **"Import"**.
5. Não precisa mudar nada nas configurações. Clique apenas em **"Deploy"**.

### 4º Passo: Pronto! 🎉
A Vercel vai levar uns 2 minutos para "construir" seu site. Quando terminar, ela vai te dar um link (ex: `https://voleipro-valentim.vercel.app`). 

**Mande esse link para a galera de Valentim Gentil e pronto!**

---

### ⚠️ Dica de Ouro sobre os Dados
Como te falei, a Vercel é "volátil". Se você cadastrar um campeonato hoje, e a Vercel reiniciar o servidor amanhã, os dados do arquivo JSON podem sumir.

**Para uso real com seus amigos:**
Se você perceber que os dados estão sumindo, me avise! Eu posso te ajudar a conectar um banco de dados chamado **MongoDB Atlas** (que também é grátis e eterno) para que os dados nunca sumam, mesmo que o servidor reinicie.

**Créditos no ar:**
O site já vai subir com seu nome **Jhony Brando** e a logo da **Hiccup Games** brilhando no topo!
