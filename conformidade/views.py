from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse, reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.utils.text import slugify
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
import json
import csv
import tempfile
import os
from .models import Rubrica, Empresa, PadraoConformidade, VerificacaoConformidade
from .forms import RubricaForm, EmpresaForm, PadraoConformidadeForm, PadraoComparacaoForm, VerificacaoConformidadeForm
from .exporters import exportar_verificacoes_csv, exportar_comparacao_excel
from .relatorio_gerador import gerar_relatorio_carga_horaria
from .verificacao_utils import processar_verificacao, comparar_extrator_por_mes
from .agent import gerar_resposta_agente


def agente_assistente_view(request):
    resposta = ''
    if request.method == 'POST':
        pergunta = request.POST.get('pergunta', '').strip()
        if pergunta:
            resposta = gerar_resposta_agente(pergunta)
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'resposta': resposta})
    return render(request, 'conformidade/agente.html', {'resposta': resposta})


# ===== RUBRICAS =====

class RubricaListView(LoginRequiredMixin, ListView):
    model = Rubrica
    template_name = 'conformidade/rubrica_list.html'
    context_object_name = 'rubricas'
    paginate_by = 20


class RubricaDetailView(LoginRequiredMixin, DetailView):
    model = Rubrica
    template_name = 'conformidade/rubrica_detail.html'
    context_object_name = 'rubrica'


class RubricaCreateView(LoginRequiredMixin, CreateView):
    model = Rubrica
    form_class = RubricaForm
    template_name = 'conformidade/rubrica_form.html'
    success_url = reverse_lazy('rubrica_list')

    def form_valid(self, form):
        messages.success(self.request, 'Rubrica criada com sucesso!')
        return super().form_valid(form)


class RubricaUpdateView(LoginRequiredMixin, UpdateView):
    model = Rubrica
    form_class = RubricaForm
    template_name = 'conformidade/rubrica_form.html'
    success_url = reverse_lazy('rubrica_list')

    def form_valid(self, form):
        messages.success(self.request, 'Rubrica atualizada com sucesso!')
        return super().form_valid(form)


class RubricaDeleteView(LoginRequiredMixin, DeleteView):
    model = Rubrica
    template_name = 'conformidade/rubrica_confirm_delete.html'
    success_url = reverse_lazy('rubrica_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Rubrica deletada com sucesso!')
        return super().delete(request, *args, **kwargs)


# ===== EMPRESAS =====

class EmpresaListView(LoginRequiredMixin, ListView):
    model = Empresa
    template_name = 'conformidade/empresa_list.html'
    context_object_name = 'empresas'
    paginate_by = 20


class EmpresaDetailView(LoginRequiredMixin, DetailView):
    model = Empresa
    template_name = 'conformidade/empresa_detail.html'
    context_object_name = 'empresa'


class EmpresaCreateView(LoginRequiredMixin, CreateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'conformidade/empresa_form.html'
    success_url = reverse_lazy('empresa_list')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa criada com sucesso!')
        return super().form_valid(form)


class EmpresaUpdateView(LoginRequiredMixin, UpdateView):
    model = Empresa
    form_class = EmpresaForm
    template_name = 'conformidade/empresa_form.html'
    success_url = reverse_lazy('empresa_list')

    def form_valid(self, form):
        messages.success(self.request, 'Empresa atualizada com sucesso!')
        return super().form_valid(form)


class EmpresaDeleteView(LoginRequiredMixin, DeleteView):
    model = Empresa
    template_name = 'conformidade/empresa_confirm_delete.html'
    success_url = reverse_lazy('empresa_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Empresa deletada com sucesso!')
        return super().delete(request, *args, **kwargs)


# ===== PADRÕES DE CONFORMIDADE =====

class PadraoConformidadeListView(LoginRequiredMixin, FormView):
    template_name = 'conformidade/padrao_list.html'
    form_class = PadraoComparacaoForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Se há dados na sessão, usar para paginação (navegação entre páginas)
        if 'comparacao_data' in self.request.session:
            comparacao_data = self.request.session.get('comparacao_data', [])
            rubrica_codigo = self.request.session.get('rubrica_codigo', '')
            rubrica_nome = self.request.session.get('rubrica_nome', '')
            descricao_rubrica = self.request.session.get('descricao_rubrica', '')
            status_filter = self.request.GET.get('status', 'todos')
            matricula_filter = self.request.GET.get('matricula', '').strip()

            # Aplicar filtro por matrícula
            if matricula_filter:
                comparacao_data = [
                    item for item in comparacao_data
                    if matricula_filter.lower() in str(item.get('matricula', '')).lower()
                ]

            if status_filter != 'todos':
                comparacao_data = [
                    item for item in comparacao_data
                    if item.get('status') and slugify(item.get('status')) == status_filter
                ]

            # Aplicar paginação
            page = self.request.GET.get('page', 1)
            paginator = Paginator(comparacao_data, 50)  # 50 itens por página
            try:
                comparacao_paginada = paginator.page(page)
            except PageNotAnInteger:
                comparacao_paginada = paginator.page(1)
            except EmptyPage:
                comparacao_paginada = paginator.page(paginator.num_pages)

            start_index = comparacao_paginada.start_index() - 1
            for i, item in enumerate(comparacao_paginada.object_list):
                item['global_index'] = start_index + i
            
            # Criar um objeto Rubrica com os dados da sessão
            from .models import Rubrica
            try:
                rubrica = Rubrica.objects.get(codigo=rubrica_codigo)
            except:
                class RubricaTemp:
                    codigo = rubrica_codigo
                    nome = rubrica_nome
                rubrica = RubricaTemp()
            
            context.update({
                'comparacao': comparacao_paginada,
                'rubrica': rubrica,
                'descricao_rubrica': descricao_rubrica,
                'status_filter': status_filter,
                'matricula_filter': matricula_filter,
                'comparacao_total': len(comparacao_data),
            })
        
        return context

    def form_valid(self, form):
        rubrica_input = form.cleaned_data.get('rubrica', '').strip()
        descricao_rubrica = form.cleaned_data.get('descricao_rubrica', '').strip()
        anterior = form.cleaned_data['arquivo_extrator_mes_anterior']
        atual = form.cleaned_data['arquivo_extrator_mes_atual']

        # Verificar se os arquivos foram enviados
        if not anterior:
            messages.error(self.request, "Arquivo do mês anterior não foi enviado.")
            return self.form_invalid(form)
        if not atual:
            messages.error(self.request, "Arquivo do mês atual não foi enviado.")
            return self.form_invalid(form)

        # Permite comparar uma rubrica específica ou todas as rubricas detectadas no arquivo.
        resultado = comparar_extrator_por_mes(anterior, atual, rubrica_input or None)
        if resultado.get('erro'):
            messages.error(self.request, resultado['erro'])
            return self.form_invalid(form)

        comparacao = resultado['comparacao']

        if descricao_rubrica:
            for item in comparacao:
                item['dc_rubrica'] = descricao_rubrica
        
        # Armazenar na sessão para manter entre requisições
        self.request.session['comparacao_data'] = comparacao
        self.request.session['descricao_rubrica'] = descricao_rubrica
        if rubrica_input:
            self.request.session['rubrica_codigo'] = rubrica_input
            self.request.session['rubrica_nome'] = f'Rubrica informada: {rubrica_input}'
        else:
            self.request.session['rubrica_codigo'] = 'TODAS'
            self.request.session['rubrica_nome'] = 'Todas as rubricas detectadas nos arquivos'
        
        # Aplicar paginação
        page = self.request.GET.get('page', 1)
        paginator = Paginator(comparacao, 50)  # 50 itens por página
        try:
            comparacao_paginada = paginator.page(page)
        except PageNotAnInteger:
            comparacao_paginada = paginator.page(1)
        except EmptyPage:
            comparacao_paginada = paginator.page(paginator.num_pages)

        context = self.get_context_data(
            form=form,
            comparacao=comparacao_paginada,
            rubrica={'codigo': rubrica_input or 'TODAS', 'nome': 'Todas as rubricas detectadas nos arquivos' if not rubrica_input else f'Rubrica informada: {rubrica_input}'},
            descricao_rubrica=descricao_rubrica,
            periodo_anterior=resultado.get('periodo_anterior'),
            periodo_atual=resultado.get('periodo_atual'),
        )
        return self.render_to_response(context)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class PadraoConformidadeCreateView(LoginRequiredMixin, CreateView):
    model = PadraoConformidade
    form_class = PadraoConformidadeForm
    template_name = 'conformidade/padrao_form.html'
    success_url = reverse_lazy('padrao_list')

    def form_valid(self, form):
        messages.success(self.request, 'Padrão de conformidade criado com sucesso!')
        return super().form_valid(form)


class PadraoConformidadeUpdateView(LoginRequiredMixin, UpdateView):
    model = PadraoConformidade
    form_class = PadraoConformidadeForm
    template_name = 'conformidade/padrao_form.html'
    success_url = reverse_lazy('padrao_list')

    def form_valid(self, form):
        messages.success(self.request, 'Padrão de conformidade atualizado com sucesso!')
        return super().form_valid(form)


class PadraoConformidadeDeleteView(LoginRequiredMixin, DeleteView):
    model = PadraoConformidade
    template_name = 'conformidade/padrao_confirm_delete.html'
    success_url = reverse_lazy('padrao_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Padrão de conformidade deletado com sucesso!')
        return super().delete(request, *args, **kwargs)


# ===== VERIFICAÇÕES =====

class VerificacaoListView(LoginRequiredMixin, ListView):
    model = VerificacaoConformidade
    template_name = 'conformidade/verificacao_list.html'
    context_object_name = 'verificacoes'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Calcula contagem de status
        context['total_verificacoes'] = VerificacaoConformidade.objects.count()
        context['corretos'] = VerificacaoConformidade.objects.filter(status='correto').count()
        context['verificar'] = VerificacaoConformidade.objects.filter(status='verificar').count()
        context['incorretos'] = VerificacaoConformidade.objects.filter(status='incorreto').count()
        return context


@login_required
def verificacao_create(request):
    """View para criar e processar verificação de conformidade"""
    if request.method == 'POST':
        form = VerificacaoConformidadeForm(request.POST, request.FILES)
        
        if form.is_valid():
            # Extrai dados do formulário
            rubrica = form.cleaned_data.get('rubrica', '')
            ano_referencia = form.cleaned_data.get('ano_referencia')
            mes_referencia_input = form.cleaned_data.get('mes_referencia')
            carga_horaria = form.cleaned_data.get('carga_horaria')
            arquivo_vencimento = request.FILES.get('arquivo_vencimento')
            arquivo_extrator = request.FILES.get('arquivo_extrator')
            
            # Valida se há arquivos
            if not arquivo_extrator:
                messages.error(request, 'Por favor, selecione o arquivo Extrator.')
                return render(request, 'conformidade/verificacao_form.html', {'form': form})

            rubrica_str = str(rubrica).strip()
            if rubrica_str not in ('10926', '10014', '11187') and not arquivo_vencimento:
                messages.error(request, 'Por favor, selecione o arquivo Vencimento.')
                return render(request, 'conformidade/verificacao_form.html', {'form': form})

            # Processa verificação
            resultado = processar_verificacao(
                arquivo_vencimento,
                arquivo_extrator,
                rubrica,
                ano_referencia,
                carga_horaria,
                rubrica_obj=None,
            )
            
            if 'erro' in resultado:
                messages.error(request, f'Erro na verificação: {resultado["erro"]}')
                return render(request, 'conformidade/verificacao_form.html', {'form': form})

            # Use mês do arquivo quando disponível
            mes_referencia = resultado.get('mes_referencia') or mes_referencia_input

            # Salva histórico de verificação
            status_geral = 'correto'
            if resultado.get('incorretos', 0) > 0:
                status_geral = 'incorreto'
            elif resultado.get('verificar', 0) > 0:
                status_geral = 'verificar'

            valor_pago_total = sum([item.get('valor_total_recebido') or 0 for item in resultado.get('resultados', [])])

            padrao = PadraoConformidade.objects.filter(
                ano=ano_referencia,
                carga_horaria=carga_horaria
            ).filter(
                Q(rubrica__nome__iexact=rubrica) | Q(rubrica__codigo__iexact=rubrica)
            ).first()

            verificacao = VerificacaoConformidade.objects.create(
                padrao=padrao,
                rubrica=rubrica,
                ano_referencia=ano_referencia,
                carga_horaria=carga_horaria,
                valor_pago=valor_pago_total,
                status=status_geral,
                arquivo_vencimento=arquivo_vencimento,
                arquivo_extrator=arquivo_extrator,
                verificado_por=request.user.get_full_name() or request.user.username,
                # Salva resumo dos resultados
                total_registros=resultado.get('total', 0),
                corretos=resultado.get('corretos', 0),
                verificar=resultado.get('verificar', 0),
                incorretos=resultado.get('incorretos', 0),
                resultados_json=resultado,
            )

            # Armazena resultado em session para exibir na página de resultados
            request.session['verificacao_resultados'] = resultado
            request.session['verificacao_rubrica'] = rubrica
            request.session['verificacao_ano'] = ano_referencia
            request.session['verificacao_mes'] = mes_referencia
            request.session['verificacao_carga'] = carga_horaria
            request.session['verificacao_id'] = verificacao.id

            return redirect('verificacao_resultados')
        else:
            # Renderiza o formulário com erros
            return render(request, 'conformidade/verificacao_form.html', {'form': form})
    else:
        form = VerificacaoConformidadeForm()
        return render(request, 'conformidade/verificacao_form.html', {'form': form})


def exportar_verificacoes(request):
    """Exporta as verificações em CSV"""
    status = request.GET.get('status', 'todos')
    queryset = VerificacaoConformidade.objects.all()

    if status != 'todos':
        queryset = queryset.filter(status=status)

    response = exportar_verificacoes_csv(queryset, status)
    return response


def verificacao_resultados(request):
    """Exibe os resultados da verificação"""
    resultado = request.session.get('verificacao_resultados', {})
    
    if not resultado:
        messages.warning(request, 'Nenhuma verificação disponível.')
        return redirect('verificacao_create')
    
    rubrica = request.session.get('verificacao_rubrica', '')
    ano = request.session.get('verificacao_ano', '')
    carga = request.session.get('verificacao_carga', '')
    
    # Obtém filtro de status da query string
    status_filter = request.GET.get('status', 'todos')
    empresa_filter = request.GET.get('empresa', '').strip()
    cpf_filter = request.GET.get('cpf', '').strip()
    matricula_filter = request.GET.get('matricula', '').strip()
    nome_filter = request.GET.get('nome', '').strip()
    ref_vertical_filter = request.GET.get('ref_vertical', '').strip()
    ref_horizontal_filter = request.GET.get('ref_horizontal', '').strip()
    valor_esperado_filter = request.GET.get('valor_esperado', '').strip()
    frequencia_filter = request.GET.get('frequencia', '').strip()
    valor_recebido_filter = request.GET.get('valor_recebido', '').strip()
    diferenca_filter = request.GET.get('diferenca', '').strip()
    
    # Filtra resultados
    resultados = resultado.get('resultados', [])
    if status_filter != 'todos':
        if status_filter == 'correto':
            # Filtra APENAS linhas que começam com 'CORRETO'
            resultados = [r for r in resultados if r['status'].upper().startswith('CORRETO')]
        elif status_filter == 'verificar':
            # Filtra linhas que começam com 'VERIFICAR'
            resultados = [r for r in resultados if r['status'].upper().startswith('VERIFICAR')]
        elif status_filter == 'incorreto':
            # Filtra linhas que começam com 'INCORRETO'
            resultados = [r for r in resultados if r['status'].upper().startswith('INCORRETO')]
    
    # Filtros adicionais
    if empresa_filter:
        resultados = [r for r in resultados if empresa_filter.lower() in str(r.get('empresa', '')).lower()]
    
    if cpf_filter:
        resultados = [r for r in resultados if cpf_filter.lower() in str(r.get('cpf', '')).lower()]
    
    if matricula_filter:
        resultados = [r for r in resultados if matricula_filter.lower() in str(r.get('matricula', '')).lower()]
    
    if nome_filter:
        resultados = [r for r in resultados if nome_filter.lower() in r.get('nome_servidor', '').lower()]
    
    if ref_vertical_filter:
        resultados = [r for r in resultados if ref_vertical_filter.lower() in str(r.get('ref_vertical', '')).lower()]
    
    if ref_horizontal_filter:
        resultados = [r for r in resultados if ref_horizontal_filter.lower() in str(r.get('ref_horizontal', '')).lower()]
    
    if valor_esperado_filter:
        try:
            valor_esperado_num = float(valor_esperado_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_calculado') == valor_esperado_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if frequencia_filter:
        try:
            frequencia_num = float(frequencia_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('frequencia') == frequencia_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if valor_recebido_filter:
        try:
            valor_recebido_num = float(valor_recebido_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_total_recebido') == valor_recebido_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if diferenca_filter:
        try:
            diferenca_num = float(diferenca_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('diferenca_absoluta') == diferenca_num]
        except ValueError:
            pass  # Ignora filtro inválido

    # Paginação para não renderizar tudo de uma vez
    page_number = request.GET.get('page', 1)
    paginator = Paginator(resultados, 50)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Adiciona o índice global a cada resultado da página
    start_index = (page_obj.number - 1) * paginator.per_page
    for i, res in enumerate(page_obj.object_list):
        res['global_index'] = start_index + i

    context = {
        'resultados': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'rubrica': rubrica,
        'ano': ano,
        'carga': carga,
        'total': resultado.get('total', 0),
        'corretos': resultado.get('corretos', 0),
        'verificar': resultado.get('verificar', 0),
        'incorretos': resultado.get('incorretos', 0),
        'status_filter': status_filter,
        'empresa_filter': empresa_filter,
        'cpf_filter': cpf_filter,
        'matricula_filter': matricula_filter,
        'nome_filter': nome_filter,
        'ref_vertical_filter': ref_vertical_filter,
        'ref_horizontal_filter': ref_horizontal_filter,
        'valor_esperado_filter': valor_esperado_filter,
        'frequencia_filter': frequencia_filter,
        'valor_recebido_filter': valor_recebido_filter,
        'diferenca_filter': diferenca_filter,
    }
    
    return render(request, 'conformidade/verificacao_resultados.html', context)


@login_required
def verificacao_resultados_detail(request, pk):
    """Exibe os resultados de uma verificação específica pelo ID"""
    verificacao = get_object_or_404(VerificacaoConformidade, pk=pk)
    resultado = verificacao.resultados_json or {}
    
    if not resultado:
        messages.warning(request, 'Nenhum resultado disponível para esta verificação.')
        return redirect('verificacao_list')

    request.session['verificacao_resultados'] = resultado
    request.session['verificacao_rubrica'] = verificacao.rubrica
    request.session['verificacao_ano'] = verificacao.ano_referencia
    request.session['verificacao_mes'] = resultado.get('mes_referencia', '')
    request.session['verificacao_carga'] = verificacao.carga_horaria
    request.session['verificacao_id'] = verificacao.id
    
    rubrica = verificacao.rubrica
    ano = verificacao.ano_referencia
    carga = verificacao.carga_horaria
    
    # Obtém filtro de status da query string
    status_filter = request.GET.get('status', 'todos')
    empresa_filter = request.GET.get('empresa', '').strip()
    cpf_filter = request.GET.get('cpf', '').strip()
    matricula_filter = request.GET.get('matricula', '').strip()
    nome_filter = request.GET.get('nome', '').strip()
    ref_vertical_filter = request.GET.get('ref_vertical', '').strip()
    ref_horizontal_filter = request.GET.get('ref_horizontal', '').strip()
    valor_esperado_filter = request.GET.get('valor_esperado', '').strip()
    frequencia_filter = request.GET.get('frequencia', '').strip()
    valor_recebido_filter = request.GET.get('valor_recebido', '').strip()
    diferenca_filter = request.GET.get('diferenca', '').strip()
    
    # Filtra resultados
    resultados = resultado.get('resultados', [])
    if status_filter != 'todos':
        if status_filter == 'correto':
            resultados = [r for r in resultados if r['status'].upper().startswith('CORRETO')]
        elif status_filter == 'verificar':
            resultados = [r for r in resultados if r['status'].upper().startswith('VERIFICAR')]
        elif status_filter == 'incorreto':
            resultados = [r for r in resultados if r['status'].upper().startswith('INCORRETO')]
    
    # Filtros adicionais
    if empresa_filter:
        resultados = [r for r in resultados if empresa_filter.lower() in str(r.get('empresa', '')).lower()]
    
    if cpf_filter:
        resultados = [r for r in resultados if cpf_filter.lower() in str(r.get('cpf', '')).lower()]
    
    if matricula_filter:
        resultados = [r for r in resultados if matricula_filter.lower() in str(r.get('matricula', '')).lower()]
    
    if nome_filter:
        resultados = [r for r in resultados if nome_filter.lower() in r.get('nome_servidor', '').lower()]
    
    if ref_vertical_filter:
        resultados = [r for r in resultados if ref_vertical_filter.lower() in str(r.get('ref_vertical', '')).lower()]
    
    if ref_horizontal_filter:
        resultados = [r for r in resultados if ref_horizontal_filter.lower() in str(r.get('ref_horizontal', '')).lower()]
    
    if valor_esperado_filter:
        try:
            valor_esperado_num = float(valor_esperado_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_calculado') == valor_esperado_num]
        except ValueError:
            pass
    
    if frequencia_filter:
        try:
            frequencia_num = float(frequencia_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('frequencia') == frequencia_num]
        except ValueError:
            pass
    
    if valor_recebido_filter:
        try:
            valor_recebido_num = float(valor_recebido_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_total_recebido') == valor_recebido_num]
        except ValueError:
            pass
    
    if diferenca_filter:
        try:
            diferenca_num = float(diferenca_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('diferenca_absoluta') == diferenca_num]
        except ValueError:
            pass

    # Paginação
    page_number = request.GET.get('page', 1)
    paginator = Paginator(resultados, 50)
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Adiciona o índice global a cada resultado da página
    start_index = (page_obj.number - 1) * paginator.per_page
    for i, res in enumerate(page_obj.object_list):
        res['global_index'] = start_index + i

    context = {
        'resultados': page_obj.object_list,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'rubrica': rubrica,
        'ano': ano,
        'carga': carga,
        'total': verificacao.total_registros,
        'corretos': verificacao.corretos,
        'verificar': verificacao.verificar,
        'incorretos': verificacao.incorretos,
        'status_filter': status_filter,
        'nome_filter': nome_filter,
        'ref_vertical_filter': ref_vertical_filter,
        'ref_horizontal_filter': ref_horizontal_filter,
        'valor_esperado_filter': valor_esperado_filter,
        'frequencia_filter': frequencia_filter,
        'valor_recebido_filter': valor_recebido_filter,
        'diferenca_filter': diferenca_filter,
    }
    
    return render(request, 'conformidade/verificacao_resultados.html', context)


@login_required
def servidor_detail(request, index):
    """Exibe os detalhes completos de um servidor específico"""
    resultado = request.session.get('verificacao_resultados', {})
    comparacao_data = request.session.get('comparacao_data', [])
    source = request.GET.get('source', '')

    use_comparacao = source == 'comparacao' or (not resultado and comparacao_data)
    if use_comparacao:
        resultados = comparacao_data
        return_url = reverse('padrao_list')
    else:
        resultados = resultado.get('resultados', [])
        return_url = reverse('verificacao_resultados')

    if not resultados:
        messages.warning(request, 'Nenhuma verificação ou comparação disponível.')
        return redirect(return_url)

    # Reaplicar filtros usando os parâmetros atuais
    status_filter = request.GET.get('status', 'todos')
    empresa_filter = request.GET.get('empresa', '').strip()
    cpf_filter = request.GET.get('cpf', '').strip()
    matricula_filter = request.GET.get('matricula', '').strip()
    nome_filter = request.GET.get('nome', '').strip()
    ref_vertical_filter = request.GET.get('ref_vertical', '').strip()
    ref_horizontal_filter = request.GET.get('ref_horizontal', '').strip()
    valor_esperado_filter = request.GET.get('valor_esperado', '').strip()
    frequencia_filter = request.GET.get('frequencia', '').strip()
    valor_recebido_filter = request.GET.get('valor_recebido', '').strip()
    diferenca_filter = request.GET.get('diferenca', '').strip()

    if status_filter != 'todos':
        if use_comparacao:
            resultados = [r for r in resultados if slugify(str(r.get('status', ''))) == status_filter]
        else:
            if status_filter == 'correto':
                resultados = [r for r in resultados if r.get('status', '').upper().startswith('CORRETO')]
            elif status_filter == 'verificar':
                resultados = [r for r in resultados if r.get('status', '').upper().startswith('VERIFICAR')]
            elif status_filter == 'incorreto':
                resultados = [r for r in resultados if r.get('status', '').upper().startswith('INCORRETO')]

    if empresa_filter:
        resultados = [r for r in resultados if empresa_filter.lower() in str(r.get('empresa', '')).lower()]

    if cpf_filter:
        resultados = [r for r in resultados if cpf_filter.lower() in str(r.get('cpf', '')).lower()]

    if matricula_filter:
        resultados = [r for r in resultados if matricula_filter.lower() in str(r.get('matricula', '')).lower()]

    if nome_filter:
        resultados = [r for r in resultados if nome_filter.lower() in str(r.get('nome_servidor', '')).lower()]

    if ref_vertical_filter:
        resultados = [r for r in resultados if ref_vertical_filter.lower() in str(r.get('ref_vertical', '')).lower()]

    if ref_horizontal_filter:
        resultados = [r for r in resultados if ref_horizontal_filter.lower() in str(r.get('ref_horizontal', '')).lower()]

    if valor_esperado_filter:
        try:
            valor_esperado_num = float(valor_esperado_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_calculado') == valor_esperado_num]
        except ValueError:
            pass

    if frequencia_filter:
        try:
            frequencia_num = float(frequencia_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('frequencia') == frequencia_num]
        except ValueError:
            pass

    if valor_recebido_filter:
        try:
            valor_recebido_num = float(valor_recebido_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_total_recebido') == valor_recebido_num]
        except ValueError:
            pass

    if diferenca_filter:
        try:
            diferenca_num = float(diferenca_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('diferenca_absoluta') == diferenca_num]
        except ValueError:
            pass

    try:
        index = int(index)
    except (TypeError, ValueError):
        messages.warning(request, 'Servidor inválido.')
        return redirect(return_url)

    if index < 0 or index >= len(resultados):
        messages.warning(request, 'Servidor não encontrado.')
        return redirect(return_url)

    servidor = resultados[index]

    context = {
        'servidor': servidor,
        'index': index,
        'return_url': return_url,
    }

    return render(request, 'conformidade/servidor_detail.html', context)


def exportar_verificacao_csv(request):
    """Exporta os resultados da verificação atual para CSV"""
    resultado = request.session.get('verificacao_resultados', {})
    resultados = resultado.get('resultados', [])
    status_filter = request.GET.get('status', 'todos')
    empresa_filter = request.GET.get('empresa', '').strip()
    cpf_filter = request.GET.get('cpf', '').strip()
    matricula_filter = request.GET.get('matricula', '').strip()
    nome_filter = request.GET.get('nome', '').strip()
    ref_vertical_filter = request.GET.get('ref_vertical', '').strip()
    ref_horizontal_filter = request.GET.get('ref_horizontal', '').strip()
    valor_esperado_filter = request.GET.get('valor_esperado', '').strip()
    frequencia_filter = request.GET.get('frequencia', '').strip()
    valor_recebido_filter = request.GET.get('valor_recebido', '').strip()
    diferenca_filter = request.GET.get('diferenca', '').strip()
    
    if not resultados:
        messages.warning(request, 'Nenhum resultado para exportar.')
        return redirect('verificacao_resultados')
    
    # Filtra por status se necessário
    if status_filter != 'todos':
        if status_filter == 'correto':
            resultados = [r for r in resultados if r['status'].upper().startswith('CORRETO')]
        elif status_filter == 'verificar':
            resultados = [r for r in resultados if r['status'].upper().startswith('VERIFICAR')]
        elif status_filter == 'incorreto':
            resultados = [r for r in resultados if r['status'].upper().startswith('INCORRETO')]
    
    # Filtros adicionais
    if empresa_filter:
        resultados = [r for r in resultados if empresa_filter.lower() in str(r.get('empresa', '')).lower()]
    
    if cpf_filter:
        resultados = [r for r in resultados if cpf_filter.lower() in str(r.get('cpf', '')).lower()]
    
    if matricula_filter:
        resultados = [r for r in resultados if matricula_filter.lower() in str(r.get('matricula', '')).lower()]
    
    if nome_filter:
        resultados = [r for r in resultados if nome_filter.lower() in r.get('nome_servidor', '').lower()]
    
    if ref_vertical_filter:
        resultados = [r for r in resultados if ref_vertical_filter.lower() in str(r.get('ref_vertical', '')).lower()]
    
    if ref_horizontal_filter:
        resultados = [r for r in resultados if ref_horizontal_filter.lower() in str(r.get('ref_horizontal', '')).lower()]
    
    if valor_esperado_filter:
        try:
            valor_esperado_num = float(valor_esperado_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_calculado') == valor_esperado_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if frequencia_filter:
        try:
            frequencia_num = float(frequencia_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('frequencia') == frequencia_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if valor_recebido_filter:
        try:
            valor_recebido_num = float(valor_recebido_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('valor_total_recebido') == valor_recebido_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if diferenca_filter:
        try:
            diferenca_num = float(diferenca_filter.replace(',', '.'))
            resultados = [r for r in resultados if r.get('diferenca_absoluta') == diferenca_num]
        except ValueError:
            pass  # Ignora filtro inválido
    
    if not resultados:
        messages.warning(request, 'Nenhum resultado para exportar com os filtros selecionados.')
        return redirect('verificacao_resultados')
    
    # Cria resposta CSV com cabeçalho de relatório e metadados
    rubrica_nome = request.session.get('verificacao_rubrica', 'Todas as rubricas') or 'Todas as rubricas'
    ano_relatorio = request.session.get('verificacao_ano', '')
    carga_relatorio = request.session.get('verificacao_carga', '')
    filename_rubrica = ''.join(ch if ch.isalnum() else '_' for ch in rubrica_nome)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = (
        f'attachment; filename="relatorio_verificacao_rubrica_{filename_rubrica}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    )
    response.write('\ufeff')

    def _format_currency(value):
        try:
            return f"R$ {float(value):.2f}"
        except (TypeError, ValueError):
            return ''

    def _format_number(value):
        try:
            return f"{float(value):.2f}"
        except (TypeError, ValueError):
            return ''

    def _format_percent(value):
        try:
            return f"{float(value):.2f}%"
        except (TypeError, ValueError):
            return ''

    writer = csv.writer(response, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\r\n')
    writer.writerow(['RELATÓRIO DE VERIFICAÇÃO POR RÚBRICA'])
    writer.writerow(['Rubrica', rubrica_nome])
    writer.writerow(['Ano', ano_relatorio])
    writer.writerow(['Carga Horária', carga_relatorio])
    writer.writerow(['Status do Relatório', status_filter.capitalize()])
    writer.writerow(['Gerado em', datetime.now().strftime('%d/%m/%Y %H:%M:%S')])
    writer.writerow([])
    writer.writerow([
        'Empresa',
        'Descrição da Empresa',
        'Rubrica',
        'Descrição da Rubrica',
        'CPF',
        'Matrícula',
        'Nome do Servidor',
        'Referência Vertical',
        'Referência Horizontal',
        'Valor Vencimento',
        'Frequência',
        'Valor Recebido',
        'Valor Esperado',
        'Diferença (R$)',
        'Diferença (%)',
        'Status',
        'Justificativa',
    ])

    for item in resultados:
        writer.writerow([
            item.get('empresa', ''),
            item.get('dc_empresa', ''),
            item.get('rubrica', ''),
            item.get('dc_rubrica', ''),
            item.get('cpf', ''),
            item.get('matricula', ''),
            item.get('nome_servidor', ''),
            item.get('ref_vertical', ''),
            item.get('ref_horizontal', ''),
            _format_currency(item.get('valor_vencimento')) if item.get('valor_vencimento') is not None else '',
            _format_number(item.get('frequencia')) if item.get('frequencia') not in (None, '') else '',
            _format_currency(item.get('valor_total_recebido')) if item.get('valor_total_recebido') is not None else '',
            _format_currency(item.get('valor_calculado')) if item.get('valor_calculado') is not None else '',
            _format_currency(item.get('diferenca_absoluta')) if item.get('diferenca_absoluta') is not None else '',
            _format_percent(item.get('diferenca_percentual')) if item.get('diferenca_percentual') not in (None, '') else '',
            item.get('status', ''),
            item.get('justificativa', ''),
        ])

    return response


@login_required
def exportar_relatorio_carga_horaria(request):
    """Exporta um relatório Word com divergências de carga horária"""
    resultado = request.session.get('verificacao_resultados', {})
    rubrica = request.session.get('verificacao_rubrica', '')
    ano = request.session.get('verificacao_ano', '')
    mes = request.session.get('verificacao_mes', '')
    carga = request.session.get('verificacao_carga', '')
    
    if not resultado or not resultado.get('resultados'):
        messages.warning(request, 'Nenhuma verificação disponível para gerar relatório.')
        return redirect('verificacao_resultados')
    
    # Filtrar apenas os com carga horária divergente
    resultados = resultado.get('resultados', [])
    resultados_divergentes = [
        r for r in resultados 
        if 'divergente' in r.get('justificativa', '').lower() and 'Carga horária' in r.get('justificativa', '')
    ]
    
    if not resultados_divergentes:
        messages.warning(request, 'Nenhum registro com divergência de carga horária encontrado para gerar relatório.')
        return redirect('verificacao_resultados')
    
    # Gerar documento Word
    doc_io = gerar_relatorio_carga_horaria(resultados_divergentes, rubrica, ano, carga, mes)
    
    # Preparar resposta
    response = HttpResponse(
        doc_io.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = f'attachment; filename="relatorio_carga_horaria_{mes}_{ano}.docx"'
    
    return response


@login_required
def exportar_comparacao_excel_view(request):
    """Exporta a comparação mensal de rubricas para Excel"""
    comparacao_data = request.session.get('comparacao_data', [])
    rubrica_codigo = request.session.get('rubrica_codigo', '')
    rubrica_nome = request.session.get('rubrica_nome', '')
    descricao_rubrica = request.session.get('descricao_rubrica', '')
    
    if not comparacao_data:
        messages.warning(request, 'Nenhuma comparação disponível para exportar.')
        return redirect('padrao_list')
    
    if not rubrica_codigo:
        messages.warning(request, 'Código da rubrica não encontrado.')
        return redirect('padrao_list')
    
    return exportar_comparacao_excel(
        comparacao_data, rubrica_codigo, rubrica_nome, descricao_rubrica
    )
