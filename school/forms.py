from django import forms
from .models import Turma, Aluno, Chamada, RegistroAluno, RegistroTurma

class TurmaForm(forms.ModelForm):
    csv_file = forms.FileField(
        required=False, 
        label="Importar Alunos (CSV)", 
        help_text="Opcional. Envie um arquivo CSV com as colunas: cod_sgde, nome, data_nascimento (YYYY-MM-DD), genero (M/F)."
    )

    class Meta:
        model = Turma
        fields = ['nome', 'coordenador']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'coordenador': forms.Select(attrs={'class': 'form-select'}),
        }

class AlunoForm(forms.ModelForm):
    class Meta:
        model = Aluno
        fields = ['cod_sgde', 'nome', 'situacao', 'data_nascimento', 'turma', 'genero', 'telefone_responsavel']
        widgets = {
            'cod_sgde': forms.TextInput(attrs={'class': 'form-control'}),
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'situacao': forms.Select(attrs={'class': 'form-select'}),
            'data_nascimento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'genero': forms.Select(attrs={'class': 'form-select'}),
            'telefone_responsavel': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '(XX) XXXXX-XXXX'}),
        }

class ChamadaForm(forms.ModelForm):
    class Meta:
        model = Chamada
        fields = ['turma', 'data', 'icone_clima_evento', 'observacao']
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'data': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'icone_clima_evento': forms.Select(choices=[
                ('', 'Sem Ícone'),
                ('ensolarado', 'Ensolarado'),
                ('chovendo', 'Chovendo'),
                ('nublado', 'Nublado'),
                ('evento', 'Dia de Evento'),
                ('prova', 'Dia de Prova'),
            ], attrs={'class': 'form-select'}),
            'observacao': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

class RegistroAlunoForm(forms.ModelForm):
    class Meta:
        model = RegistroAluno
        fields = ['alunos', 'descricao']
        widgets = {
            'alunos': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva a ocorrência...'}),
        }

class RegistroTurmaForm(forms.ModelForm):
    class Meta:
        model = RegistroTurma
        fields = ['turma', 'descricao']
        widgets = {
            'turma': forms.Select(attrs={'class': 'form-select'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descreva a ocorrência para a turma...'}),
        }
