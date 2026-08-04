from django.db.models import Count, Q
from .models import Rubrica, Empresa, PadraoConformidade, VerificacaoConformidade


def gerar_resposta_agente(pergunta: str) -> str:
    """Gera uma resposta simples e útil com base nos dados do sistema."""
    pergunta = (pergunta or '').strip().lower()

    total_rubricas = Rubrica.objects.count()
    total_empresas = Empresa.objects.count()
    total_padroes = PadraoConformidade.objects.count()
    total_verificacoes = VerificacaoConformidade.objects.count()

    verificacoes_corretas = VerificacaoConformidade.objects.filter(status='correto').count()
    verificacoes_verificar = VerificacaoConformidade.objects.filter(status='verificar').count()
    verificacoes_incorretas = VerificacaoConformidade.objects.filter(status='incorreto').count()

    if 'resumo' in pergunta or 'geral' in pergunta or 'sistema' in pergunta:
        return (
            f"Resumo geral do sistema:\n"
            f"- Rubricas: {total_rubricas}\n"
            f"- Empresas: {total_empresas}\n"
            f"- Padrões: {total_padroes}\n"
            f"- Verificações: {total_verificacoes}\n"
            f"- Corretas: {verificacoes_corretas}\n"
            f"- Verificar: {verificacoes_verificar}\n"
            f"- Incorretas: {verificacoes_incorretas}\n\n"
            "Posso também ajudar a encontrar rubricas, empresas ou padrões específicos."
        )

    if 'rubrica' in pergunta:
        rubricas = Rubrica.objects.order_by('codigo')[:5]
        linhas = [f"- {r.codigo}: {r.nome}" for r in rubricas]
        return "Rubricas cadastradas:\n" + "\n".join(linhas)

    if 'empresa' in pergunta:
        empresas = Empresa.objects.order_by('nome')[:5]
        linhas = [f"- {e.codigo}: {e.nome}" for e in empresas]
        return "Empresas cadastradas:\n" + "\n".join(linhas)

    if 'padr' in pergunta or 'conformidade' in pergunta:
        padroes = PadraoConformidade.objects.select_related('rubrica', 'empresa').order_by('-ano')[:5]
        linhas = [f"- {p.ano}: {p.rubrica.codigo} / {p.empresa.nome}" for p in padroes]
        return "Padrões de conformidade recentes:\n" + "\n".join(linhas)

    if 'verific' in pergunta:
        return (
            f"Status das verificações:\n"
            f"- Corretas: {verificacoes_corretas}\n"
            f"- Verificar: {verificacoes_verificar}\n"
            f"- Incorretas: {verificacoes_incorretas}"
        )

    return (
        f"Posso ajudar com resumo do sistema, rubricas, empresas, padrões e verificações.\n"
        f"Exemplos: 'resumo geral do sistema', 'listar rubricas', 'mostrar empresas'."
    )
