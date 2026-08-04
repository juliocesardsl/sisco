from django import forms
from django.forms import ModelForm
from .models import Rubrica, Empresa, PadraoConformidade, VerificacaoConformidade


class RubricaForm(ModelForm):
    class Meta:
        model = Rubrica
        fields = [
            'codigo', 'nome', 'filtro_vencimento', 'filtro_valor_fixo',
            'tipo_orgao_por_rubrica', 'tipo_rubrica_analise', 'descricao_rubrica_sigrh',
            'descricao', 'tipo_de_rubrica', 'criterio_calculo_rubrica', 'valor',
            'legislacao_vigente', 'link_para_consulta', 'ativa'
        ]
        labels = {
            'codigo': 'RUBRICA',
            'nome': 'DC_RUBRICA',
            'descricao': 'Descrição Completa da Rubrica',
            'filtro_vencimento': 'Filtro Vencimento',
            'filtro_valor_fixo': 'Filtro Valor Fixo',
            'tipo_orgao_por_rubrica': 'Tipo de Órgão por Rubrica',
            'tipo_rubrica_analise': 'Tipo de Rubrica (Análise)',
            'descricao_rubrica_sigrh': 'Descrição da Rubrica SIGRH',
            'tipo_de_rubrica': 'Tipo de Rubrica',
            'criterio_calculo_rubrica': 'Critério de Cálculo da Rubrica',
            'valor': 'Valor',
            'legislacao_vigente': 'Legislação Vigente',
            'link_para_consulta': 'Link para Consulta',
            'ativa': 'Ativa',
        }
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'codigo': forms.TextInput(attrs={'class': 'form-control'}),
            'filtro_vencimento': forms.TextInput(attrs={'class': 'form-control'}),
            'filtro_valor_fixo': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_orgao_por_rubrica': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_rubrica_analise': forms.TextInput(attrs={'class': 'form-control'}),
            'descricao_rubrica_sigrh': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'tipo_de_rubrica': forms.TextInput(attrs={'class': 'form-control'}),
            'criterio_calculo_rubrica': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'valor': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'legislacao_vigente': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'link_para_consulta': forms.URLInput(attrs={'class': 'form-control'}),
            'ativa': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
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
    rubrica = forms.CharField(
        label='Rubrica (opcional)',
        required=False,
        help_text='Deixe em branco para comparar todas as rubricas encontradas nos arquivos.',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ex.: 10502 ou deixe em branco para todas'
        })
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
        label='Rubrica (opcional)',
        max_length=255,
        required=False,
        help_text='Deixe em branco para verificar todas as rubricas encontradas no arquivo extrator.',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Digite a rubrica ou deixe em branco para todas'})
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
