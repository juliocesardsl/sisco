from django.urls import path
from . import views

urlpatterns = [
    # Processos
    path('', views.ProcessoListView.as_view(), name='processo_list'),
    path('<int:pk>/', views.ProcessoDetailView.as_view(), name='processo_detail'),
    path('novo/', views.ProcessoCreateView.as_view(), name='processo_create'),
    path('<int:pk>/editar/', views.ProcessoUpdateView.as_view(), name='processo_update'),
    path('<int:pk>/deletar/', views.ProcessoDeleteView.as_view(), name='processo_delete'),
    
    # Documentos
    path('<int:processo_id>/documento/novo/', views.adicionar_documento, name='adicionar_documento'),
    
    # Comentários
    path('<int:processo_id>/comentario/novo/', views.adicionar_comentario, name='adicionar_comentario'),
]
