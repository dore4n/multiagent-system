# Multiagentes para Geração de Relatórios Empresariais

Este sistema é composto por **microserviços** que, em conjunto, realizam a busca e de informações empresariais em um relatório detalhado. Ele integra dados coletados de fontes externas (como SerpAPI e ReceitaWS) e utiliza a inteligência artificial da Groq via LangChain para gerar um relatório final.

---

## Estrutura do Projeto

```
/multiagent-system
│
├── .env.example             # Exemplo das variáveis de ambiente necessárias
├── .env                     # Arquivo (não versionado) com a configuração real (ex.: GROQ_API_KEY)
├── .gitignore
├── Dockerfile               # Dockerfile na raiz do projeto
├── docker-compose.yml       # Orquestração dos containers
├── requirements.txt         # Dependências do projeto
├── README.md                # Este arquivo
└── /agents
    ├── search_info.py       # Microserviço de busca de informações
    └── report_info.py       # Microserviço de geração de relatórios (utiliza Groq via LangChain)
```

---

## Como Funciona

1. **Agente de Busca (`search_info.py`):**
   - Recebe uma requisição com parâmetros como `nome` e/ou `cnpj`.
   - Realiza chamadas a serviços externos para coletar dados (ex.: resultados do Google via SerpAPI e dados cadastrais via ReceitaWS).
   - Consolida essas informações e envia automaticamente os dados coletados para o Agente de Relatório.

2. **Agente de Relatório (`report_info.py`):**
   - Recebe os dados consolidados.
   - Utiliza o LangChain integrado com a API do Groq para gerar um relatório detalhado, formatado inicialmente em Markdown e convertido para HTML.
   - Retorna o relatório final ao usuário.

O fluxo completo é automatizado: o usuário faz uma única requisição e recebe o relatório final.

---

## Tecnologias Utilizadas

- **Python 3.11**
- **Flask** – Criação da API REST.
- **LangChain & langchain_groq** – Integração com a API da Groq para geração de relatórios.
- **Requests** – Realização de chamadas HTTP.
- **python-dotenv** – Gerenciamento de variáveis de ambiente.
- **Docker & Docker Compose** – Containerização e orquestração dos microserviços.

---

## Configuração do Ambiente

### 1. Clonando o Repositório

```bash
git clone https://github.com/seu-usuario/multiagent-system.git
cd multiagent-system
```

### 2. Configurando Variáveis de Ambiente

Renomeie o arquivo de exemplo e edite-o:

```bash
cp .env.example .env
```

No arquivo **.env**, insira sua chave da API Groq:

```
GROQ_API_KEY=sua_chave_aqui
```

### 3. Instalação Manual (Opcional)

Se preferir rodar sem Docker, crie um ambiente virtual e instale as dependências:

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac (no Windows: venv\Scripts\activate)
pip install -r requirements.txt
```

---

## Executando com Docker

O projeto já possui um **Dockerfile** e um **docker-compose.yml** na raiz.

### Dockerfile

O Dockerfile copia a pasta `/agents` e instala as dependências definidas em `requirements.txt`.

### docker-compose.yml

```yaml
version: "3.8"

services:
  search_info:
    build: .
    container_name: search_info
    command: ["python", "agents/search_info.py"]
    ports:
      - "5000:5000"
    networks:
      - agentes_net
    env_file:
      - .env

  report_info:
    build: .
    container_name: report_info
    command: ["python", "agents/report_info.py"]
    ports:
      - "5001:5001"
    networks:
      - agentes_net
    env_file:
      - .env

networks:
  agentes_net:
    driver: bridge
```

### Para Construir e Rodar os Containers

Na raiz do projeto, execute:

```bash
docker-compose up --build
```

Os microserviços serão iniciados e estarão disponíveis em:
- **search_info:** [http://localhost:5000](http://localhost:5000)
- **report_info:** [http://localhost:5001](http://localhost:5001)

---

## Uso da API

### Endpoint: `/buscar`

- **Método:** `POST`
- **Formato de Entrada:** JSON contendo os dados para gerar o relatório.
- **Formato de Saída:** Relatório formatado (HTML).

### Exemplo de Requisição (usando cURL):

```bash
curl -X POST http://localhost:5001/buscar?nome=correios \
     -H "Content-Type: application/json" \
     -d '{"nome": "Empresa XYZ", "dados": "Informações sobre a empresa XYZ"}'
```

<img src="/public/example.png">

O relatório será gerado com base nos dados fornecidos e retornado diretamente ao usuário.

---

## Fluxo Completo

1. O usuário faz uma requisição para o endpoint de busca (`/buscar`) no Agente de Busca.
2. O Agente de Busca coleta os dados de fontes externas e os envia automaticamente para o Agente de Relatório.
3. O Agente de Relatório utiliza a IA da Groq para gerar um relatório detalhado e o retorna ao usuário.
4. O usuário recebe o relatório final, pronto para visualização.

---

## Possíveis Melhorias Futuras

- Refinar o prompt enviado à API Groq para relatórios ainda mais personalizados.
- Adicionar cache para evitar chamadas repetidas e reduzir o tempo de resposta.
- Desenvolver uma interface web interativa para upload de dados e visualização dos relatórios.
- Expandir a integração com outras fontes de dados para enriquecer os relatórios.

---

## Licença

Este projeto é open-source e pode ser utilizado e modificado livremente.
