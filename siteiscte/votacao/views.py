from django.utils import timezone
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User, AnonymousUser
from .models import Questao, Opcao, Aluno
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status, request
from .serializers import *
from .models import Questao, Opcao



def check_superuser(user):
    return user.is_superuser


@login_required
def index(request):
    latest_question_list = Questao.objects.order_by('-pub_data')
    user = request.user

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


# TO-DO: Tratar deste request.user.is_superuser para ser user_passes_test
@login_required()
def voto(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)

    try:
        opcao_selecionada = questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': 'Não escolheu uma opção'})
    else:
        if not request.user.is_superuser:
            aluno = get_object_or_404(Aluno, user_id=request.user)
            limit_votos = aluno.grupo_trab + 10
            if aluno.votos + 1 > limit_votos:
                error_message = 'Esgotou o limite de votos de ' + str(limit_votos)
                return render(request, 'votacao/detalhe.html', {'questao': questao, 'error_message': error_message})
            aluno.votos += 1
            aluno.save()

        opcao_selecionada.votos += 1
        opcao_selecionada.save()
        return HttpResponseRedirect(reverse('votacao:resultados', args=(questao_id,)))


@user_passes_test(check_superuser)
def criarquestao(request):
    if request.method == 'POST':

        if not request.POST['questao_texto']:
            return render(request, 'votacao/criarquestao.html',
                          {'error_message': 'Preencha o campo antes de submeter.'})
        else:
            Questao(questao_texto=request.POST['questao_texto'], pub_data=timezone.now()).save()
            return HttpResponseRedirect(reverse('votacao:index'))
    else:
        return render(request, 'votacao/criarquestao.html')


@user_passes_test(check_superuser)
def eliminar(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    questao.delete()
    return HttpResponseRedirect(reverse('votacao:index'))


@user_passes_test(check_superuser)
def criaropcao(request, questao_id):
    questao = get_object_or_404(Questao, pk=questao_id)
    if request.method == 'POST':
        opcao_texto = request.POST.get('opcao_texto', '').strip()
        if not opcao_texto:
            error_message = 'Preencha o campo antes de submeter.'
            return render(request, 'votacao/criaropcao.html', {'questao': questao, 'error_message': error_message})

        questao.opcao_set.create(opcao_texto=opcao_texto, votos=0)
        return render(request, 'votacao/detalhe.html', {'questao': questao})
    return render(request, 'votacao/criaropcao.html', {'questao': questao})


@user_passes_test(check_superuser)
def eliminaropcao(request, questao_id, opcao_id):
    opcao = get_object_or_404(Opcao, pk=opcao_id)
    opcao.delete()
    questao = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': questao})


def login(request):
    latest_question_list = Questao.objects.order_by('-pub_data')
    header(request)
    if request.method == 'POST':
        try:
            password = request.POST['password']
            userid = request.POST['username']
            user = authenticate(username=userid, password=password)
            if user is not None:
                context = {'latest_question_list': latest_question_list}
                auth_login(request, user)
                request.session['userid'] = user.username
                return render(request, 'votacao/index.html', context)
            else:
                return render(request, 'votacao/login.html')
        except KeyError:
            return render(request, 'votacao/login.html')
    else:
        return render(request, 'votacao/login.html')


@login_required()
def dashboard(request):
    userid = request.user.username
    userPage = User.objects.get(username=userid)

    return render(request, 'votacao/dashboard.html', {'userPage': userPage})


def header(request):
    userid = request.user.username
    print("Header")
    if userid:
        print("userPage")
        userPage = User.objects.get(username=userid)
        avatar = (userPage.aluno.avatar)
    else:
        avatar = ''
    return render(request, 'votacao/header.html', {'avatar': avatar})


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

        if 'avatar' in request.FILES:
            avatar = request.FILES['avatar']
            fs = FileSystemStorage()
            filename = fs.save(avatar.name, avatar)
            uploaded_file_url = fs.url(filename)
            # had to remove first '/' because of linux
            aluno.avatar = uploaded_file_url[1:]
            aluno.save()
        else:
            default_image = 'votacao/images/person_empty_holder.png'
            fs = FileSystemStorage()
            uploaded_file_url = fs.url(default_image)
            # had to remove first '/' because of linux
            aluno.avatar = uploaded_file_url
            aluno.save()
        if aluno.pk is not None:
            return HttpResponseRedirect(reverse('votacao:index'))
    else:
        return render(request, 'votacao/criarutilizador.html')


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('votacao:index'))


def fazer_upload(request):
    if request.method == 'POST' and request.FILES.get('myfile'):
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = fs.url(filename)
        return render(request, 'votacao/fazer_upload.html', {'uploaded_file_url': uploaded_file_url})
    return render(request, 'votacao/fazer_upload.html')


@api_view(['GET', 'POST'])
def questoes_lista(request):
    if request.method == 'GET':
        questoes = Questao.objects.all()
        serializerQ = QuestaoSerializer(questoes, context={'request': request}, many=True)
        return Response(serializerQ.data)
    elif request.method == 'POST':
        serializer = QuestaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def questoes_edita(request, pk):
    try:
        questao = Questao.objects.get(pk=pk)
    except Questao.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'PUT':
        serializer = QuestaoSerializer(questao, data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        questao.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
def opcoes_lista(request):
    if request.method == 'GET':
        opcoes = Opcao.objects.all()
        serializerO = OpcaoSerializer(opcoes, context={'request': request}, many=True)
        return Response(serializerO.data)
    elif request.method == 'POST':
        serializer = OpcaoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'DELETE'])
def opcoes_edita(request, pk):
    try:
        opcao = Opcao.objects.get(pk=pk)
    except Opcao.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'PUT':
        serializer = OpcaoSerializer(opcao, data=request.data, context={'request': request})
        if serializer.is_valid():
            opcao.votos = opcao.votos + 1
            opcao.save()
            # serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        opcao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
