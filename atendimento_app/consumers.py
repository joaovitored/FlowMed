# atendimento_app/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PainelTVConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.channel_layer.group_add(
            'painel_tv',
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            'painel_tv',
            self.channel_name
        )

    async def senha_chamada(self, event):
        await self.send(text_data=json.dumps({
            'numero': event['numero'],
            'nome_paciente': event['nome_paciente'],
            'consultorio': event['consultorio'],
            'horario': event['horario'],
        }))


class PainelConsultorioConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # cada consultório tem seu próprio grupo
        self.consultorio_id = self.scope['url_route']['kwargs']['consultorio_id']
        self.grupo = f'consultorio_{self.consultorio_id}'
        await self.channel_layer.group_add(self.grupo, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.grupo, self.channel_name)

    async def senha_adicionada(self, event):
        await self.send(text_data=json.dumps({
            'tipo': 'nova_senha',
            'numero': event['numero'],
            'nome_paciente': event['nome_paciente'],
            'tipo_servico': event['tipo_servico'],
            'prioridade': event['prioridade'],
            'senha_id': event['senha_id'],
            'horario': event['horario'],
        }))