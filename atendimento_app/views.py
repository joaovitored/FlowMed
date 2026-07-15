from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Senha,Perfil,Consultorio
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST


def index(request):
    return render(request, "index.html")

#o login vai verificar se a conta admin ou uma conta criada no django admin existe pra poder ir pra parte do painel
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # redireciona dependendo do perfil
            try:
                if user.perfil.tipo == 'recepcionista':
                    return redirect('atendimento_app:painel_recepcao')
                elif user.perfil.tipo == 'medico':
                    return redirect('atendimento_app:painel_consultorio')
            except Perfil.DoesNotExist:
                # usuário sem perfil (ex: superuser) vai pro admin
                return redirect('/admin/')

        messages.error(request, 'Usuário ou senha inválidos.')

    return render(request, 'login.html')

#vai dar logout caso clique no botao de sair no dashboard
@require_POST
def logout_view(request):
    logout(request)
    return redirect('atendimento_app:login')

@login_required
def painel_recepcao(request):
    """só vai mostrar a listagem para quem é da recepção, nenhum tipo de POST"""
    try:
        if request.user.perfil.tipo != 'recepcionista':
            return redirect('atendimento_app:painel_consultorio')
    except Perfil.DoesNotExist:
        return redirect('/admin/')

    busca_paciente = request.GET.get('g', '').strip()

    senhas_aguardando = Senha.objects.filter(status='aguardando_recepcao')

    if busca_paciente:
        senhas_aguardando = senhas_aguardando.filter(
            nome_paciente__icontains=busca_paciente
        )

    ultima_chamada = Senha.objects.filter(
        status='aguardando_consultorio'
    ).order_by('-chamado_recepcao').first()

    contexto = {
        'senhas_aguardando': senhas_aguardando,
        'busca_paciente': busca_paciente,
        'ultima_chamada': ultima_chamada,
        'consultorios': Consultorio.objects.filter(ativo=True),
    }
    return render(request, 'painel_recepcao.html', contexto)

@login_required
def painel_consultorio(request):
    try:
        if request.user.perfil.tipo != 'medico':
            return redirect('atendimento_app:painel_recepcao')
    except Perfil.DoesNotExist:
        return redirect('/admin/')
    
    consultorio = request.user.perfil.consultorio

    # senhas direcionadas pro consultório do médico logado
    senhas_aguardando = Senha.objects.filter(
        status='aguardando_consultorio',
        consultorio=consultorio
    )
     # senha atualmente sendo atendida   
    senha_atual = Senha.objects.filter(
        status='chamado',
        consultorio=consultorio
    ).order_by('-chamado_consultorio').first()

    contexto ={
        'senhas_aguardando':senhas_aguardando,
        'senha_atual':senha_atual,
        'consultorio': consultorio
    }

    return render(request, 'painel_consultorio.html', contexto)

@login_required
def historico(request):
    
    try:
        if request.user.perfil.tipo not in ['recepcionista', 'medico']:
            return redirect('/admin/')
    except Perfil.DoesNotExist:
        return redirect('/admin/')
    
    
    #filtro por data: pega o valor da URL (?data=2024-03-15)
    data_filtro = request.GET.get('data', '').strip()

    #busca senhas finalizadas ou canceladas
    senhas =Senha.objects.filter(
        status__in=['atendido','cancelado']
    ).order_by('-criado_em')

    # adicionar depois do filter inicial
    if request.user.perfil.tipo == 'medico':
        senhas = senhas.filter(consultorio=request.user.perfil.consultorio)

    # aplica filtro de data se foi informado
    if data_filtro:
        senhas = senhas.filter(criado_em__date=data_filtro)

    contexto ={
        'senhas':senhas,
        'data_filtro':data_filtro
    }

    return render(request, 'historico.html',contexto)





@login_required
@require_POST
def chamar_consultorio(request,senha_id):
    try:
        if request.user.perfil.tipo != 'medico':
            return redirect('atendimento_app:painel_consultorio')
    except Perfil.DoesNotExist:
        return redirect('/admin/')
    
    senha = get_object_or_404(Senha, id=senha_id)

    if senha.status != 'aguardando_consultorio':
        messages.error(request, 'Essa senha não pode ser chamada.')
        return redirect('atendimento_app:painel_consultorio')  
    
    # vincula o consultório do médico logado
    consultorio = request.user.perfil.consultorio
    senha.status='chamado'
    senha.chamado_consultorio = timezone.now()
    senha.consultorio = consultorio
    senha.save()

    # envia mensagem pra tela de TV via WebSocket
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'painel_tv',
        {
            'type': 'senha_chamada',
            'numero': senha.numero,
            'nome_paciente': senha.nome_paciente,
            'consultorio': consultorio.nome,
            'horario': senha.chamado_consultorio.strftime('%H:%M'),
        }
    )

    messages.success(request, f'Paciente {senha.nome_paciente} chamado!')
    
    return redirect('atendimento_app:painel_consultorio')


def painel_tv(request):
    ultimas_chamadas = Senha.objects.filter(
        status__in=['chamado', 'atendido']
    ).order_by('-chamado_consultorio')[:5]

    contexto = {
        'ultimas_chamadas': ultimas_chamadas,
    }
    return render(request, 'painel_tv.html', contexto)


@login_required
@require_POST
def finalizar_atendimento(request,senha_id):
    try:
        if request.user.perfil.tipo != 'medico':
            return redirect('atendimento_app:painel_consultorio')
    except Perfil.DoesNotExist:
        return redirect('/admin/')
    
    senha = get_object_or_404(Senha, id=senha_id)

    if senha.status not in ['chamado']:
        messages.error(request, 'Esta senha não pode ser finalizada.')
        return redirect('atendimento_app:painel_consultorio')
    
    senha.status = 'atendido'
    senha.finalizado_em = timezone.now()
    senha.save()
    
    messages.success(request, f'Atendimento de {senha.nome_paciente} finalizado!')
    return redirect('atendimento_app:painel_consultorio')

    
@login_required
@require_POST
def cadastrar_senha(request):

    try:
        if request.user.perfil.tipo != 'recepcionista':
            return redirect('atendimento_app:painel_consultorio')
    except Perfil.DoesNotExist:
        return redirect('/admin/')
    

    nome_paciente = request.POST.get('nome_paciente', '').strip()
    tipo_servico = request.POST.get('tipo_servico', '').strip()
    prioridade = request.POST.get('prioridade', 'media')

    if not nome_paciente or not tipo_servico:
        messages.error(request,'São obrigatórios inserir o nome do paciente e o tipo de serviço')
        return redirect('atendimento_app:painel_recepcao')
    
    Senha.objects.create(
        nome_paciente =nome_paciente,
        tipo_servico = tipo_servico,
        prioridade = prioridade,
    )
    
    messages.success(request,f'A senha foi cadastrada para o paciente: {nome_paciente} !')
    return redirect('atendimento_app:painel_recepcao')



@login_required
@require_POST
def cancelar_senha(request, senha_id):
    try:
        perfil = request.user.perfil
    except Perfil.DoesNotExist:
        return redirect('/admin/')

    senha = get_object_or_404(Senha, id=senha_id)

    if perfil.tipo == 'recepcionista':

        if senha.status not in ['aguardando_recepcao', 'aguardando_consultorio']:
            messages.error(request, 'Esta senha não pode ser cancelada.')
            return redirect('atendimento_app:painel_recepcao')

    elif perfil.tipo == 'medico':

        # Garante que o médico só cancele pacientes do seu consultório
        if senha.consultorio != perfil.consultorio:
            messages.error(request, 'Você não pode cancelar essa senha.')
            return redirect('atendimento_app:painel_consultorio')

        if senha.status not in ['aguardando_consultorio', 'chamado']:
            messages.error(request, 'Esta senha não pode ser cancelada.')
            return redirect('atendimento_app:painel_consultorio')

    else:
        return redirect('/admin/')

    senha.status = 'cancelado'
    senha.save()

    messages.success(request, f'Paciente {senha.nome_paciente} cancelado com sucesso.')

    if perfil.tipo == 'recepcionista':
        return redirect('atendimento_app:painel_recepcao')

    return redirect('atendimento_app:painel_consultorio')


@login_required
@require_POST
def chamar_recepcao(request, senha_id):
    try:
        if request.user.perfil.tipo != 'recepcionista':
            return redirect('atendimento_app:painel_consultorio')
    except Perfil.DoesNotExist:
        return redirect('/admin/')

    senha = get_object_or_404(Senha, id=senha_id)

    if senha.status != 'aguardando_recepcao':
        messages.error(request, 'Esta senha não pode ser chamada.')
        return redirect('atendimento_app:painel_recepcao')

    consultorio_id = request.POST.get('consultorio_id')
    consultorio = get_object_or_404(Consultorio, id=consultorio_id)

    senha.status = 'aguardando_consultorio'
    senha.chamado_recepcao = timezone.now()
    senha.consultorio = consultorio  # ← vincula o consultório
    senha.save()

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'consultorio_{consultorio.id}',
        {
            'type': 'senha_adicionada',
            'numero': senha.numero,
            'nome_paciente': senha.nome_paciente,
            'tipo_servico': senha.get_tipo_servico_display(),
            'prioridade': senha.get_prioridade_display(),
            'senha_id': senha.id,
            'horario': senha.chamado_recepcao.strftime('%H:%M'),
        }
    )
    
    messages.success(request, f'Paciente {senha.nome_paciente} direcionado para {consultorio.nome}!')
    return redirect('atendimento_app:painel_recepcao')

