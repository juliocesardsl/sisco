#!/usr/bin/env python
"""Script para criar dados de exemplo no banco de dados"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

from conformidade.models import Rubrica, Empresa, PadraoConformidade

# Limpar dados antigos
Rubrica.objects.all().delete()
Empresa.objects.all().delete()
PadraoConformidade.objects.all().delete()

# Criar Rubricas
r1 = Rubrica.objects.create(
    nome='Folha de Pagamento',
    codigo='FOLHA',
    descricao='Despesas com folha de pagamento',
    valor_padrao=100000.00,
    ativa=True
)

r2 = Rubrica.objects.create(
    nome='Encargos Sociais',
    codigo='ENCARGOS',
    descricao='Encargos sociais e contribuições',
    valor_padrao=50000.00,
    ativa=True
)

r3 = Rubrica.objects.create(
    nome='Benefícios',
    codigo='BENEFICIOS',
    descricao='Benefícios aos funcionários',
    valor_padrao=30000.00,
    ativa=True
)

print('✓ 3 Rubricas criadas')

# Criar Empresas
e1 = Empresa.objects.create(
    nome='Empresa Teste A',
    cnpj='00.000.000/0001-00',
    razao_social='Empresa Teste A LTDA',
    email='contato@empresaa.com',
    telefone='(61) 9999-9999'
)

e2 = Empresa.objects.create(
    nome='Empresa Teste B',
    cnpj='11.111.111/0001-11',
    razao_social='Empresa Teste B LTDA',
    email='contato@empresab.com',
    telefone='(61) 8888-8888'
)

print('✓ 2 Empresas criadas')

# Criar Padrões de Conformidade
p1 = PadraoConformidade.objects.create(
    rubrica=r1,
    empresa=e1,
    ano=2026,
    valor_minimo=80000.00,
    valor_maximo=120000.00,
    carga_horaria=40
)

p2 = PadraoConformidade.objects.create(
    rubrica=r2,
    empresa=e1,
    ano=2026,
    valor_minimo=40000.00,
    valor_maximo=60000.00,
    carga_horaria=0
)

p3 = PadraoConformidade.objects.create(
    rubrica=r3,
    empresa=e1,
    ano=2026,
    valor_minimo=20000.00,
    valor_maximo=40000.00,
    carga_horaria=0
)

p4 = PadraoConformidade.objects.create(
    rubrica=r1,
    empresa=e2,
    ano=2026,
    valor_minimo=50000.00,
    valor_maximo=90000.00,
    carga_horaria=40
)

p5 = PadraoConformidade.objects.create(
    rubrica=r2,
    empresa=e2,
    ano=2026,
    valor_minimo=25000.00,
    valor_maximo=45000.00,
    carga_horaria=0
)

print('✓ 5 Padrões de Conformidade criados')
print('\n✅ Banco de dados pronto para uso!')
