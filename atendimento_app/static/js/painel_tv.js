// relógio
function atualizarHora() {
    const agora = new Date();
    const horas = String(agora.getHours()).padStart(2, '0');
    const minutos = String(agora.getMinutes()).padStart(2, '0');
    document.getElementById('hora').textContent = `${horas}:${minutos}`;
}
atualizarHora();
setInterval(atualizarHora, 1000);

// WebSocket
const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(wsProtocol + window.location.host + '/ws/tv/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    document.getElementById('numero').textContent = data.numero;
    document.getElementById('nome').textContent = data.nome_paciente;
    document.getElementById('consultorio').textContent = data.consultorio;

    const lista = document.getElementById('historico-lista');
    const item = document.createElement('div');
    item.className = 'historico-item';
    item.innerHTML = `
        <div class="num">${data.numero}</div>
        <div class="info">
            <small>${data.horario}</small>
            <strong>${data.nome_paciente}</strong>
            <small>${data.consultorio}</small>
        </div>
    `;
    lista.insertBefore(item, lista.firstChild);

    while (lista.children.length > 4) {
        lista.removeChild(lista.lastChild);
    }

    const fala = new SpeechSynthesisUtterance(
        `Senha ${data.numero}, ${data.nome_paciente}, dirija-se ao ${data.consultorio}`
    );
    fala.lang = 'pt-BR';
    fala.rate = 0.9;
    window.speechSynthesis.speak(fala);
};

ws.onclose = function() {
    setTimeout(() => location.reload(), 3000);
};