"""
Script detalhado para debugar TODAS as colunas do arquivo EXTRATOR
Mostra cada coluna e seus valores únicos
"""
import pandas as pd
import os

arquivo = './ppgg.xlsx'

if not os.path.exists(arquivo):
    print(f"❌ Arquivo não encontrado: {arquivo}")
else:
    df = pd.read_excel(arquivo)
    
    print(f"\n{'='*100}")
    print(f"ANÁLISE COMPLETA DO ARQUIVO: {arquivo}")
    print(f"{'='*100}\n")
    
    print(f"Shape: {df.shape[0]} linhas x {df.shape[1]} colunas\n")
    
    print(f"{'='*100}")
    print(f"TODAS AS COLUNAS E SEUS VALORES ÚNICOS")
    print(f"{'='*100}\n")
    
    for i, col in enumerate(df.columns, 1):
        print(f"\n[{i}] COLUNA: '{col}'")
        print(f"    Tipo de dado: {df[col].dtype}")
        print(f"    Total de valores: {len(df[col])}")
        print(f"    Não-nulos: {df[col].notna().sum()}")
        
        # Valores únicos
        unicos = df[col].dropna().unique()
        print(f"    Valores únicos: {len(unicos)}")
        
        # Mostrar valores
        if len(unicos) <= 20:
            print(f"    Todos os valores: {unicos.tolist()}")
        else:
            print(f"    Primeiros 20 valores: {unicos[:20].tolist()}")
            print(f"    ... e mais {len(unicos) - 20} valores")
    
    print(f"\n{'='*100}")
    print(f"ANÁLISE DE COLUNAS COM 'RUBRICA' NA DESCRIÇÃO")
    print(f"{'='*100}\n")
    
    for col in df.columns:
        col_lower = col.lower()
        if any(term in col_lower for term in ['rubrica', 'prov', 'desc', 'ar', 'funcao', 'cargo', 'nivel', 'referencia']):
            print(f"\n✓ POSSÍVEL COLUNA DE RUBRICA: '{col}'")
            unicos = df[col].dropna().unique()
            print(f"  Valores únicos: {unicos[:10].tolist()}")
