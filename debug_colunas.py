"""Script para debugar e listar todas as colunas do arquivo EXTRATOR"""
import pandas as pd
import os

# Procura por arquivos Excel na pasta
excel_files = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith(('.xlsx', '.xls')):
            full_path = os.path.join(root, file)
            excel_files.append(full_path)
            print(f"✓ Encontrado: {full_path}")

if not excel_files:
    print("❌ Nenhum arquivo Excel encontrado!")
    print("\nCrie um arquivo test_extrator.xlsx ou ppgg.xlsx e coloque na pasta do projeto")
else:
    for arquivo in excel_files:
        print(f"\n{'='*80}")
        print(f"ANALISANDO: {arquivo}")
        print(f"{'='*80}")
        
        try:
            df = pd.read_excel(arquivo)
            
            print(f"\nShape: {df.shape[0]} linhas x {df.shape[1]} colunas")
            print(f"\n📋 LISTA DE COLUNAS:")
            for i, col in enumerate(df.columns):
                print(f"  {i+1}. '{col}'")
            
            print(f"\n📊 PRIMEIRAS 3 LINHAS:")
            print(df.head(3).to_string())
            
            print(f"\n🔍 VALORES ÚNICOS DE CADA COLUNA (até 10):")
            for col in df.columns:
                unicos = df[col].unique()[:10]
                print(f"  {col}: {unicos.tolist()}")
                
        except Exception as e:
            print(f"❌ Erro ao ler {arquivo}: {e}")
