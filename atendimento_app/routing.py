# atendimento_app/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/tv/$', consumers.PainelTVConsumer.as_asgi()),
    re_path(r'ws/consultorio/(?P<consultorio_id>\d+)/$', consumers.PainelConsultorioConsumer.as_asgi()),

]