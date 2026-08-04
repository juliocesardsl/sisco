from django import forms
from django.forms import ModelForm
from .models import Processo, DocumentoProcesso, ComentarioProcesso


class ProcessoForm(ModelForm):
    class Meta:
        model = Processo
        fields = ['numero', 'tipo', 'titulo', 'descricao', 'status']
        widgets = {
            'numero': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.TextInput(attrs={'class': 'form-control'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


class DocumentoProcessoForm(ModelForm):
    class Meta:
        model = DocumentoProcesso
        fields = ['titulo', 'arquivo']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'arquivo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class ComentarioProcessoForm(ModelForm):
    class Meta:
        model = ComentarioProcesso
        fields = ['texto']
        widgets = {
            'texto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
