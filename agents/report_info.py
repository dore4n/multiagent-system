import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()

app = Flask(__name__)

llm = ChatGroq(api_key=os.getenv("GROQ_API_KEY"), model_name="llama3-8b-8192")

def gerar_relatorio_groq(dados):
    """Gera um relatório detalhado e formatado em Markdown a partir dos dados fornecidos."""
    if not dados:
        return {"erro": "Nenhum dado fornecido para gerar o relatório."}

    prompt = f"""
    Gere um relatório detalhado e formatado em Markdown com os seguintes dados:
    {dados}

    **Regras:**
    - Use títulos e subtítulos claros.
    - Liste os resultados de forma numerada.
    - Utilize negrito para destacar informações importantes.
    - Gere um relatório bem organizado e legível.
    """

    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        relatorio_markdown = response.content.strip()
        return {"relatorio": relatorio_markdown}
    except Exception as e:
        return {"erro": f"Erro ao gerar relatório: {str(e)}"}

@app.route('/gerar_relatorio', methods=['POST'])
def gerar_relatorio():
    """Recebe os dados e retorna o relatório formatado em Markdown."""
    dados = request.get_json()
    if not dados:
        return jsonify({"erro": "Nenhum dado enviado no corpo da requisição."}), 400

    resultado = gerar_relatorio_groq(dados)
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5001)