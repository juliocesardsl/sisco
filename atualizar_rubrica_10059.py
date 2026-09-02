#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica

# Atualizar ou criar rubrica 10059
rubrica, criada = Rubrica.objects.get_or_create(codigo='10059')

# Preencher/atualizar os campos - mesmo padrão da 10020
rubrica.nome = 'Gratificação de Atividade - Ativo (10059)'
rubrica.tipo_calculo = 'percentual'
rubrica.formula_calculo = 'vencimento * 0.25 * frequencia / 30'
rubrica.base_calculo = 'valor_vencimento'
rubrica.base_legal = 'Decreto regulamentador de gratificações'
rubrica.descricao = 'Gratificação de atividade calculada como 25% do valor do vencimento proporcional à frequência (mesma regra da 10020)'
rubrica.ativa = True
rubrica.save()

status = 'Criada' if criada else 'Atualizada'
print(f"✓ Rubrica 10059 {status.lower()} com sucesso!")
print(f"  Código: {rubrica.codigo}")
print(f"  Nome: {rubrica.nome}")
print(f"  Fórmula: {rubrica.formula_calculo}")
print(f"  Tipo: {rubrica.tipo_calculo}")
print(f"  Descrição: {rubrica.descricao}")
print(f"  Nota: mesma regra da rubrica 10020")
