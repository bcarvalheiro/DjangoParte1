from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, AnonymousUser
from .models import Questao, Opcao, Aluno


# Create your views here.

def index(request):
    latest_question_list = Questao.objects.order_by('-pub_data')
    user = request.user
    if user.is_authenticated:
        try:
            aluno = user.aluno
            context = {'latest_question_list': latest_question_list, 'aluno': aluno}
        except Aluno.DoesNotExist:
            context = {'latest_question_list': latest_question_list}
    context = {'latest_question_list': latest_question_list}
    return render(request, 'votacao/index.html', context)


def detalhe(request, questao_id):
    question = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': question})


def resultados(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/resultados.html', {'questao': questao})


def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)

    if not request.user.is_authenticated:
        error_message = 'Apenas utilizadores logados podem votar'
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': error_message})

    try:
        opcao_selecionada = questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        # Apresenta de novo form para vota
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': 'Não escolheu uma opção'})
    else:
        if not request.user.is_superuser:
            aluno = get_object_or_404(Aluno, user_id=request.user)
            limit_votos = aluno.grupo_trab + 10
            if aluno.votos + 1 > limit_votos:
                error_message= 'Esgotou o limite de votos de ' + str(limit_votos)
                return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': error_message})

            aluno.votos += 1
            aluno.save()

        opcao_selecionada.votos += 1
        opcao_selecionada.save()
        # Retorne sempre o HttpResponseRedirect depois de tratar os dados Post de um form
        # pois isso impede os dados de serem tratados repetidamente se o utilizador voltar para
        # a mpágina web anterior
        return HttpResponseRedirect(reverse('votacao:resultados', args=(questao_id,)))


def criarquestao(request):
    if request.method == 'POST':
        userid = request.user.username
        userPage = User.objects.get(username=userid)
        if userPage.is_superuser:
            if not request.POST['questao_texto']:
                return render(request, 'votacao/criarquestao.html',
                              {'error_message': 'Preencha o campo antes de submeter.'})
            else:
                Questao(questao_texto=request.POST['questao_texto'], pub_data=timezone.now()).save()
                return HttpResponseRedirect(reverse('votacao:index'))
        else:
            return render(request, 'votacao/criarquestao.html',
                          {'error_message': 'Apenas administradores podem criar questões.'})
    else:
        return render(request, 'votacao/criarquestao.html')


def eliminar(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    if not request.user.is_superuser:
        error_message = 'Apenas administradores podem eliminar questões'
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': error_message})

    questao.delete()
    return HttpResponseRedirect(reverse('votacao:index'))


def criaropcao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)

    if not request.user.is_superuser:
        error_message = 'Apenas administradores podem acrescentar opções'
        return render(request, 'votacao/criaropcao.html', {'questao': questao, 'error_message': error_message})

    if request.method == 'POST':
        opcao_texto = request.POST.get('opcao_texto', '').strip()
        if not opcao_texto:
            error_message = 'Preencha o campo antes de submeter.'
            return render(request, 'votacao/criaropcao.html', {'questao': questao, 'error_message': error_message})

        questao.opcao_set.create(opcao_texto=opcao_texto, votos=0)
        return HttpResponseRedirect(reverse('votacao:index'))
    return render(request, 'votacao/criaropcao.html', {'questao': questao})


def eliminaropcao(request, questao_id, opcao_id):
    opcao = get_object_or_404(Opcao, pk=opcao_id)

    if not request.user.is_superuser:
        error_message = 'Apenas administradores podem eliminar opções'
        return render(request, 'votacao/detalhe.html', {'questao': opcao.questao, 'error_message': error_message})

    opcao.delete()
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': questao})


def login(request):
    latest_question_list = Questao.objects.order_by('-pub_data')
    if request.method == 'POST':
        try:
            password = request.POST['password']
            userid = request.POST['username']
            user = authenticate(username=userid, password=password)
            if user is not None:
                userPage = User.objects.get(username=userid)
                context = {'latest_question_list': latest_question_list, 'userPage': userPage}
                auth_login(request, user)
                request.session['userid'] = user.username
                return render(request, 'votacao/index.html', context)
            else:
                return render(request, 'votacao/login.html')
        except KeyError:
            return render(request, 'votacao/login.html')
    else:
        return render(request, 'votacao/login.html')


def dashboard(request):
    userid = request.user.username
    userPage = User.objects.get(username=userid)
    return render(request, 'votacao/dashboard.html', {'userPage': userPage})


def novouser(request):
    if request.method == 'POST':
        password = request.POST['password']
        username = request.POST['username']
        curso = request.POST['curso']
        nome_completo = request.POST['nome_completo']
        grupo_trab = request.POST['grupo_trab']
        email = request.POST['email']
        user = User.objects.create_user(username, email, password)
        aluno = Aluno.objects.create(user=user, nome_completo=nome_completo, grupo_trab=grupo_trab, curso=curso,
                                     votos=0)
        aluno.save()
        if aluno.pk is not None:
            return HttpResponseRedirect(reverse('votacao:index'))
    else:
        return render(request, 'votacao/criarutilizador.html')


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('votacao:index'))
