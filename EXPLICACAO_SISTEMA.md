# Explicação do Sistema de Conformidade

## 📋 Visão Geral

O **Sistema de Conformidade** é uma aplicação desktop desenvolvida em Python que valida se os pagamentos de pessoal estão em conformidade com os padrões estabelecidos pela organização. O sistema compara dois arquivos Excel (Vencimento e Extrator) para identificar discrepâncias entre pagamentos esperados e pagamentos realizados.

---

## 🎯 Objetivo Principal

Verificar automaticamente se os pagamentos de pessoal seguem os padrões definidos considerando:
- **Rubricas** (categorias de pagamento)
- **Ano de Referência** (período de análise)
- **Carga Horária** (jornada de trabalho)

---

## 🏗️ Arquitetura do Sistema

### Estrutura de Arquivos

```
SisConformidade/
├── main.py                # Interface gráfica e lógica principal
├── database_manager.py    # Gerenciamento do banco de dados
├── init_db.py             # Inicialização do banco de dados
├── export_utils.py        # Exportação para CSV
├── test_conformidade.py   # Testes de conformidade
├── test_export.py         # Testes de exportação
├── banco.db               # Banco de dados SQLite (gerado em tempo de execução)
└── README.md              # Documentação do projeto
```

---

## 🔧 Componentes Principais

### 1. **main.py** - Interface Gráfica Principal
Arquivo principal que contém:
- **Interface Gráfica** (CustomTkinter - interface moderna)
- **Painel Inicial**: Tela de boas-vindas com opções principais
- **Menu de Ferramentas**: Cadastro de rubricas e empresas
- **Tela de Conformidade**: Processamento de arquivos e comparação

#### Funcionalidades:
- ✅ Cadastro de rubricas
- ✅ Cadastro de empresas
- ✅ Seleção e upload de arquivos Excel
- ✅ Processamento de conformidade
- ✅ Exportação de resultados

---

### 2. **database_manager.py** - Gerenciador de Banco de Dados

**Responsabilidade**: Gerenciar todas as operações com o banco de dados SQLite

#### Principais Funções:

```python
def get_db_path()
```
- Retorna o caminho do banco de dados
- Funciona tanto em modo desenvolvimento como em executável (PyInstaller)

```python
def execute_query(query, params=(), fetch=None)
```
- Executa consultas SQL de forma segura
- Parâmetros:
  - `query`: String SQL
  - `params`: Tupla com parâmetros (proteção contra SQL injection)
  - `fetch`: 'one' (uma linha), 'all' (todas as linhas), ou None (escrita)
- Trata exceções de banco de dados
- Implementa timeout para evitar deadlocks

---

### 3. **init_db.py** - Inicialização do Banco de Dados

**Responsabilidade**: Criar as tabelas necessárias na primeira execução

#### Tabelas Criadas:

**Tabela: `rubricas`**
```sql
CREATE TABLE rubricas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_rubricas TEXT UNIQUE NOT NULL
)
```
- Armazena códigos de rubricas de pagamento
- Campo UNIQUE garante que não haja duplicatas

**Tabela: `empresas`** (comentada no código atual)
```sql
CREATE TABLE empresas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    num_empresas TEXT UNIQUE NOT NULL
)
```

---

### 4. **export_utils.py** - Exportação para CSV

**Responsabilidade**: Exportar resultados da conformidade para arquivos CSV

#### Função Principal:

```python
def export_items_to_csv(items_to_export, path, choice='Todos')
```

**Parâmetros:**
- `items_to_export`: Lista de dicionários com os dados
- `path`: Caminho do arquivo de saída
- `choice`: Filtro de status - 'Todos', 'Corretos', 'Verificar', 'Incorretos' ou lista

**Colunas do CSV:**
- Matrícula
- CPF
- Nome
- Rubrica (B)
- Valor (B)
- Rubrica Esperada
- Valor Esperado (A)
- Status

**Retorno**: Número de linhas exportadas

---

## 📊 Fluxo de Funcionamento

### 1. **Inicialização**
```
Executa main.py
    ↓
init_database() é chamado
    ↓
Banco de dados é criado/verificado
    ↓
Painel Principal é exibido
```

### 2. **Cadastro de Rubricas**
```
Usuário clica em "Ferramentas" → "Cadastrar Rubrica"
    ↓
Janela modal abre
    ↓
Usuário digita código da rubrica
    ↓
Clica "Salvar"
    ↓
INSERT INTO rubricas (num_rubricas) VALUES (?)
    ↓
Sucesso ou erro de duplicata
```

### 3. **Verificação de Conformidade** (Fluxo Principal)
```
Usuário clica em "Verificar Conformidade"
    ↓
Tela de Conformidade abre
    ↓
Usuário preenche:
  - Rubrica (dropdown carregado do BD)
  - Ano de Referência (ex: 2024)
  - Carga Horária (ex: 40)
    ↓
Seleciona dois arquivos Excel:
  - VENCIMENTO (Arquivo A) - pagamentos esperados
  - EXTRATOR (Arquivo B) - pagamentos realizados
    ↓
Clica "Comparar Arquivos"
    ↓
PROCESSAMENTO:
  1. Lê ambos os arquivos com pandas
  2. Normaliza nomes de colunas
  3. Encontra colunas relevantes (Ano, Carga, Rubrica, Valores, etc)
  4. Filtra dados por Ano, Carga e Rubrica
  5. Compara valores e gera status
  6. Exibe resultados em tabela
  7. Opção de exportar para CSV
```

---

## 🔍 Detalhes do Processamento de Conformidade

### Normalização de Dados

O sistema implementa normalização robusta para lidar com diferentes formatos de arquivos:

#### 1. **Limpeza de Nomes de Colunas**
```python
def flatten_and_clean_columns(df)
```
- Remove espaços extras
- Normaliza quebras de linha
- Trata colunas multi-índice do pandas

#### 2. **Normalização de Texto**
```python
def norm_text(s)
```
- Remove acentuação (transforma "Pós" em "pos")
- Converte para minúsculas
- Remove espaços extras
- Flexibiliza comparações de strings

#### 3. **Extração de Números**
```python
def extract_year(s)
def extract_number(s)
def extract_month_from_date(date_value)
def extract_month_from_reference(ref_value)
```
- Extrai anos (YYYY) de strings
- Extrai números inteiros
- Extrai mês de datas e referências
- Converte strings para inteiros para comparação numérica

### Filtragem de Dados

O sistema filtra ambos os arquivos pelos critérios fornecidos:

**Arquivo B (EXTRATOR):**
```python
df_b_filtrado = df_b[
    (df_b['ANO_NORM'] == ano_int) &
    (df_b['CARGA_NORM'] == carga_int) &
    (df_b['PROV/DESC'].str.contains(rubrica, case=False, na=False))
]
```

**Arquivo A (VENCIMENTO):**
```python
df_a_filtrado = df_a[
    (df_a['ANO_NORM'] == ano_int) &
    (df_a['CARGA_NORM'] == carga_int)
]
```

### Geração de Status

Para cada linha do arquivo A (esperado), o sistema busca correspondentes no arquivo B e compara:

| Status | Significado |
|--------|-------------|
| **Correto** | Valor encontrado em B matches o valor em A |
| **Verificar** | Valor encontrado, mas com discrepância ou informações incompletas |
| **Incorreto** | Valor não encontrado ou muito diferente do esperado |

---

## 🎨 Interface Gráfica

### Tecnologia
- **CustomTkinter**: Framework moderno de GUI baseado em Tkinter
- **Modo Light/Dark**: Suporte a temas
- **Cores Personalizadas**: Paleta verde (#324E3E)

### Telas Principais

#### 1. **Painel Inicial**
- Logotipo/Header com título
- Botão principal "Verificar Conformidade"
- Menu superior com ferramentas

#### 2. **Tela de Conformidade**
- ComboBox para seleção de rubrica (carregada do BD)
- Entrada para ano de referência
- Entrada para carga horária
- Botões para selecionar arquivos Excel
- Botão para processar comparação
- Janela de resultados em tabela

#### 3. **Janela de Resultados**
- Treeview (tabela) com colunas de comparação
- Status de conformidade
- Botão para exportar para CSV

---

## 💾 Fluxo de Dados

```
┌─────────────────────┐
│  Arquivos Excel     │
│  (VENCIMENTO)       │
│  (EXTRATOR)         │
└──────────┬──────────┘
           │
           ├─→ Pandas Lee e Processa
           │
           ├─→ Normaliza Colunas e Dados
           │
           ├─→ Filtra por Ano/Carga/Rubrica
           │
           ├─→ Compara Valores
           │
           ├─→ Gera Status
           │
           ├─→ Exibe em Tabela
           │
           └─→ Exporta para CSV (opcional)
```

---

## 🗄️ Banco de Dados

### Localização
- **Desenvolvimento**: Mesma pasta do script
- **Executável (PyInstaller)**: Mesma pasta do .exe
- **Nome**: `banco.db`

### Tabelas Usadas

**rubricas**: Armazena as rubricas disponíveis para filtro
```
id | num_rubricas
---|----------------
1  | 1000 - Salário
2  | 2000 - Vale Refeição
3  | 3000 - Vale Transporte
```

---

## 📦 Dependências

```
Python 3.x
├── customtkinter      # Interface gráfica
├── pandas            # Manipulação de dados
├── openpyxl          # Leitura de Excel (via pandas)
├── sqlite3           # Banco de dados (built-in)
└── tkinter           # Framework base (built-in)
```

### Instalação
```bash
pip install customtkinter pandas openpyxl
```

---

## 🚀 Execução

### Modo Desenvolvimento
```bash
python main.py
```

### Modo Produção (Executável)
```bash
# Gerar .exe com PyInstaller
pyinstaller --onefile main.spec

# Executar
main.exe
```

---

## 🧪 Testes

### test_conformidade.py
Testa a lógica de conformidade e normalização de dados

### test_export.py
Testa a exportação para CSV com diferentes filtros

### Executar Testes
```bash
python -m pytest test_conformidade.py
python -m pytest test_export.py
```

---

## ⚙️ Configurações Importantes

### Timeout do Banco de Dados
```python
sqlite3.connect(get_db_path(), timeout=10)
```
- 10 segundos de timeout
- Evita erros de "database is locked" em operações concorrentes

### Codificação de Arquivos
```python
open(path, 'w', newline='', encoding='utf-8')
```
- Sempre usa UTF-8 para compatibilidade
- Newline vazio para evitar problemas em diferentes SOs

---

## 🔒 Segurança

### SQL Injection Prevention
```python
cursor.execute(query, params)  # Usa parametrização
```
- Nunca faz string concatenation
- Sempre usa placeholders `?`

### Tratamento de Erros
```python
try:
    # código
except sqlite3.Error as e:
    print(f"ERRO DE BANCO DE DADOS: {e}")
```
- Trata exceções específicas
- Log de erros

---

## 📈 Workflow Típico

1. **Administrador** abre o sistema
2. **Cadastra rubricas** relevantes no banco
3. **Recebe** dois arquivos Excel:
   - Arquivo A: Pagamentos esperados (VENCIMENTO)
   - Arquivo B: Pagamentos realizados (EXTRATOR)
4. **Seleciona** no sistema:
   - Rubrica a verificar
   - Ano de referência
   - Carga horária
5. **Faz upload** dos dois arquivos
6. **Sistema processa** e gera relatório
7. **Exporta resultados** para CSV
8. **Analisa** discrepâncias e toma ações corretivas

---

## 🎯 Casos de Uso

### Caso 1: Verificação Simples
- Um funcionário
- Uma rubrica
- Um período

### Caso 2: Verificação em Massa
- Múltiplos funcionários
- Múltiplas rubricas
- Período específico

### Caso 3: Auditoria
- Período completo de um ano
- Todas as rubricas
- Exportação para análise

---

## 🐛 Tratamento de Exceções Comuns

| Erro | Causa | Solução |
|------|-------|---------|
| "database is locked" | Acesso simultâneo | Aumentar timeout |
| "Coluna não encontrada" | Formato diferente | Verificar normalização |
| "Pandas não instalado" | Dependência faltando | `pip install pandas` |
| "Arquivo inválido" | Excel corrompido | Verificar integridade do arquivo |

---

## 🔄 Fluxo de Desenvolvimento Futuro

- [ ] Integração com API de RH
- [ ] Dashboard com gráficos
- [ ] Notificações automáticas
- [ ] Histórico de conformidade
- [ ] Multi-usuário com login
- [ ] Backup automático de BD
- [ ] Importação de rubricas via Excel

---

## 📝 Notas Técnicas

### Por que CustomTkinter?
- Interface moderna em comparação com Tkinter puro
- Suporte a temas
- Componentes com melhor aparência
- Compatível com Tkinter

### Por que SQLite?
- Leve e sem servidor
- Perfeito para aplicação desktop
- Não requer instalação de BD externo
- Arquivo único portável

### Por que Pandas?
- Poderosa manipulação de dados
- Fácil leitura de Excel
- Operações em massa eficientes
- Indexação e filtragem flexível

---

## 🎓 Resumo

O Sistema de Conformidade automatiza a validação de pagamentos através de:

1. **Captura de dados** via interface gráfica
2. **Carregamento de arquivos** Excel
3. **Normalização e limpeza** de dados
4. **Comparação** conforme critérios
5. **Geração de relatórios** com status
6. **Exportação** para análise posterior

O sistema é modular, testável e fácil de manter, com separação clara de responsabilidades entre componentes.
