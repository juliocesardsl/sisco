from django.urls import path
from . import views

urlpatterns = [
    # Rubricas
    path('rubricas/', views.RubricaListView.as_view(), name='rubrica_list'),
    path('rubricas/<int:pk>/', views.RubricaDetailView.as_view(), name='rubrica_detail'),
    path('rubricas/novo/', views.RubricaCreateView.as_view(), name='rubrica_create'),
    path('rubricas/<int:pk>/editar/', views.RubricaUpdateView.as_view(), name='rubrica_update'),
    path('rubricas/<int:pk>/deletar/', views.RubricaDeleteView.as_view(), name='rubrica_delete'),

    # Empresas
    path('empresas/', views.EmpresaListView.as_view(), name='empresa_list'),
    path('empresas/<int:pk>/', views.EmpresaDetailView.as_view(), name='empresa_detail'),
    path('empresas/novo/', views.EmpresaCreateView.as_view(), name='empresa_create'),
    path('empresas/<int:pk>/editar/', views.EmpresaUpdateView.as_view(), name='empresa_update'),
    path('empresas/<int:pk>/deletar/', views.EmpresaDeleteView.as_view(), name='empresa_delete'),

    # Padrões de Conformidade
    path('padroes/', views.PadraoConformidadeListView.as_view(), name='padrao_list'),
    path('padroes/novo/', views.PadraoConformidadeCreateView.as_view(), name='padrao_create'),
    path('padroes/<int:pk>/editar/', views.PadraoConformidadeUpdateView.as_view(), name='padrao_update'),
    path('padroes/<int:pk>/deletar/', views.PadraoConformidadeDeleteView.as_view(), name='padrao_delete'),
    path('padroes/exportar-comparacao/', views.exportar_comparacao_excel_view, name='exportar_comparacao'),

    # Verificações
    path('verificacoes/', views.VerificacaoListView.as_view(), name='verificacao_list'),
    path('verificacoes/novo/', views.verificacao_create, name='verificacao_create'),
    path('verificacoes/novo/', views.verificacao_create, name='verificacao_form'),
    path('verificacoes/exportar/', views.exportar_verificacoes, name='verificacao_export'),
    path('verificacoes/resultados/', views.verificacao_resultados, name='verificacao_resultados'),
    path('verificacoes/<int:pk>/resultados/', views.verificacao_resultados_detail, name='verificacao_resultados_detail'),
    path('verificacoes/resultados/exportar/', views.exportar_verificacao_csv, name='verificacao_resultados_export'),
    path('verificacoes/resultados/relatorio-carga-horaria/', views.exportar_relatorio_carga_horaria, name='relatorio_carga_horaria'),
    path('servidor/<int:index>/', views.servidor_detail, name='servidor_detail'),
    path('agente/', views.agente_assistente_view, name='agente_assistente'),
    path('reavaliar-faixas/', views.reavaliar_faixas, name='reavaliar_faixas'),
]
