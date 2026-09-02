#!/usr/bin/env python
"""
Teste para validar a regra da rubrica 10059
Valida que a rubrica 10059 usa a mesma regra que 10020: ((valor_vencimento / 30) * frequencia) * 0.25
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica
from conformidade.verificacao_utils import _calcular_valor_esperado_rubrica_10020

# Teste 1: Verificar se a rubrica está configurada corretamente
print("=" * 60)
print("TESTE 1: Validar configuração da rubrica 10059 no banco")
print("=" * 60)

try:
    rubrica = Rubrica.objects.get(codigo='10059')
    print(f"Rubrica encontrada: {rubrica.nome}")
    print(f"  Código: {rubrica.codigo}")
    print(f"  Tipo de cálculo: {rubrica.tipo_calculo}")
    print(f"  Fórmula: {rubrica.formula_calculo}")
    print(f"  Descrição: {rubrica.descricao}")
    
    assert 'frequencia' in rubrica.formula_calculo.lower(), "Fórmula deveria incluir frequência"
    assert '0.25' in rubrica.formula_calculo or '25%' in rubrica.formula_calculo, "Fórmula deveria incluir 25%"
    
    print("✓ Rubrica 10059 configurada corretamente!")
    
except Rubrica.DoesNotExist:
    print("✗ ERRO: Rubrica 10059 não encontrada no banco!")
    exit(1)

# Teste 2: Validar cálculo com diferentes cenários
print("\n" + "=" * 60)
print("TESTE 2: Validar cálculos com diferentes cenários")
print("=" * 60)

cenarios = [
    (1000, 30, "Vencimento 1000, frequência 30 (mês completo)"),
    (1000, 15, "Vencimento 1000, frequência 15 (meio mês)"),
    (2000, 20, "Vencimento 2000, frequência 20 (2/3 do mês)"),
    (1500, 10, "Vencimento 1500, frequência 10"),
]

for valor_vencimento, frequencia, descricao in cenarios:
    valor_esperado = _calcular_valor_esperado_rubrica_10020(
        valor_vencimento, 
        frequencia,
        None
    )
    
    # Cálculo manual para validação
    valor_esperado_manual = round((valor_vencimento / 30) * frequencia * 0.25, 2)
    
    print(f"✓ {descricao}")
    print(f"  Valor vencimento: R$ {valor_vencimento}")
    print(f"  Frequência: {frequencia} dias")
    print(f"  Valor esperado (função): R$ {valor_esperado}")
    print(f"  Valor esperado (manual): R$ {valor_esperado_manual}")
    
    assert valor_esperado == valor_esperado_manual, \
        f"Valores não correspondem: {valor_esperado} vs {valor_esperado_manual}"

print("\n" + "=" * 60)
print("✓ TODOS OS TESTES PASSARAM!")
print("=" * 60)
print("\nResumo:")
print("  • Rubrica 10059 configurada com mesma regra de 10020")
print("  • Fórmula: ((valor_vencimento / 30) * frequencia) * 0.25")
print("  • Validação: percentual com base em frequência")
print("  • Origem de cálculo: Regra 10059")
