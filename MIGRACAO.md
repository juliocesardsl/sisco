# 🔄 Integrando o Código Antigo com Django

Este documento explica como integrar sua lógica antiga (database_manager.py, export_utils.py) com o novo sistema Django.

## 1. Sua Lógica Antiga

Você tem:
- `database_manager.py` - Gerenciamento de SQLite
- `export_utils.py` - Exportação para CSV  
- Lógica de verificação de conformidade
- Interface CustomTkinter (desktop)

## 2. Como Django Substitui Essas Funções

### ❌ Antes (Desktop):
```python
# database_manager.py
execute_query("INSERT INTO ...", params)
resultado = execute_query("SELECT * FROM ...", fetch='all')
```

### ✅ Agora (Django):
```python
# models.py - Automático!
Rubrica.objects.create(nome="...", codigo="...")
rubrica = Rubrica.objects.get(id=1)
ruins = Rubrica.objects.filter(ativa=True)

# ORM do Django cuida do banco!
```

---

## 3. Migrando Sua Lógica de Verificação

### Sua Lógica Antiga (Python Puro):
```python
def verificar_pagamento(valor, valor_minimo, valor_maximo):
    if valor < valor_minimo or valor > valor_maximo:
        return "incorreto"
    return "correto"
```

### Integrado no Django:
```python
# conformidade/models.py - JÁ IMPLEMENTADO!

class VerificacaoConformidade(models.Model):
    def verificar_conformidade(self):
        """Verifica se o valor pago está em conformidade"""
        if self.valor_pago < self.padrao.valor_minimo or \
           self.valor_pago > self.padrao.valor_maximo:
            self.status = 'incorreto'
        else:
            self.status = 'correto'
        return self.status
```

---

## 4. Exportação para CSV

### Sua Lógica Antiga:
```python
# export_utils.py
# Código que escrevia em arquivo CSV
```

### Integrado no Django:
```python
# conformidade/exporters.py - JÁ IMPLEMENTADO!

def exportar_verificacoes_csv(queryset, status='todos'):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    # Escreve dados do queryset em CSV
    return response

# URL: /conformidade/verificacoes/exportar/
```

---

## 5. Bancos de Dados

### Seu Banco Antigo:
- SQLite simples (`banco.db`)
- Sem versionamento
- Sem integridade referencial

### Novo (Django):
- SQLite com **migrações** (controle de versão)
- **Integridade referencial automática**
- Suporta PostgreSQL, MySQL, outros bancos em produção

**Migrar dados antigos:**
```bash
# 1. Django cria novo banco com models
python manage.py migrate

# 2. Importar dados do banco antigo (se necessário)
python manage.py shell
>>> from conformidade.models import Rubrica
>>> # Importar dados... (script Python)
```

---

## 6. Exemplos de Uso

### ✅ Criar Rubrica
```python
# Antes (Django forms)
from conformidade.models import Rubrica

# Automático via template HTML ou:
rubrica = Rubrica.objects.create(
    nome="Salário Mínimo",
    codigo="RUBA001",
    valor_padrao=1412.00,
    ativa=True
)
```

### ✅ Listar Rubricas
```python
# Antes
resultados = execute_query("SELECT * FROM rubricas", fetch='all')

# Agora
rubricas = Rubrica.objects.filter(ativa=True)
for r in rubricas:
    print(f"{r.codigo} - {r.nome}: R$ {r.valor_padrao}")
```

### ✅ Verificar Conformidade
```python
# Criar padrão
padrao = PadraoConformidade.objects.create(
    rubrica=rubrica,
    empresa=empresa,
    ano=2024,
    valor_minimo=1000.00,
    valor_maximo=1500.00,
    carga_horaria=40
)

# Verificar pagamento
verificacao = VerificacaoConformidade.objects.create(
    padrao=padrao,
    valor_pago=1200.00
)
verificacao.verificar_conformidade()  # Retorna 'correto'
```

### ✅ Exportar para CSV
```python
# Via URL:
GET /conformidade/verificacoes/exportar/?status=incorreto

# Programaticamente:
from conformidade.exporters import exportar_verificacoes_csv

verificacoes = VerificacaoConformidade.objects.filter(status='incorreto')
response = exportar_verificacoes_csv(verificacoes, 'incorreto')
```

---

## 7. Estrutura de Pastas - Antes vs Depois

### ❌ Antes (Desktop):
```
SisConformidade/
├── main.py
├── database_manager.py
├── export_utils.py
├── init_db.py
├── test_*.py
└── banco.db
```

### ✅ Depois (Django Web):
```
SisConformidade/
├── manage.py                    # ← Novo
├── requirements.txt             # ← Novo
├── sisconformidade/             # ← Novo - Projeto
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── conformidade/                # ← App Django
│   ├── models.py               # ← Seu banco em classes
│   ├── views.py                # ← Sua lógica em views
│   ├── forms.py                # ← Forms HTML
│   ├── urls.py                 # ← Rotas
│   ├── exporters.py            # ← export_utils.py integrado!
│   └── migrations/             # ← Controle de versão do banco
├── processos/                  # ← Nova app
├── templates/                  # ← HTML (antes era Tkinter)
├── static/                     # ← CSS/JS/Imagens
└── db.sqlite3                  # ← Novo banco com migrações
```

---

## 8. Views - Comparação

### Antes (Tkinter):
```python
class MainApp(ctk.CTk):
    def __init__(self):
        self.criar_interface()
        self.carregar_dados()
        
    def carregar_dados(self):
        resultados = execute_query("SELECT ...", fetch='all')
        # Atualizar interface gráfica
```

### Agora (Django):
```python
# conformidade/views.py

from django.views.generic import ListView

class VerificacaoListView(LoginRequiredMixin, ListView):
    model = VerificacaoConformidade
    template_name = 'conformidade/verificacao_list.html'
    
# URL: /conformidade/verificacoes/
# Template: verificacao_list.html (HTML + CSS)
# Automático: Carrega dados, renderiza, retorna HTML
```

---

## 9. Forms (Formulários)

### Antes:
Campos Tkinter criados manualmente na interface

### Agora:
```python
# conformidade/forms.py - JÁ FOI CRIADO!

class RubricaForm(ModelForm):
    class Meta:
        model = Rubrica
        fields = ['nome', 'codigo', 'valor_padrao', 'ativa']

# Gera HTML automaticamente no template!
```

---

## 10. Admin Django

Uma das maiores vantagens do Django: **Painel Admin automático**

```bash
python manage.py createsuperuser
# Acesse: http://127.0.0.1:8000/admin/
```

Você pode gerenciar dados sem escrever código HTML/CSS!

---

## 11. Deploy (Produção)

### Seu sistema desktop:
- Roda localmente
- Atualizar = distribuir novo EXE

### Django web:
- Deploy em cloud (Heroku, DigitalOcean, AWS)
- Múltiplos usuários simultâneos
- Backup automático
- HTTPS/SSL

---

## 12. Próximos Passos

### Curto Prazo (Esta Semana):
1. ✅ Estrutura criada (FEITO)
2. ⏳ Executar migrações
3. ⏳ Teste os templates
4. ⏳ Criar alguns dados no admin
5. ⏳ Testar CRUD

### Médio Prazo (Este Mês):
- Dashboards com gráficos
- Relatórios avançados
- Melhorias de UX/UI
- Testes automatizados

### Longo Prazo:
- Deploy em produção
- API REST (Django REST Framework)
- Mobile app (conexão com API)
- Notificações por email
- Backup automático

---

## 13. Troubleshooting

**P: Posso usar meu banco antigo (banco.db)?**
R: Não diretamente. Opções:
1. Exportar dados antigos via CSV
2. Importar via script Python + Django shell
3. Recriar manualmente no admin

**P: Preciso remover a lógica que tinha em database_manager.py?**
R: Sim! Django ORM substitui tudo. Delete:
- `database_manager.py` (não precisa mais)
- `init_db.py` (Django faz com migrations)
- `main.py` (era Tkinter, agora é web)
- `export_utils.py` (já integrado em `exporters.py`)

**P: Como rodar testes?**
R: Django tem test framework integrado:
```bash
python manage.py test
```

**P: Como adicionar novos campos?**
R:
1. Edite `models.py`
2. `python manage.py makemigrations`
3. `python manage.py migrate`

---

## 📚 Recursos:

- [Django Docs](https://docs.djangoproject.com/)
- [Django ORM](https://docs.djangoproject.com/en/4.2/topics/db/models/)
- [Django Views](https://docs.djangoproject.com/en/4.2/topics/views/)
- [Django Templates](https://docs.djangoproject.com/en/4.2/topics/templates/)

---

**Seu sistema está evoluindo de desktop para web. Parabéns! 🎉**
