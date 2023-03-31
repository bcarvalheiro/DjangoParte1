from django.urls import include, path
from . import views
from django.conf import settings
from django.conf.urls.static import static
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
    path('<int:questao_id>/criaropcao', views.criaropcao, name='criaropcao'),
    path('login', views.login, name='login'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('novouser', views.novouser, name='novouser'),
    path('logout', views.logout, name='logout'),
    path('<int:questao_id>/eliminar', views.eliminar, name='eliminar'),
    path('<int:questao_id>/eliminaropcao/<int:opcao_id>', views.eliminaropcao, name='eliminaropcao'),
    path('fazer_upload', views.fazer_upload, name='fazer_upload')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

