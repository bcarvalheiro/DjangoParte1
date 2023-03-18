from django.utils import timezone

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from .models import Questao, Opcao


# Create your views here.

def index(request):
    latest_question_list = Questao.objects.order_by('-pub_data')
    #template = loader.get_template('votacao/templates/index.html')
    context= {'latest_question_list': latest_question_list}
    #output = ', '.join([q.questao_texto for q in latest_question_list])
    #return HttpResponse(template.render(context,request))
    return render(request, 'votacao/index.html', context)

def detalhe(request, questao_id):
    question = get_object_or_404(Questao, pk=questao_id)
    return render(request, 'votacao/detalhe.html', {'questao': question})

def resultados(request, questao_id):
    questao= get_object_or_404(Questao,pk=questao_id)
    return render(request, 'votacao/resultados.html', {'questao':questao})

def voto(request,questao_id):
    questao = get_object_or_404(Questao,pk=questao_id)
    try:
        opcao_selecionada= questao.opcao_set.get(pk=request.POST['opcao'])
    except (KeyError, Opcao.DoesNotExist):
        #Apresenta de novo form para vota
        return render(request, 'votacao/detalhe.html', {'questao' : questao, 'error_message': 'Não escolheu uma opção'})
    else:
        opcao_selecionada.votos += 1
        opcao_selecionada.save()
        #Retorne sempre o HttpResponseRedirect depois de tratar os dados Post de um form
        #pois isso impede os dados de serem tratados repetidamente se o utilizador voltar para
        #a mpágina web anterior
    return HttpResponseRedirect(reverse('votacao:resultados', args=(questao_id,)))
def criarquestao(request):
    return render(request, 'votacao/criarquestao.html')


def inserirquestao(request):
        Questao(questao_texto=request.POST['questao_texto'], pub_data=timezone.now()).save()
        return HttpResponseRedirect(reverse('votacao:index'))


def criaropcao(request, questao_id):
    questao = get_object_or_404(Questao,pk=questao_id)
    return render(request, 'votacao/criaropcao.html', {'questao': questao})


def inseriropcao(request, questao_id):
    question = Questao.objects.get(pk=questao_id)
    question.opcao_set.create(opcao_texto=request.POST['opcao_texto'], votos=0)
    return HttpResponseRedirect(reverse('votacao:index'))







