from django import forms
from django.forms import ModelForm
from .models import Rubrica, Empresa, PadraoConformidade, VerificacaoConformidade


class RubricaForm(ModelForm):
    tolerancia = forms.DecimalField(
        required=False,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'})
    )
    tipo_calculo = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    tipo_validacao = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Rubrica
        fields = [
            'nome', 'codigo', 'descricao', 'valor_padrao', 'ativa',
            'formula_calculo', 'tipo_calculo', 'base_calculo', 'base_legal', 'incidencia', 'caracteristicas',
            'regras_verificacao', 'tolerancia', 'tipo_validacao',
            'valor_minimo_padrao', 'valor_maximo_padrao', 'carga_horaria_padrao'
        ]
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'valor_padrao': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'formula_calculo': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'tipo_calculo': forms.TextInput(attrs={'class': 'form-control'}),
            'base_calculo': forms.TextInput(attrs={'class': 'form-control'}),
            'base_legal': forms.TextInput(attrs={'class': 'form-control'}),
            'incidencia': forms.TextInput(attrs={'class': 'form-control'}),
            'caracteristicas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'regras_verificacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'tolerancia': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_validacao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_minimo_padrao': forms.TextInput(attrs={'class': 'form-control'}),
            'valor_maximo_padrao': forms.TextInput(attrs={'class': 'form-control'}),
            'carga_horaria_padrao': forms.TextInput(attrs={'class': 'form-control'}),
        }


class EmpresaForm(ModelForm):
    class Meta:
        model = Empresa
        fields = ['nome', 'codigo', 'cnpj', 'razao_social', 'email', 'telefone', 'ativa']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite o código'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'XX.XXX.XXX/XXXX-XX'}),
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefone': forms.TextInput(attrs={'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PadraoConformidadeForm(ModelForm):
    class Meta:
        model = PadraoConformidade
        fields = ['rubrica', 'empresa', 'ano', 'valor_minimo', 'valor_maximo', 'carga_horaria']
        widgets = {
            'rubrica': forms.Select(attrs={'class': 'form-control'}),
            'empresa': forms.Select(attrs={'class': 'form-control'}),
            'ano': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_minimo': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_maximo': forms.NumberInput(attrs={'class': 'form-control'}),
            'carga_horaria': forms.NumberInput(attrs={'class': 'form-control'}),
        }


class PadraoComparacaoForm(forms.Form):
    rubrica = forms.ModelChoiceField(
        queryset=Rubrica.objects.order_by('nome'),
        label='Rubrica',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    arquivo_extrator_mes_anterior = forms.FileField(
        label='Arquivo Extrator - mês anterior',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )
    arquivo_extrator_mes_atual = forms.FileField(
        label='Arquivo Extrator - mês atual',
        widget=forms.FileInput(attrs={'class': 'form-control', 'accept': '.xlsx,.xls'})
    )


class VerificacaoConformidadeForm(ModelForm):
    rubrica = forms.CharField(
        label='Rubrica',
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a rubrica'})
    )
    ano_referencia = forms.IntegerField(
        label='Ano da Referência',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    mes_referencia = forms.IntegerField(
        label='Mês da Referência',
        required=True,
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '1-12'})
    )
    carga_horaria = forms.IntegerField(
        label='Carga Horária',
        required=True,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = VerificacaoConformidade
        fields = ['arquivo_vencimento', 'arquivo_extrator']
        widgets = {
            'arquivo_vencimento': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.xlsx,.xls,.doc,.docx'}),
            'arquivo_extrator': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.xlsx,.xls,.doc,.docx'}),
        }
