// static/script.js (confirmar se o seu está assim ou similar)
document.getElementById('atualizarJogos').addEventListener('click', function() {
    const resultadosDiv = document.getElementById('resultados');
    resultadosDiv.innerHTML = 'Buscando informações dos jogos... Por favor, aguarde.'; // Feedback para o usuário

    fetch('/buscar-jogos')
        .then(response => {
            if (!response.ok) {
                // Se a resposta não for ok (ex: status 500, 404),
                // tenta ler o corpo da resposta como JSON para pegar a mensagem de erro.
                return response.json().then(errData => {
                    // errData.error é o que definimos no jsonify(error=...) do Flask
                    throw new Error(errData.error || `Erro do servidor: ${response.status}`);
                }).catch(jsonParseError => {
                    // Se não conseguir parsear como JSON (ex: HTML de erro inesperado),
                    // retorna o status da resposta.
                    throw new Error(`Erro HTTP: ${response.status}. A resposta não foi um JSON válido.`);
                });
            }
            return response.json(); // Prossegue se a resposta for OK (2xx)
        })
        .then(data => {
            if (data.error) {
                // Se a API retornou um JSON com uma chave 'error' (definido no nosso backend)
                resultadosDiv.innerHTML = `<p style="color: red;">${data.error}</p>`;
            } else if (data.jogos) {
                // Formata o texto para preservar quebras de linha e espaços
                resultadosDiv.innerHTML = `<pre style="white-space: pre-wrap; word-wrap: break-word;">${data.jogos}</pre>`;
            } else {
                resultadosDiv.innerHTML = 'Nenhuma informação de jogo encontrada ou resposta inesperada.';
            }
        })
        .catch(error => {
            console.error('Erro detalhado ao buscar jogos:', error);
            resultadosDiv.innerHTML = `<p style="color: red;">Falha ao buscar jogos: ${error.message}</p><p>Verifique o console do navegador (F12) e o terminal do servidor para mais detalhes.</p>`;
        });
});