#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica

# Atualizar ou criar rubrica 10265
rubrica, criada = Rubrica.objects.get_or_create(codigo='10265')

# Preencher/atualizar os campos
rubrica.nome = 'Percentual sobre Vencimento - 15%'
rubrica.tipo_calculo = 'percentual'
rubrica.formula_calculo = 'vencimento * 0.15'
rubrica.base_calculo = 'valor_vencimento'
rubrica.base_legal = 'Legislação de complementos'
rubrica.descricao = 'Valor calculado como 15% do vencimento base'
rubrica.ativa = True
rubrica.save()

status = 'Criada' if criada else 'Atualizada'
print(f"✓ Rubrica 10265 {status.lower()} com sucesso!")
print(f"  Código: {rubrica.codigo}")
print(f"  Nome: {rubrica.nome}")
print(f"  Fórmula: {rubrica.formula_calculo}")
print(f"  Tipo: {rubrica.tipo_calculo}")
print(f"  Descrição: {rubrica.descricao}")