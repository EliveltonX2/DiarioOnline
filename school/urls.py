from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('turmas/', views.turma_list, name='turma_list'),
    path('turmas/nova/', views.turma_form, name='turma_create'),
    path('turmas/<int:pk>/', views.turma_detail, name='turma_detail'),
    path('turmas/<int:pk>/editar/', views.turma_form, name='turma_edit'),
    
    path('alunos/', views.aluno_list, name='aluno_list'),
    path('alunos/novo/', views.aluno_form, name='aluno_create'),
    path('alunos/<int:pk>/', views.aluno_detail, name='aluno_detail'),
    path('alunos/<int:pk>/editar/', views.aluno_form, name='aluno_edit'),
    
    path('chamadas/', views.chamada_list, name='chamada_list'),
    path('chamadas/iniciar/', views.chamada_start, name='chamada_start'),
    path('chamadas/realizar/', views.chamada_realizar, name='chamada_realizar'),
    path('chamadas/<int:pk>/', views.chamada_detail, name='chamada_detail'),
    path('chamadas/<int:pk>/editar/', views.chamada_edit, name='chamada_edit'),
    
    path('registros/', views.registro_list, name='registro_list'),
    path('registros/aluno/novo/', views.registro_aluno_create, name='registro_aluno_create'),
    path('registros/aluno/<int:pk>/editar/', views.registro_aluno_edit, name='registro_aluno_edit'),
    path('registros/turma/novo/', views.registro_turma_create, name='registro_turma_create'),
    path('registros/turma/<int:pk>/editar/', views.registro_turma_edit, name='registro_turma_edit'),
    path('registros/marcar-lido/<int:pk>/', views.marcar_lido, name='marcar_lido'),
    
    path('relatorios/', views.relatorios, name='relatorios'),
]
