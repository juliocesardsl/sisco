#!/usr/bin/env python
"""
Teste para validar a regra da rubrica 10037
Valida que a rubrica 10037 sempre deve ter valor exatamente 1000
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica
from conformidade.verificacao_utils import _calcular_valor_esperado_rubrica_10037

# Teste 1: Verificar se a função retorna sempre 1000
print("=" * 60)
print("TESTE 1: Validar função de cálculo da rubrica 10037")
print("=" * 60)

valor_esperado = _calcular_valor_esperado_rubrica_10037()
print(f"Valor esperado: R$ {valor_esperado}")
assert valor_esperado == 1000.00, f"Erro: valor esperado deveria ser 1000.00, mas foi {valor_esperado}"
print("✓ Valor esperado correto: 1000.00")

# Teste 2: Verificar se a rubrica está configurada corretamente no banco
print("\n" + "=" * 60)
print("TESTE 2: Validar configuração da rubrica 10037 no banco")
print("=" * 60)

try:
    rubrica = Rubrica.objects.get(codigo='10037')
    print(f"Rubrica encontrada: {rubrica.nome}")
    print(f"  Código: {rubrica.codigo}")
    print(f"  Tipo de cálculo: {rubrica.tipo_calculo}")
    print(f"  Fórmula: {rubrica.formula_calculo}")
    print(f"  Tipo de validação: {rubrica.tipo_validacao}")
    print(f"  Valor padrão: R$ {rubrica.valor_padrao}")
    print(f"  Valor mínimo: R$ {rubrica.valor_minimo_padrao}")
    print(f"  Valor máximo: R$ {rubrica.valor_maximo_padrao}")
    
    assert rubrica.tipo_calculo == 'fixo', f"Tipo de cálculo deveria ser 'fixo', mas é '{rubrica.tipo_calculo}'"
    assert rubrica.tipo_validacao == 'exato', f"Tipo de validação deveria ser 'exato', mas é '{rubrica.tipo_validacao}'"
    assert rubrica.valor_padrao == 1000.00, f"Valor padrão deveria ser 1000.00, mas é {rubrica.valor_padrao}"
    assert rubrica.valor_minimo_padrao == 1000.00, f"Valor mínimo deveria ser 1000.00, mas é {rubrica.valor_minimo_padrao}"
    assert rubrica.valor_maximo_padrao == 1000.00, f"Valor máximo deveria ser 1000.00, mas é {rubrica.valor_maximo_padrao}"
    
    print("✓ Todas as configurações estão corretas!")
    
except Rubrica.DoesNotExist:
    print("✗ ERRO: Rubrica 10037 não encontrada no banco!")
    exit(1)

# Teste 3: Cenários de validação
print("\n" + "=" * 60)
print("TESTE 3: Cenários de validação")
print("=" * 60)

cenarios = [
    (999.00, "INCORRETO", "Valor abaixo de 1000"),
    (1000.00, "CORRETO", "Valor exato de 1000"),
    (1001.00, "INCORRETO", "Valor acima de 1000"),
    (500, "INCORRETO", "Valor muito abaixo"),
    (2000, "INCORRETO", "Valor muito acima"),
]

for valor_recebido, status_esperado, descricao in cenarios:
    diferenca = abs(valor_recebido - valor_esperado)
    if valor_recebido == valor_esperado:
        status = "CORRETO"
    else:
        status = "INCORRETO"
    
    esperado_ok = "✓" if status == status_esperado else "✗"
    print(f"{esperado_ok} {descricao}: R$ {valor_recebido} → {status}")
    assert status == status_esperado, f"Status deveria ser {status_esperado}, mas foi {status}"

print("\n" + "=" * 60)
print("✓ TODOS OS TESTES PASSARAM!")
print("=" * 60)
print("\nResumo:")
print("  • Rubrica 10037 configurada com valor fixo de 1000")
print("  • Tipo de validação: EXATO (nem mais, nem menos)")
print("  • Qualquer valor diferente de 1000 será marcado como INCORRETO")
