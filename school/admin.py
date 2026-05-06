from django.contrib import admin
from .models import Turma, Aluno, RegistroAluno, RegistroTurma, Chamada, RegistroChamada

@admin.register(Turma)
class TurmaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'criado_em')
    search_fields = ('nome',)
    filter_horizontal = ('coordenadores',)

@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cod_sgde', 'turma', 'situacao')
    list_filter = ('turma', 'situacao', 'genero')
    search_fields = ('nome', 'cod_sgde')

@admin.register(RegistroAluno)
class RegistroAlunoAdmin(admin.ModelAdmin):
    list_display = ('data', 'criado_por', 'criado_em')
    list_filter = ('data', 'criado_por')
    filter_horizontal = ('alunos',)

@admin.register(RegistroTurma)
class RegistroTurmaAdmin(admin.ModelAdmin):
    list_display = ('data', 'turma', 'criado_por', 'criado_em')
    list_filter = ('data', 'turma', 'criado_por')

@admin.register(Chamada)
class ChamadaAdmin(admin.ModelAdmin):
    list_display = ('data', 'turma', 'criado_por', 'criado_em')
    list_filter = ('data', 'turma')

@admin.register(RegistroChamada)
class RegistroChamadaAdmin(admin.ModelAdmin):
    list_display = ('chamada', 'aluno', 'status')
    list_filter = ('status', 'chamada__data')
