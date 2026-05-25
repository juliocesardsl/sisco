"""
Script de teste para validar a regra especial de rubrica 10502
Quando rubrica = 10502, valor_esperado = valor_vencimento × (frequência / 100)

Executa: python test_rubrica_10502.py
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

print(f"\n{'='*80}")
print(f"TESTE DA REGRA ESPECIAL - RUBRICA 10502")
print(f"{'='*80}")
print(f"Fórmula: valor_esperado = valor_vencimento × (frequência / 100)")
print(f"Exemplo: 6183,38 × (22/100) = 1360,34")
print(f"{'='*80}\n")

# Arquivos de teste
arquivo_extrator = './ppgg.xlsx'
arquivo_vencimento = './VENCIMENTO 10004.xlsx'

# Verificar se os arquivos existem
if not os.path.exists(arquivo_extrator):
    print(f"❌ Arquivo não encontrado: {arquivo_extrator}")
    print(f"   Certifique-se de que o arquivo está na raiz do projeto")
    sys.exit(1)

if not os.path.exists(arquivo_vencimento):
    print(f"❌ Arquivo não encontrado: {arquivo_vencimento}")
    print(f"   Certifique-se de que o arquivo está na raiz do projeto")
    sys.exit(1)

print(f"✓ Arquivo EXTRATOR: {arquivo_extrator}")
print(f"✓ Arquivo VENCIMENTO: {arquivo_vencimento}\n")

# Ler arquivos para validar estrutura
print(f"{'='*80}")
print(f"VALIDANDO ESTRUTURA DOS ARQUIVOS")
print(f"{'='*80}\n")

df_ext = pd.read_excel(arquivo_extrator)
print(f"EXTRATOR: {df_ext.shape[0]} linhas × {df_ext.shape[1]} colunas")
print(f"Colunas: {df_ext.columns.tolist()}\n")

df_venc = pd.read_excel(arquivo_vencimento)
print(f"VENCIMENTO: {df_venc.shape[0]} linhas × {df_venc.shape[1]} colunas")
print(f"Colunas: {df_venc.columns.tolist()}\n")

# Procurar pela coluna FREQUENCIA
print(f"{'='*80}")
print(f"PROCURANDO COLUNA FREQUENCIA")
print(f"{'='*80}\n")

col_frequencia = None
for col in df_ext.columns:
    if 'frequencia' in col.lower():
        col_frequencia = col
        print(f"✓ Coluna FREQUENCIA encontrada: '{col}'")
        print(f"  Primeiros 10 valores: {df_ext[col].head(10).tolist()}\n")
        break

if not col_frequencia:
    print(f"⚠️  AVISO: Coluna FREQUENCIA não encontrada!")
    print(f"   Colunas disponíveis no extrator: {df_ext.columns.tolist()}")
    print(f"   A regra 10502 não funcionará sem essa coluna!\n")

# Procurar pela rubrica 10502
print(f"{'='*80}")
print(f"PROCURANDO RUBRICA 10502")
print(f"{'='*80}\n")

col_prov = None
for col in df_ext.columns:
    if any(term in col.lower() for term in ['rubrica', 'prov', 'desc', 'ar', 'funcao']):
        col_prov = col
        break

if col_prov:
    rubricas = df_ext[col_prov].unique()
    print(f"Coluna de rubrica: '{col_prov}'")
    print(f"Total de rubricas: {len(rubricas)}")
    
    # Procurar especificamente por 10502
    rubricas_10502 = [r for r in rubricas if str(r).strip() == '10502']
    if rubricas_10502:
        print(f"✓ Rubrica 10502 encontrada!")
        print(f"  Registros com rubrica 10502: {len(df_ext[df_ext[col_prov].astype(str).str.strip() == '10502'])}\n")
        
        # Executar teste com rubrica 10502
        print(f"{'='*80}")
        print(f"EXECUTANDO TESTE COM RUBRICA 10502")
        print(f"{'='*80}\n")
        
        resultado = processar_verificacao(
            arquivo_vencimento,
            arquivo_extrator,
            rubrica='10502',
            ano=2024,
            carga_horaria=8
        )
        
        if 'erro' in resultado:
            print(f"\n❌ ERRO DURANTE O TESTE:")
            print(f"   {resultado['erro']}\n")
        else:
            print(f"\n✓ TESTE EXECUTADO COM SUCESSO!")
            print(f"\nRESULTADOS:")
            print(f"  Total de registros: {resultado.get('total', 0)}")
            print(f"  Status CORRETO: {resultado.get('corretos', 0)}")
            print(f"  Status VERIFICAR: {resultado.get('verificar', 0)}")
            print(f"  Status INCORRETO: {resultado.get('incorretos', 0)}\n")
            
            # Mostrar alguns exemplos
            if resultado.get('resultados'):
                print(f"{'='*80}")
                print(f"EXEMPLOS DE RESULTADOS (primeiros 5)")
                print(f"{'='*80}\n")
                
                for i, res in enumerate(resultado['resultados'][:5], 1):
                    print(f"{i}. {res['nome_servidor']}")
                    print(f"   Ref Vertical: {res['ref_vertical']} | Horizontal: {res['ref_horizontal']}")
                    print(f"   Valor Extrator: R$ {res['valor_extrator']}")
                    print(f"   Valor Vencimento: R$ {res['valor_vencimento']}")
                    print(f"   Status: {res['status']}")
                    if res['diferenca_percentual'] is not None:
                        print(f"   Diferença: {res['diferenca_absoluta']} ({res['diferenca_percentual']}%)")
                    print()
    else:
        print(f"❌ Rubrica 10502 NÃO encontrada!")
        print(f"   Rubricas disponíveis (primeiras 20): {rubricas.tolist()[:20]}\n")
        print(f"   Certifique-se de que há dados com rubrica 10502 nos arquivos.\n")
else:
    print(f"❌ Coluna de rubrica não encontrada!")
    print(f"   Colunas disponíveis: {df_ext.columns.tolist()}")

print(f"\n{'='*80}")
print(f"FIM DO TESTE")
print(f"{'='*80}\n")
