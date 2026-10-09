# Django Setup Guide - SISCO

## 1. Criar um ambiente virtual

```bash
# Power Shell
python -m venv venv
./venv/Scripts/Activate.ps1

# CMD
python -m venv venv
venv\Scripts\activate.bat
```

## 2. Instalar as dependências

```bash
pip install -r requirements.txt
```

## 3. Configurar o banco de dados

Por padrão, o projeto usa SQLite em `db.sqlite3`. Para usar PostgreSQL, crie
um arquivo `.env` na raiz do projeto (não compartilhe nem versione esse arquivo)
e configure as variáveis abaixo com os dados do banco:

```env
DB_ENGINE=postgresql
DB_NAME=sisco_db
DB_USER=sisco_app
DB_PASSWORD=senha_definida_no_PostgreSQL
DB_HOST=localhost
DB_PORT=5432
```

O usuário `sisco_app` precisa ter permissão para criar e alterar tabelas no
banco `sisco_db`, pois o Django aplica as migrações.

> **Atenção:** `migrate` cria a estrutura das tabelas, mas não copia os dados
> do SQLite. Antes de apontar para PostgreSQL, faça backup do banco SQLite e
> planeje a transferência dos dados e dos arquivos enviados. Não apague nem
> substitua `db.sqlite3` durante essa etapa.

## 4. Executar migrações

Confirme primeiro que `DB_ENGINE`, usuário, senha, host e porta estão corretos.
O comando abaixo aplica as migrações no banco configurado em `.env`.

```bash
python manage.py migrate
```

## 5. Criar superusuário (admin)

```bash
python manage.py createsuperuser
```

## 6. Executar o servidor de desenvolvimento

```bash
python manage.py runserver
```

Acesse http://127.0.0.1:8000/

## 7. Acessar o painel administrativo

```
URL: http://127.0.0.1:8000/admin/
Usuário: (criado no passo 4)
Senha: (criada no passo 4)
```

## Estrutura do Projeto

```
SisConformidade/
├── manage.py                 # Script de gerenciamento Django
├── requirements.txt          # Dependências do projeto
├── sisconformidade/          # Configurações do projeto
│   ├── __init__.py
│   ├── settings.py           # Configurações do Django
│   ├── urls.py               # Rotas principais
│   ├── wsgi.py               # WSGI para produção
│   └── asgi.py               # ASGI para WebSockets (futuro)
├── conformidade/             # App de Conformidade
│   ├── migrations/
│   ├── models.py             # Modelos: Rubrica, Empresa, Padrão, Verificação
│   ├── views.py              # Views para CRUD
│   ├── urls.py               # Rotas da app
│   ├── forms.py              # Formulários
│   ├── admin.py              # Admin do Django
│   └── exporters.py          # Exportação para CSV
├── processos/                # App de Processos
│   ├── migrations/
│   ├── models.py             # Modelos: Processo, Documento, Comentário
│   ├── views.py              # Views para CRUD
│   ├── urls.py               # Rotas da app
│   ├── forms.py              # Formulários
│   └── admin.py              # Admin do Django
├── templates/                # Templates HTML
│   ├── home.html             # Página inicial
│   ├── login.html            # Login (criar)
│   └── (outras páginas)
└── static/                   # Arquivos estáticos
    ├── css/
    │   ├── style.css
    │   └── dashboard.css
    └── images/
```

## Comandos Úteis

```bash
# Criar uma nova migration após alterar modelos
python manage.py makemigrations

# Aplicar migrations
python manage.py migrate

# Criar superusuário
python manage.py createsuperuser

# Coletar arquivos estáticos (em produção)
python manage.py collectstatic

# Shell interativo do Django
python manage.py shell

# Teste de email
python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('teste', 'corpo', 'from@example.com', ['to@example.com'])
```

## Próximos Passos

1. ✅ Criar templates para CRUD (rubricas, empresas, etc)
2. ✅ Implementar autenticação e permissões
3. ✅ Criar dashboards com estatísticas
4. ✅ Implementar relatórios avançados
5. ✅ Adicionar paginação e filtros
6. ✅ Deploy em produção (Gunicorn + Nginx)

## Dependências Principais

- **Django 4.2.11**: Framework web Python
- **Pillow**: Processamento de imagens (opcional, para perfil de usuários)
- **python-decouple**: Gerenciamento de variáveis de ambiente

## Configuração de Ambiente (.env - opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
DEBUG=True
SECRET_KEY=seu-secret-key-aqui
ALLOWED_HOSTS=127.0.0.1,localhost
```

Depois instale `python-decouple` e use no `settings.py`:

```python
from decouple import config
DEBUG = config('DEBUG', default=True, cast=bool)
SECRET_KEY = config('SECRET_KEY')
```
