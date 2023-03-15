from votacao.models import Questao, Opcao
from colorama import Fore
from colorama import Style
from django.db.models import Max
print(f'{Fore.LIGHTBLUE_EX}4.4 Processamento de Dados da BD{Style.RESET_ALL}')
print(f'{Fore.YELLOW}\na){Style.RESET_ALL}')
#Devolve todas a perguntas, todas as opções de resposta e o numero de votos por opção
votos_totais = 0
for question in Questao.objects.all():
    q_texto = question.questao_texto
    print(f'{Fore.LIGHTGREEN_EX}{q_texto}{Style.RESET_ALL}')
    for opcao in Questao.objects.get(questao_texto=q_texto).opcao_set.all():
        #soma todos os votos
        votos_totais += opcao.votos
        print(f'{Fore.GREEN}{opcao}: {Style.RESET_ALL}{opcao.votos}')
#imprime o total de votos na base de dados
print(f'\n\n{Fore.GREEN}Total votos na BD é: {Style.RESET_ALL}{votos_totais}')

print(f'\n{Fore.YELLOW}\nb)\nA pergunta com mais votos com opção mais votada:\b{Style.RESET_ALL}')
#Se quizessemos ir buscar a pergunta com mais votos , e imprimir qual a pergunta, e a opção:
questao = Questao.objects.annotate(max_votos=Max('opcao__votos')).order_by('-max_votos').values('questao_texto', 'opcao__opcao_texto').first()
print(f'{Fore.LIGHTGREEN_EX}{questao}{Style.RESET_ALL}')
print(f'\n{Fore.YELLOW}\nOpção mais votada por pergunta:\b{Style.RESET_ALL}')
#Mas queremos, a opção com mais votos de cada pergunta
for question in Questao.objects.all():
    max_opcao = question.opcao_set.order_by('-votos').first()
    if max_opcao:
        print(f'{Fore.LIGHTGREEN_EX}Questão{Style.RESET_ALL} {question.questao_texto}\n{Fore.GREEN}Opção:{Style.RESET_ALL}{max_opcao.opcao_texto} com {max_opcao.votos} votos')
    else:
        print(f'Não há Opções para a Questão {question.questao_texto}')
