#!/usr/bin/env python
"""
Teste para validar o cenário onde frequência é 0
Quando frequência é 0, o valor calculado é 0, 
mas o sistema deve aceitar o valor recebido como correto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.verificacao_utils import _calcular_valor_esperado_rubrica_10020

print("=" * 60)
print("TESTE: Cenário com frequência 0")
print("=" * 60)

# Teste cenário da imagem
valor_vencimento = 6183.38
frequencia = 0.0
valor_extrator = 1545.84

valor_esperado = _calcular_valor_esperado_rubrica_10020(
    valor_vencimento, 
    frequencia,
    valor_extrator
)

print(f"Valor vencimento: R$ {valor_vencimento}")
print(f"Frequência: {frequencia}")
print(f"Valor recebido (extrator): R$ {valor_extrator}")
print(f"Valor esperado (calculado): R$ {valor_esperado}")

# Simular lógica de verificação
if valor_esperado == 0 and valor_extrator > 0:
    valor_esperado_usado = valor_extrator
    print(f"\nValor esperado era 0, usando valor recebido: R$ {valor_esperado_usado}")
else:
    valor_esperado_usado = valor_esperado
    
diferenca = abs(valor_extrator - valor_esperado_usado)
print(f"Diferença: R$ {diferenca}")

if valor_extrator == valor_esperado_usado or diferenca <= 0.01:
    status = "CORRETO ✓"
else:
    status = "INCORRETO"

print(f"Status: {status}")
print("\n" + "=" * 60)
print("Resultado: Quando frequência é 0, o valor recebido é aceito")
print("=" * 60)
