from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Consultorio(models.Model):
    nome = models.CharField(max_length=50)
    profissional = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True)
    ativo = models.BooleanField(default=True)

    class Meta:
            verbose_name = 'Consultório'
            verbose_name_plural = 'Consultórios'
            ordering = ['nome']

    def __str__(self):
        return self.nome
    

class Perfil(models.Model):
    TIPO_CHOICES = [
        ('recepcionista', 'Recepcionista'),
        ('medico', 'Médico'),
    ]
    usuario = models.OneToOneField(User,on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    consultorio = models.ForeignKey(Consultorio,on_delete=models.SET_NULL,null=True,blank=True)

    def __str__(self):
        return f"{self.usuario.username} ({self.get_tipo_display()})"
     
    class Meta:
        verbose_name = 'Perfil'
        verbose_name_plural = 'Perfis'

     
class Senha(models.Model):

    TIPO_SERVICO_CHOICES = [
        ('consulta', 'Consulta'),
        ('exame', 'Exame'),
        ('retorno', 'Retorno'), 
    ]

    PRIORIDADE_CHOICES=[
        ('minima', 'Minima'),
        ('baixa', 'Baixa'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('maxima', 'Maxima')
    ]
    STATUS_CHOICES =[
        ('aguardando_recepcao', 'Aguardando Recepção'),
        ('aguardando_consultorio', 'Aguardando Consultório'),
        ('chamado', 'Chamado'),
        ('atendido', 'Atendido'),
        ('cancelado', 'Cancelado'),
    ]
    nome_paciente = models.CharField(max_length=100, unique=False)
    consultorio = models.ForeignKey(Consultorio, on_delete=models.SET_NULL, null=True, blank=True)

    numero = models.PositiveBigIntegerField(unique=True, editable=False)

    tipo_servico = models.CharField(max_length=20, choices=TIPO_SERVICO_CHOICES)
    prioridade = models.CharField(max_length=20, choices=PRIORIDADE_CHOICES, default='media')
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='aguardando_recepcao')

    criado_em = models.DateTimeField(auto_now_add=True)
    chamado_recepcao = models.DateTimeField(null=True,blank=True)
    chamado_consultorio = models.DateTimeField(null=True,blank=True)
    finalizado_em= models.DateTimeField(null=True, blank=True)


    class Meta:
        verbose_name = 'Senha'
        verbose_name_plural = 'Senhas'
        ordering = ['-prioridade', 'criado_em']

    def save(self, *args, **kwargs):
            if not self.numero:
                ultimo = Senha.objects.order_by('-numero').first()
                self.numero = (ultimo.numero + 1) if ultimo else 1
            super().save(*args, **kwargs)
        
    def __str__(self):
        return f"Senha {self.numero} ({self.get_tipo_servico_display()})"