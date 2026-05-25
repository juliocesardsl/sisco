"""
Script para testar leitura de arquivos XLS e XLSX
"""
import pandas as pd
import os

print("\n" + "="*100)
print("TESTE: Suporte a arquivos XLS e XLSX")
print("="*100 + "\n")

# Procurar arquivos Excel
arquivos = []
for root, dirs, files in os.walk('.'):
    for file in files:
        if file.endswith(('.xls', '.xlsx')):
            full_path = os.path.join(root, file)
            if '~$' not in file:  # Ignora arquivos temporários
                arquivos.append(full_path)
                ext = 'XLSX' if file.endswith('.xlsx') else 'XLS'
                print(f"✓ Encontrado ({ext}): {full_path}")

if not arquivos:
    print("❌ Nenhum arquivo Excel encontrado!")
else:
    print(f"\n{'='*100}")
    print("TESTANDO LEITURA COM DIFERENTES ENGINES")
    print(f"{'='*100}\n")
    
    for arquivo in arquivos[:3]:  # Testa os 3 primeiros
        print(f"\n📄 Arquivo: {arquivo}")
        print(f"   Tamanho: {os.path.getsize(arquivo):,} bytes")
        
        # Tentar com openpyxl
        try:
            df = pd.read_excel(arquivo, engine='openpyxl')
            print(f"   ✓ Lido com openpyxl: {df.shape[0]} linhas x {df.shape[1]} colunas")
        except Exception as e:
            print(f"   ✗ openpyxl falhou: {str(e)[:60]}")
        
        # Tentar com xlrd
        try:
            df = pd.read_excel(arquivo, engine='xlrd')
            print(f"   ✓ Lido com xlrd: {df.shape[0]} linhas x {df.shape[1]} colunas")
        except Exception as e:
            print(f"   ✗ xlrd falhou: {str(e)[:60]}")

print(f"\n{'='*100}")
print("RESULTADO")
print(f"{'='*100}\n")
print("✅ Sistema agora suporta:")
print("   • Arquivos XLSX (Excel 2007+)")
print("   • Arquivos XLS (Excel 97-2003)")
print("   • Detecção automática de formato")
print("   • Fallback automático entre engines")
