# Sistema de Conformidade

## Descrição

O Sistema de Conformidade é uma aplicação desktop desenvolvida em Python para verificar se os pagamentos seguem os padrões definidos de acordo com rubricas, ano de referência e carga horária. O sistema permite cadastrar rubricas e empresas, realizar verificações de conformidade e exportar os resultados para arquivos CSV.

## Funcionalidades Principais

- **Cadastro de Rubricas**: Permite cadastrar novas rubricas no sistema.
- **Cadastro de Empresas**: Permite cadastrar novas empresas no sistema.
- **Verificação de Conformidade**: Valida se os pagamentos estão em conformidade com os padrões definidos.
- **Exportação de Dados**: Exporta os resultados da verificação para arquivos CSV, filtrando por status (Corretos, Verificar, Incorretos ou Todos).
- **Interface Gráfica**: Utiliza CustomTkinter para uma interface moderna e intuitiva.

## Estrutura do Projeto

- `main.py`: Arquivo principal da aplicação, contém a interface gráfica e lógica principal.
- `database_manager.py`: Gerencia as conexões e operações com o banco de dados SQLite.
- `init_db.py`: Inicializa o banco de dados e cria as tabelas necessárias.
- `export_utils.py`: Utilitários para exportação de dados para CSV.
- `test_conformidade.py`: Script de teste para validar a lógica de conformidade.
- `test_export.py`: Testes para as funcionalidades de exportação.

## Requisitos do Sistema

- Python 3.x
- Bibliotecas:
  - customtkinter
  - pandas
  - sqlite3 (incluído no Python)
  - tkinter (incluído no Python)

## Instalação

1. Clone ou baixe o repositório do projeto.
2. Instale as dependências necessárias:
   ```
   pip install customtkinter pandas
   ```
3. Execute o script de inicialização do banco de dados:
   ```
   python init_db.py
   ```

## Como Usar

1. Execute a aplicação principal:
   ```
   python main.py
   ```

2. Na tela inicial, clique em "Verificar Conformidade" para acessar a tela de verificação.

3. Na tela de verificação:
   - Selecione a rubrica desejada.
   - Insira o ano de referência.
   - Insira a carga horária.
   - Clique em "Verificar" para executar a validação.

4. Para cadastrar novas rubricas ou empresas, utilize o menu "Ferramentas" na barra superior.

5. Para exportar os resultados, clique no botão "Exportar CSV" e selecione o filtro desejado.

## Banco de Dados

O sistema utiliza SQLite como banco de dados. As tabelas principais são:

- `rubricas`: Armazena os códigos das rubricas cadastradas.
- `empresas`: Armazena os códigos das empresas cadastradas.

O arquivo do banco de dados (`banco.db`) é criado automaticamente na pasta do projeto.

## Testes

Para executar os testes:

- `test_conformidade.py`: Valida a lógica de extração de meses de datas e referências.
- `test_export.py`: Testa as funcionalidades de exportação.

Execute os testes com:
```
python test_conformidade.py
python test_export.py
```

## Arquitetura

- **Interface**: CustomTkinter para GUI moderna.
- **Banco de Dados**: SQLite para armazenamento local.
- **Lógica de Negócios**: Funções Python para validação de conformidade.
- **Exportação**: Utiliza a biblioteca csv do Python para gerar arquivos CSV.

## Desenvolvimento

O sistema foi desenvolvido com foco em:
- Facilidade de uso
- Validação robusta de dados
- Interface intuitiva
- Modularidade do código

## Suporte

Para dúvidas ou problemas, consulte os arquivos de teste ou a documentação inline no código.</content>
<filePath">f:\SEGEA\RECENTES\SUGEP\COPAG\DICOP\Julio\SisConformidade\README.md