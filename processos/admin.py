from django.contrib import admin
from .models import Processo, TipoProcesso, DocumentoProcesso, ComentarioProcesso


@admin.register(TipoProcesso)
class TipoProcessoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')
    search_fields = ('nome',)


@admin.register(Processo)
class ProcessoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'titulo', 'status', 'responsavel', 'data_criacao')
    list_filter = ('status', 'data_criacao', 'tipo')
    search_fields = ('numero', 'titulo')
    readonly_fields = ('data_criacao', 'data_atualizacao')


@admin.register(DocumentoProcesso)
class DocumentoProcessoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'processo', 'data_upload', 'tamanho')
    list_filter = ('data_upload', 'processo')
    search_fields = ('titulo', 'processo__numero')
    readonly_fields = ('data_upload', 'tamanho')


@admin.register(ComentarioProcesso)
class ComentarioProcessoAdmin(admin.ModelAdmin):
    list_display = ('processo', 'autor', 'data_criacao')
    list_filter = ('data_criacao', 'autor')
    search_fields = ('processo__numero', 'autor__username')
    readonly_fields = ('data_criacao',)
