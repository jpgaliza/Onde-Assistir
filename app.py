import os
import google.generativeai as genai
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
import traceback # Para logging detalhado de erros
from datetime import datetime # Para obter a data atual
import locale               # Para formatar a data em português

# Tenta configurar o locale para Português do Brasil para formatar a data
# Isso garante que o nome do mês e dia da semana saiam em português.
try:
    # Para Linux/macOS:
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')
except locale.Error:
    try:
        # Para Windows:
        locale.setlocale(locale.LC_TIME, 'Portuguese_Brazil')
    except locale.Error:
        print("Aviso: Não foi possível configurar o locale para pt_BR. A data pode não ser formatada em português.")
        # Se falhar, a data será formatada no padrão do sistema ou em inglês.

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

# Configuração da API Gemini com Google Search Grounding
gemini_model = None
gemini_initialization_error = None
model_name_for_log = 'gemini-1.5-flash' # Modelo com excelente suporte a ferramentas

try:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        gemini_initialization_error = "A variável de ambiente GOOGLE_API_KEY não foi encontrada no arquivo .env. Verifique o nome da variável e do arquivo."
    else:
        genai.configure(api_key=api_key)
        
        # Configurar o modelo Gemini com Google Search
        gemini_model = genai.GenerativeModel(
            model_name=model_name_for_log,
            tools='google_search_retrieval'  # Habilita Google Search
        )
        
        print(f"API Gemini configurada com sucesso usando o modelo: {model_name_for_log}")
        print("🔍 Google Search Grounding ATIVADO - Informações em tempo real habilitadas!")
except Exception as e:
    gemini_initialization_error = f"Falha ao configurar a API Gemini: {e}"

if gemini_initialization_error:
    print(f"ALERTA CRÍTICO: {gemini_initialization_error}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/buscar-jogos')
def buscar_jogos():
    if gemini_initialization_error or not gemini_model:
        print(f"Erro na rota /buscar-jogos: API Gemini não inicializada. Erro: {gemini_initialization_error}")
        return jsonify(error=f"Erro de configuração da API Gemini: {gemini_initialization_error}"), 500
    
    try:
        # Obter a data atual
        now = datetime.now()
        # Formatar a data para um formato legível em português
        # Ex: "sexta-feira, 23 de maio de 2025"
        try:
            current_date_formatted = now.strftime("%A, %d de %B de %Y")
        except UnicodeEncodeError: # Algumas configurações de locale em Windows podem dar erro com strftime e acentos
            print("Aviso: Erro de encoding ao formatar data com locale. Tentando formato alternativo.")
            current_date_formatted = now.strftime("%Y-%m-%d") # Formato ISO como fallback seguro
        except Exception as e_date: # Qualquer outra exceção na formatação
            print(f"Aviso: Falha ao formatar data com locale ({e_date}). Usando formato YYYY-MM-DD.")
            current_date_formatted = now.strftime("%Y-%m-%d")

        print(f"Data atual formatada para o prompt: {current_date_formatted}")        # Prompt otimizado para Google Search em tempo real
        prompt = (
            f"🔍 BUSQUE NO GOOGLE informações ATUALIZADAS sobre jogos de futebol para HOJE - {current_date_formatted} "
            f"(16 de junho de 2025, domingo - fuso horário de Brasília/BRT GMT-3).\n\n"
            
            "📊 **TERMOS DE BUSCA ESPECÍFICOS:**\n"
            "- 'jogos de futebol hoje 16 junho 2025'\n"
            "- 'futebol domingo transmissão TV Brasil'\n"
            "- 'onde assistir jogos hoje Globo SBT ESPN'\n"
            "- 'brasileirão libertadores jogos domingo'\n"
            "- 'futebol europeu transmissão Brasil hoje'\n\n"
            
            "🎯 **ENCONTRE ESPECIFICAMENTE:**\n"
            "1. ⚽ JOGOS CONFIRMADOS para 16/06/2025 (domingo)\n"
            "2. 🕐 HORÁRIOS EXATOS em BRT (GMT-3)\n"
            "3. 📺 CANAIS DE TV: Globo, SBT, Band, Record, ESPN, Fox Sports, SportTV\n"
            "4. 📱 STREAMING: Globoplay, Paramount+, Amazon Prime Video, Disney+, Apple TV+\n"
            "5. 🏆 CAMPEONATOS: Brasileirão, Copa do Brasil, Libertadores, Champions League, Premier League, La Liga\n\n"
            
            "� **FORMATO DA RESPOSTA:**\n"
            "Para cada jogo encontrado:\n"
            "🕐 **[HORÁRIO BRT]** - **[TIME A] x [TIME B]**\n"
            "🏆 **Campeonato:** [Nome completo]\n"
            "📺 **Onde assistir:** [TV/Streaming]\n"
            "📍 **Local:** [Estádio - Cidade]\n"
            "➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
            
            "⚠️ **INSTRUÇÕES CRÍTICAS:**\n"
            "- Use APENAS informações encontradas no Google Search\n"
            "- Confirme os dados em sites oficiais como GloboEsporte, ESPN, SportTV\n"
            "- Priorize jogos com times brasileiros\n"
            "- Se NÃO encontrar jogos hoje, seja claro: 'Não há jogos confirmados para hoje'\n"
            "- Inclua links das fontes consultadas\n\n"
            
            f"🔍 **BUSQUE AGORA** informações atualizadas para {current_date_formatted}!"
        )
        
        print(f"🔍 Enviando busca GOOGLE SEARCH para Gemini: {current_date_formatted}")
        
        response_gemini = gemini_model.generate_content(prompt)
        print("✅ Resposta recebida do Google Search via Gemini!")        # Tratamento para respostas bloqueadas ou vazias da Gemini API
        if not response_gemini.parts: # Verifica se há partes na resposta
            feedback = getattr(response_gemini, 'prompt_feedback', None)
            block_reason_message = "A API Gemini retornou uma resposta vazia ou sem conteúdo."
            if feedback and getattr(feedback, 'block_reason', None): # Verifica se foi bloqueado e qual a razão
                block_reason_message = f"Conteúdo bloqueado pela API Gemini. Razão: {feedback.block_reason}"
            
            print(f"Aviso API Gemini: {block_reason_message}")
            # Retorna a mensagem para o usuário
            return jsonify(jogos=f"Não foi possível obter os dados dos jogos: {block_reason_message}")

        game_info_text = response_gemini.text
        if not game_info_text or not game_info_text.strip(): # Verifica se o texto está vazio
            game_info_text = f"❌ Nenhuma informação de jogos encontrada para {current_date_formatted} através do Google Search."
        
        # Adiciona cabeçalho informativo
        header_info = f"🔍 **BUSCA REALIZADA VIA GOOGLE SEARCH**\n"
        header_info += f"📅 **Data consultada:** {current_date_formatted}\n"
        header_info += f"🕐 **Horário da consulta:** {datetime.now().strftime('%H:%M:%S')} BRT\n"
        header_info += f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n\n"
        
        # Adiciona rodapé informativo
        footer_info = "\n\n➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n"
        footer_info += "� **Informações obtidas via Google Search em tempo real**\n"
        footer_info += "⚠️ **IMPORTANTE:** Verifique horários e canais nos sites oficiais antes dos jogos\n"
        footer_info += "📱 **Sugestão:** Consulte também ESPN, GloboEsporte, SportTV para confirmação"
        
        final_response = header_info + game_info_text + footer_info
        
        print("🎯 Dados dos jogos formatados com Google Search Grounding.")
        return jsonify(jogos=final_response)

    except Exception as e:
        print(f"Erro crítico na rota /buscar-jogos: {type(e).__name__} - {e}")
        print(traceback.format_exc()) # Imprime o stack trace completo no console do servidor
        return jsonify(error=f"Erro interno ao processar sua solicitação. Verifique os logs do servidor para mais detalhes."), 500

if __name__ == '__main__':
    # Alerta inicial se a chave não estiver configurada ou se houve erro na inicialização do Gemini
    if not os.getenv("GOOGLE_API_KEY") or gemini_initialization_error: # Verifica ambas as condições
        print("---------------------------------------------------------")
        print("ALERTA IMPORTANTE:")
        # Mostra o erro de inicialização se houver, senão a mensagem de chave API
        print(gemini_initialization_error if gemini_initialization_error else "A chave API do Google (GOOGLE_API_KEY) não está configurada no arquivo .env.")
        print("A aplicação pode não funcionar corretamente.")
        print("---------------------------------------------------------")
    else:
        print("---------------------------------------------------------")
        print("🚀 APLICAÇÃO INICIALIZADA COM SUCESSO!")
        print("✅ Google Gemini API configurada")
        print("🔍 Google Search Grounding ATIVADO")
        print("📺 Pronto para buscar jogos EM TEMPO REAL!")
        print("---------------------------------------------------------")
    
    # Executa o servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000)