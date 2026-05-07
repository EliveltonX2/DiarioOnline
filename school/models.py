from django.db import models
from django.conf import settings

class Turma(models.Model):
    nome = models.CharField(max_length=100)
    coordenadores = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='turmas')
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nome

class Aluno(models.Model):
    SITUACAO_CHOICES = [
        ('em_curso', 'Em Curso'),
        ('transferido', 'Transferido'),
        ('remanejado', 'Remanejado'),
    ]
    GENERO_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Feminino'),
        ('O', 'Outro'),
    ]

    cod_sgde = models.CharField(max_length=50, unique=True, verbose_name="Cód SGDE")
    nome = models.CharField(max_length=200)
    situacao = models.CharField(max_length=20, choices=SITUACAO_CHOICES, default='em_curso')
    data_nascimento = models.DateField(null=True, blank=True)
    turma = models.ForeignKey(Turma, on_delete=models.SET_NULL, null=True, related_name='alunos')
    genero = models.CharField(max_length=1, choices=GENERO_CHOICES)
    telefone_responsavel = models.CharField(max_length=20, blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} ({self.cod_sgde})"

class RegistroAluno(models.Model):
    data = models.DateField(auto_now_add=True)
    descricao = models.TextField()
    alunos = models.ManyToManyField(Aluno, related_name='registros')
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    lido_por = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='registros_aluno_lidos', blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro em {self.data}"

class RegistroTurma(models.Model):
    data = models.DateField(auto_now_add=True)
    descricao = models.TextField()
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='registros')
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registro de Turma {self.turma.nome} em {self.data}"

class Chamada(models.Model):
    data = models.DateField()
    turma = models.ForeignKey(Turma, on_delete=models.CASCADE, related_name='chamadas')
    observacao = models.TextField(blank=True)
    icone_clima_evento = models.CharField(max_length=50, blank=True, help_text="Ex: ensolarado, chovendo, evento, prova")
    criado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('data', 'turma')

    def __str__(self):
        return f"Chamada {self.turma.nome} - {self.data}"

class RegistroChamada(models.Model):
    STATUS_CHOICES = [
        ('P', 'Presença'),
        ('F', 'Falta'),
    ]
    chamada = models.ForeignKey(Chamada, on_delete=models.CASCADE, related_name='registros')
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE, related_name='frequencias')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)

    class Meta:
        unique_together = ('chamada', 'aluno')

    def __str__(self):
        return f"{self.aluno.nome} - {self.get_status_display()}"
