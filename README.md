# 🏥 FlowMed — Sistema de Gestão de Filas para Clínicas

Sistema web de gestão de filas de atendimento desenvolvido em Django, com atualização em tempo real via WebSockets e anúncio de chamadas por voz automático no navegador.

> Projeto desenvolvido para resolver um problema real: clínicas populares e UBSs que ainda dependem de senha de papel e atendente gritando número — sem organização, sem transparência e sem respeito à fila de prioridade.

---

## 📋 Funcionalidades

- **Dois painéis separados por perfil**: recepcionista e médico acessam interfaces diferentes
- **Cadastro de senhas**: recepcionista define nome, tipo de serviço e prioridade do paciente
- **Fila com prioridade**: pacientes prioritários (idosos, gestantes, PCD) são atendidos antes
- **Duas etapas de chamada**: recepção direciona o paciente ao consultório correto, médico chama para atendimento
- **Tela de TV em tempo real**: atualiza automaticamente via WebSocket sem precisar recarregar a página
- **Anúncio por voz**: Web Speech API anuncia a chamada automaticamente ("Senha 042, João Silva, dirija-se ao Consultório 3")
- **Painel do consultório em tempo real**: médico vê novas senhas aparecerem sem F5
- **Histórico de atendimentos**: com filtro por data e separação por perfil
- **Número de senha automático**: gerado via `save()` do model, resetando todo dia
- **Autenticação por perfil**: login redireciona automaticamente pro painel certo

---

## 🛠️ Stack

| Tecnologia | Uso |
|---|---|
| Python + Django | Back-end e lógica de negócio |
| Django Channels | Suporte a WebSockets |
| Daphne | Servidor ASGI |
| InMemoryChannelLayer | Channel layer (sem Redis) |
| SQLite | Banco de dados |
| HTML + CSS + JavaScript | Front-end |
| Web Speech API | Anúncio por voz no navegador |

---

## 🏗️ Arquitetura

```
atendimento/              ← configurações do projeto
│   ├── settings.py
│   ├── urls.py
│   └── asgi.py           ← configuração do Channels

atendimento_app/          ← app principal
│   ├── models.py         ← Consultorio, Perfil, Senha
│   ├── views.py          ← todas as views
│   ├── urls.py           ← rotas HTTP
│   ├── consumers.py      ← consumers WebSocket (TV + Consultório)
│   ├── routing.py        ← rotas WebSocket
│   └── admin.py

templates/                ← telas do sistema
│   ├── login.html
│   ├── painel_recepcao.html
│   ├── painel_consultorio.html
│   ├── historico.html
│   └── painel_tv.html

static/
│   ├── css/              ← estilos de cada tela
│   └── js/
│       ├── painel_tv.js          ← WebSocket + voz da TV
│       └── painel_consultorio.js ← WebSocket do consultório
```

### Fluxo de atendimento

```
Recepcionista cadastra senha
        ↓
Paciente aguarda na fila (aguardando_recepcao)
        ↓
Recepcionista chama e direciona ao consultório
        ↓
Paciente aguarda ser chamado (aguardando_consultorio)
        ↓
Médico chama → TV atualiza em tempo real + anuncia por voz (chamado)
        ↓
Médico finaliza atendimento (atendido) → vai pro histórico
```

### Como o tempo real funciona

```
Médico clica "Chamar"
        ↓
View salva no banco + dispara group_send via Channels
        ↓
InMemoryChannelLayer distribui para todos os consumers conectados
        ↓
JavaScript na TV recebe via WebSocket → atualiza tela + fala por voz
```

---

## 🚀 Como rodar localmente

### Pré-requisitos

- Python 3.10+
- pip

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/joaovitored/FlowMed
cd FlowMed

# 2. Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Rode as migrations
python manage.py migrate

# 5. Crie o superusuário
python manage.py createsuperuser

# 6. Rode o servidor
python manage.py runserver
```

### Configuração inicial (pelo Admin)

Acesse `http://127.0.0.1:8000/admin/` e siga essa ordem:

1. **Consultórios** → cadastre os consultórios (ex: "Consultório 1")
2. **Usuários** → crie os usuários (recepcionista e médico)
3. **Perfis** → vincule cada usuário ao seu tipo e consultório (se médico)

### URLs do sistema

| URL | Acesso |
|---|---|
| `/` | Página inicial |
| `/login/` | Login |
| `/recepcao/` | Painel da recepcionista |
| `/consultorio/` | Painel do médico |
| `/historico/` | Histórico de atendimentos |
| `/tv/` | Tela pública de chamadas (sem login) |
| `/admin/` | Django Admin |

---

## 📦 Dependências

```
Django
channels
daphne
```

> Sem Redis, sem Docker, sem framework JS — só Django e suas extensões.

---

## 💡 Decisões técnicas

- **Máquina de estados**: o ciclo de vida da senha tem 5 etapas (`aguardando_recepcao → aguardando_consultorio → chamado → atendido → cancelado`), modeladas como choices no Django — isso força pensar nas transições de estado antes de escrever qualquer view
- **Número gerado via `save()`**: o método `save()` do model gera o número automaticamente e reseta todo dia, sem precisar de lógica na view
- **InMemoryChannelLayer**: substitui o Redis pra simplificar o setup — ideal pra projetos com baixo tráfego e sem necessidade de múltiplos workers
- **Web Speech API**: síntese de voz nativa do navegador, sem custo e sem API externa
- **Dois WebSocket consumers**: um pra TV (`painel_tv`) e um por consultório (`consultorio_{id}`) — cada médico recebe só as senhas do seu consultório

---

## 🔮 Próximos passos

- [ ] Métricas de atendimento no histórico (tempo médio de espera, pico de atendimento)
- [ ] Estimativa de tempo de espera pra cada paciente na fila
- [ ] Suporte a múltiplas filas por especialidade
- [ ] Deploy com Redis gerenciado e múltiplos workers
- [ ] Testes automatizados

---

## 👨‍💻 Autor

**João Vitor** — Estudante de Análise e Desenvolvimento de Sistemas

[![GitHub](https://img.shields.io/badge/GitHub-joaovitored-black?logo=github)](https://github.com/joaovitored)
