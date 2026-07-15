const body = document.body;
const consultorioId = body.dataset.consultorioId;
const csrfToken = body.dataset.csrf;

const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
const ws = new WebSocket(wsProtocol + window.location.host + '/ws/consultorio/' + consultorioId + '/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);

    if (data.tipo === 'nova_senha') {
        const tbody = document.querySelector('tbody');

        const empty = tbody.querySelector('.empty');
        if (empty) empty.parentElement.remove();

        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td><strong>${data.numero}</strong></td>
            <td>${data.nome_paciente}</td>
            <td>${data.tipo_servico}</td>
            <td><span class="badge">${data.prioridade}</span></td>
            <td>${data.horario}</td>
            <td>
                <form method="POST" action="/chamar-consultorio/${data.senha_id}/">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                    <button type="submit" class="btn-chamar">Chamar</button>
                </form>
            </td>
        `;
        tbody.appendChild(tr);
    }
};

ws.onclose = function() {
    setTimeout(() => location.reload(), 3000);
};