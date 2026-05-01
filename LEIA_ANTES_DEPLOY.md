# ⚠️ IMPORTANTE - LEIA ANTES DE FAZER O DEPLOY NA VERCEL

## Problema da Logo Não Aparecer

Se a logo não está aparecendo no seu site na Vercel, o problema é que a pasta `static` não está sendo incluída corretamente no deploy.

### Solução:

1. **Certifique-se de que o arquivo `.vercelignore` existe** na raiz do seu projeto (mesmo nível que `app.py`). Este arquivo garante que a pasta `static` seja incluída no deploy.

2. **Verifique se a pasta `static/img/` contém `logo_hiccup.png`**:
   ```
   static/
   └── img/
       └── logo_hiccup.png
   ```

3. **No seu repositório Git, faça:**
   ```bash
   git add .vercelignore
   git add static/
   git commit -m "Fix: Include static files in Vercel deployment"
   git push
   ```

4. **Na Vercel, faça um novo deploy:**
   - Vá para o seu projeto na Vercel
   - Clique em "Deployments"
   - Clique no botão "..." ao lado do último deploy
   - Selecione "Redeploy"

5. **Aguarde o deploy terminar** e recarregue o site. A logo deve aparecer agora!

### Se ainda não funcionar:

- Abra o DevTools do navegador (F12)
- Vá para a aba "Network"
- Procure por requisições para `/static/img/logo_hiccup.png`
- Se retornar 404, o arquivo não está sendo servido corretamente
- Verifique se o arquivo existe no seu repositório Git

### Arquivos Importantes:

- `.vercelignore` - Garante que static/ seja incluído
- `vercel.json` - Configuração de rotas e build
- `app.py` - Aplicação Flask com rota para servir estáticos

---

**Desenvolvido por:** Jhony Brando  
**Projeto:** VôleiPro - Valentim Gentil  
**Data:** Maio de 2026
