from flask import Flask, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
import requests
import os
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

load_dotenv()

app = Flask(__name__)

# Configurar a API key do Gemini
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("A variável de ambiente GOOGLE_API_KEY não está definida.")
genai.configure(api_key=GOOGLE_API_KEY)
modelo = genai.GenerativeModel("gemini-pro")

# Função para buscar os jogos do dia
def buscar_jogos():
    hoje = datetime.now(timezone(timedelta(hours=-3)))  # Usar o fuso horário de Brasília
    data_formatada = hoje.strftime("%Y-%m-%d")
    url = f"https://api.api-futebol.com.br/v1/campeonatos?data_inicio={data_formatada}&data_fim={data_formatada}"
    headers = {"Authorization": "Bearer live_1074c1cd7b14f4e1e24c790590cc2a"}  # Substitua YOUR_API_KEY pela sua chave da API Futebol

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Erro ao buscar jogos: {response.status_code}")
        return []

    campeonatos = response.json()['data']
    jogos_do_dia = []

    # Filtra os campeonatos de interesse
    campeonatos_brasileiros = [c for c in campeonatos if "Campeonato Brasileiro" in c['nome']]
    campeonatos_brasileiros = [c for c in campeonatos if "Campeonato Brasileiro Série B" in c['nome']]
    libertadores = [c for c in campeonatos if "Libertadores" in c['nome']]
    sulamericana = [c for c in campeonatos if "Sul-Americana" in c['nome']]
    copa_brasil = [c for c in campeonatos if "Copa do Brasil" in c['nome']]
    premier_league = [c for c in campeonatos if "Premier League" in c['nome']]

    campeonatos_filtrados = (
        campeonatos_brasileiros + libertadores + sulamericana + copa_brasil + premier_league
    )

    for campeonato in campeonatos_filtrados:
        url_campeonato = f"https://api.api-futebol.com.br/v1/campeonatos/{campeonato['id']}"
        response_campeonato = requests.get(url_campeonato, headers=headers)

        if response_campeonato.status_code == 200:
            dados_campeonato = response_campeonato.json()['data']
            fase_atual = dados_campeonato.get('fase_atual', None)

            if fase_atual:
                url_jogos = f"https://api.api-futebol.com.br/v1/fases/{fase_atual['id']}/jogos"
                response_jogos = requests.get(url_jogos, headers=headers)

                if response_jogos.status_code == 200:
                    jogos = response_jogos.json()['data']
                    for jogo in jogos:
                        if jogo['status'] != 'Finalizado' and jogo['status'] != 'Cancelado':
                            hora_str = jogo['horario_jogo']
                            try:
                                hora_jogo = datetime.strptime(hora_str, "%Y-%m-%d %H:%M:%S")
                                hora_local = hora_jogo.astimezone(timezone(timedelta(hours=-3)))
                                hora_formatada = hora_local.strftime("%Hh%M")
                            except ValueError:
                                hora_formatada = "Horário Indefinido"

                            jogo_info = {
                                "time1": jogo['time_mandante']['nome_popular'],
                                "time2": jogo['time_visitante']['nome_popular'],
                                "escudo1": jogo['time_mandante']['escudo'],
                                "escudo2": jogo['time_visitante']['escudo'],
                                "campeonato": campeonato['nome'],
                                "hora": hora_formatada,
                            }
                            jogos_do_dia.append(jogo_info)
        else:
            print(f"Erro ao buscar detalhes do campeonato {campeonato['nome']}: {response_campeonato.status_code}")

    return jogos_do_dia

def buscar_transmissao(jogo):
    prompt = f"Qual emissora transmite o jogo de futebol {jogo['time1']} x {jogo['time2']}?"
    response = modelo.generate_content(prompt, tools=[{"google_search": {}}])
    return response.text

@app.route('/jogos')
def listar_jogos():
    jogos = buscar_jogos()
    if not jogos:
        return jsonify({"error": "Não há jogos disponíveis para hoje."})

    resultados = []
    for jogo in jogos:
        try:
            transmissao = buscar_transmissao(jogo)
            # Tenta extrair o nome da emissora de forma mais robusta
            emissora_nome = ""
            if "transmitido" in transmissao.lower():
              emissora_nome = transmissao.lower().split("transmitido por")[-1].split('.')[0].strip()
            elif "passa em" in transmissao.lower():
                emissora_nome = transmissao.lower().split("passa em")[-1].split('.')[0].strip()
            elif "vai passar em" in transmissao.lower():
                emissora_nome = transmissao.lower().split("vai passar em")[-1].split('.')[0].strip()
            else:
              emissora_nome = transmissao

            emissora_nome = emissora_nome.title() # Capitaliza para ficar mais apresentável

            emissora_imagem_url = buscar_logo_emissora(emissora_nome) # Busca o logo

            resultados.append({
                "time1": jogo['time1'],
                "time2": jogo['time2'],
                "escudo1": jogo['escudo1'],
                "escudo2": jogo['escudo2'],
                "campeonato": jogo['campeonato'],
                "hora": jogo['hora'],
                "emissora": emissora_nome,
                "emissora_imagem": emissora_imagem_url, # Adiciona a URL da imagem
            })
        except Exception as e:
            print(f"Erro ao buscar transmissão do jogo {jogo['time1']} x {jogo['time2']}: {e}")
            resultados.append({
                "time1": jogo['time1'],
                "time2": jogo['time2'],
                "escudo1": jogo['escudo1'],
                "escudo2": jogo['escudo2'],
                "campeonato": jogo['campeonato'],
                "hora": jogo['hora'],
                "emissora": "Informação não disponível",
                "emissora_imagem": "",
            })

    return jsonify(resultados)

def buscar_logo_emissora(nome_emissora):
  """
  Busca a URL do logo de uma emissora de TV usando a API do Google Search.

  Args:
    nome_emissora: Nome da emissora (string).

  Returns:
    URL do logo da emissora (string) ou None se não encontrar.
  """
  try:
      nome_emissora_encoded = quote(nome_emissora)
      url = f"https://www.google.com/search?q={nome_emissora_encoded}+logo&tbm=isch"
      response = requests.get(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"})
      response.raise_for_status()  # Lança uma exceção para status de erro

      # Tenta encontrar a URL da imagem na resposta HTML
      # Esta é uma maneira simplificada e pode precisar de ajustes dependendo da estrutura do Google Search
      import re
      match = re.search(r"img.*?src=\"(https?://.*?)\"", response.text)
      if match:
          return match.group(1)
      else:
        return ""
  except Exception as e:
      print(f"Erro ao buscar logo da emissora {nome_emissora}: {e}")
      return ""


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)