import json
import requests
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

app = Flask(__name__)

class AgenteInformacoesBasicas:
    def __init__(self):
        self.serp_api_key = os.getenv("SERPAPI_KEY")  # Carrega a chave da SerpAPI do .env
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def buscar_no_google(self, query):
        """Busca informações no Google usando SerpAPI."""
        if not query:
            return {"erro": "Consulta não fornecida para busca no Google"}

        url = "https://serpapi.com/search"
        params = {
            "q": f"{query} empresa",
            "api_key": self.serp_api_key,
            "gl": "br",  # Google Brasil
            "hl": "pt"   # Idioma português
        }
        try:
            response = requests.get(url, params=params, timeout=20)
            data = response.json()

            if "error" in data:
                return {"erro": f"Erro da SerpAPI: {data['error']}"}
            
            resultados = data.get("organic_results", [])
            if not resultados:
                return {"erro": "Nenhum resultado encontrado no Google. Pode ser um bloqueio da SerpAPI."}
            
            return {"google_results": resultados}
        except requests.exceptions.RequestException as e:
            return {"erro": f"Falha na requisição ao Google: {str(e)}"}
        except json.JSONDecodeError:
            return {"erro": "Erro ao decodificar JSON da SerpAPI"}

    def buscar_cnpj(self, cnpj):
        """Consulta CNPJ na API ReceitaWS."""
        if not cnpj:
            return {"erro": "CNPJ não fornecido"}
        
        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            data = response.json()

            if "status" in data and data["status"] == "ERROR":
                return {"erro": f"Erro na consulta de CNPJ: {data.get('message', 'Motivo desconhecido')}"}

            if not data:
                return {"erro": "A API ReceitaWS retornou uma resposta vazia."}

            return data
        except requests.exceptions.RequestException as e:
            return {"erro": f"Erro na consulta de CNPJ: {str(e)}"}
        except json.JSONDecodeError:
            return {"erro": "Erro ao decodificar JSON da ReceitaWS"}

    def buscar_informacoes(self, nome=None, cnpj=None):
        """Consolida informações básicas para os parâmetros fornecidos."""
        informacoes = {}

        if nome:
            dados_google = self.buscar_no_google(nome)
            informacoes["google"] = dados_google

        if cnpj:
            dados_cnpj = self.buscar_cnpj(cnpj)
            informacoes["cnpj"] = dados_cnpj

            nome_empresa = dados_cnpj.get("nome") or dados_cnpj.get("razao_social")
            if not nome and nome_empresa:
                informacoes["google"] = self.buscar_no_google(nome_empresa)

        return informacoes

@app.route('/buscar', methods=['GET'])
def buscar():
    nome = request.args.get('nome')
    cnpj = request.args.get('cnpj')

    if not nome and not cnpj:
        return jsonify({"erro": "É necessário fornecer pelo menos um dos parâmetros: nome ou CNPJ."}), 400

    agente = AgenteInformacoesBasicas()
    resultado = agente.buscar_informacoes(nome, cnpj)

    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
