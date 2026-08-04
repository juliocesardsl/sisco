from django.contrib import admin
from .models import Rubrica, Empresa, PadraoConformidade, VerificacaoConformidade


@admin.register(Rubrica)
class RubricaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nome', 'ativa')
    list_filter = ('ativa', 'criada_em')
    search_fields = ('codigo', 'nome')
    readonly_fields = ('criada_em', 'atualizada_em')


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'email', 'ativa')
    list_filter = ('ativa', 'criada_em')
    search_fields = ('nome', 'cnpj')
    readonly_fields = ('criada_em', 'atualizada_em')


@admin.register(PadraoConformidade)
class PadraoConformidadeAdmin(admin.ModelAdmin):
    list_display = ('rubrica', 'empresa', 'ano', 'valor_minimo', 'valor_maximo')
    list_filter = ('ano', 'empresa', 'rubrica')
    search_fields = ('rubrica__nome', 'empresa__nome')
    readonly_fields = ('criado_em', 'atualizado_em')


@admin.register(VerificacaoConformidade)
class VerificacaoConformidadeAdmin(admin.ModelAdmin):
    list_display = ('padrao', 'valor_pago', 'status', 'data_verificacao')
    list_filter = ('status', 'data_verificacao')
    search_fields = ('padrao__rubrica__nome', 'padrao__empresa__nome')
    readonly_fields = ('data_verificacao', 'status')
