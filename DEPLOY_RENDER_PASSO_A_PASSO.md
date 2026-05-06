# Passo a Passo para Deploy do DiOn no Render

Este guia detalha como colocar o sistema Diário Online (DiOn) em produção na plataforma gratuita do Render usando o banco de dados PostgreSQL.

## Fase 1: Preparando o Repositório no GitHub
Como o Render busca o código diretamente do GitHub, o primeiro passo é ter seu projeto lá.
1. Crie uma conta no [GitHub](https://github.com/).
2. Crie um novo repositório (pode ser Privado ou Público).
3. No terminal do seu computador, na pasta do projeto `x:\DiarioOnline`, rode:
   ```bash
   git init
   git add .
   git commit -m "Versão 1.0 DiOn"
   git branch -M main
   git remote add origin URL_DO_SEU_REPOSITORIO
   git push -u origin main
   ```

## Fase 2: Criando o Banco de Dados no Render
1. Acesse o [Render Dashboard](https://dashboard.render.com/) e crie uma conta (use o login com o próprio GitHub para facilitar).
2. Clique no botão **"New +"** no canto superior direito e escolha **"PostgreSQL"**.
3. Preencha os campos:
   - **Name**: `dion-db`
   - **Database**: `dion`
   - **User**: `dion_admin`
   - **Instance Type**: Escolha a opção **Free** (Gratuita).
4. Clique em **Create Database**.
5. Na página que abrir, role para baixo até encontrar a sessão **"Connections"**. Copie o valor de **Internal Database URL** (ele será usado mais à frente e começará com `postgres://`).

## Fase 3: Criando o Web Service (O Sistema)
1. Volte ao Dashboard do Render, clique em **"New +"** e escolha **"Web Service"**.
2. Escolha a opção **"Build and deploy from a Git repository"** e conecte seu GitHub. Selecione o repositório do `DiOn`.
3. Preencha as configurações do serviço:
   - **Name**: `dion-app` (ou o nome que preferir para a URL).
   - **Region**: Pode deixar a padrão.
   - **Branch**: `main`.
   - **Runtime / Environment**: Selecione `Python 3`.
   - **Build Command**: `./build.sh` (Este script que criamos já vai baixar os requirements, coletar arquivos estáticos e rodar as migrações).
   - **Start Command**: `gunicorn dion_project.wsgi:application`
   - **Instance Type**: Escolha a opção **Free** (Gratuita).

## Fase 4: Configurando as Variáveis de Ambiente (.env)
Ainda na tela de criação do Web Service (ou na aba "Environment" se já criou), adicione as **Environment Variables**:

1. Clique em **Add Environment Variable** e adicione as chaves abaixo:
   - **Key:** `DATABASE_URL`
     **Value:** Cole aqui o "Internal Database URL" que você copiou do banco de dados no passo 2.
   - **Key:** `SECRET_KEY`
     **Value:** Escreva qualquer texto longo e maluco (ex: `dion_chave_secreta_kjs89d2k#dsj!2@sd`).
   - **Key:** `DEBUG`
     **Value:** `False`
   
   **Criando o usuário Administrador (Superuser):**
   Como o terminal interativo é limitado na conta gratuita, criamos um script para gerar seu login automaticamente. Crie essas variáveis:
   - **Key:** `ADMIN_USERNAME`
     **Value:** O login que você quer usar (ex: `diretoria`).
   - **Key:** `ADMIN_PASSWORD`
     **Value:** Sua senha segura (ex: `Dion@2026`).

2. Opcionalmente, pode configurar a versão do Python:
   - **Key:** `PYTHON_VERSION`
     **Value:** `3.11.0` (ou a versão exata que você está usando localmente).

3. Clique em **"Create Web Service"** no final da página.

## Fase 5: Monitorando o Deploy e Acessando o Sistema
1. Após clicar em Create, o Render começará o deploy. Você verá um terminal preta rodando os comandos. Aguarde até aparecer a mensagem **"Your service is live 🎉"**.
2. O nosso arquivo `build.sh` vai automaticamente rodar as migrações do banco de dados e criar seu superusuário usando as senhas que você colocou nas variáveis de ambiente.
3. Se o serviço ficar verde, ótimo! Seu site já está no ar na URL fornecida no canto superior esquerdo (ex: `https://dion-app.onrender.com`).
   - Basta acessar essa URL, clicar em Login e entrar com o seu `ADMIN_USERNAME` e `ADMIN_PASSWORD`.

Pronto! Agora é só acessar a URL do seu sistema, fazer login com o usuário criado e começar a gerenciar sua escola online.

> **Importante no Plano Grátis do Render:** 
> - O serviço entra em modo de "sono" se ficar 15 minutos sem ser acessado. O primeiro acesso do dia pode demorar cerca de 40 a 50 segundos para carregar enquanto a máquina "acorda". Depois disso, fica rápido normalmente.
> - O banco de dados grátis dura 90 dias. Para projetos sérios de longo prazo, é recomendado um upgrade para o banco mais simples pago (7 dólares/mês).

## Fase 6: Detalhes de Segurança (Por que o DiOn é Seguro na Nuvem)
Nesta versão de produção, o sistema está configurado com várias camadas de segurança essenciais:
1. **`ALLOWED_HOSTS` Automático:** O sistema bloqueia requisições que não sejam direcionadas especificamente para a URL gerada pelo Render (`RENDER_EXTERNAL_HOSTNAME`), evitando ataques de host spoofing.
2. **`CSRF_TRUSTED_ORIGINS`:** O Render serve a aplicação utilizando certificados SSL (HTTPS). Adicionamos uma verificação rigorosa para que o Django confie na origem dos envios de formulários (como a tela de Login ou realização de Chamadas), evitando os comuns erros de *CSRF Verification Failed*.
3. **Cookies Seguros e SSL Redirect:** Ao desativarmos o modo de Desenvolvimento (`DEBUG=False` no painel do Render), o DiOn automaticamente liga as proteções `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` e `SECURE_SSL_REDIRECT`. Isso garante que os cookies de sessão de professores e as informações dos alunos transitem *exclusivamente* via HTTPS criptografado.
4. **Criação Segura de Usuário:** Ao usarmos o `create_superuser.py` alimentado por Variáveis de Ambiente ocultas no painel do Render, evitamos expor senhas no código ou em scripts rodando abertamente, além de inibir tentativas de usar um shell que poderia estar comprometido.
