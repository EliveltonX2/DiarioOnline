from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turma, Aluno, RegistroAluno, Chamada, RegistroChamada, RegistroTurma
from .forms import TurmaForm, AlunoForm, ChamadaForm, RegistroAlunoForm, RegistroTurmaForm
import csv
import io
from django.forms.models import model_to_dict
from django.db.models import Count, Q
import json
from datetime import datetime

@login_required
def dashboard(request):
    turmas_count = Turma.objects.filter(coordenador=request.user).count()
    alunos_count = Aluno.objects.filter(turma__coordenador=request.user).count()
    
    # Exemplo de lembretes: últimos registros
    ultimos_registros = RegistroAluno.objects.filter(alunos__turma__coordenador=request.user).distinct().order_by('-criado_em')[:5]

    # Chart Data: Total de presenças e faltas geral
    registros = RegistroChamada.objects.filter(chamada__turma__coordenador=request.user)
    presencas = registros.filter(status='P').count()
    faltas = registros.filter(status='F').count()
    
    chart_data = {
        'labels': ['Presenças', 'Faltas'],
        'data': [presencas, faltas]
    }

    context = {
        'turmas_count': turmas_count,
        'alunos_count': alunos_count,
        'ultimos_registros': ultimos_registros,
        'chart_data_json': json.dumps(chart_data)
    }
    return render(request, 'school/dashboard.html', context)

@login_required
def turma_list(request):
    turmas = Turma.objects.all().order_by('-criado_em')
    return render(request, 'school/turma_list.html', {'turmas': turmas})

@login_required
def turma_detail(request, pk):
    turma = get_object_or_404(Turma, pk=pk)
    alunos = turma.alunos.all().order_by('nome')
    registros = turma.registros.all().order_by('-data', '-criado_em')
    
    # Chart Data: Faltas e Presenças por dia (Últimas 7 chamadas)
    ultimas_chamadas = Chamada.objects.filter(turma=turma).order_by('-data')[:7]
    ultimas_chamadas = reversed(list(ultimas_chamadas)) # ordem cronológica
    
    labels = []
    presencas_data = []
    faltas_data = []
    
    for c in ultimas_chamadas:
        labels.append(c.data.strftime("%d/%m"))
        p = RegistroChamada.objects.filter(chamada=c, status='P').count()
        f = RegistroChamada.objects.filter(chamada=c, status='F').count()
        presencas_data.append(p)
        faltas_data.append(f)
        
    chart_data = {
        'labels': labels,
        'presencas': presencas_data,
        'faltas': faltas_data
    }
    
    return render(request, 'school/turma_detail.html', {
        'turma': turma, 
        'alunos': alunos, 
        'registros': registros,
        'chart_data_json': json.dumps(chart_data)
    })

@login_required
def turma_form(request, pk=None):
    if pk:
        turma = get_object_or_404(Turma, pk=pk)
        action = "Editar"
    else:
        turma = None
        action = "Nova"

    if request.method == 'POST':
        form = TurmaForm(request.POST, request.FILES, instance=turma)
        if form.is_valid():
            turma_obj = form.save()
            
            # Processar CSV se houver
            csv_file = form.cleaned_data.get('csv_file')
            if csv_file:
                try:
                    data_set = csv_file.read().decode('UTF-8')
                    io_string = io.StringIO(data_set)
                    # Ignora o cabeçalho
                    next(io_string, None) 
                    
                    for row in csv.reader(io_string, delimiter=',', quotechar='"'):
                        # Padrão: cod_sgde, nome, data_nascimento, genero
                        if len(row) >= 4:
                            cod_sgde = row[0].strip()
                            nome = row[1].strip()
                            
                            try:
                                data_nasc = datetime.strptime(row[2].strip(), '%Y-%m-%d').date()
                            except ValueError:
                                data_nasc = None
                                
                            genero = row[3].strip().upper()
                            if genero not in ['M', 'F']:
                                genero = 'O'
                                
                            Aluno.objects.update_or_create(
                                cod_sgde=cod_sgde,
                                defaults={
                                    'nome': nome,
                                    'data_nascimento': data_nasc,
                                    'genero': genero,
                                    'turma': turma_obj,
                                    'situacao': 'em_curso'
                                }
                            )
                    messages.success(request, f"Alunos importados com sucesso para a turma {turma_obj.nome}.")
                except Exception as e:
                    messages.error(request, f"Erro ao processar arquivo CSV: {str(e)}")

            messages.success(request, f"Turma {action.lower()} com sucesso!")
            return redirect('turma_detail', pk=turma_obj.pk)
    else:
        form = TurmaForm(instance=turma)

    return render(request, 'school/turma_form.html', {'form': form, 'action': action, 'turma': turma})


@login_required
def aluno_list(request):
    alunos = Aluno.objects.all().select_related('turma').order_by('nome')
    return render(request, 'school/aluno_list.html', {'alunos': alunos})

@login_required
def aluno_detail(request, pk):
    aluno = get_object_or_404(Aluno, pk=pk)
    # Buscamos também os registros (ocorrências) em que o aluno está envolvido
    registros = aluno.registros.all().order_by('-data', '-criado_em')
    
    # Chart Data: Total presenças e faltas do aluno
    registros_chamada = RegistroChamada.objects.filter(aluno=aluno)
    presencas = registros_chamada.filter(status='P').count()
    faltas = registros_chamada.filter(status='F').count()
    
    chart_data = {
        'labels': ['Presenças', 'Faltas'],
        'data': [presencas, faltas]
    }
    
    return render(request, 'school/aluno_detail.html', {
        'aluno': aluno, 
        'registros': registros,
        'chart_data_json': json.dumps(chart_data)
    })

@login_required
def aluno_form(request, pk=None):
    if pk:
        aluno = get_object_or_404(Aluno, pk=pk)
        action = "Editar"
    else:
        aluno = None
        action = "Novo"

    if request.method == 'POST':
        form = AlunoForm(request.POST, instance=aluno)
        if form.is_valid():
            aluno_obj = form.save()
            messages.success(request, f"Aluno {action.lower()} com sucesso!")
            return redirect('aluno_detail', pk=aluno_obj.pk)
    else:
        form = AlunoForm(instance=aluno)

    return render(request, 'school/aluno_form.html', {'form': form, 'action': action, 'aluno': aluno})


@login_required
def chamada_start(request):
    if request.method == 'POST':
        form = ChamadaForm(request.POST)
        if form.is_valid():
            # Salva os dados na sessão temporariamente e vai para a tela interativa
            request.session['chamada_data'] = {
                'turma_id': form.cleaned_data['turma'].id,
                'data': form.cleaned_data['data'].strftime('%Y-%m-%d'),
                'icone_clima_evento': form.cleaned_data['icone_clima_evento'],
                'observacao': form.cleaned_data['observacao'],
            }
            return redirect('chamada_realizar')
    else:
        # Tenta pegar turma inicial da URL se vier de um atalho
        initial_turma = request.GET.get('turma')
        form = ChamadaForm(initial={'turma': initial_turma, 'data': datetime.now().date()})
        
    return render(request, 'school/chamada_start.html', {'form': form})

@login_required
def chamada_realizar(request):
    chamada_info = request.session.get('chamada_data')
    if not chamada_info:
        messages.warning(request, "Nenhuma chamada iniciada.")
        return redirect('chamada_start')
        
    turma = get_object_or_404(Turma, id=chamada_info['turma_id'])
    
    # Verifica se já existe chamada para esta turma nesta data
    if Chamada.objects.filter(turma=turma, data=chamada_info['data']).exists():
        messages.error(request, f"Já existe uma chamada registrada para a turma {turma.nome} na data {chamada_info['data']}.")
        del request.session['chamada_data']
        return redirect('chamada_start')

    alunos = turma.alunos.filter(situacao='em_curso').order_by('nome')
    
    if request.method == 'POST':
        # Recebe os dados da UI interativa via formulário oculto
        # O formulário vai mandar arrays tipo aluno_1=P, aluno_2=F
        
        # Cria a Chamada
        chamada = Chamada.objects.create(
            turma=turma,
            data=chamada_info['data'],
            icone_clima_evento=chamada_info['icone_clima_evento'],
            observacao=chamada_info['observacao'],
            criado_por=request.user
        )
        
        faltas_count = 0
        
        # Cria os Registros de Frequência
        for aluno in alunos:
            status = request.POST.get(f'aluno_{aluno.id}')
            if status in ['P', 'F']:
                RegistroChamada.objects.create(
                    chamada=chamada,
                    aluno=aluno,
                    status=status
                )
                if status == 'F':
                    faltas_count += 1
                    
        # Aqui poderíamos implementar a lógica de verificar 3 faltas consecutivas e gerar aviso.
        
        messages.success(request, f"Chamada salva com sucesso! {faltas_count} faltas registradas.")
        del request.session['chamada_data']
        return redirect('turma_detail', pk=turma.pk)

    return render(request, 'school/chamada_realizar.html', {
        'turma': turma,
        'alunos': alunos,
        'chamada_info': chamada_info
    })

@login_required
def chamada_list(request):
    chamadas = Chamada.objects.all().select_related('turma', 'criado_por').order_by('-data')
    return render(request, 'school/chamada_list.html', {'chamadas': chamadas})

@login_required
def relatorios(request):
    turmas = Turma.objects.all()
    alunos = Aluno.objects.all()
    
    # Processa os filtros
    tipo = request.GET.get('tipo')
    turma_id = request.GET.get('turma')
    aluno_id = request.GET.get('aluno')
    data_inicio = request.GET.get('data_inicio')
    data_fim = request.GET.get('data_fim')
    
    resultados = None
    titulo_relatorio = ""
    
    if tipo == 'faltas':
        titulo_relatorio = "Matriz de Frequência"
        
        # 1. Buscar chamadas baseado nos filtros (Turma é obrigatório ou pega todas, mas matriz fica melhor por turma)
        chamadas_query = Chamada.objects.all().order_by('data')
        if turma_id:
            chamadas_query = chamadas_query.filter(turma_id=turma_id)
        if data_inicio:
            chamadas_query = chamadas_query.filter(data__gte=data_inicio)
        if data_fim:
            chamadas_query = chamadas_query.filter(data__lte=data_fim)
            
        chamadas_list = list(chamadas_query)
        
        # 2. Buscar alunos baseado na turma
        alunos_query = Aluno.objects.all().order_by('nome')
        if turma_id:
            alunos_query = alunos_query.filter(turma_id=turma_id)
        if aluno_id:
            alunos_query = alunos_query.filter(id=aluno_id)
            
        alunos_list = list(alunos_query)
        
        # 3. Buscar todos os registros dessas chamadas para esses alunos
        registros_chamada = RegistroChamada.objects.filter(
            chamada__in=chamadas_list,
            aluno__in=alunos_list
        ).select_related('chamada', 'aluno')
        
        # Criar dicionário de rápido acesso: (aluno_id, chamada_id) -> status
        mapa_registros = {(r.aluno_id, r.chamada_id): r.status for r in registros_chamada}
        
        # 4. Construir a matriz
        matriz = []
        for aluno in alunos_list:
            linha = {
                'aluno': aluno,
                'frequencias': [],
                'total_p': 0,
                'total_f': 0,
                'porcentagem': 0
            }
            
            for chamada in chamadas_list:
                status = mapa_registros.get((aluno.id, chamada.id), '-')
                linha['frequencias'].append(status)
                if status == 'P':
                    linha['total_p'] += 1
                elif status == 'F':
                    linha['total_f'] += 1
                    
            total_chamadas = linha['total_p'] + linha['total_f']
            if total_chamadas > 0:
                linha['porcentagem'] = round((linha['total_p'] / total_chamadas) * 100, 1)
                
            matriz.append(linha)
            
        resultados = {
            'chamadas': chamadas_list,
            'matriz': matriz
        }
        
    elif tipo == 'registros':
        titulo_relatorio = "Histórico de Ocorrências e Registros"
        query = RegistroAluno.objects.prefetch_related('alunos').select_related('criado_por')
        if turma_id:
            query = query.filter(alunos__turma_id=turma_id).distinct()
        if aluno_id:
            query = query.filter(alunos__id=aluno_id)
        if data_inicio:
            query = query.filter(data__gte=data_inicio)
        if data_fim:
            query = query.filter(data__lte=data_fim)
            
        resultados = query.order_by('-data')

    context = {
        'turmas': turmas,
        'alunos': alunos,
        'resultados': resultados,
        'tipo': tipo,
        'titulo_relatorio': titulo_relatorio
    }
    return render(request, 'school/relatorios.html', context)

@login_required
def registro_aluno_create(request):
    if request.method == 'POST':
        form = RegistroAlunoForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.criado_por = request.user
            registro.save()
            form.save_m2m() # Importante para salvar o ManyToManyField 'alunos'
            messages.success(request, "Registro de aluno(s) criado com sucesso!")
            # Tentar redirecionar para o primeiro aluno selecionado ou voltar
            primeiro_aluno = registro.alunos.first()
            if primeiro_aluno:
                return redirect('aluno_detail', pk=primeiro_aluno.pk)
            return redirect('dashboard')
    else:
        initial_aluno = request.GET.get('aluno')
        form = RegistroAlunoForm(initial={'alunos': [initial_aluno]} if initial_aluno else None)
        
    return render(request, 'school/registro_form.html', {'form': form, 'titulo': 'Novo Registro de Aluno'})

@login_required
def registro_turma_create(request):
    if request.method == 'POST':
        form = RegistroTurmaForm(request.POST)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.criado_por = request.user
            registro.save()
            messages.success(request, f"Registro para a turma {registro.turma.nome} criado com sucesso!")
            return redirect('turma_detail', pk=registro.turma.pk)
    else:
        initial_turma = request.GET.get('turma')
        form = RegistroTurmaForm(initial={'turma': initial_turma})
        
    return render(request, 'school/registro_form.html', {'form': form, 'titulo': 'Novo Registro de Turma'})

