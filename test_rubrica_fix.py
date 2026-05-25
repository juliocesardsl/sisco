"""
Script de teste para verificar o filtro de rubrica corrigido
Executa: python test_rubrica_fix.py
"""
import sys
import os

# Adicionar o diretório do projeto ao path
sys.path.insert(0, os.path.dirname(__file__))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')

import django
django.setup()

from conformidade.verificacao_utils import processar_verificacao
import pandas as pd

# Arquivos de teste
arquivo_extrator = './ppgg.xlsx'
arquivo_vencimento = './VENCIMENTO 10004.xlsx'

print(f"\n{'='*80}")
print(f"TESTE DE FILTRO DE RUBRICA")
print(f"{'='*80}\n")

# Verificar se os arquivos existem
if not os.path.exists(arquivo_extrator):
    print(f"❌ Arquivo não encontrado: {arquivo_extrator}")
    sys.exit(1)

if not os.path.exists(arquivo_vencimento):
    print(f"❌ Arquivo não encontrado: {arquivo_vencimento}")
    sys.exit(1)

print(f"✓ Arquivo EXTRATOR: {arquivo_extrator}")
print(f"✓ Arquivo VENCIMENTO: {arquivo_vencimento}\n")

# Ler arquivos para ver rubricas disponíveis
print(f"{'='*80}")
print(f"RUBRICAS DISPONÍVEIS NO ARQUIVO EXTRATOR:")
print(f"{'='*80}\n")

df_ext = pd.read_excel(arquivo_extrator)
print(f"Colunas: {df_ext.columns.tolist()}\n")

# Tentar encontrar coluna de rubrica
rubricas_col = None
for col in df_ext.columns:
    if any(term in col.lower() for term in ['rubrica', 'prov', 'desc', 'ar', 'funcao']):
        rubricas_col = col
        break

if rubricas_col:
    rubricas = df_ext[rubricas_col].unique()[:20]
    print(f"Coluna encontrada: '{rubricas_col}'")
    print(f"Rubricas (primeiras 20): {rubricas.tolist()}\n")
    
    # Testar com primeira rubrica
    rubrica_teste = str(rubricas[0]).strip()
    print(f"{'='*80}")
    print(f"TESTANDO COM RUBRICA: {rubrica_teste}")
    print(f"{'='*80}\n")
    
    resultado = processar_verificacao(
        arquivo_vencimento,
        arquivo_extrator,
        rubrica=rubrica_teste,
        ano=2024,
        carga_horaria=8
    )
    
    if 'erro' in resultado:
        print(f"\n❌ ERRO: {resultado['erro']}")
    else:
        print(f"\n✓ SUCESSO!")
        print(f"  Total encontrados: {resultado.get('total', 0)}")
        print(f"  Corretos: {resultado.get('corretos', 0)}")
        print(f"  Incorretos: {resultado.get('incorretos', 0)}")
else:
    print("❌ Não foi possível encontrar coluna de rubrica")
    print(f"Colunas disponíveis: {df_ext.columns.tolist()}")
