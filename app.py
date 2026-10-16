"""
MIT License

Copyright (c) 2026 Arquiteto de Software Especialista em IA e Python

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

# ==============================================================================
# GUIA DE CONFIGURAÇÃO DO .streamlit/secrets.toml
# ==============================================================================
# Para que o aplicativo funcione de forma segura na sua máquina, crie uma pasta
# chamada `.streamlit` na raiz do seu projeto e dentro dela um arquivo chamado `secrets.toml`.
# 
# Conteúdo do arquivo `.streamlit/secrets.toml`:
# 
# [azure_openai]
# api_key = "SUA_API_KEY_AQUI"
# endpoint = "SEU_ENDPOINT_AQUI"
# deployment_name = "gpt-4.1-mini"
# ==============================================================================

import json
import streamlit as st
from openai import AzureOpenAI

# Configuração da Página do Streamlit
st.set_page_config(
    page_title="Extrator de Dados Inteligente - Azure OpenAI",
    page_icon="🤖",
    layout="centered"
)

# Estilização CSS personalizada para um design moderno
st.markdown("""
    <style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #0078D4;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        padding: 0.5rem 1rem;
    }
    .stButton>button:hover {
        background-color: #005A9E;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho da Aplicação
st.markdown('<p class="main-title">Extrator de Dados Inteligente</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Utilizando infraestrutura Microsoft Azure OpenAI para análise estruturada de texto.</p>', unsafe_allow_html=True)

# Carregamento seguro das credenciais via st.secrets ou valores padrão para testes
try:
    AZURE_API_KEY = st.secrets["azure_openai"]["api_key"]
    AZURE_ENDPOINT = st.secrets["azure_openai"]["endpoint"]
    DEPLOYMENT_NAME = st.secrets["azure_openai"]["deployment_name"]
except Exception:
    # Fallback direto fornecido para fins educacionais (caso o secrets.toml não esteja configurado)
    AZURE_API_KEY = "6t2pTNsmNafDyo53MDAFIrvvQRBZXP7dLcr5j3TLxMS34LQVq3ZUJQQJ99CHACHYHv6XJ3w3AAAAACOGT7os"
    AZURE_ENDPOINT = "https://marcelomaffeis-05082026-resource.services.ai.azure.com/"
    DEPLOYMENT_NAME = "gpt-4.1-mini"

# Limpeza e normalização da URL do Endpoint (removendo caracteres indesejados como &quot;)
AZURE_ENDPOINT = AZURE_ENDPOINT.replace("&quot;", "").strip()
if AZURE_ENDPOINT.endswith("/"):
    AZURE_ENDPOINT = AZURE_ENDPOINT[:-1]

# Entrada de Texto do Usuário
texto_usuario = st.text_area(
    "Digite ou cole o texto que deseja analisar:",
    placeholder="Ex: Reunião urgente marcada com Carlos e Ana amanhã às 10h para resolver o problema crítico no servidor principal.",
    height=150
)

# Botão de Ação
if st.button("Processar Texto"):
    if not texto_usuario.strip():
        st.warning("⚠️ Por favor, insira um texto válido antes de processar.")
    else:
        with st.spinner("Analisando dados via Azure OpenAI..."):
            try:
                # Inicialização do cliente Azure OpenAI
                client = AzureOpenAI(
                    api_key=AZURE_API_KEY,
                    api_version="2024-08-01-preview",
                    azure_endpoint=AZURE_ENDPOINT
                )

                # Definição do System Prompt Rígido
                system_prompt = (
                    "Você é um extrator de dados especialista. Analise o texto fornecido e retorne "
                    "estritamente UM JSON válido (sem blocos de código markdown ou texto adicional) contendo exatamente as seguintes chaves:\n"
                    "- 'sentimento': string descritiva do sentimento geral (ex: Positivo, Negativo, Neutro, Tenso, etc.)\n"
                    "- 'porcentagem_sentimento': número inteiro de 0 a 100 representando a intensidade/confiança do sentimento predominante\n"
                    "- 'assunto_principal': string resumindo o tema central do texto\n"
                    "- 'pessoas_citadas': lista de strings contendo os nomes das pessoas identificadas no texto (vazia se não houver)\n"
                    "- 'nivel_de_urgencia': string restrita a exatamente uma das três opções: 'Baixo', 'Medio', ou 'Alto'"
                )

                # Chamada à API da Microsoft Azure OpenAI
                response = client.chat.completions.create(
                    model=DEPLOYMENT_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": texto_usuario}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )

                # Extração e decodificação do conteúdo retornado
                conteudo_resposta = response.choices[0].message.content
                dados_json = json.loads(conteudo_resposta)

                st.success("✨ Processamento concluído com sucesso!")
                st.divider()

                # Exibição Estruturada na Interface
                st.subheader("📊 Resultados da Análise")

                # Métricas Principais
                col1, col2 = st.columns(2)
                
                with col1:
                    sentimento_val = dados_json.get("sentimento", "N/A")
                    porcentagem_val = dados_json.get("porcentagem_sentimento", 0)
                    st.metric(label="Sentimento Predominante", value=sentimento_val, delta=f"{porcentagem_val}% de intensidade")

                with col2:
                    urgencia = dados_json.get("nivel_de_urgencia", "Baixo")
                    # Cor dinâmica baseada na urgência
                    st.metric(label="Nível de Urgência", value=urgencia)

                # Assunto Principal
                st.info(f"**Assunto Principal:** {dados_json.get('assunto_principal', 'Não especificado')}")

                # Pessoas Citadas
                pessoas = dados_json.get("pessoas_citadas", [])
                if pessoas:
                    st.write("**👥 Pessoas Citadas:**")
                    for pessoa in pessoas:
                        st.markdown(f"- {pessoa}")
                else:
                    st.write("**👥 Pessoas Citadas:** Nenhuma pessoa identificada.")

                # Visualizador do JSON bruto em expansor
                with st.expander("Ver JSON Bruto Retornado"):
                    st.json(dados_json)

            except Exception as e:
                st.error(f"❌ Ocorreu um erro ao processar a requisição: {e}")
