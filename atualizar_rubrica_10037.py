#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica

# Atualizar ou criar rubrica 10037
rubrica, criada = Rubrica.objects.get_or_create(codigo='10037')

# Preencher/atualizar os campos
rubrica.nome = 'Auxílio Fixo'
rubrica.tipo_calculo = 'fixo'
rubrica.formula_calculo = '1000'
rubrica.base_calculo = 'valor_fixo'
rubrica.base_legal = 'Legislação de auxílios'
rubrica.descricao = 'Valor fixo de 1000 - sem variação por frequência ou outros fatores'
rubrica.ativa = True
rubrica.valor_padrao = 1000.00
rubrica.valor_minimo_padrao = 1000.00
rubrica.valor_maximo_padrao = 1000.00
rubrica.tipo_validacao = 'exato'
rubrica.save()

status = 'Criada' if criada else 'Atualizada'
print(f"✓ Rubrica 10037 {status.lower()} com sucesso!")
print(f"  Código: {rubrica.codigo}")
print(f"  Nome: {rubrica.nome}")
print(f"  Fórmula: {rubrica.formula_calculo}")
print(f"  Tipo: {rubrica.tipo_calculo}")
print(f"  Valor esperado: R$ {rubrica.valor_padrao}")
print(f"  Tipo de validação: {rubrica.tipo_validacao}")
print(f"  Descrição: {rubrica.descricao}")
