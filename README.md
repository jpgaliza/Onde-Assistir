# Onde Assistir?

## Descrição do Projeto

O "Onde Assistir?" é um site que fornece informações sobre onde assistir a jogos de futebol ao vivo. Ele busca dados de jogos de uma API externa e utiliza o Google Search para encontrar informações sobre a transmissão de cada partida. O site foi desenvolvido para facilitar o acesso à informação sobre onde assistir aos jogos de futebol de forma rápida e prática.

## Funcionalidades

- **Informações sobre Jogos:** O site exibe informações sobre os jogos de futebol do dia, incluindo horário, times e campeonato.
- **Transmissão ao Vivo:** Utiliza o Google Search para buscar e exibir em qual(is) emissora(s) cada jogo será transmitido.
- **Visualização Amigável:** Apresenta os jogos em um layout organizado, com escudos dos times e logos das emissoras.
- **Filtro de Campeonatos:** Exibe jogos dos seguintes campeonatos:
  - Campeonato Brasileiro
  - Copa Libertadores da América
  - Copa Sul-Americana
  - Copa do Brasil
  - Premier League

## Como Instalar e Executar Localmente

Siga estas instruções para instalar e executar o site no seu computador:

### Pré-requisitos

- **Python 3.x:** Certifique-se de ter o Python instalado. Você pode baixá-lo em https://www.python.org/downloads/.
- **Pip:** O gestor de pacotes do Python. Normalmente, o Pip já vem instalado com o Python.
- **Git:** (Opcional, mas recomendado) Para clonar o repositório do projeto. Você pode baixá-lo em https://git-scm.com/downloads.
- **Chave da API do API Futebol:** É necessário obter uma chave de API do site APIFutebol para buscar os dados dos jogos.
- **Chave da API do Google Gemini:** É necessário obter uma chave da API do Google Cloud para utilizar o Gemini.

### Passos

1. **Clonar o repositório (opcional):**
   - Abra o terminal ou prompt de comando.
   - Navegue até o diretório onde deseja salvar o projeto: `cd /caminho/para/o/diretorio`
   - Clone o repositório do GitHub: `git clone <URL do repositório>`

2. **Criar e ativar um ambiente virtual (recomendado):**
   - No terminal, navegue até o diretório do projeto: `cd onde_passa_o_jogo`
   - Crie um ambiente virtual: `python -m venv venv`
   - Ative o ambiente virtual:
     - No Linux/macOS: `source venv/bin/activate`
     - No Windows: `venv\Scripts\activate`

3. **Instalar as dependências do Python:**
   - Com o ambiente virtual ativado, instale as bibliotecas necessárias: `pip install Flask requests google-genai`

4. **Configurar as variáveis de ambiente:**
   - Defina as variáveis de ambiente para as chaves das APIs:
     - `GOOGLE_API_KEY`: Sua chave da API do Google Gemini.
     - `API_FUTEBOL_KEY`: Sua chave da API do API Futebol.
   - Você pode definir essas variáveis no seu sistema operacional ou diretamente no terminal antes de executar o aplicativo:
     - No Linux/macOS: 
       ```
       export GOOGLE_API_KEY="sua_chave_gemini"
       export API_FUTEBOL_KEY="sua_chave_api_futebol"
       ```
     - No Windows (Prompt de Comando): 
       ```
       set GOOGLE_API_KEY="sua_chave_gemini"
       set API_FUTEBOL_KEY="sua_chave_api_futebol"
       ```
     - No Windows (PowerShell): 
       ```
       $env:GOOGLE_API_KEY = "sua_chave_gemini"
       $env:API_FUTEBOL_KEY = "sua_chave_api_futebol"
       ```

5. **Executar o aplicativo:**
   - No terminal, com o ambiente virtual ativado e no diretório do projeto, execute o aplicativo Flask: `python app.py`

6. **Abrir o site no navegador:**
   - Abra o seu navegador e acesse o endereço: `http://127.0.0.1:5000/`
   - Clique no botão "Atualizar Jogos" para ver as informações.