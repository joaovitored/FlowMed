from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'atendimento_app'

urlpatterns = [
    # http://127.0.0
    # Esta rota agora controla a listagem, o filtro por ID e o Modal ao mesmo tempo!
    path('', views.index, name='index'),

]


