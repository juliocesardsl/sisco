from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from .models import Processo, TipoProcesso, DocumentoProcesso, ComentarioProcesso
from .forms import ProcessoForm, DocumentoProcessoForm, ComentarioProcessoForm


class ProcessoListView(LoginRequiredMixin, ListView):
    model = Processo
    template_name = 'processos/processo_list.html'
    context_object_name = 'processos'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class ProcessoDetailView(LoginRequiredMixin, DetailView):
    model = Processo
    template_name = 'processos/processo_detail.html'
    context_object_name = 'processo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documentos'] = self.object.documentos.all()
        context['comentarios'] = self.object.comentarios.all()
        return context


class ProcessoCreateView(LoginRequiredMixin, CreateView):
    model = Processo
    form_class = ProcessoForm
    template_name = 'processos/processo_form.html'
    success_url = reverse_lazy('processo_list')

    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        messages.success(self.request, 'Processo criado com sucesso!')
        return super().form_valid(form)


class ProcessoUpdateView(LoginRequiredMixin, UpdateView):
    model = Processo
    form_class = ProcessoForm
    template_name = 'processos/processo_form.html'
    success_url = reverse_lazy('processo_list')

    def form_valid(self, form):
        messages.success(self.request, 'Processo atualizado com sucesso!')
        return super().form_valid(form)


class ProcessoDeleteView(LoginRequiredMixin, DeleteView):
    model = Processo
    template_name = 'processos/processo_confirm_delete.html'
    success_url = reverse_lazy('processo_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Processo deletado com sucesso!')
        return super().delete(request, *args, **kwargs)


def adicionar_documento(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    if request.method == 'POST':
        form = DocumentoProcessoForm(request.POST, request.FILES)
        if form.is_valid():
            documento = form.save(commit=False)
            documento.processo = processo
            documento.tamanho = request.FILES['arquivo'].size
            documento.save()
            messages.success(request, 'Documento adicionado com sucesso!')
            return redirect('processo_detail', pk=processo_id)
    else:
        form = DocumentoProcessoForm()
    
    return render(request, 'processos/documento_form.html', {
        'form': form,
        'processo': processo,
    })


def adicionar_comentario(request, processo_id):
    processo = get_object_or_404(Processo, id=processo_id)
    
    if request.method == 'POST':
        form = ComentarioProcessoForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.processo = processo
            comentario.autor = request.user
            comentario.save()
            messages.success(request, 'Comentário adicionado com sucesso!')
            return redirect('processo_detail', pk=processo_id)
    else:
        form = ComentarioProcessoForm()
    
    return render(request, 'processos/comentario_form.html', {
        'form': form,
        'processo': processo,
    })
