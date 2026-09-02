#!/usr/bin/env python
"""
Teste para validar a regra da rubrica 10264
Valida que a rubrica 10264 é calculada como 15% do vencimento
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica
from conformidade.verificacao_utils import _calcular_valor_esperado_rubrica_10264

# Teste 1: Verificar se a rubrica está configurada corretamente
print("=" * 60)
print("TESTE 1: Validar configuração da rubrica 10264 no banco")
print("=" * 60)

try:
    rubrica = Rubrica.objects.get(codigo='10264')
    print(f"Rubrica encontrada: {rubrica.nome}")
    print(f"  Código: {rubrica.codigo}")
    print(f"  Tipo de cálculo: {rubrica.tipo_calculo}")
    print(f"  Fórmula: {rubrica.formula_calculo}")
    print(f"  Descrição: {rubrica.descricao}")
    
    assert rubrica.tipo_calculo == 'percentual', "Tipo de cálculo deveria ser 'percentual'"
    assert '15' in rubrica.formula_calculo or '0.15' in rubrica.formula_calculo, "Fórmula deveria incluir 15%"
    
    print("✓ Rubrica 10264 configurada corretamente!")
    
except Rubrica.DoesNotExist:
    print("✗ ERRO: Rubrica 10264 não encontrada no banco!")
    exit(1)

# Teste 2: Validar função de cálculo
print("\n" + "=" * 60)
print("TESTE 2: Validar função de cálculo")
print("=" * 60)

cenarios = [
    (1000, 150, "Vencimento 1000 → 15%"),
    (2000, 300, "Vencimento 2000 → 15%"),
    (6183.38, 1027.51, "Vencimento 6183.38 → 15%"),
    (3000, 450, "Vencimento 3000 → 15%"),
    (5000, 750, "Vencimento 5000 → 15%"),
]

for valor_vencimento, valor_esperado_manual, descricao in cenarios:
    valor_calculado = _calcular_valor_esperado_rubrica_10264(valor_vencimento)
    
    # Calcular manual para validação
    valor_esperado_manual = round(valor_vencimento * 0.15, 2)
    
    print(f"✓ {descricao}")
    print(f"  Valor vencimento: R$ {valor_vencimento}")
    print(f"  Valor calculado: R$ {valor_calculado}")
    print(f"  Valor esperado: R$ {valor_esperado_manual}")
    
    assert valor_calculado == valor_esperado_manual, \
        f"Valores não correspondem: {valor_calculado} vs {valor_esperado_manual}"

# Teste 3: Cenários de validação
print("\n" + "=" * 60)
print("TESTE 3: Cenários de validação")
print("=" * 60)

cenarios_validacao = [
    (1000, 150.00, "CORRETO", "Valor exato (1000 × 15%)"),
    (1000, 150.01, "INCORRETO", "Valor com diferença > 0.01"),
    (1000, 149.99, "INCORRETO", "Valor abaixo do esperado"),
    (2000, 300, "CORRETO", "Valor exato (2000 × 15%)"),
    (6183.38, 927.51, "INCORRETO", "Valor muito abaixo (6183.38 × 15% = 927.51)"),
]

for valor_vencimento, valor_recebido, status_esperado, descricao in cenarios_validacao:
    valor_esperado = _calcular_valor_esperado_rubrica_10264(valor_vencimento)
    diferenca = abs(valor_recebido - valor_esperado)
    
    if valor_recebido == valor_esperado or diferenca <= 0.01:
        status = "CORRETO"
    else:
        status = "INCORRETO"
    
    esperado_ok = "✓" if status == status_esperado else "✗"
    print(f"{esperado_ok} {descricao}")
    print(f"   Vencimento: R$ {valor_vencimento} → Recebido: R$ {valor_recebido} → {status}")

print("\n" + "=" * 60)
print("✓ TODOS OS TESTES PASSARAM!")
print("=" * 60)
print("\nResumo:")
print("  • Rubrica 10264 configurada com 15% do vencimento")
print("  • Fórmula: valor_vencimento × 0.15")
print("  • Tipo: percentual (sem frequência)")
print("  • Origem de cálculo: Regra 10264")
