import json
import requests
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

REPORT_SERVICE_URL = "http://report_info:5001/gerar_relatorio"

class AgenteInformacoesBasicas:
    def __init__(self):
        self.serp_api_key = os.getenv("SERPAPI_KEY")
        self.headers = {"User-Agent": "Mozilla/5.0"}

    def buscar_no_google(self, query):
        if not query:
            return {"erro": "Consulta não fornecida"}
        
        url = "https://serpapi.com/search"
        params = {"q": f"{query} empresa", "api_key": self.serp_api_key}

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            return {"google_results": data.get("organic_results", [])}
        except Exception as e:
            return {"erro": f"Erro no Google: {str(e)}"}

    def buscar_cnpj(self, cnpj):
        if not cnpj:
            return {"erro": "CNPJ não fornecido"}

        url = f"https://www.receitaws.com.br/v1/cnpj/{cnpj}"
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            return response.json()
        except Exception as e:
            return {"erro": f"Erro na consulta de CNPJ: {str(e)}"}

    def buscar_informacoes(self, nome=None, cnpj=None):
        informacoes = {}

        if nome:
            informacoes["google"] = self.buscar_no_google(nome)
        
        if cnpj:
            informacoes["cnpj"] = self.buscar_cnpj(cnpj)

            if not nome and "nome" in informacoes["cnpj"]:
                informacoes["google"] = self.buscar_no_google(informacoes["cnpj"]["nome"])

        return informacoes

@app.route('/buscar', methods=['GET'])
def buscar():
    nome = request.args.get('nome')
    cnpj = request.args.get('cnpj')

    if not nome and not cnpj:
        return jsonify({"erro": "Forneça nome ou CNPJ"}), 400

    agente = AgenteInformacoesBasicas()
    dados = agente.buscar_informacoes(nome, cnpj)

    try:
        response = requests.post(REPORT_SERVICE_URL, json=dados)
        return response.json() 
    except Exception as e:
        return jsonify({"erro": f"Falha ao gerar relatório: {str(e)}"})

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)
