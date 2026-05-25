"""
Script para testar geração de relatório de carga horária
Executa: python test_relatorio_carga_horaria.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')

import django
django.setup()

from conformidade.relatorio_gerador import gerar_relatorio_carga_horaria

print(f"\n{'='*80}")
print(f"TESTE DE GERAÇÃO DE RELATÓRIO DE CARGA HORÁRIA")
print(f"{'='*80}\n")

# Dados de teste
resultados_teste = [
    {
        'nome_servidor': 'ROSANGELA MOREIRA MARQUES',
        'matricula': '123456',
        'empresa': '001',
        'cpf': '123.456.789-00',
        'ref_vertical': 'S3',
        'ref_horizontal': '25',
        'valor_vencimento': 5812.14,
        'valor_total_recebido': 4359.11,
        'frequencia': None,
        'valor_calculado': 5812.14,
        'status': 'INCORRETO',
        'diferenca_absoluta': 1453.03,
        'diferenca_percentual': 25.0,
        'justificativa': 'Carga horária divergente: recebeu como 30h (R$ 4359.11) em vez de 40h.',
    },
    {
        'nome_servidor': 'JOÃO SILVA SANTOS',
        'matricula': '654321',
        'empresa': '002',
        'cpf': '987.654.321-11',
        'ref_vertical': 'S2',
        'ref_horizontal': '20',
        'valor_vencimento': 4500.00,
        'valor_total_recebido': 3375.00,
        'frequencia': None,
        'valor_calculado': 4500.00,
        'status': 'INCORRETO',
        'diferenca_absoluta': 1125.00,
        'diferenca_percentual': 25.0,
        'justificativa': 'Carga horária divergente: recebeu como 30h (R$ 3375.00) em vez de 40h.',
    },
]

# Gerar documento
try:
    print("Gerando documento...")
    doc_io = gerar_relatorio_carga_horaria(
        resultados=resultados_teste,
        rubrica='10004',
        ano=2026,
        carga_cadastrada=40
    )
    
    # Salvar em arquivo
    arquivo_saida = './relatorio_teste_carga_horaria.docx'
    with open(arquivo_saida, 'wb') as f:
        f.write(doc_io.getvalue())
    
    print(f"✓ Documento gerado com sucesso!")
    print(f"✓ Arquivo salvo em: {arquivo_saida}")
    print(f"✓ Servidores inclusos: {len(resultados_teste)}")
    print(f"\n{'='*80}\n")
    
except Exception as e:
    print(f"✗ Erro ao gerar documento:")
    print(f"  {str(e)}")
    import traceback
    traceback.print_exc()
