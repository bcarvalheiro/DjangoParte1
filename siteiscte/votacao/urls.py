from django.urls import include, path
from . import views
# O import apartir de . significa que importa views da mesma diretoria

# Quando invocado o url "" o django procura e executa a função index em views.py
app_name = 'votacao'
urlpatterns = [

    #ex: votacao&
    path("", views.index, name="index"),
    #ex: votacao/1
    path('<int:questao_id>', views.detalhe, name='detalhe'),
    #ex:votacao/1/resultados
    path('<int:questao_id>/resultados', views.resultados, name='resultados'),
    #ex:votacao/1/voto
    path('<int:questao_id>/voto', views.voto, name='voto'),
    path('criarquestao', views.criarquestao, name='criarquestao'),
    path('inserirquestao', views.inserirquestao, name='inserirquestao'),
    path('<int:questao_id>/criaropcao', views.criaropcao, name='criaropcao'),
    path('<int:questao_id>/inseriropcao', views.inseriropcao, name='inseriropcao'),
]

