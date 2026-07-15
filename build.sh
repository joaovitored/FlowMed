#!/usr/bin/env bash
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py shell -c "
from django.contrib.auth.models import User
from atendimento_app.models import Perfil, Consultorio
import os

# Cria superusuário
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@flowmed.com', os.environ.get('ADMIN_PASSWORD'))
    print('Superusuário criado')

# Cria consultório
if not Consultorio.objects.filter(nome='Consultório 1').exists():
    c = Consultorio.objects.create(nome='Consultório 1', ativo=True)

# Cria recepcionista
if not User.objects.filter(username='recepcao').exists():
    u = User.objects.create_user('recepcao', password=os.environ.get('RECEPCAO_PASSWORD'))
    Perfil.objects.create(usuario=u, tipo='recepcionista')

# Cria médico
if not User.objects.filter(username='medico').exists():
    u = User.objects.create_user('medico', password=os.environ.get('MEDICO_PASSWORD'))
    c = Consultorio.objects.get(nome='Consultório 1')
    Perfil.objects.create(usuario=u, tipo='medico', consultorio=c)
"