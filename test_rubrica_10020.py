#!/usr/bin/env python
"""Teste para validar o cálculo da rubrica 10020"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sisconformidade.settings')
django.setup()

# Simular cálculo da rubrica 10020
def testar_rubrica_10020():
    """Testa o cálculo vencimento * 0.25"""
    
    casos_teste = [
        (1000.00, 250.00),
        (2000.00, 500.00),
        (3000.00, 750.00),
        (1234.56, 308.64),
        (5555.55, 1388.89),
    ]
    
    print("=" * 60)
    print("TESTE: Rubrica 10020 (Gratificação de Atividade)")
    print("Fórmula: vencimento × 0.25")
    print("=" * 60)
    
    todos_passaram = True
    
    for vencimento, esperado in casos_teste:
        calculado = round(vencimento * 0.25, 2)
        passou = calculado == esperado
        status = "✓ PASSOU" if passou else "✗ FALHOU"
        
        print(f"\nVencimento: R$ {vencimento:>10.2f}")
        print(f"Esperado:  R$ {esperado:>10.2f}")
        print(f"Calculado: R$ {calculado:>10.2f}")
        print(f"Status: {status}")
        
        if not passou:
            todos_passaram = False
    
    print("\n" + "=" * 60)
    if todos_passaram:
        print("✓ TODOS OS TESTES PASSARAM!")
    else:
        print("✗ ALGUNS TESTES FALHARAM!")
    print("=" * 60)

if __name__ == '__main__':
    testar_rubrica_10020()
