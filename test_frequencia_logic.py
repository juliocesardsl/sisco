#!/usr/bin/env python
"""
Teste para validar o comportamento da frequência = 0
Quando frequência é 0 mas a pessoa está recebendo um valor,
o sistema calcula como se fosse mês completo (frequência = 30)
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.verificacao_utils import _calcular_valor_esperado_rubrica_10020

print("=" * 70)
print("TESTE: Frequência = 0 com valor recebido = assume frequência 30")
print("=" * 70)

cenarios = [
    {
        'nome': 'Cenário 1: Frequência 0 com valor recebido',
        'valor_vencimento': 6183.38,
        'frequencia': 0,
        'valor_extrator': 1545.84,
        'esperado_manual': 1545.85  # (6183.38 / 30) * 30 * 0.25 = 1545.845
    },
    {
        'nome': 'Cenário 2: Frequência 0 com valor recebido (vencimento menor)',
        'valor_vencimento': 3000,
        'frequencia': 0,
        'valor_extrator': 750,
        'esperado_manual': 750.00  # (3000 / 30) * 30 * 0.25 = 750
    },
    {
        'nome': 'Cenário 3: Frequência 0 sem valor recebido',
        'valor_vencimento': 2000,
        'frequencia': 0,
        'valor_extrator': None,
        'esperado_manual': 500.00  # (2000 / 30) * 30 * 0.25 = 500
    },
    {
        'nome': 'Cenário 4: Frequência = 15 (meio mês) com valor recebido',
        'valor_vencimento': 6000,
        'frequencia': 15,
        'valor_extrator': 250,
        'esperado_manual': 250.00  # (6000 / 30) * 15 * 0.25 = 250
    },
]

print()
for cenario in cenarios:
    valor_calculado = _calcular_valor_esperado_rubrica_10020(
        cenario['valor_vencimento'],
        cenario['frequencia'],
        cenario['valor_extrator']
    )
    
    print(f"📋 {cenario['nome']}")
    print(f"   Valor vencimento: R$ {cenario['valor_vencimento']}")
    print(f"   Frequência: {cenario['frequencia']} dias")
    if cenario['valor_extrator'] is not None:
        print(f"   Valor recebido: R$ {cenario['valor_extrator']}")
    else:
        print(f"   Valor recebido: (não informado)")
    print(f"   Valor calculado: R$ {valor_calculado}")
    print(f"   Valor esperado: R$ {cenario['esperado_manual']}")
    
    # Validar
    diferenca = abs(valor_calculado - cenario['esperado_manual'])
    if diferenca <= 0.01:
        print(f"   Status: ✓ CORRETO (diferença: R$ {diferenca:.6f})")
    else:
        print(f"   Status: ✗ INCORRETO (diferença: R$ {diferenca:.6f})")
    
    print()

print("=" * 70)
print("LÓGICA IMPLEMENTADA:")
print("=" * 70)
print("""
1. Se frequência = 0 E valor_extrator > 0:
   → Assume frequência = 30 (mês completo)
   → Calcula como se a pessoa trabalhou o mês inteiro

2. Se frequência = 0 E valor_extrator = None/0:
   → Assume frequência = 30 (padrão por segurança)

3. Se frequência > 0:
   → Usa o valor informado normalmente

Fórmula: ((valor_vencimento / 30) * frequencia) * 0.25
""")
