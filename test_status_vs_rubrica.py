"""
Script para mostrar a diferença entre STATUS e RUBRICA
e testar o filtro corrigido
"""
import pandas as pd
import os

arquivo = './ppgg.xlsx'

print(f"\n{'='*100}")
print(f"ESCLARECIMENTO: STATUS vs RUBRICA/PROVENTO")
print(f"{'='*100}\n")

df = pd.read_excel(arquivo)

print("❌ INCORRETO - Você estava procurando por:")
print(f"   'DESCRIÃ‡ÃƒO STATUS' = '2 - NORMAL'")
print(f"   Esta coluna tem valores: {df['DESCRIÃ‡ÃƒO STATUS'].unique().tolist()}")
print(f"   STATUS é SITUAÇÃO do servidor (Normal, Cedido, Afastado)")

print("\n✅ CORRETO - Coluna de RUBRICA/PROVENTO:")
print(f"   'PROV/DESC' = '10004'")
print(f"   Esta coluna tem valores: {df['PROV/DESC'].unique().tolist()}")
print(f"   RUBRICA é o CÓDIGO DO PROVENTO que o servidor recebe")

print(f"\n{'='*100}")
print(f"TESTANDO COM A RUBRICA CORRETA")
print(f"{'='*100}\n")

# Agora rodar com a rubrica correta
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')

import django
django.setup()

from conformidade.verificacao_utils import processar_verificacao

# Usar a rubrica correta
rubrica_teste = '10004'
arquivo_extrator = './ppgg.xlsx'
arquivo_vencimento = './VENCIMENTO 10004.xlsx'

print(f"\nTentando com:")
print(f"  - Rubrica: {rubrica_teste}")
print(f"  - Arquivo Extrator: {arquivo_extrator}")
print(f"  - Arquivo Vencimento: {arquivo_vencimento}\n")

resultado = processar_verificacao(
    arquivo_vencimento,
    arquivo_extrator,
    rubrica=rubrica_teste,
    ano=2026,
    carga_horaria=40
)

if 'erro' in resultado:
    print(f"\n❌ ERRO: {resultado['erro']}")
else:
    print(f"\n✅ SUCESSO!")
    print(f"  Total encontrados: {resultado.get('total', 0)}")
    print(f"  Corretos: {resultado.get('corretos', 0)}")
    print(f"  Incorretos: {resultado.get('incorretos', 0)}")
    if resultado.get('resultados'):
        print(f"\n  Primeiros 5 resultados:")
        for r in resultado['resultados'][:5]:
            print(f"    - {r}")
