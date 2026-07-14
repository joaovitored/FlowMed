from django.urls import path
from . import views

app_name = 'atendimento_app'

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('recepcao/', views.painel_recepcao, name='painel_recepcao'),
    path('consultorio/', views.painel_consultorio, name='painel_consultorio'),
    path('cadastrar-senha/', views.cadastrar_senha, name='cadastrar_senha'),
    path('chamar-recepcao/<int:senha_id>/', views.chamar_recepcao, name='chamar_recepcao'),
    path('chamar-consultorio/<int:senha_id>/', views.chamar_consultorio, name='chamar_consultorio'),
    path('finalizar/<int:senha_id>/', views.finalizar_atendimento, name='finalizar_atendimento'),
    path('cancelar/<int:senha_id>/', views.cancelar_senha, name='cancelar_senha'),
    path('historico/', views.historico, name='historico'),
    path('tv/', views.painel_tv, name='painel_tv'),
]