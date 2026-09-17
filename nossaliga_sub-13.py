import io
import re
import pandas as pd
import requests
import streamlit as st
import urllib3
from bs4 import BeautifulSoup

# Desativa avisos de SSL não verificado
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DA INTERFACE E DESIGN
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nossa Liga Futsal 2026 - Sub-13 Masculino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #f8f9fa; }
    .header-box {
        background: linear-gradient(135deg, #160e91, #215ea0);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .header-title { font-size: 28px; font-weight: 800; margin: 0; color: #ffffff; }
    .header-subtitle { font-size: 14px; color: #f8f063; margin-top: 4px; font-weight: 600; }
    .metric-card {
        background: white;
        padding: 16px;
        border-radius: 10px;
        border-left: 5px solid #215ea0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
    }
    .metric-value { font-size: 24px; font-weight: bold; color: #160e91; }
    .metric-label { font-size: 12px; color: #64748b; text-transform: uppercase; font-weight: 600; }
    .card-jogo {
        background: white;
        padding: 18px;
        border-radius: 10px;
        border-left: 6px solid #160e91;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .placar-badge {
        background-color: #160e91;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        display: inline-block;
        margin: 0 8px;
    }
    .placar-badge-final {
        background-color: #28a745;
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 16px;
        display: inline-block;
        margin: 0 8px;
    }
    /* Estilização reduzida dos botões de navegação (Fundo Azul e Texto Branco Negrito) */
    .stButton > button {
        background-color: #160e91 !important;
        border: none !important;
        border-left: 4px solid #215ea0 !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.1) !important;
        color: white !important;
        font-weight: bold !important;
        font-size: 12px !important;
        height: 48px !important;
        width: 100% !important;
        text-align: center !important;
        transition: all 0.2s ease-in-out;
    }
    .stButton > button:hover {
        box-shadow: 0 4px 10px rgba(0,0,0,0.15) !important;
        border-left-color: #ffffff !important;
        background-color: #215ea0 !important;
        color: white !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# CONSTANTES E ENDPOINTS DA NOSSA LIGA
# -----------------------------------------------------------------------------
BASE_URL = "https://www.nossaliga.com.br"
URL_SUB13_BASE = f"{BASE_URL}/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978"

FASES_CLASSIFICACAO = {
    "Classificação Geral": f"{URL_SUB13_BASE}/classificacao/geral/0",
    "Etapa 1": f"{URL_SUB13_BASE}/classificacao/fase/53332",
    "Oitavas de Final": f"{URL_SUB13_BASE}/classificacao/fase/55495",
    "Mata-Mata Bronze": f"{URL_SUB13_BASE}/classificacao/fase/55498",
    "Quartas de Final": f"{URL_SUB13_BASE}/classificacao/fase/56799",
    "Chaveamento Bronze": f"{URL_SUB13_BASE}/classificacao/fase/56800",
    "Semi Final Ouro": f"{URL_SUB13_BASE}/classificacao/fase/56801",
    "Semi Final Prata": f"{URL_SUB13_BASE}/classificacao/fase/57073",
    "Semi Final Bronze": f"{URL_SUB13_BASE}/classificacao/fase/57074",
    "Final com 3º Lugar Ouro": f"{URL_SUB13_BASE}/classificacao/fase/57075",
    "Final Prata": f"{URL_SUB13_BASE}/classificacao/fase/57076",
    "Final Bronze": f"{URL_SUB13_BASE}/classificacao/fase/57077",
}

URL_CARTOES = f"{URL_SUB13_BASE}/estatisticas/cartoes"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Referer": BASE_URL,
}

PADRAO_NOMES_EQUIPES = {
    "GGE": "Colégio GGE",
    "GGE BOA VIAGEM": "Colégio GGE",
    "GGE BENFICA": "Colégio GGE B",
    "SANTA MARIA": "Colégio Santa Maria",
    "SANTA MARIA B": "Colégio Santa Maria B",
    "AMERICANA": "Escola Americana do Recife",
    "BEM-ME-QUER": "Escola Bem-me-quer",
    "DECISÃO": "Colégio Decisão",
    "DECISAO": "Colégio Decisão",
    "PIEDADE": "Colégio Piedade",
    "ELO CORDEIRO": "Colégio Elo Cordeiro",
    "ELO BOA VIAGEM": "Colégio Elo Boa Viagem",
    "DAMAS": "Colégio Damas",
    "EQUIPE": "Colégio Equipe",
    "CBV JAQUEIRA": "CBV Jaqueira",
    "CASA FORTE": "Colégio Casa Forte",
    "MANGUEIRA DA TORRE": "Projeto Mangueira da Torre",
    "NÚCLEO": "Colégio Núcleo",
    "NUCLEO": "Colégio Núcleo",
    "SÃO JOSÉ": "Colégio São José - Abreu e Lima",
    "SAO JOSE": "Colégio São José - Abreu e Lima",
    "MARISTA SÃO LUIS": "Colégio Marista São Luis",
    "MARISTA": "Colégio Marista São Luis",
    "MACKENZIE AGNES": "Mackenzie Agnes",
    "MACKENZIE B": "Mackenzie Agnes B",
    "APOIO": "Colégio Apoio",
    "GRANDE PASSO": "Colegio Grande Passo",
    "EXIMIUS": "Colégio Eximius",
    "COGNITIVO": "Colégio Cognitivo",
    "VISÃO": "Colégio Visão",
    "VISAO": "Colégio Visão",
    "MOTIVO": "Colégio Motivo Boa Viagem",
    "MOTIVO BOA VIAGEM": "Colégio Motivo Boa Viagem",
    "ELEVA RECIFE": "Escola Eleva Recife",
    "ELEVA": "Escola Eleva Recife",
}

# -----------------------------------------------------------------------------
# BASES OFICIAIS DE CARTÕES (AMARELOS E VERMELHOS)
# -----------------------------------------------------------------------------
DADOS_CARTOES_AMARELOS = [
    {
        "Atleta": "PEDRO GARCIA RAMALHO DE ANDRADE",
        "Equipe": "Colégio Visão",
        "Cartões": "3 (22/4/2026,29/4/2026,10/9/2026)",
    },
    {
        "Atleta": "ARTHUR ROMERO ALENCAR LOURENÇO",
        "Equipe": "Colégio Damas",
        "Cartões": "2 (25/8/2026,8/9/2026)",
    },
    {
        "Atleta": "GUILHERME HOLANDA CANUTO",
        "Equipe": "Colégio Damas",
        "Cartões": "2 (3/9/2026,10/9/2026)",
    },
    {
        "Atleta": "GUSTAVO NOGUEIRA LEITÃO",
        "Equipe": "Colégio Decisão",
        "Cartões": "2 (13/5/2026,1/6/2026)",
    },
    {
        "Atleta": "JOÃO GABRIEL HERMÍNIO BARROSO",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Cartões": "2 (2/6/2026,15/9/2026)",
    },
    {
        "Atleta": "JOSÉ CARLOS PEREIRA SANTOS NETO",
        "Equipe": "Colégio Santa Maria",
        "Cartões": "2 (6/5/2026,15/9/2026)",
    },
    {
        "Atleta": "ARTHUR GABRIEL ARRUDA DE CARVALHO",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Cartões": "2 (29/4/2026,13/8/2026)",
    },
    {
        "Atleta": "CAIO HENRIQUE ARAÚJO DE FREITAS",
        "Equipe": "Escola Bem-me-quer",
        "Cartões": "2 (11/8/2026,14/9/2026)",
    },
    {
        "Atleta": "CARLOS EDUARDO DE OLIVEIRA ANDRADE",
        "Equipe": "Projeto Mangueira da Torre",
        "Cartões": "2 (12/8/2026,19/8/2026)",
    },
    {
        "Atleta": "MARCELO COLAÇO FERRAZ REGUEIRA PESSOA",
        "Equipe": "CBV Jaqueira",
        "Cartões": "1 (14/9/2026)",
    },
    {
        "Atleta": "JOAQUIM AIRES MATTOSO",
        "Equipe": "Colégio Apoio",
        "Cartões": "1 (16/9/2026)",
    },
]

DADOS_CARTOES_VERMELHOS = [
    {
        "Atleta": "ALESSANDRO SAMUEL DA SILVA",
        "Equipe": "Colégio Decisão",
        "Cartões": "1 (8/6/2026)",
    },
    {
        "Atleta": "ANDRÉ JUAN DE OLIVEIRA SILVA",
        "Equipe": "Colégio Decisão",
        "Cartões": "1 (8/6/2026)",
    },
    {
        "Atleta": "HENRIQUE JUREMA MARINHO",
        "Equipe": "Colégio Núcleo",
        "Cartões": "1 (8/6/2026)",
    },
    {
        "Atleta": "JOSÉ CAVALCANTI NEVES",
        "Equipe": "Colégio Núcleo",
        "Cartões": "1 (8/6/2026)",
    },
    {
        "Atleta": "THIAGO ALBUQUERQUE DE MIRANDA MARTINS",
        "Equipe": "Colégio Núcleo",
        "Cartões": "1 (22/4/2026)",
    },
    {
        "Atleta": "LUCCA DE MELO CALDAS CAVALCANTI",
        "Equipe": "Mackenzie Agnes",
        "Cartões": "1 (14/9/2026)",
    },
    {
        "Atleta": "RUAN VICTOR BARROS DOS SANTOS",
        "Equipe": "Mackenzie Agnes",
        "Cartões": "1 (24/4/2026)",
    },
]

# -----------------------------------------------------------------------------
# BASE OFICIAL DA ARTILHARIA COMPLETA (1º AO 233º)
# -----------------------------------------------------------------------------
DADOS_ARTILHARIA = [
    {
        "Pos": "1º",
        "Atleta": "Lucas da Rosa Borges Pereira",
        "Equipe": "Escola Americana do Recife",
        "Gols": 23,
    },
    {
        "Pos": "2º",
        "Atleta": "Heitor Correia Batista",
        "Equipe": "Colégio Núcleo",
        "Gols": 12,
    },
    {
        "Pos": "3º",
        "Atleta": "Calebe Bezerra de Souza",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 11,
    },
    {
        "Pos": "4º",
        "Atleta": "Bernardo Paz Carneiro",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 11,
    },
    {
        "Pos": "5º",
        "Atleta": "Davi Luiz Batista de Oliveira",
        "Equipe": "Colégio Decisão",
        "Gols": 9,
    },
    {
        "Pos": "6º",
        "Atleta": "Fernando Vasconcelos de Siqueira Alencar",
        "Equipe": "Colégio GGE",
        "Gols": 9,
    },
    {
        "Pos": "7º",
        "Atleta": "Davi Alcântara Rodrigues Ramos",
        "Equipe": "Mackenzie Agnes",
        "Gols": 9,
    },
    {
        "Pos": "8º",
        "Atleta": "Heitor Macedo Cavalcanti",
        "Equipe": "Colégio Piedade",
        "Gols": 9,
    },
    {
        "Pos": "9º",
        "Atleta": "Caio Henrique Araújo de Freitas",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 9,
    },
    {
        "Pos": "10º",
        "Atleta": "Henrique Jurema Marinho",
        "Equipe": "Colégio Núcleo",
        "Gols": 9,
    },
    {
        "Pos": "11º",
        "Atleta": "Arthur Gabriel Arruda de Carvalho",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 9,
    },
    {
        "Pos": "12º",
        "Atleta": "Guilherme Bastos Colaço Dias Neto",
        "Equipe": "Escola Americana do Recife",
        "Gols": 8,
    },
    {
        "Pos": "13º",
        "Atleta": "Miguel Freire O de Sobral",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 8,
    },
    {
        "Pos": "14º",
        "Atleta": "Ray Cavalcanti dos Santos",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 8,
    },
    {
        "Pos": "15º",
        "Atleta": "Mateus Guerra Mota Moreira",
        "Equipe": "Colégio GGE",
        "Gols": 8,
    },
    {
        "Pos": "16º",
        "Atleta": "João Gabriel Hermínio Barroso",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Gols": 8,
    },
    {
        "Pos": "17º",
        "Atleta": "Gustavo Araújo Petribú Fraga Rocha",
        "Equipe": "Escola Americana do Recife",
        "Gols": 8,
    },
    {
        "Pos": "18º",
        "Atleta": "Matheus Azevedo Morais",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 8,
    },
    {
        "Pos": "19º",
        "Atleta": "João Mateus Verdião Galindo",
        "Equipe": "Colégio Apoio",
        "Gols": 7,
    },
    {
        "Pos": "20º",
        "Atleta": "Gabriel Modesto Pereira Minghini Quirino dos Santos",
        "Equipe": "Colégio Santa Maria",
        "Gols": 7,
    },
    {
        "Pos": "21º",
        "Atleta": "Daniel Moura do Nascimento",
        "Equipe": "Mackenzie Agnes",
        "Gols": 7,
    },
    {
        "Pos": "22º",
        "Atleta": "Vitor Torquato Valente Bulhões Cavalcanti",
        "Equipe": "CBV Jaqueira",
        "Gols": 7,
    },
    {
        "Pos": "23º",
        "Atleta": "Francisco Menelau Correia Lima",
        "Equipe": "Colégio Damas",
        "Gols": 7,
    },
    {
        "Pos": "24º",
        "Atleta": "Bernardo Freire Cavalcante Gonçalves",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 7,
    },
    {
        "Pos": "25º",
        "Atleta": "Victor Luiz de Albuquerque Santos",
        "Equipe": "Colégio GGE B",
        "Gols": 7,
    },
    {
        "Pos": "26º",
        "Atleta": "Henrique Ponce Maranhão Miranda",
        "Equipe": "Colégio Santa Maria",
        "Gols": 7,
    },
    {
        "Pos": "27º",
        "Atleta": "Arthur Remígio Mendes",
        "Equipe": "Mackenzie Agnes",
        "Gols": 7,
    },
    {
        "Pos": "28º",
        "Atleta": "Leonardo Apolinário Valadares Rabelo",
        "Equipe": "Mackenzie Agnes",
        "Gols": 7,
    },
    {
        "Pos": "29º",
        "Atleta": "João Davi Santos Soares",
        "Equipe": "Colégio GGE C",
        "Gols": 7,
    },
    {
        "Pos": "30º",
        "Atleta": "Luiz Miguel Voznihinsky de Oliveira Falcão",
        "Equipe": "CBV Jaqueira",
        "Gols": 7,
    },
    {
        "Pos": "31º",
        "Atleta": "José Cavalcanti Neves",
        "Equipe": "Colégio Núcleo",
        "Gols": 6,
    },
    {
        "Pos": "32º",
        "Atleta": "Ravi Machado Melo",
        "Equipe": "Colégio Visão",
        "Gols": 6,
    },
    {
        "Pos": "33º",
        "Atleta": "Fabio Lucas Ferreira Coutinho da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 5,
    },
    {
        "Pos": "34º",
        "Atleta": "Lucas Gouveia Castor",
        "Equipe": "Colégio Apoio",
        "Gols": 5,
    },
    {
        "Pos": "35º",
        "Atleta": "Alessandro Samuel da Silva",
        "Equipe": "Colégio Decisão",
        "Gols": 5,
    },
    {
        "Pos": "36º",
        "Atleta": "Kaua Felipe Oliveira de Aguiar",
        "Equipe": "Colégio Decisão",
        "Gols": 5,
    },
    {
        "Pos": "37º",
        "Atleta": "Henrique Osias de Souza Andrade",
        "Equipe": "Colégio Eximius",
        "Gols": 5,
    },
    {
        "Pos": "38º",
        "Atleta": "Lucas Santana Teixeira",
        "Equipe": "Colégio Núcleo",
        "Gols": 5,
    },
    {
        "Pos": "39º",
        "Atleta": "Brenno Marques Marinho",
        "Equipe": "Colégio Piedade",
        "Gols": 5,
    },
    {
        "Pos": "40º",
        "Atleta": "André Monte Figueiredo",
        "Equipe": "Colégio Santa Maria",
        "Gols": 5,
    },
    {
        "Pos": "41º",
        "Atleta": "Joaquim Ribeiro Duarte",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 5,
    },
    {
        "Pos": "42º",
        "Atleta": "André Juan de Oliveira Silva",
        "Equipe": "Colégio Decisão",
        "Gols": 5,
    },
    {
        "Pos": "43º",
        "Atleta": "Gabriel Freitas Lins Sarfestein",
        "Equipe": "Colégio GGE",
        "Gols": 5,
    },
    {
        "Pos": "44º",
        "Atleta": "Rafael Alves Alcantara",
        "Equipe": "Colégio GGE",
        "Gols": 5,
    },
    {
        "Pos": "45º",
        "Atleta": "Bruno Othon de Freitas Bernardo",
        "Equipe": "Colégio Cognitivo",
        "Gols": 5,
    },
    {
        "Pos": "46º",
        "Atleta": "Levi Vanderlei Silvério",
        "Equipe": "Colégio Equipe",
        "Gols": 4,
    },
    {
        "Pos": "47º",
        "Atleta": "Bruno Monteiro Loureiro Amorim Filho",
        "Equipe": "Colégio Santa Maria",
        "Gols": 4,
    },
    {
        "Pos": "48º",
        "Atleta": "Arthur Gomes Grund Lopes",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 4,
    },
    {
        "Pos": "49º",
        "Atleta": "José Eraldo de Melo Herculano Rocha",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 4,
    },
    {
        "Pos": "50º",
        "Atleta": "Alfredo José Carneiro Neto",
        "Equipe": "Colégio Equipe",
        "Gols": 4,
    },
    {
        "Pos": "51º",
        "Atleta": "Arthur Carneiro Torres Cabral",
        "Equipe": "Colégio Equipe",
        "Gols": 4,
    },
    {
        "Pos": "52º",
        "Atleta": "João Pedro Machado Ferreira",
        "Equipe": "Colégio GGE",
        "Gols": 4,
    },
    {
        "Pos": "53º",
        "Atleta": "Lucca Normande Peixoto",
        "Equipe": "Colégio Santa Maria",
        "Gols": 4,
    },
    {
        "Pos": "54º",
        "Atleta": "Lucas Moneta Fragoso",
        "Equipe": "Colégio Visão",
        "Gols": 4,
    },
    {
        "Pos": "55º",
        "Atleta": "Enzo Cassiano Andrade Silva",
        "Equipe": "Colégio Decisão",
        "Gols": 4,
    },
    {
        "Pos": "56º",
        "Atleta": "João Felipe dos Anjos G Ramos de Gusmão",
        "Equipe": "Colégio Decisão",
        "Gols": 4,
    },
    {
        "Pos": "57º",
        "Atleta": "Heitor de Oliveira Motta Medeiros",
        "Equipe": "Colégio Equipe",
        "Gols": 4,
    },
    {
        "Pos": "58º",
        "Atleta": "André Luis Mendes",
        "Equipe": "Colégio Eximius",
        "Gols": 4,
    },
    {
        "Pos": "59º",
        "Atleta": "Victor Camargo Silva",
        "Equipe": "Colégio GGE",
        "Gols": 4,
    },
    {
        "Pos": "60º",
        "Atleta": "Henrique Caminha Romeiro de Melo",
        "Equipe": "Colégio GGE C",
        "Gols": 4,
    },
    {
        "Pos": "61º",
        "Atleta": "Daniel Cintra de Andrade",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Gols": 4,
    },
    {
        "Pos": "62º",
        "Atleta": "Pedro Fortaleza Bezerra de Menezes",
        "Equipe": "Colégio Casa Forte",
        "Gols": 4,
    },
    {
        "Pos": "63º",
        "Atleta": "Lucca de Melo Caldas Cavalcanti",
        "Equipe": "Mackenzie Agnes",
        "Gols": 4,
    },
    {
        "Pos": "64º",
        "Atleta": "Vinicius da Costa Pinto Pereira",
        "Equipe": "Colégio Apoio",
        "Gols": 4,
    },
    {
        "Pos": "65º",
        "Atleta": "Davi Lucas Bezerra da Silva",
        "Equipe": "Colégio Decisão",
        "Gols": 3,
    },
    {
        "Pos": "66º",
        "Atleta": "Vinicius do A Guedes",
        "Equipe": "Colégio Elo Boa Viagem",
        "Gols": 3,
    },
    {
        "Pos": "67º",
        "Atleta": "Miguel Martins Maciel",
        "Equipe": "Colégio Equipe",
        "Gols": 3,
    },
    {
        "Pos": "68º",
        "Atleta": "Gabriel Ferreira Marinho Pereira",
        "Equipe": "Colégio GGE B",
        "Gols": 3,
    },
    {
        "Pos": "69º",
        "Atleta": "Maria Cecília Santos Alves",
        "Equipe": "Colégio GGE C",
        "Gols": 3,
    },
    {
        "Pos": "70º",
        "Atleta": "Rodrigo de Moraes Calazans",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 3,
    },
    {
        "Pos": "71º",
        "Atleta": "James Lee Rodrigues Loifman",
        "Equipe": "Colégio Piedade",
        "Gols": 3,
    },
    {
        "Pos": "72º",
        "Atleta": "Davi da Rosa Borges Pereira",
        "Equipe": "Escola Americana do Recife",
        "Gols": 3,
    },
    {
        "Pos": "73º",
        "Atleta": "Carlos Eduardo Sasson Negreiros",
        "Equipe": "Escola Eleva Recife",
        "Gols": 3,
    },
    {
        "Pos": "74º",
        "Atleta": "Arthur Otaviano Pimenta",
        "Equipe": "Colégio Cognitivo",
        "Gols": 3,
    },
    {
        "Pos": "75º",
        "Atleta": "Bernardo Vilas Foerster Moura",
        "Equipe": "Colégio Cognitivo",
        "Gols": 3,
    },
    {
        "Pos": "76º",
        "Atleta": "Luiz Felipe Veloso Freire Tiburtius",
        "Equipe": "Colégio Damas",
        "Gols": 3,
    },
    {
        "Pos": "77º",
        "Atleta": "Mateus Dias Borges",
        "Equipe": "Colégio Damas",
        "Gols": 3,
    },
    {
        "Pos": "78º",
        "Atleta": "Daniel Henrique Gomes da Silva",
        "Equipe": "Colégio Decisão",
        "Gols": 3,
    },
    {
        "Pos": "79º",
        "Atleta": "João Paulo de Oliveira Cruz",
        "Equipe": "Colégio Elo Boa Viagem",
        "Gols": 3,
    },
    {
        "Pos": "80º",
        "Atleta": "Adam Bernardo Rodrigues Vilaça",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 3,
    },
    {
        "Pos": "81º",
        "Atleta": "Arthur Gouveia Soares",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 3,
    },
    {
        "Pos": "82º",
        "Atleta": "Beatriz Rocha da Silva",
        "Equipe": "Colégio Equipe",
        "Gols": 3,
    },
    {
        "Pos": "83º",
        "Atleta": "Lucas Vidal Morais",
        "Equipe": "Colégio Equipe",
        "Gols": 3,
    },
    {
        "Pos": "84º",
        "Atleta": "Lucca Nunes de Araújo Teixeira Perrelli",
        "Equipe": "Colégio Eximius",
        "Gols": 3,
    },
    {
        "Pos": "85º",
        "Atleta": "Heitor de Melo Chacon Belmonte",
        "Equipe": "Colégio GGE B",
        "Gols": 3,
    },
    {
        "Pos": "86º",
        "Atleta": "Davi Lucas Aguiar Farias",
        "Equipe": "Colegio Grande Passo",
        "Gols": 3,
    },
    {
        "Pos": "87º",
        "Atleta": "Davi Spindola Priori",
        "Equipe": "Colegio Grande Passo",
        "Gols": 3,
    },
    {
        "Pos": "88º",
        "Atleta": "Alysson Henrique Silva da Paz",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 3,
    },
    {
        "Pos": "89º",
        "Atleta": "Arthur Neumann Monteiro Henrique",
        "Equipe": "Escola Americana do Recife",
        "Gols": 3,
    },
    {
        "Pos": "90º",
        "Atleta": "Valentina Fernandes do Rêgo",
        "Equipe": "Escola Eleva Recife",
        "Gols": 3,
    },
    {
        "Pos": "91º",
        "Atleta": "Davi Lucas de Oliveira Carneiro da Silva",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 3,
    },
    {
        "Pos": "92º",
        "Atleta": "Heitor Gomes de Lima Santos",
        "Equipe": "Escola Eleva Recife",
        "Gols": 3,
    },
    {
        "Pos": "93º",
        "Atleta": "Luiz Paulo Magalhães Bittencourt Freire de Oliveira",
        "Equipe": "Escola Eleva Recife",
        "Gols": 3,
    },
    {
        "Pos": "94º",
        "Atleta": "José Carlos Pereira Santos Neto",
        "Equipe": "Colégio Santa Maria",
        "Gols": 3,
    },
    {
        "Pos": "95º",
        "Atleta": "Tiago Belfort Lustosa",
        "Equipe": "Colégio Cognitivo",
        "Gols": 3,
    },
    {
        "Pos": "96º",
        "Atleta": "Davi Alencar Fragoso de Menezes",
        "Equipe": "Colégio Damas",
        "Gols": 2,
    },
    {
        "Pos": "97º",
        "Atleta": "Bernardo Caldas Cavalcanti",
        "Equipe": "Colégio Eximius",
        "Gols": 2,
    },
    {
        "Pos": "98º",
        "Atleta": "Igor Nunes Ferraz",
        "Equipe": "Colégio GGE C",
        "Gols": 2,
    },
    {
        "Pos": "99º",
        "Atleta": "Marcelo Mendonça Costa",
        "Equipe": "Colegio Grande Passo",
        "Gols": 2,
    },
    {
        "Pos": "100º",
        "Atleta": "Tiago Dourado Figueiredo",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 2,
    },
    {
        "Pos": "101º",
        "Atleta": "Vinicius Correia Sampaio de Souza",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 2,
    },
    {
        "Pos": "102º",
        "Atleta": "Guilherme Marroquim Braga de Morais",
        "Equipe": "Colégio Santa Maria",
        "Gols": 2,
    },
    {
        "Pos": "103º",
        "Atleta": "Matheus Sales Carvalheira",
        "Equipe": "Mackenzie Agnes",
        "Gols": 2,
    },
    {
        "Pos": "104º",
        "Atleta": "Daniel Cavalcante Bezerra de Menezes",
        "Equipe": "Mackenzie Agnes B",
        "Gols": 2,
    },
    {
        "Pos": "105º",
        "Atleta": "Eduardo Arraes de Barros Pinto",
        "Equipe": "Colégio Apoio",
        "Gols": 2,
    },
    {
        "Pos": "106º",
        "Atleta": "Pedro Barreto Duque Simões",
        "Equipe": "Colégio Apoio",
        "Gols": 2,
    },
    {
        "Pos": "107º",
        "Atleta": "Théo Machado de Morais",
        "Equipe": "Colégio Apoio",
        "Gols": 2,
    },
    {
        "Pos": "108º",
        "Atleta": "João Carrazzone Amaral G Maciel",
        "Equipe": "Colégio Casa Forte",
        "Gols": 2,
    },
    {
        "Pos": "109º",
        "Atleta": "Pedro Gregório de Oliveira",
        "Equipe": "Colégio Casa Forte",
        "Gols": 2,
    },
    {
        "Pos": "110º",
        "Atleta": "Tomas Fortaleza Bezerra de Menezes",
        "Equipe": "Colégio Casa Forte",
        "Gols": 2,
    },
    {
        "Pos": "111º",
        "Atleta": "Pedro Augusto de Carvalho Xavier Lacerda",
        "Equipe": "Colégio Cognitivo",
        "Gols": 2,
    },
    {
        "Pos": "112º",
        "Atleta": "Deyvid Lázaro Queiroz da Silva Lima",
        "Equipe": "Colégio Decisão",
        "Gols": 2,
    },
    {
        "Pos": "113º",
        "Atleta": "Arthur Ramos Pontual da Silva",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 2,
    },
    {
        "Pos": "114º",
        "Atleta": "Bernardo Felix da Silva",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 2,
    },
    {
        "Pos": "115º",
        "Atleta": "Julio Cesar Lopes Galvão Farias",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 2,
    },
    {
        "Pos": "116º",
        "Atleta": "Felipe Santos Braga",
        "Equipe": "Colégio GGE B",
        "Gols": 2,
    },
    {
        "Pos": "117º",
        "Atleta": "João Gabriel Lira da Silva Holanda",
        "Equipe": "Colégio GGE B",
        "Gols": 2,
    },
    {
        "Pos": "118º",
        "Atleta": "Tobias Ribeiro de Figueiredo",
        "Equipe": "Colégio GGE B",
        "Gols": 2,
    },
    {
        "Pos": "119º",
        "Atleta": "Henrique Almeida de Azevedo",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 2,
    },
    {
        "Pos": "120º",
        "Atleta": "João Marcelo D'Amorim Oliveira",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 2,
    },
    {
        "Pos": "121º",
        "Atleta": "Anderson Wanderley Oliveira Lima Filho",
        "Equipe": "Colégio Piedade",
        "Gols": 2,
    },
    {
        "Pos": "122º",
        "Atleta": "Pedro Othuki Hermes de Melo",
        "Equipe": "Colégio Piedade",
        "Gols": 2,
    },
    {
        "Pos": "123º",
        "Atleta": "Henrique Carvalho Tenório Cavalcanti",
        "Equipe": "Colégio Santa Maria",
        "Gols": 2,
    },
    {
        "Pos": "124º",
        "Atleta": "José Anacleto de Andrade do Nascimento Neto",
        "Equipe": "Colégio Santa Maria",
        "Gols": 2,
    },
    {
        "Pos": "125º",
        "Atleta": "Willyam Ponzi Neto",
        "Equipe": "Colégio Santa Maria",
        "Gols": 2,
    },
    {
        "Pos": "126º",
        "Atleta": "Saulo Bryan de Moura Bandeira",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 2,
    },
    {
        "Pos": "127º",
        "Atleta": "Antônio Muniz Marcondes",
        "Equipe": "Colégio Visão",
        "Gols": 2,
    },
    {
        "Pos": "128º",
        "Atleta": "Pedro Emmanuel de Santana Santos",
        "Equipe": "Colégio Visão",
        "Gols": 2,
    },
    {
        "Pos": "129º",
        "Atleta": "Felipe Monte Barbosa",
        "Equipe": "Escola Americana do Recife",
        "Gols": 2,
    },
    {
        "Pos": "130º",
        "Atleta": "João Carlos Nobrega Fontes",
        "Equipe": "Escola Eleva Recife",
        "Gols": 2,
    },
    {
        "Pos": "131º",
        "Atleta": "Benjamin Alitto Siqueira",
        "Equipe": "Mackenzie Agnes",
        "Gols": 2,
    },
    {
        "Pos": "132º",
        "Atleta": "Bernardo Guerra Wanderley Cavalcanti",
        "Equipe": "Mackenzie Agnes",
        "Gols": 2,
    },
    {
        "Pos": "133º",
        "Atleta": "Rafael Guimarães Negromonte Bezerra",
        "Equipe": "Mackenzie Agnes",
        "Gols": 2,
    },
    {
        "Pos": "134º",
        "Atleta": "Antônio Miguel Leôncio da Silva Chacon",
        "Equipe": "Mackenzie Agnes B",
        "Gols": 2,
    },
    {
        "Pos": "135º",
        "Atleta": "Bernardo Ribeiro Fidelis da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 2,
    },
    {
        "Pos": "136º",
        "Atleta": "João Pedro Sales Pereira da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 2,
    },
    {
        "Pos": "137º",
        "Atleta": "João Vitor Amaral da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 2,
    },
    {
        "Pos": "138º",
        "Atleta": "Arthur Menezes Lima",
        "Equipe": "Colégio Decisão",
        "Gols": 2,
    },
    {
        "Pos": "139º",
        "Atleta": "Gustavo Nogueira Leitão",
        "Equipe": "Colégio Decisão",
        "Gols": 2,
    },
    {
        "Pos": "140º",
        "Atleta": "Marina Souto Albuquerque",
        "Equipe": "Colégio Elo Boa Viagem",
        "Gols": 2,
    },
    {
        "Pos": "141º",
        "Atleta": "Bernardo Marques Xavier Lins",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Gols": 2,
    },
    {
        "Pos": "142º",
        "Atleta": "Joaquim Barbosa Reis de Melo",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Gols": 2,
    },
    {
        "Pos": "143º",
        "Atleta": "Pedro Jordão Allouchie Carneiro",
        "Equipe": "Colégio Núcleo",
        "Gols": 2,
    },
    {
        "Pos": "144º",
        "Atleta": "Rodrigo Coutinho Filho",
        "Equipe": "Colégio Piedade",
        "Gols": 2,
    },
    {
        "Pos": "145º",
        "Atleta": "Pedro Henrique Vaz Manso Braga",
        "Equipe": "Colégio Santa Maria",
        "Gols": 2,
    },
    {
        "Pos": "146º",
        "Atleta": "Ruan Victor Barros dos Santos",
        "Equipe": "Mackenzie Agnes",
        "Gols": 2,
    },
    {
        "Pos": "147º",
        "Atleta": "Gabriel Bandeira Meireles Barros",
        "Equipe": "Mackenzie Agnes B",
        "Gols": 2,
    },
    {
        "Pos": "148º",
        "Atleta": "Guilherme Holanda Canuto",
        "Equipe": "Colégio Damas",
        "Gols": 2,
    },
    {
        "Pos": "149º",
        "Atleta": "Carlos Eduardo de Oliveira Andrade",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 2,
    },
    {
        "Pos": "150º",
        "Atleta": "David França Alcantara",
        "Equipe": "CBV Jaqueira",
        "Gols": 1,
    },
    {
        "Pos": "151º",
        "Atleta": "Guilherme Soares de Castro Silva",
        "Equipe": "CBV Jaqueira",
        "Gols": 1,
    },
    {
        "Pos": "152º",
        "Atleta": "Matheus Yuri Ferrão de Santana",
        "Equipe": "CBV Jaqueira",
        "Gols": 1,
    },
    {
        "Pos": "153º",
        "Atleta": "Bernardo Henriques Leitão",
        "Equipe": "Colégio Apoio",
        "Gols": 1,
    },
    {
        "Pos": "154º",
        "Atleta": "Joaquim Medeiros Muniz Ramos",
        "Equipe": "Colégio Apoio",
        "Gols": 1,
    },
    {
        "Pos": "155º",
        "Atleta": "Tomás Vale Borges dos Santos",
        "Equipe": "Colégio Apoio",
        "Gols": 1,
    },
    {
        "Pos": "156º",
        "Atleta": "Heitor Silverio Borba Oliveira Lima",
        "Equipe": "Colégio Casa Forte",
        "Gols": 1,
    },
    {
        "Pos": "157º",
        "Atleta": "Deni Henrique Cavalcanti de Lima",
        "Equipe": "Colégio Cognitivo",
        "Gols": 1,
    },
    {
        "Pos": "158º",
        "Atleta": "Henrique Casé Moraes Filho",
        "Equipe": "Colégio Cognitivo",
        "Gols": 1,
    },
    {
        "Pos": "159º",
        "Atleta": "João Vasconcelos Gonçalves Rangel Siqueira",
        "Equipe": "Colégio Cognitivo",
        "Gols": 1,
    },
    {
        "Pos": "160º",
        "Atleta": "Miguel Bittencourt de Andrade",
        "Equipe": "Colégio Cognitivo",
        "Gols": 1,
    },
    {
        "Pos": "161º",
        "Atleta": "Pedro Henrique Véras Araújo d'Ávila",
        "Equipe": "Colégio Cognitivo",
        "Gols": 1,
    },
    {
        "Pos": "162º",
        "Atleta": "Pedro Neiva de Mendonça",
        "Equipe": "Colégio Cognitivo",
        "Gols": 1,
    },
    {
        "Pos": "163º",
        "Atleta": "João Barbosa Tavares de Sá",
        "Equipe": "Colégio Damas",
        "Gols": 1,
    },
    {
        "Pos": "164º",
        "Atleta": "Pedro Augusto Ferreira Eustaquio",
        "Equipe": "Colégio Damas",
        "Gols": 1,
    },
    {
        "Pos": "165º",
        "Atleta": "Alice Pierrotti Santos",
        "Equipe": "Colégio Elo Boa Viagem",
        "Gols": 1,
    },
    {
        "Pos": "166º",
        "Atleta": "Davi Carvalho de Pontes",
        "Equipe": "Colégio Elo Boa Viagem",
        "Gols": 1,
    },
    {
        "Pos": "167º",
        "Atleta": "Iuri Miguel Vicente de Moura",
        "Equipe": "Colégio Elo Boa Viagem",
        "Gols": 1,
    },
    {
        "Pos": "168º",
        "Atleta": "Cauâ Henrique Santos do Nascimento",
        "Equipe": "Colégio Elo Cordeiro",
        "Gols": 1,
    },
    {
        "Pos": "169º",
        "Atleta": "João Arthur Marcelino Alves de França Souza",
        "Equipe": "Colégio Equipe",
        "Gols": 1,
    },
    {
        "Pos": "170º",
        "Atleta": "Joaquim Paes Barreto Morais",
        "Equipe": "Colégio Eximius",
        "Gols": 1,
    },
    {
        "Pos": "171º",
        "Atleta": "Luiz Felipe Tavares Barreto de Souza",
        "Equipe": "Colégio Eximius",
        "Gols": 1,
    },
    {
        "Pos": "172º",
        "Atleta": "Ricardo de O Paes Barreto Neto",
        "Equipe": "Colégio Eximius",
        "Gols": 1,
    },
    {
        "Pos": "173º",
        "Atleta": "Bernardo Durand Rego Fernandes",
        "Equipe": "Colégio GGE",
        "Gols": 1,
    },
    {
        "Pos": "174º",
        "Atleta": "Gustavo Aurelio Souto Maior Aguiar de Melo",
        "Equipe": "Colégio GGE",
        "Gols": 1,
    },
    {
        "Pos": "175º",
        "Atleta": "Pedro Xavier Asfora da C Cavalcanti",
        "Equipe": "Colégio GGE",
        "Gols": 1,
    },
    {
        "Pos": "176º",
        "Atleta": "Pedro Henrique da Silva Carvalho",
        "Equipe": "Colégio GGE B",
        "Gols": 1,
    },
    {
        "Pos": "177º",
        "Atleta": "Francisco de Moura Prudente",
        "Equipe": "Colégio GGE C",
        "Gols": 1,
    },
    {
        "Pos": "178º",
        "Atleta": "Gabriel Melo Carvalho Alves",
        "Equipe": "Colégio GGE C",
        "Gols": 1,
    },
    {
        "Pos": "179º",
        "Atleta": "Vinicius Kazuo Ribeiro Gushiken",
        "Equipe": "Colégio GGE C",
        "Gols": 1,
    },
    {
        "Pos": "180º",
        "Atleta": "Lucca Gonçalves Mariano",
        "Equipe": "Colegio Grande Passo",
        "Gols": 1,
    },
    {
        "Pos": "181º",
        "Atleta": "Eduardo Torres Camara Lins",
        "Equipe": "Colégio Marista São Luis",
        "Gols": 1,
    },
    {
        "Pos": "182º",
        "Atleta": "Francisco Acioli Lins da Rocha",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Gols": 1,
    },
    {
        "Pos": "183º",
        "Atleta": "João Francisco Gouveia Marques Siqueira",
        "Equipe": "Colégio Motivo Boa Viagem",
        "Gols": 1,
    },
    {
        "Pos": "184º",
        "Atleta": "Benoah Carvalho Mesel Côrtes",
        "Equipe": "Colégio Núcleo",
        "Gols": 1,
    },
    {
        "Pos": "185º",
        "Atleta": "Marcelo Antônio Vasconcelos Barbosa",
        "Equipe": "Colégio Núcleo",
        "Gols": 1,
    },
    {
        "Pos": "186º",
        "Atleta": "Matheus Morim Moura de Vasconcelos Brennand",
        "Equipe": "Colégio Núcleo",
        "Gols": 1,
    },
    {
        "Pos": "187º",
        "Atleta": "Fábio Stott Amaral Nolasco Cavalcanti",
        "Equipe": "Colégio Piedade",
        "Gols": 1,
    },
    {
        "Pos": "188º",
        "Atleta": "Gabriel Martins de Brito",
        "Equipe": "Colégio Piedade",
        "Gols": 1,
    },
    {
        "Pos": "189º",
        "Atleta": "Lucas Aragão Andrade",
        "Equipe": "Colégio Piedade",
        "Gols": 1,
    },
    {
        "Pos": "190º",
        "Atleta": "Heitor Marques Maciel Pinheiro",
        "Equipe": "Colégio Santa Maria",
        "Gols": 1,
    },
    {
        "Pos": "191º",
        "Atleta": "Théo Dall Agnol Albuquerque",
        "Equipe": "Colégio Santa Maria",
        "Gols": 1,
    },
    {
        "Pos": "192º",
        "Atleta": "Eduardo Leite Maia de Oliveira Gois",
        "Equipe": "Colégio Santa Maria B",
        "Gols": 1,
    },
    {
        "Pos": "193º",
        "Atleta": "Enzo Carvalho Campos",
        "Equipe": "Colégio Santa Maria B",
        "Gols": 1,
    },
    {
        "Pos": "194º",
        "Atleta": "Guilherme Antonio Fernandes Sotero",
        "Equipe": "Colégio Santa Maria B",
        "Gols": 1,
    },
    {
        "Pos": "195º",
        "Atleta": "Guilherme Raposo Gonçalves Correia de Araújo",
        "Equipe": "Colégio Santa Maria B",
        "Gols": 1,
    },
    {
        "Pos": "196º",
        "Atleta": "Anderson Henrique Coelho de O Silva",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 1,
    },
    {
        "Pos": "197º",
        "Atleta": "Arthur Oliveira de Amorim",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 1,
    },
    {
        "Pos": "198º",
        "Atleta": "Edmilson Silva de Lima Junior",
        "Equipe": "Colégio São José - Abreu e Lima",
        "Gols": 1,
    },
    {
        "Pos": "199º",
        "Atleta": "Arthur Rubens Ferreira e Silva",
        "Equipe": "Colégio Visão",
        "Gols": 1,
    },
    {
        "Pos": "200º",
        "Atleta": "Bento José Santos Melo",
        "Equipe": "Colégio Visão",
        "Gols": 1,
    },
    {
        "Pos": "201º",
        "Atleta": "Davi Lauriano da Silva",
        "Equipe": "Colégio Visão",
        "Gols": 1,
    },
    {
        "Pos": "202º",
        "Atleta": "João Vitor Magalhães P da Silva Ramos",
        "Equipe": "Colégio Visão",
        "Gols": 1,
    },
    {
        "Pos": "203º",
        "Atleta": "Antônio Araújo de Petribú Fraga Rocha",
        "Equipe": "Escola Americana do Recife",
        "Gols": 1,
    },
    {
        "Pos": "204º",
        "Atleta": "Carlos Eduardo Fellows Maia de Almeida",
        "Equipe": "Escola Americana do Recife",
        "Gols": 1,
    },
    {
        "Pos": "205º",
        "Atleta": "Guilherme Assis Souto do Espirito Santo",
        "Equipe": "Escola Americana do Recife",
        "Gols": 1,
    },
    {
        "Pos": "206º",
        "Atleta": "Luiz Felipe Oliveira da Costa",
        "Equipe": "Escola Americana do Recife",
        "Gols": 1,
    },
    {
        "Pos": "207º",
        "Atleta": "Davi Simões Ferraz Nunes Beserra",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 1,
    },
    {
        "Pos": "208º",
        "Atleta": "Eduardo Monteiro de Moares Casanova",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 1,
    },
    {
        "Pos": "209º",
        "Atleta": "Felipe de Araújo Camello",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 1,
    },
    {
        "Pos": "210º",
        "Atleta": "João Henrique Batista de Moraes Lêdo",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 1,
    },
    {
        "Pos": "211º",
        "Atleta": "Théo Holanda Hawson",
        "Equipe": "Escola Bem-me-quer",
        "Gols": 1,
    },
    {
        "Pos": "212º",
        "Atleta": "Silvio Gaspar Hacker Côrte Real",
        "Equipe": "Escola Eleva Recife",
        "Gols": 1,
    },
    {
        "Pos": "213º",
        "Atleta": "Natan Soares Alves da Silva",
        "Equipe": "Mackenzie Agnes",
        "Gols": 1,
    },
    {
        "Pos": "214º",
        "Atleta": "Bernardo de Salles Dutra Rabello",
        "Equipe": "Mackenzie Agnes B",
        "Gols": 1,
    },
    {
        "Pos": "215º",
        "Atleta": "Christopher Walmir Silva Pereira",
        "Equipe": "Mackenzie Agnes B",
        "Gols": 1,
    },
    {
        "Pos": "216º",
        "Atleta": "Douglas Junior Rodrigues da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 1,
    },
    {
        "Pos": "217º",
        "Atleta": "Gabriella Sophya Maciel dos Santos",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 1,
    },
    {
        "Pos": "218º",
        "Atleta": "Ryan Marques da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 1,
    },
    {
        "Pos": "219º",
        "Atleta": "Marcelo Colaço Ferraz Regueira Pessoa",
        "Equipe": "CBV Jaqueira",
        "Gols": 1,
    },
    {
        "Pos": "220º",
        "Atleta": "Lucas Gustavo Galvão de Almeida Carvalho Rosas",
        "Equipe": "Colégio Damas",
        "Gols": 1,
    },
    {
        "Pos": "221º",
        "Atleta": "Fernando Barreto Faria",
        "Equipe": "Colégio Eximius",
        "Gols": 1,
    },
    {
        "Pos": "222º",
        "Atleta": "Francisco Barreto Faria",
        "Equipe": "Colégio Eximius",
        "Gols": 1,
    },
    {
        "Pos": "223º",
        "Atleta": "Gabriel Tavares Bezerra",
        "Equipe": "Colégio GGE B",
        "Gols": 1,
    },
    {
        "Pos": "224º",
        "Atleta": "Italo Miguel Marques de Araújo",
        "Equipe": "Colegio Grande Passo",
        "Gols": 1,
    },
    {
        "Pos": "225º",
        "Atleta": "Pedro Veloso Benevides",
        "Equipe": "Colegio Grande Passo",
        "Gols": 1,
    },
    {
        "Pos": "226º",
        "Atleta": "Thiago Albuquerque de Miranda Martins",
        "Equipe": "Colégio Núcleo",
        "Gols": 1,
    },
    {
        "Pos": "227º",
        "Atleta": "Victor Romeiro Maia",
        "Equipe": "Colégio Núcleo",
        "Gols": 1,
    },
    {
        "Pos": "228º",
        "Atleta": "Nicolas Maximiano Ribeiro",
        "Equipe": "Mackenzie Agnes",
        "Gols": 1,
    },
    {
        "Pos": "229º",
        "Atleta": "Caique Levi Tavares Santana",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 1,
    },
    {
        "Pos": "230º",
        "Atleta": "Flavio Gabriel Ferreira C da Silva",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 1,
    },
    {
        "Pos": "231º",
        "Atleta": "Nicolas Berto Ferreira da S Jardim",
        "Equipe": "Projeto Mangueira da Torre",
        "Gols": 1,
    },
    {
        "Pos": "232º",
        "Atleta": "Arthur Romero Alencar Lourenço",
        "Equipe": "Colégio Damas",
        "Gols": 1,
    },
    {
        "Pos": "233º",
        "Atleta": "Pedro Garcia Ramalho de Andrade",
        "Equipe": "Colégio Visão",
        "Gols": 1,
    },
]

# -----------------------------------------------------------------------------
# BASES OFICIAL DE CLASSIFICAÇÃO E JOGOS
# -----------------------------------------------------------------------------
DADOS_CLASSIFICACAO_GERAL = [
    {
        "Pos": "1º",
        "Equipe": "Colégio Santa Maria",
        "P": 27,
        "J": 10,
        "V": 9,
        "E": 0,
        "D": 1,
        "GP": 43,
        "GC": 7,
        "SG": 36,
        "Avg": 6.14,
        "%A": "90.0%",
    },
    {
        "Pos": "2º",
        "Equipe": "Colégio Marista São Luis",
        "P": 21,
        "J": 8,
        "V": 7,
        "E": 0,
        "D": 1,
        "GP": 35,
        "GC": 14,
        "SG": 21,
        "Avg": 2.50,
        "%A": "87.5%",
    },
    {
        "Pos": "3º",
        "Equipe": "Colégio Núcleo",
        "P": 28,
        "J": 12,
        "V": 9,
        "E": 1,
        "D": 2,
        "GP": 40,
        "GC": 14,
        "SG": 26,
        "Avg": 2.86,
        "%A": "77.8%",
    },
    {
        "Pos": "4º",
        "Equipe": "Colégio GGE",
        "P": 28,
        "J": 11,
        "V": 9,
        "E": 1,
        "D": 1,
        "GP": 38,
        "GC": 16,
        "SG": 22,
        "Avg": 2.38,
        "%A": "84.8%",
    },
    {
        "Pos": "5º",
        "Equipe": "Escola Bem-me-quer",
        "P": 22,
        "J": 10,
        "V": 6,
        "E": 3,
        "D": 1,
        "GP": 32,
        "GC": 16,
        "SG": 16,
        "Avg": 2.00,
        "%A": "73.3%",
    },
    {
        "Pos": "6º",
        "Equipe": "Escola Americana do Recife",
        "P": 24,
        "J": 11,
        "V": 8,
        "E": 0,
        "D": 3,
        "GP": 51,
        "GC": 19,
        "SG": 32,
        "Avg": 2.68,
        "%A": "72.7%",
    },
    {
        "Pos": "7º",
        "Equipe": "Colégio Piedade",
        "P": 21,
        "J": 10,
        "V": 7,
        "E": 1,
        "D": 2,
        "GP": 26,
        "GC": 12,
        "SG": 14,
        "Avg": 2.17,
        "%A": "70.0%",
    },
    {
        "Pos": "8º",
        "Equipe": "Colégio Elo Cordeiro",
        "P": 21,
        "J": 10,
        "V": 7,
        "E": 0,
        "D": 3,
        "GP": 30,
        "GC": 20,
        "SG": 10,
        "Avg": 1.50,
        "%A": "70.0%",
    },
    {
        "Pos": "9º",
        "Equipe": "Colégio GGE B",
        "P": 21,
        "J": 10,
        "V": 6,
        "E": 2,
        "D": 2,
        "GP": 22,
        "GC": 17,
        "SG": 5,
        "Avg": 1.29,
        "%A": "70.0%",
    },
    {
        "Pos": "10º",
        "Equipe": "Colégio Damas",
        "P": 20,
        "J": 10,
        "V": 6,
        "E": 0,
        "D": 4,
        "GP": 22,
        "GC": 10,
        "SG": 12,
        "Avg": 2.20,
        "%A": "66.7%",
    },
    {
        "Pos": "11º",
        "Equipe": "Colégio Apoio",
        "P": 18,
        "J": 9,
        "V": 5,
        "E": 2,
        "D": 2,
        "GP": 24,
        "GC": 15,
        "SG": 9,
        "Avg": 1.60,
        "%A": "66.7%",
    },
    {
        "Pos": "12º",
        "Equipe": "Colégio Decisão",
        "P": 22,
        "J": 11,
        "V": 6,
        "E": 2,
        "D": 3,
        "GP": 44,
        "GC": 23,
        "SG": 21,
        "Avg": 1.91,
        "%A": "66.7%",
    },
    {
        "Pos": "13º",
        "Equipe": "Colégio São José - Abreu e Lima",
        "P": 24,
        "J": 13,
        "V": 8,
        "E": 1,
        "D": 4,
        "GP": 31,
        "GC": 15,
        "SG": 16,
        "Avg": 2.07,
        "%A": "61.5%",
    },
    {
        "Pos": "14º",
        "Equipe": "Colégio Equipe",
        "P": 17,
        "J": 10,
        "V": 4,
        "E": 3,
        "D": 3,
        "GP": 26,
        "GC": 20,
        "SG": 6,
        "Avg": 1.30,
        "%A": "56.7%",
    },
    {
        "Pos": "15º",
        "Equipe": "Mackenzie Agnes",
        "P": 21,
        "J": 13,
        "V": 6,
        "E": 2,
        "D": 5,
        "GP": 46,
        "GC": 22,
        "SG": 24,
        "Avg": 2.09,
        "%A": "53.8%",
    },
    {
        "Pos": "16º",
        "Equipe": "Colégio Eximius",
        "P": 13,
        "J": 9,
        "V": 4,
        "E": 1,
        "D": 4,
        "GP": 19,
        "GC": 26,
        "SG": -7,
        "Avg": 0.73,
        "%A": "48.1%",
    },
    {
        "Pos": "17º",
        "Equipe": "Colegio Grande Passo",
        "P": 13,
        "J": 9,
        "V": 3,
        "E": 2,
        "D": 4,
        "GP": 12,
        "GC": 16,
        "SG": -4,
        "Avg": 0.75,
        "%A": "48.1%",
    },
    {
        "Pos": "18º",
        "Equipe": "Colégio Visão",
        "P": 11,
        "J": 9,
        "V": 2,
        "E": 2,
        "D": 5,
        "GP": 18,
        "GC": 26,
        "SG": -8,
        "Avg": 0.69,
        "%A": "40.7%",
    },
    {
        "Pos": "19º",
        "Equipe": "Colégio Cognitivo",
        "P": 12,
        "J": 11,
        "V": 4,
        "E": 0,
        "D": 7,
        "GP": 20,
        "GC": 26,
        "SG": -6,
        "Avg": 0.77,
        "%A": "36.4%",
    },
    {
        "Pos": "20º",
        "Equipe": "Colégio Elo Boa Viagem",
        "P": 7,
        "J": 9,
        "V": 2,
        "E": 1,
        "D": 6,
        "GP": 11,
        "GC": 28,
        "SG": -17,
        "Avg": 0.39,
        "%A": "25.9%",
    },
    {
        "Pos": "21º",
        "Equipe": "Escola Eleva Recife",
        "P": 6,
        "J": 8,
        "V": 2,
        "E": 0,
        "D": 6,
        "GP": 16,
        "GC": 44,
        "SG": -28,
        "Avg": 0.36,
        "%A": "25.0%",
    },
    {
        "Pos": "22º",
        "Equipe": "Colégio Motivo Boa Viagem",
        "P": 8,
        "J": 11,
        "V": 2,
        "E": 2,
        "D": 7,
        "GP": 18,
        "GC": 36,
        "SG": -18,
        "Avg": 0.50,
        "%A": "24.2%",
    },
    {
        "Pos": "23º",
        "Equipe": "Mackenzie Agnes B",
        "P": 5,
        "J": 8,
        "V": 0,
        "E": 0,
        "D": 8,
        "GP": 8,
        "GC": 40,
        "SG": -32,
        "Avg": 0.20,
        "%A": "20.8%",
    },
    {
        "Pos": "24º",
        "Equipe": "Colégio GGE C",
        "P": 8,
        "J": 13,
        "V": 2,
        "E": 0,
        "D": 11,
        "GP": 19,
        "GC": 48,
        "SG": -29,
        "Avg": 0.40,
        "%A": "20.5%",
    },
    {
        "Pos": "25º",
        "Equipe": "CBV Jaqueira",
        "P": 4,
        "J": 9,
        "V": 2,
        "E": 0,
        "D": 7,
        "GP": 17,
        "GC": 36,
        "SG": -19,
        "Avg": 0.47,
        "%A": "14.8%",
    },
    {
        "Pos": "26º",
        "Equipe": "Colégio Casa Forte",
        "P": 4,
        "J": 10,
        "V": 2,
        "E": 0,
        "D": 8,
        "GP": 11,
        "GC": 33,
        "SG": -22,
        "Avg": 0.33,
        "%A": "13.3%",
    },
    {
        "Pos": "27º",
        "Equipe": "Projeto Mangueira da Torre",
        "P": 0,
        "J": 11,
        "V": 1,
        "E": 0,
        "D": 10,
        "GP": 19,
        "GC": 53,
        "SG": -34,
        "Avg": 0.36,
        "%A": "0.0%",
    },
    {
        "Pos": "28º",
        "Equipe": "Colégio Santa Maria B",
        "P": 0,
        "J": 9,
        "V": 0,
        "E": 0,
        "D": 9,
        "GP": 4,
        "GC": 50,
        "SG": -46,
        "Avg": 0.08,
        "%A": "0.0%",
    },
]

TODOS_OS_JOGOS_OFICIAIS = [
    {
        "Jogo": "143",
        "Data": "08/04/2026",
        "Horário": "20:40",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "0 x 4",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Finalizado",
    },
    {
        "Jogo": "001",
        "Data": "13/04/2026",
        "Horário": "19:30",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Casa Forte",
        "Placar": "1 x 3",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "073",
        "Data": "13/04/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "Escola Eleva Recife",
        "Placar": "2 x 7",
        "Visitante": "Colégio Decisão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "185",
        "Data": "15/04/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE C",
        "Placar": "1 x 2",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "171",
        "Data": "16/04/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio Cognitivo",
        "Placar": "1 x 3",
        "Visitante": "Colégio GGE",
        "Status": "Finalizado",
    },
    {
        "Jogo": "002",
        "Data": "22/04/2026",
        "Horário": "19:30",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Eximius",
        "Placar": "1 x 1",
        "Visitante": "Colégio Piedade",
        "Status": "Finalizado",
    },
    {
        "Jogo": "059",
        "Data": "22/04/2026",
        "Horário": "19:30",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Apoio",
        "Placar": "3 x 5",
        "Visitante": "Escola Americana do Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "128",
        "Data": "22/04/2026",
        "Horário": "20:20",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "3 x 0",
        "Visitante": "Colégio Visão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "101",
        "Data": "22/04/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Núcleo",
        "Placar": "2 x 2",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "156",
        "Data": "22/04/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "4 x 2",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "157",
        "Data": "24/04/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "0 x 2",
        "Visitante": "Colégio Santa Maria",
        "Status": "Finalizado",
    },
    {
        "Jogo": "114",
        "Data": "24/04/2026",
        "Horário": "19:01",
        "Local": "Colégio Marista São Luis",
        "Mandante": "CBV Jaqueira",
        "Placar": "0 x 7",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Finalizado",
    },
    {
        "Jogo": "044",
        "Data": "27/04/2026",
        "Horário": "18:30",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "7 x 1",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "116",
        "Data": "27/04/2026",
        "Horário": "20:40",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Marista São Luis",
        "Placar": "3 x 0",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "170",
        "Data": "29/04/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Elo Boa Viagem",
        "Placar": "0 x 4",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "086",
        "Data": "29/04/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Equipe",
        "Placar": "2 x 1",
        "Visitante": "Colégio São José - Abreu e Lima",
        "Status": "Finalizado",
    },
    {
        "Jogo": "072",
        "Data": "29/04/2026",
        "Horário": "20:40",
        "Local": "Colégio Santa Maria",
        "Mandante": "Escola Bem-me-quer",
        "Placar": "5 x 1",
        "Visitante": "Escola Eleva Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "130",
        "Data": "29/04/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "2 x 0",
        "Visitante": "Colégio Visão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "033",
        "Data": "29/04/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "8 x 5",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "144",
        "Data": "30/04/2026",
        "Horário": "19:30",
        "Local": "Colégio Santa Maria",
        "Mandante": "CBV Jaqueira",
        "Placar": "3 x 1",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "186",
        "Data": "30/04/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "6 x 3",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "188",
        "Data": "04/05/2026",
        "Horário": "19:00",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "3 x 2",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "003",
        "Data": "04/05/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "1 x 3",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "175",
        "Data": "04/05/2026",
        "Horário": "20:40",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Cognitivo",
        "Placar": "0 x 2",
        "Visitante": "Colégio GGE B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "087",
        "Data": "04/05/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "3 x 3",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Finalizado",
    },
    {
        "Jogo": "158",
        "Data": "06/05/2026",
        "Horário": "19:00",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "0 x 5",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "142",
        "Data": "06/05/2026",
        "Horário": "20:40",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "8 x 1",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "118",
        "Data": "08/05/2026",
        "Horário": "19:00",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Decisão",
        "Placar": "5 x 3",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Finalizado",
    },
    {
        "Jogo": "004",
        "Data": "13/05/2026",
        "Horário": "20:10",
        "Local": "Colégio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "3 x 0",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "148",
        "Data": "13/05/2026",
        "Horário": "20:40",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Decisão",
        "Placar": "9 x 1",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "200",
        "Data": "13/05/2026",
        "Horário": "20:50",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colégio Elo Boa Viagem",
        "Placar": "0 x 0",
        "Visitante": "Colegio Grande Passo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "132",
        "Data": "15/05/2026",
        "Horário": "20:10",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Visão",
        "Placar": "0 x 4",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Finalizado",
    },
    {
        "Jogo": "036",
        "Data": "15/05/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "4 x 0",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "076",
        "Data": "18/05/2026",
        "Horário": "20:10",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "5 x 1",
        "Visitante": "Colégio Casa Forte",
        "Status": "Finalizado",
    },
    {
        "Jogo": "198",
        "Data": "18/05/2026",
        "Horário": "21:00",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "2 x 4",
        "Visitante": "Colegio Grande Passo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "018",
        "Data": "19/05/2026",
        "Horário": "20:10",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "4 x 2",
        "Visitante": "Projeto Mangueira da Torre",
        "Status": "Finalizado",
    },
    {
        "Jogo": "005",
        "Data": "20/05/2026",
        "Horário": "19:30",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Elo Boa Viagem",
        "Placar": "0 x 3",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "159",
        "Data": "20/05/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "CBV Jaqueira",
        "Placar": "1 x 6",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "184",
        "Data": "20/05/2026",
        "Horário": "20:50",
        "Local": "Colégio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "3 x 0",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "147",
        "Data": "21/05/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "0 x 4",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Finalizado",
    },
    {
        "Jogo": "058",
        "Data": "21/05/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Decisão",
        "Placar": "3 x 3",
        "Visitante": "Colégio Apoio",
        "Status": "Finalizado",
    },
    {
        "Jogo": "189",
        "Data": "25/05/2026",
        "Horário": "18:20",
        "Local": "GGE Benfica",
        "Mandante": "CBV Jaqueira",
        "Placar": "5 x 3",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "034",
        "Data": "25/05/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes B",
        "Placar": "0 x 5",
        "Visitante": "Colégio Damas",
        "Status": "Finalizado",
    },
    {
        "Jogo": "006",
        "Data": "25/05/2026",
        "Horário": "19:10",
        "Local": "GGE Benfica",
        "Mandante": "Colégio GGE",
        "Placar": "5 x 2",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "077",
        "Data": "25/05/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "0 x 1",
        "Visitante": "Colégio Piedade",
        "Status": "Finalizado",
    },
    {
        "Jogo": "100",
        "Data": "25/05/2026",
        "Horário": "20:50",
        "Local": "GGE Benfica",
        "Mandante": "Colégio GGE B",
        "Placar": "0 x 8",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "048",
        "Data": "25/05/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Apoio",
        "Placar": "5 x 0",
        "Visitante": "Projeto Mangueira da Torre",
        "Status": "Finalizado",
    },
    {
        "Jogo": "074",
        "Data": "26/05/2026",
        "Horário": "19:00",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "8 x 3",
        "Visitante": "Escola Eleva Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "201",
        "Data": "26/05/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "4 x 1",
        "Visitante": "Colegio Grande Passo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "145",
        "Data": "27/05/2026",
        "Horário": "19:00",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "0 x 5",
        "Visitante": "Colégio GGE B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "187",
        "Data": "27/05/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "1 x 2",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "173",
        "Data": "27/05/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "4 x 1",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "019",
        "Data": "27/05/2026",
        "Horário": "21:00",
        "Local": "Colégio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "6 x 0",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "161",
        "Data": "28/05/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "1 x 2",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "021",
        "Data": "28/05/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "3 x 0",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "190",
        "Data": "28/05/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "3 x 0",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "031",
        "Data": "29/05/2026",
        "Horário": "19:50",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Casa Forte",
        "Placar": "2 x 1",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "117",
        "Data": "29/05/2026",
        "Horário": "20:40",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Marista São Luis",
        "Placar": "5 x 3",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Finalizado",
    },
    {
        "Jogo": "133",
        "Data": "30/05/2026",
        "Horário": "09:40",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Visão",
        "Placar": "3 x 3",
        "Visitante": "Colégio Decisão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "160",
        "Data": "01/06/2026",
        "Horário": "18:50",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "3 x 3",
        "Visitante": "Colégio GGE B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "008",
        "Data": "01/06/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Eximius",
        "Placar": "6 x 2",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Finalizado",
    },
    {
        "Jogo": "088",
        "Data": "01/06/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Decisão",
        "Placar": "1 x 2",
        "Visitante": "Colégio São José - Abreu e Lima",
        "Status": "Finalizado",
    },
    {
        "Jogo": "104",
        "Data": "02/06/2026",
        "Horário": "19:50",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "0 x 1",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "020",
        "Data": "02/06/2026",
        "Horário": "20:10",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "3 x 1",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "172",
        "Data": "03/06/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "2 x 1",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "049",
        "Data": "03/06/2026",
        "Horário": "20:10",
        "Local": "Colégio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "0 x 1",
        "Visitante": "Colégio Apoio",
        "Status": "Finalizado",
    },
    {
        "Jogo": "176",
        "Data": "08/06/2026",
        "Horário": "19:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Equipe",
        "Placar": "0 x 1",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "032",
        "Data": "08/06/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes B",
        "Placar": "0 x 6",
        "Visitante": "Colégio Piedade",
        "Status": "Finalizado",
    },
    {
        "Jogo": "119",
        "Data": "08/06/2026",
        "Horário": "19:50",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Marista São Luis",
        "Placar": "4 x 3",
        "Visitante": "Escola Americana do Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "103",
        "Data": "08/06/2026",
        "Horário": "20:40",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Núcleo",
        "Placar": "3 x 2",
        "Visitante": "Colégio Decisão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "174",
        "Data": "09/06/2026",
        "Horário": "19:20",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "CBV Jaqueira",
        "Placar": "4 x 5",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "115",
        "Data": "09/06/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "1 x 3",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Finalizado",
    },
    {
        "Jogo": "134",
        "Data": "09/06/2026",
        "Horário": "20:10",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "2 x 0",
        "Visitante": "Colégio Visão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "146",
        "Data": "10/06/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Equipe",
        "Placar": "5 x 0",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "204",
        "Data": "11/06/2026",
        "Horário": "20:20",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colegio Grande Passo",
        "Placar": "2 x 1",
        "Visitante": "CBV Jaqueira",
        "Status": "Finalizado",
    },
    {
        "Jogo": "102",
        "Data": "15/06/2026",
        "Horário": "19:50",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Escola Bem-me-quer",
        "Placar": "2 x 1",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "203",
        "Data": "15/06/2026",
        "Horário": "20:40",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "2 x 1",
        "Visitante": "Colegio Grande Passo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "046",
        "Data": "16/06/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Colégio Apoio",
        "Placar": "4 x 1",
        "Visitante": "Colégio Casa Forte",
        "Status": "Finalizado",
    },
    {
        "Jogo": "089",
        "Data": "17/06/2026",
        "Horário": "19:00",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "1 x 2",
        "Visitante": "Colégio São José - Abreu e Lima",
        "Status": "Finalizado",
    },
    {
        "Jogo": "202",
        "Data": "17/06/2026",
        "Horário": "19:30",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "3 x 0",
        "Visitante": "Colegio Grande Passo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "199",
        "Data": "18/06/2026",
        "Horário": "19:30",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colegio Grande Passo",
        "Placar": "0 x 1",
        "Visitante": "Colégio Damas",
        "Status": "Finalizado",
    },
    {
        "Jogo": "017",
        "Data": "18/06/2026",
        "Horário": "20:20",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colégio Piedade",
        "Placar": "2 x 1",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "007",
        "Data": "18/06/2026",
        "Horário": "20:20",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "11 x 0",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "131",
        "Data": "26/06/2026",
        "Horário": "20:00",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Visão",
        "Placar": "5 x 5",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "061",
        "Data": "06/08/2026",
        "Horário": "19:10",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Casa Forte",
        "Placar": "0 x 1",
        "Visitante": "Escola Eleva Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "129",
        "Data": "06/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Eximius",
        "Mandante": "CBV Jaqueira",
        "Placar": "2 x 5",
        "Visitante": "Colégio Visão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "163",
        "Data": "10/08/2026",
        "Horário": "18:00",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "3 x 2",
        "Visitante": "Colégio Decisão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "078",
        "Data": "10/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "4 x 0",
        "Visitante": "Projeto Mangueira da Torre",
        "Status": "Finalizado",
    },
    {
        "Jogo": "092",
        "Data": "10/08/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Núcleo",
        "Placar": "5 x 1",
        "Visitante": "Colégio Piedade",
        "Status": "Finalizado",
    },
    {
        "Jogo": "207",
        "Data": "11/08/2026",
        "Horário": "20:20",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colegio Grande Passo",
        "Placar": "3 x 3",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Finalizado",
    },
    {
        "Jogo": "047",
        "Data": "12/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Piedade",
        "Placar": "4 x 1",
        "Visitante": "Colégio Apoio",
        "Status": "Finalizado",
    },
    {
        "Jogo": "063",
        "Data": "12/08/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "1 x 4",
        "Visitante": "Escola Eleva Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "081",
        "Data": "13/08/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "1 x 0",
        "Visitante": "Colégio São José - Abreu e Lima",
        "Status": "Finalizado",
    },
    {
        "Jogo": "035",
        "Data": "17/08/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes B",
        "Placar": "1 x 6",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "149",
        "Data": "19/08/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "1 x 9",
        "Visitante": "Escola Americana do Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "080",
        "Data": "19/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "4 x 0",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "193",
        "Data": "19/08/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE C",
        "Placar": "2 x 3",
        "Visitante": "Colégio Decisão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "067",
        "Data": "19/08/2026",
        "Horário": "20:40",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "8 x 0",
        "Visitante": "Escola Eleva Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "051",
        "Data": "19/08/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "2 x 2",
        "Visitante": "Colégio Apoio",
        "Status": "Finalizado",
    },
    {
        "Jogo": "093",
        "Data": "19/08/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "2 x 8",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "010",
        "Data": "21/08/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "2 x 1",
        "Visitante": "Colégio Eximius",
        "Status": "Finalizado",
    },
    {
        "Jogo": "192",
        "Data": "21/08/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Escola Bem-me-quer",
        "Placar": "2 x 1",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "068",
        "Data": "24/08/2026",
        "Horário": "19:00",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Escola Eleva Recife",
        "Placar": "3 x 10",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Finalizado",
    },
    {
        "Jogo": "054",
        "Data": "24/08/2026",
        "Horário": "19:30",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Apoio",
        "Placar": "3 x 0",
        "Visitante": "CBV Jaqueira",
        "Status": "Finalizado",
    },
    {
        "Jogo": "153",
        "Data": "24/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "1 x 9",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "028",
        "Data": "24/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Decisão",
        "Placar": "6 x 1",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "106",
        "Data": "24/08/2026",
        "Horário": "20:20",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Marista São Luis",
        "Placar": "7 x 1",
        "Visitante": "Colégio Casa Forte",
        "Status": "Finalizado",
    },
    {
        "Jogo": "179",
        "Data": "24/08/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Cognitivo",
        "Placar": "1 x 5",
        "Visitante": "Escola Americana do Recife",
        "Status": "Finalizado",
    },
    {
        "Jogo": "026",
        "Data": "25/08/2026",
        "Horário": "20:00",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "4 x 4",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "094",
        "Data": "25/08/2026",
        "Horário": "20:50",
        "Local": "Colegio Damas",
        "Mandante": "Colégio Núcleo",
        "Placar": "2 x 0",
        "Visitante": "Colégio Damas",
        "Status": "Finalizado",
    },
    {
        "Jogo": "155",
        "Data": "26/08/2026",
        "Horário": "19:10",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "9 x 1",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "082",
        "Data": "26/08/2026",
        "Horário": "20:20",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "1 x 3",
        "Visitante": "Colégio Santa Maria",
        "Status": "Finalizado",
    },
    {
        "Jogo": "121",
        "Data": "27/08/2026",
        "Horário": "20:50",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Casa Forte",
        "Placar": "1 x 4",
        "Visitante": "Colégio Visão",
        "Status": "Finalizado",
    },
    {
        "Jogo": "178",
        "Data": "28/08/2026",
        "Horário": "20:50",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Decisão",
        "Placar": "3 x 0",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "182",
        "Data": "31/08/2026",
        "Horário": "19:00",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Piedade",
        "Placar": "5 x 1",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "095",
        "Data": "31/08/2026",
        "Horário": "19:50",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Boa Viagem",
        "Placar": "1 x 3",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "023",
        "Data": "31/08/2026",
        "Horário": "20:40",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "2 x 0",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "164",
        "Data": "01/09/2026",
        "Horário": "18:30",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "3 x 2",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "091",
        "Data": "01/09/2026",
        "Horário": "19:20",
        "Local": "Escola Americana do Recife",
        "Mandante": "Colégio Casa Forte",
        "Placar": "1 x 4",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "191",
        "Data": "01/09/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE C",
        "Placar": "1 x 6",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "066",
        "Data": "02/09/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Escola Eleva Recife",
        "Placar": "2 x 5",
        "Visitante": "Colégio GGE",
        "Status": "Finalizado",
    },
    {
        "Jogo": "109",
        "Data": "03/09/2026",
        "Horário": "20:00",
        "Local": "Colegio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "1 x 3",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Finalizado",
    },
    {
        "Jogo": "194",
        "Data": "08/09/2026",
        "Horário": "18:30",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "8 x 1",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "168",
        "Data": "08/09/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Colégio Cognitivo",
        "Placar": "5 x 1",
        "Visitante": "Projeto Mangueira da Torre",
        "Status": "Finalizado",
    },
    {
        "Jogo": "152",
        "Data": "08/09/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "1 x 2",
        "Visitante": "Colégio Piedade",
        "Status": "Finalizado",
    },
    {
        "Jogo": "022",
        "Data": "08/09/2026",
        "Horário": "20:00",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "2 x 3",
        "Visitante": "Colégio Santa Maria",
        "Status": "Finalizado",
    },
    {
        "Jogo": "079",
        "Data": "08/09/2026",
        "Horário": "20:50",
        "Local": "Colegio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "1 x 3",
        "Visitante": "Colégio São José - Abreu e Lima",
        "Status": "Finalizado",
    },
    {
        "Jogo": "040",
        "Data": "09/09/2026",
        "Horário": "18:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes B",
        "Placar": "0 x 2",
        "Visitante": "Colégio GGE B",
        "Status": "Finalizado",
    },
    {
        "Jogo": "151",
        "Data": "09/09/2026",
        "Horário": "19:10",
        "Local": "Mackenzie Agnes",
        "Mandante": "Colégio Casa Forte",
        "Placar": "0 x 4",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "096",
        "Data": "09/09/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio Núcleo",
        "Placar": "3 x 1",
        "Visitante": "Colégio GGE",
        "Status": "Finalizado",
    },
    {
        "Jogo": "083",
        "Data": "09/09/2026",
        "Horário": "20:20",
        "Local": "Colégio São José - Abreu e Lima",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "2 x 0",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Finalizado",
    },
    {
        "Jogo": "136",
        "Data": "10/09/2026",
        "Horário": "20:20",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "0 x 3",
        "Visitante": "Colégio Casa Forte",
        "Status": "Finalizado",
    },
    {
        "Jogo": "122",
        "Data": "10/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Visão",
        "Placar": "1 x 4",
        "Visitante": "Colégio Piedade",
        "Status": "Finalizado",
    },
    {
        "Jogo": "025",
        "Data": "10/09/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "2 x 2",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "169",
        "Data": "10/09/2026",
        "Horário": "20:50",
        "Local": "Colegio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "2 x 1",
        "Visitante": "Colégio Cognitivo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "162",
        "Data": "14/09/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Escola Bem-me-quer",
        "Placar": "1 x 1",
        "Visitante": "Mackenzie Agnes",
        "Status": "Finalizado",
    },
    {
        "Jogo": "084",
        "Data": "14/09/2026",
        "Horário": "19:30",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio São José - Abreu e Lima",
        "Placar": "4 x 1",
        "Visitante": "CBV Jaqueira",
        "Status": "Finalizado",
    },
    {
        "Jogo": "183",
        "Data": "14/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "1 x 2",
        "Visitante": "Colégio GGE C",
        "Status": "Finalizado",
    },
    {
        "Jogo": "197",
        "Data": "15/09/2026",
        "Horário": "19:30",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colégio Piedade",
        "Placar": "0 x 1",
        "Visitante": "Colegio Grande Passo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "097",
        "Data": "15/09/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "2 x 0",
        "Visitante": "Colégio Núcleo",
        "Status": "Finalizado",
    },
    {
        "Jogo": "027",
        "Data": "15/09/2026",
        "Horário": "20:00",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Escola Bem-me-quer",
        "Placar": "5 x 1",
        "Visitante": "Colégio Motivo Boa Viagem",
        "Status": "Finalizado",
    },
    {
        "Jogo": "056",
        "Data": "16/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Apoio",
        "Placar": "2 x 0",
        "Visitante": "Colégio Equipe",
        "Status": "Finalizado",
    },
    {
        "Jogo": "053",
        "Data": "17/09/2026",
        "Horário": "19:50",
        "Local": "Escola Americana do Recife",
        "Mandante": "Colégio Apoio",
        "Placar": "VS",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Agendado",
    },
    {
        "Jogo": "126",
        "Data": "17/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Visão",
        "Placar": "VS",
        "Visitante": "Colégio GGE",
        "Status": "Agendado",
    },
    {
        "Jogo": "069",
        "Data": "18/09/2026",
        "Horário": "19:00",
        "Local": "Colégio Marista São Luis",
        "Mandante": "CBV Jaqueira",
        "Placar": "VS",
        "Visitante": "Escola Eleva Recife",
        "Status": "Agendado",
    },
    {
        "Jogo": "055",
        "Data": "18/09/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "VS",
        "Visitante": "Colégio Apoio",
        "Status": "Agendado",
    },
    {
        "Jogo": "111",
        "Data": "18/09/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "VS",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Agendado",
    },
    {
        "Jogo": "098",
        "Data": "21/09/2026",
        "Horário": "19:30",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Núcleo",
        "Placar": "VS",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Agendado",
    },
    {
        "Jogo": "024",
        "Data": "21/09/2026",
        "Horário": "19:50",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "VS",
        "Visitante": "CBV Jaqueira",
        "Status": "Agendado",
    },
    {
        "Jogo": "041",
        "Data": "21/09/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Equipe",
        "Placar": "VS",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Agendado",
    },
    {
        "Jogo": "125",
        "Data": "21/09/2026",
        "Horário": "20:20",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Boa Viagem",
        "Placar": "VS",
        "Visitante": "Colégio Visão",
        "Status": "Agendado",
    },
    {
        "Jogo": "177",
        "Data": "21/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Cognitivo",
        "Placar": "VS",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Agendado",
    },
    {
        "Jogo": "009",
        "Data": "22/09/2026",
        "Horário": "19:50",
        "Local": "CBV Jaqueira",
        "Mandante": "CBV Jaqueira",
        "Placar": "VS",
        "Visitante": "Colégio Eximius",
        "Status": "Agendado",
    },
    {
        "Jogo": "167",
        "Data": "23/09/2026",
        "Horário": "19:00",
        "Local": "Escola Americana do Recife",
        "Mandante": "Colégio Piedade",
        "Placar": "VS",
        "Visitante": "Colégio Cognitivo",
        "Status": "Agendado",
    },
    {
        "Jogo": "014",
        "Data": "23/09/2026",
        "Horário": "19:50",
        "Local": "Escola Americana do Recife",
        "Mandante": "Colégio Eximius",
        "Placar": "VS",
        "Visitante": "Escola Americana do Recife",
        "Status": "Agendado",
    },
    {
        "Jogo": "127",
        "Data": "23/09/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "VS",
        "Visitante": "Colégio Visão",
        "Status": "Agendado",
    },
    {
        "Jogo": "206",
        "Data": "23/09/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Equipe",
        "Placar": "VS",
        "Visitante": "Colegio Grande Passo",
        "Status": "Agendado",
    },
    {
        "Jogo": "108",
        "Data": "23/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "VS",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Agendado",
    },
    {
        "Jogo": "196",
        "Data": "24/09/2026",
        "Horário": "19:30",
        "Local": "Colégio Grande Passo",
        "Mandante": "Colegio Grande Passo",
        "Placar": "VS",
        "Visitante": "Colégio Casa Forte",
        "Status": "Agendado",
    },
    {
        "Jogo": "140",
        "Data": "24/09/2026",
        "Horário": "20:20",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "VS",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Agendado",
    },
    {
        "Jogo": "064",
        "Data": "24/09/2026",
        "Horário": "20:40",
        "Local": "Colegio Damas",
        "Mandante": "Escola Eleva Recife",
        "Placar": "VS",
        "Visitante": "Colégio Damas",
        "Status": "Agendado",
    },
    {
        "Jogo": "110",
        "Data": "25/09/2026",
        "Horário": "19:00",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Marista São Luis",
        "Placar": "VS",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Agendado",
    },
    {
        "Jogo": "042",
        "Data": "25/09/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes B",
        "Placar": "VS",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Agendado",
    },
    {
        "Jogo": "037",
        "Data": "28/09/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Colégio Santa Maria",
        "Placar": "VS",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Agendado",
    },
    {
        "Jogo": "099",
        "Data": "28/09/2026",
        "Horário": "19:30",
        "Local": "Colégio Eximius",
        "Mandante": "CBV Jaqueira",
        "Placar": "VS",
        "Visitante": "Colégio Núcleo",
        "Status": "Agendado",
    },
    {
        "Jogo": "013",
        "Data": "28/09/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Decisão",
        "Placar": "VS",
        "Visitante": "Colégio Eximius",
        "Status": "Agendado",
    },
    {
        "Jogo": "065",
        "Data": "28/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Elo Boa Viagem",
        "Placar": "VS",
        "Visitante": "Escola Eleva Recife",
        "Status": "Agendado",
    },
    {
        "Jogo": "209",
        "Data": "29/09/2026",
        "Horário": "18:30",
        "Local": "Escola Americana do Recife",
        "Mandante": "Escola Americana do Recife",
        "Placar": "VS",
        "Visitante": "Colegio Grande Passo",
        "Status": "Agendado",
    },
    {
        "Jogo": "016",
        "Data": "29/09/2026",
        "Horário": "20:00",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "VS",
        "Visitante": "Colégio Casa Forte",
        "Status": "Agendado",
    },
    {
        "Jogo": "139",
        "Data": "30/09/2026",
        "Horário": "20:00",
        "Local": "Colegio Damas",
        "Mandante": "Colégio Damas",
        "Placar": "VS",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Agendado",
    },
    {
        "Jogo": "071",
        "Data": "30/09/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Equipe",
        "Placar": "VS",
        "Visitante": "Escola Eleva Recife",
        "Status": "Agendado",
    },
    {
        "Jogo": "039",
        "Data": "30/09/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "CBV Jaqueira",
        "Placar": "VS",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Agendado",
    },
    {
        "Jogo": "208",
        "Data": "30/09/2026",
        "Horário": "20:20",
        "Local": "Colegio Grande Passo",
        "Mandante": "Colégio Decisão",
        "Placar": "VS",
        "Visitante": "Colegio Grande Passo",
        "Status": "Agendado",
    },
    {
        "Jogo": "166",
        "Data": "30/09/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Cognitivo",
        "Placar": "VS",
        "Visitante": "Colégio Casa Forte",
        "Status": "Agendado",
    },
    {
        "Jogo": "052",
        "Data": "01/10/2026",
        "Horário": "19:50",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Apoio",
        "Placar": "VS",
        "Visitante": "Colégio Santa Maria",
        "Status": "Agendado",
    },
    {
        "Jogo": "137",
        "Data": "01/10/2026",
        "Horário": "20:40",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Piedade",
        "Placar": "VS",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Agendado",
    },
    {
        "Jogo": "124",
        "Data": "01/10/2026",
        "Horário": "20:50",
        "Local": "Colégio Visão",
        "Mandante": "Colégio Visão",
        "Placar": "VS",
        "Visitante": "Colégio Damas",
        "Status": "Agendado",
    },
    {
        "Jogo": "043",
        "Data": "02/10/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Colégio Decisão",
        "Placar": "VS",
        "Visitante": "Mackenzie Agnes B",
        "Status": "Agendado",
    },
    {
        "Jogo": "107",
        "Data": "02/10/2026",
        "Horário": "19:50",
        "Local": "Colégio Marista São Luis",
        "Mandante": "Colégio Piedade",
        "Placar": "VS",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Agendado",
    },
    {
        "Jogo": "050",
        "Data": "02/10/2026",
        "Horário": "20:00",
        "Local": "Colégio Equipe",
        "Mandante": "Colégio Apoio",
        "Placar": "VS",
        "Visitante": "Colégio Elo Boa Viagem",
        "Status": "Agendado",
    },
    {
        "Jogo": "181",
        "Data": "02/10/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio Casa Forte",
        "Placar": "VS",
        "Visitante": "Colégio GGE C",
        "Status": "Agendado",
    },
    {
        "Jogo": "011",
        "Data": "02/10/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio Equipe",
        "Placar": "VS",
        "Visitante": "Colégio Eximius",
        "Status": "Agendado",
    },
    {
        "Jogo": "085",
        "Data": "02/10/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE B",
        "Placar": "VS",
        "Visitante": "Colégio São José - Abreu e Lima",
        "Status": "Agendado",
    },
    {
        "Jogo": "112",
        "Data": "05/10/2026",
        "Horário": "19:30",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria",
        "Placar": "VS",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Agendado",
    },
    {
        "Jogo": "123",
        "Data": "05/10/2026",
        "Horário": "20:50",
        "Local": "Colégio Equipe",
        "Mandante": "Projeto Mangueira da Torre",
        "Placar": "VS",
        "Visitante": "Colégio Visão",
        "Status": "Agendado",
    },
    {
        "Jogo": "154",
        "Data": "06/10/2026",
        "Horário": "18:30",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes",
        "Placar": "VS",
        "Visitante": "Colégio Damas",
        "Status": "Agendado",
    },
    {
        "Jogo": "038",
        "Data": "06/10/2026",
        "Horário": "19:20",
        "Local": "Mackenzie Agnes",
        "Mandante": "Mackenzie Agnes B",
        "Placar": "VS",
        "Visitante": "Colégio Elo Cordeiro",
        "Status": "Agendado",
    },
    {
        "Jogo": "062",
        "Data": "06/10/2026",
        "Horário": "19:30",
        "Local": "Colegio Grande Passo",
        "Mandante": "Escola Eleva Recife",
        "Placar": "VS",
        "Visitante": "Colégio Piedade",
        "Status": "Agendado",
    },
    {
        "Jogo": "205",
        "Data": "06/10/2026",
        "Horário": "20:20",
        "Local": "Colegio Grande Passo",
        "Mandante": "Colegio Grande Passo",
        "Placar": "VS",
        "Visitante": "Colégio GGE B",
        "Status": "Agendado",
    },
    {
        "Jogo": "029",
        "Data": "06/10/2026",
        "Horário": "20:50",
        "Local": "Colégio Motivo Boa Viagem",
        "Mandante": "Colégio Motivo Boa Viagem",
        "Placar": "VS",
        "Visitante": "Escola Americana do Recife",
        "Status": "Agendado",
    },
    {
        "Jogo": "113",
        "Data": "07/10/2026",
        "Horário": "19:30",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Colégio Elo Cordeiro",
        "Placar": "VS",
        "Visitante": "Colégio Marista São Luis",
        "Status": "Agendado",
    },
    {
        "Jogo": "070",
        "Data": "07/10/2026",
        "Horário": "20:00",
        "Local": "GGE Boa Viagem",
        "Mandante": "Escola Eleva Recife",
        "Placar": "VS",
        "Visitante": "Colégio GGE B",
        "Status": "Agendado",
    },
    {
        "Jogo": "057",
        "Data": "07/10/2026",
        "Horário": "20:20",
        "Local": "Colégio Elo Cordeiro",
        "Mandante": "Escola Bem-me-quer",
        "Placar": "VS",
        "Visitante": "Colégio Apoio",
        "Status": "Agendado",
    },
    {
        "Jogo": "141",
        "Data": "07/10/2026",
        "Horário": "20:50",
        "Local": "GGE Boa Viagem",
        "Mandante": "Colégio GGE",
        "Placar": "VS",
        "Visitante": "Colégio Santa Maria B",
        "Status": "Agendado",
    },
    {
        "Jogo": "012",
        "Data": "08/10/2026",
        "Horário": "20:20",
        "Local": "Colégio Eximius",
        "Mandante": "Colégio Eximius",
        "Placar": "VS",
        "Visitante": "Escola Bem-me-quer",
        "Status": "Agendado",
    },
    {
        "Jogo": "138",
        "Data": "08/10/2026",
        "Horário": "20:20",
        "Local": "Colégio Santa Maria",
        "Mandante": "Colégio Santa Maria B",
        "Placar": "VS",
        "Visitante": "Projeto Mangueira da Torre",
        "Status": "Agendado",
    },
]


# -----------------------------------------------------------------------------
# FUNÇÕES DE PROCESSAMENTO
# -----------------------------------------------------------------------------
def padronizar_nome_escola(nome):
    if not nome:
        return nome
    nome_clean = str(nome).strip()
    for k, v in PADRAO_NOMES_EQUIPES.items():
        if re.search(r"\b" + re.escape(k) + r"\b", nome_clean, re.IGNORECASE):
            return v
    return nome_clean


def obter_tabelas_classificacao_oficiais():
    df_ga = pd.DataFrame(
        [
            {
                "Pos": "1º",
                "Equipe": "Colégio GGE",
                "P": 28,
                "J": 11,
                "V": 9,
                "E": 1,
                "D": 1,
                "GP": 38,
                "GC": 16,
                "SG": 22,
                "Avg": 2.38,
                "%A": "89.9%",
            },
            {
                "Pos": "2º",
                "Equipe": "Colégio Santa Maria",
                "P": 27,
                "J": 10,
                "V": 9,
                "E": 0,
                "D": 1,
                "GP": 43,
                "GC": 7,
                "SG": 36,
                "Avg": 6.14,
                "%A": "89.9%",
            },
            {
                "Pos": "3º",
                "Equipe": "Escola Americana do Recife",
                "P": 24,
                "J": 11,
                "V": 8,
                "E": 0,
                "D": 3,
                "GP": 51,
                "GC": 19,
                "SG": 32,
                "Avg": 2.68,
                "%A": "89.9%",
            },
            {
                "Pos": "4º",
                "Equipe": "Escola Bem-me-quer",
                "P": 22,
                "J": 10,
                "V": 6,
                "E": 3,
                "D": 1,
                "GP": 32,
                "GC": 16,
                "SG": 16,
                "Avg": 2.00,
                "%A": "89.9%",
            },
            {
                "Pos": "5º",
                "Equipe": "Colégio Decisão",
                "P": 22,
                "J": 11,
                "V": 6,
                "E": 2,
                "D": 3,
                "GP": 44,
                "GC": 23,
                "SG": 21,
                "Avg": 1.91,
                "%A": "89.9%",
            },
            {
                "Pos": "6º",
                "Equipe": "Colégio Piedade",
                "P": 21,
                "J": 10,
                "V": 7,
                "E": 1,
                "D": 2,
                "GP": 26,
                "GC": 12,
                "SG": 14,
                "Avg": 2.17,
                "%A": "89.9%",
            },
            {
                "Pos": "7º",
                "Equipe": "Colégio Elo Cordeiro",
                "P": 21,
                "J": 10,
                "V": 7,
                "E": 0,
                "D": 3,
                "GP": 30,
                "GC": 20,
                "SG": 10,
                "Avg": 1.50,
                "%A": "89.9%",
            },
            {
                "Pos": "8º",
                "Equipe": "Colégio GGE B",
                "P": 21,
                "J": 10,
                "V": 6,
                "E": 2,
                "D": 2,
                "GP": 22,
                "GC": 17,
                "SG": 5,
                "Avg": 1.29,
                "%A": "89.9%",
            },
            {
                "Pos": "9º",
                "Equipe": "Colégio Damas",
                "P": 20,
                "J": 10,
                "V": 6,
                "E": 0,
                "D": 4,
                "GP": 22,
                "GC": 10,
                "SG": 12,
                "Avg": 2.20,
                "%A": "89.9%",
            },
            {
                "Pos": "10º",
                "Equipe": "Colégio Equipe",
                "P": 17,
                "J": 9,
                "V": 4,
                "E": 3,
                "D": 2,
                "GP": 26,
                "GC": 18,
                "SG": 8,
                "Avg": 1.44,
                "%A": "89.9%",
            },
            {
                "Pos": "11º",
                "Equipe": "Colégio Elo Boa Viagem",
                "P": 7,
                "J": 9,
                "V": 2,
                "E": 1,
                "D": 6,
                "GP": 11,
                "GC": 28,
                "SG": -17,
                "Avg": 0.39,
                "%A": "89.9%",
            },
            {
                "Pos": "12º",
                "Equipe": "CBV Jaqueira",
                "P": 4,
                "J": 9,
                "V": 2,
                "E": 0,
                "D": 7,
                "GP": 17,
                "GC": 36,
                "SG": -19,
                "Avg": 0.47,
                "%A": "89.9%",
            },
            {
                "Pos": "13º",
                "Equipe": "Colégio Casa Forte",
                "P": 4,
                "J": 10,
                "V": 2,
                "E": 0,
                "D": 8,
                "GP": 11,
                "GC": 33,
                "SG": -22,
                "Avg": 0.33,
                "%A": "89.9%",
            },
            {
                "Pos": "14º",
                "Equipe": "Projeto Mangueira da Torre",
                "P": 0,
                "J": 11,
                "V": 1,
                "E": 0,
                "D": 10,
                "GP": 19,
                "GC": 53,
                "SG": -34,
                "Avg": 0.36,
                "%A": "0.00%",
            },
        ]
    )
    df_gb = pd.DataFrame(
        [
            {
                "Pos": "1º",
                "Equipe": "Colégio Núcleo",
                "P": 28,
                "J": 12,
                "V": 9,
                "E": 1,
                "D": 2,
                "GP": 40,
                "GC": 14,
                "SG": 26,
                "Avg": 2.86,
                "%A": "89.9%",
            },
            {
                "Pos": "2º",
                "Equipe": "Colégio São José - Abreu e Lima",
                "P": 24,
                "J": 13,
                "V": 8,
                "E": 1,
                "D": 4,
                "GP": 31,
                "GC": 15,
                "SG": 16,
                "Avg": 2.07,
                "%A": "89.9%",
            },
            {
                "Pos": "3º",
                "Equipe": "Colégio Marista São Luis",
                "P": 21,
                "J": 8,
                "V": 7,
                "E": 0,
                "D": 1,
                "GP": 35,
                "GC": 14,
                "SG": 21,
                "Avg": 2.50,
                "%A": "89.9%",
            },
            {
                "Pos": "4º",
                "Equipe": "Mackenzie Agnes",
                "P": 21,
                "J": 13,
                "V": 6,
                "E": 2,
                "D": 5,
                "GP": 46,
                "GC": 22,
                "SG": 24,
                "Avg": 2.09,
                "%A": "89.9%",
            },
            {
                "Pos": "5º",
                "Equipe": "Colégio Apoio",
                "P": 15,
                "J": 8,
                "V": 4,
                "E": 2,
                "D": 2,
                "GP": 22,
                "GC": 15,
                "SG": 7,
                "Avg": 1.47,
                "%A": "89.9%",
            },
            {
                "Pos": "6º",
                "Equipe": "Colegio Grande Passo",
                "P": 13,
                "J": 9,
                "V": 3,
                "E": 2,
                "D": 4,
                "GP": 12,
                "GC": 16,
                "SG": -4,
                "Avg": 0.75,
                "%A": "89.9%",
            },
            {
                "Pos": "7º",
                "Equipe": "Colégio Eximius",
                "P": 13,
                "J": 9,
                "V": 4,
                "E": 1,
                "D": 4,
                "GP": 19,
                "GC": 26,
                "SG": -7,
                "Avg": 0.73,
                "%A": "89.9%",
            },
            {
                "Pos": "8º",
                "Equipe": "Colégio Cognitivo",
                "P": 12,
                "J": 11,
                "V": 4,
                "E": 0,
                "D": 7,
                "GP": 20,
                "GC": 26,
                "SG": -6,
                "Avg": 0.77,
                "%A": "89.9%",
            },
            {
                "Pos": "9º",
                "Equipe": "Colégio Visão",
                "P": 11,
                "J": 9,
                "V": 2,
                "E": 2,
                "D": 5,
                "GP": 18,
                "GC": 26,
                "SG": -8,
                "Avg": 0.69,
                "%A": "89.9%",
            },
            {
                "Pos": "10º",
                "Equipe": "Colégio Motivo Boa Viagem",
                "P": 8,
                "J": 11,
                "V": 2,
                "E": 2,
                "D": 7,
                "GP": 18,
                "GC": 36,
                "SG": -18,
                "Avg": 0.50,
                "%A": "89.9%",
            },
            {
                "Pos": "11º",
                "Equipe": "Colégio GGE C",
                "P": 8,
                "J": 13,
                "V": 2,
                "E": 0,
                "D": 11,
                "GP": 19,
                "GC": 48,
                "SG": -29,
                "Avg": 0.40,
                "%A": "89.9%",
            },
            {
                "Pos": "12º",
                "Equipe": "Escola Eleva Recife",
                "P": 6,
                "J": 8,
                "V": 2,
                "E": 0,
                "D": 6,
                "GP": 16,
                "GC": 44,
                "SG": -28,
                "Avg": 0.36,
                "%A": "89.9%",
            },
            {
                "Pos": "13º",
                "Equipe": "Mackenzie Agnes B",
                "P": 5,
                "J": 8,
                "V": 0,
                "E": 0,
                "D": 8,
                "GP": 8,
                "GC": 40,
                "SG": -32,
                "Avg": 0.20,
                "%A": "89.9%",
            },
            {
                "Pos": "14º",
                "Equipe": "Colégio Santa Maria B",
                "P": 0,
                "J": 9,
                "V": 0,
                "E": 0,
                "D": 9,
                "GP": 4,
                "GC": 50,
                "SG": -46,
                "Avg": 0.08,
                "%A": "0.00%",
            },
        ]
    )
    return df_ga, df_gb


# -----------------------------------------------------------------------------
# BARRA LATERAL E FILTROS COM SUPORTE A SESSION STATE
# -----------------------------------------------------------------------------
df_grupo_a, df_grupo_b = obter_tabelas_classificacao_oficiais()
df_geral_oficial = pd.DataFrame(DADOS_CLASSIFICACAO_GERAL)

df_artilharia_oficial = pd.DataFrame(
    [
        {
            "Posição": item["Pos"],
            "Nome do Atleta": item["Atleta"],
            "Equipe": padronizar_nome_escola(item["Equipe"]),
            "Qtde. de Gols": item["Gols"],
        }
        for item in DADOS_ARTILHARIA
    ]
)

df_cartoes_amarelos = pd.DataFrame(
    [
        {
            "Atleta": item["Atleta"],
            "Equipe": padronizar_nome_escola(item["Equipe"]),
            "Cartões": item["Cartões"],
        }
        for item in DADOS_CARTOES_AMARELOS
    ]
)

df_cartoes_vermelhos = pd.DataFrame(
    [
        {
            "Atleta": item["Atleta"],
            "Equipe": padronizar_nome_escola(item["Equipe"]),
            "Cartões": item["Cartões"],
        }
        for item in DADOS_CARTOES_VERMELHOS
    ]
)

df_jogos = pd.DataFrame(TODOS_OS_JOGOS_OFICIAIS)

lista_equipes = sorted(
    list(set(df_grupo_a["Equipe"].tolist() + df_grupo_b["Equipe"].tolist()))
)

st.sidebar.image(
    "https://ritmo-images.s3.amazonaws.com/images/Organizador/353.jpeg",
    use_container_width=True,
)
st.sidebar.header("⚙️ Opções de Consulta")

if st.sidebar.button("🧹 Limpar Filtros", use_container_width=True):
    st.session_state["fase_sel"] = list(FASES_CLASSIFICACAO.keys())[0]
    st.session_state["grupo_sel"] = "Todos os Grupos"
    st.session_state["equipe_sel"] = "Todas as Equipes"
    st.rerun()

fase_selecionada = st.sidebar.selectbox(
    "Fase do Campeonato:",
    options=list(FASES_CLASSIFICACAO.keys()),
    key="fase_sel",
)

grupo_selecionado = st.sidebar.selectbox(
    "Filtrar por Grupo:",
    options=["Todos os Grupos", "Grupo A", "Grupo B"],
    key="grupo_sel",
)

url_classificacao_atual = FASES_CLASSIFICACAO[fase_selecionada]

equipe_selecionada = st.sidebar.selectbox(
    "Filtrar por Equipe:",
    options=["Todas as Equipes"] + lista_equipes,
    key="equipe_sel",
)

if st.sidebar.button("🔄 Atualizar Dados Agora", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.caption("📌 **Categoria:** Sub-13 Masculino")
st.sidebar.caption(
    f"[🔗 Abrir Página da Fase na Liga]({url_classificacao_atual})"
)

# -----------------------------------------------------------------------------
# PAINEL PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-box">
        <div class="header-title">⚽ NOSSA LIGA FUTSAL 2026</div>
        <div class="header-subtitle">16ª EDIÇÃO — PAINEL OFICIAL SUB-13 MASCULINO</div>
    </div>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# MÉTRICAS FIXAS DO COLÉGIO SANTA MARIA (INDEPENDENTES DOS FILTROS DA BARRA LATERAL)
# -----------------------------------------------------------------------------
equipe_alvo_cards = "Colégio Santa Maria"
df_j_cards = (
    df_jogos[
        (df_jogos["Mandante"] == equipe_alvo_cards)
        | (df_jogos["Visitante"] == equipe_alvo_cards)
    ]
    if not df_jogos.empty
    else pd.DataFrame()
)
qtd_realizados_csm = len(df_j_cards[df_j_cards["Status"] == "Finalizado"])
qtd_restantes_csm = len(df_j_cards[df_j_cards["Status"] == "Agendado"])

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        f'<div class="metric-card"><div class="metric-value"'
        ' style="font-size:15px; overflow:hidden; text-overflow:ellipsis;'
        f' white-space:nowrap;">{equipe_alvo_cards}</div><div'
        ' class="metric-label">Nome da Equipe</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><div'
        f' class="metric-value">{qtd_realizados_csm}</div><div'
        ' class="metric-label">Jogos Realizados</div></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><div'
        f' class="metric-value">{qtd_restantes_csm}</div><div'
        ' class="metric-label">Jogos Restantes</div></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        '<div class="metric-card"><div class="metric-value"'
        ' style="font-size:18px;">Sub-13 Masculino</div><div'
        ' class="metric-label">Categoria Sub-13 Masculino</div></div>',
        unsafe_allow_html=True,
    )

st.write("")

# -----------------------------------------------------------------------------
# BOTÕES DE NAVEGAÇÃO ESTILIZADOS COMO CARTÕES (AZUL COM TEXTO BRANCO EM NEGRITO)
# -----------------------------------------------------------------------------
if "aba_ativa" not in st.session_state:
    st.session_state["aba_ativa"] = "Início"

abas = [
    "Início",
    "Classificação",
    "Próximos Jogos",
    "Jogos Anteriores",
    "Artilharia",
    "Cartões Amarelos e Vermelhos",
]

cols_abas = st.columns(6)

for i, aba in enumerate(abas):
    with cols_abas[i]:
        if st.button(aba, key=f"btn_aba_{i}", use_container_width=True):
            st.session_state["aba_ativa"] = aba

st.write("")

# -----------------------------------------------------------------------------
# CONTEÚDO DAS ABAS
# -----------------------------------------------------------------------------
aba_atual = st.session_state["aba_ativa"]

# 0. PÁGINA INICIAL (INÍCIO) - FIXA PARA COLÉGIO SANTA MARIA (SEM FILTRO LATERAL)
if aba_atual == "Início":
    equipe_alvo = "Colégio Santa Maria"

    meses_pt = {
        1: "JAN",
        2: "FEV",
        3: "MAR",
        4: "ABR",
        5: "MAI",
        6: "JUN",
        7: "JUL",
        8: "AGO",
        9: "SET",
        10: "OUT",
        11: "NOV",
        12: "DEZ",
    }
    dias_pt = {
        0: "SEGUNDA",
        1: "TERÇA",
        2: "QUARTA",
        3: "QUINTA",
        4: "SEXTA",
        5: "SÁBADO",
        6: "DOMINGO",
    }

    def parse_data_jogo(data_str):
        try:
            dt = pd.to_datetime(data_str, format="%d/%m/%Y")
            return dt.day, meses_pt.get(dt.month, ""), dias_pt.get(dt.dayofweek, ""), dt
        except:
            return 5, "OUT", "SEGUNDA", pd.Timestamp("2026-10-05")

    df_j = df_jogos.copy()
    df_j_equipe = df_j[
        (df_j["Mandante"] == equipe_alvo)
        | (df_j["Visitante"] == equipe_alvo)
    ]

    # Próximo Jogo
    df_prox = df_j_equipe[df_j_equipe["Status"] == "Agendado"]
    if not df_prox.empty:
        df_prox["dt_obj"] = pd.to_datetime(df_prox["Data"], format="%d/%m/%Y")
        df_prox = df_prox.sort_values("dt_obj")
        prox_jogo = df_prox.iloc[0]
    else:
        prox_jogo = None

    # Último Jogo Finalizado
    df_ant = df_j_equipe[df_j_equipe["Status"] == "Finalizado"]
    if not df_ant.empty:
        df_ant["dt_obj"] = pd.to_datetime(df_ant["Data"], format="%d/%m/%Y")
        df_ant = df_ant.sort_values("dt_obj", ascending=False)
        ult_jogo = df_ant.iloc[0]
    else:
        ult_jogo = None

    # SEÇÃO PRÓXIMO JOGO
    st.markdown(
        f"<div style='font-size: 13px; font-weight: 800; color: #64748b;"
        f" text-transform: uppercase; margin-bottom: 8px;'>PRÓXIMO JOGO ·"
        f" {equipe_alvo.upper()}</div>",
        unsafe_allow_html=True,
    )

    if prox_jogo is not None:
        d_dia, d_mes, d_sem, _ = parse_data_jogo(prox_jogo["Data"])
        is_casa = prox_jogo["Mandante"] == equipe_alvo
        local_casa_fora = "CASA" if is_casa else "FORA"
        hora_jogo = prox_jogo["Horário"]
        try:
            h_parts = hora_jogo.split(":")
            chegada_dt = (
                pd.Timestamp(2026, 1, 1, int(h_parts[0]), int(h_parts[1]))
                - pd.Timedelta(minutes=30)
            )
            hora_chegada = chegada_dt.strftime("%H:%M")
        except:
            hora_chegada = "18:30"

        st.markdown(
            f"""
        <div style="background: white; padding: 22px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 15px;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #f1f5f9; padding-bottom: 15px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="text-align: center; background: #f8fafc; padding: 10px 16px; border-radius: 8px; border-left: 5px solid #b45309;">
                        <div style="font-size: 10px; font-weight: bold; color: #64748b;">{d_sem}</div>
                        <div style="font-size: 30px; font-weight: 900; color: #160e91; line-height: 1;">{d_dia:02d}</div>
                        <div style="font-size: 12px; font-weight: bold; color: #b45309;">{d_mes}</div>
                    </div>
                    <div>
                        <div style="font-size: 16px; font-weight: bold; color: #1e293b;">🕒 {hora_jogo} &nbsp;&nbsp; <span style="color: #64748b; font-weight: normal; font-size: 13px;">Chegada: {hora_chegada}</span></div>
                        <div style="margin-top: 6px; font-size: 13px; color: #475569;">
                            <span style="background: #160e91; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{local_casa_fora}</span> 
                            &nbsp;📍 {prox_jogo['Local']} &nbsp;|&nbsp; Jogo #{prox_jogo['Jogo']}
                        </div>
                    </div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-around; align-items: center; padding: 10px 0;">
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 16px; font-weight: 800; color: #160e91;">{prox_jogo['Mandante']}</div>
                    <div style="font-size: 11px; color: #64748b; font-weight: bold; margin-top: 2px;">MANDANTE</div>
                </div>
                <div style="font-size: 20px; font-weight: bold; color: #cbd5e1; padding: 0 20px;">✖</div>
                <div style="text-align: center; flex: 1;">
                    <div style="font-size: 16px; font-weight: 800; color: #160e91;">{prox_jogo['Visitante']}</div>
                    <div style="font-size: 11px; color: #64748b; font-weight: bold; margin-top: 2px;">VISITANTE</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Nenhum próximo jogo agendado.")

    # SEÇÃO ÚLTIMO JOGO
    st.markdown(
        f"<div style='font-size: 13px; font-weight: 800; color: #64748b;"
        f" text-transform: uppercase; margin: 25px 0 8px 0;'>ÚLTIMO RESULTADO"
        f" · {equipe_alvo.upper()}</div>",
        unsafe_allow_html=True,
    )

    if ult_jogo is not None:
        d_dia_u, d_mes_u, d_sem_u, _ = parse_data_jogo(ult_jogo["Data"])
        is_casa_u = ult_jogo["Mandante"] == equipe_alvo
        local_casa_fora_u = "CASA" if is_casa_u else "FORA"
        placar_u = ult_jogo["Placar"]

        badge_res = '<span style="background: #28a745; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">VITÓRIA</span>'
        parts_placar = placar_u.split("x")
        if len(parts_placar) == 2:
            try:
                g_m = int(parts_placar[0].strip())
                g_v = int(parts_placar[1].strip())
                if is_casa_u:
                    if g_m < g_v:
                        badge_res = '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">DERROTA</span>'
                    elif g_m == g_v:
                        badge_res = '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">EMPATE</span>'
                else:
                    if g_v < g_m:
                        badge_res = '<span style="background: #dc3545; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">DERROTA</span>'
                    elif g_v == g_m:
                        badge_res = '<span style="background: #ffc107; color: black; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">EMPATE</span>'
            except:
                pass

        st.markdown(
            f"""
        <div style="background: white; padding: 22px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.06); margin-bottom: 20px;">
            <div style="display: flex; align-items: center; justify-content: space-between; border-bottom: 2px solid #f1f5f9; padding-bottom: 15px; margin-bottom: 15px;">
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div style="text-align: center; background: #f8fafc; padding: 10px 16px; border-radius: 8px; border-left: 5px solid #28a745;">
                        <div style="font-size: 10px; font-weight: bold; color: #64748b;">{d_sem_u}</div>
                        <div style="font-size: 30px; font-weight: 900; color: #160e91; line-height: 1;">{d_dia_u:02d}</div>
                        <div style="font-size: 12px; font-weight: bold; color: #b45309;">{d_mes_u}</div>
                    </div>
                    <div>
                        <div style="margin-bottom: 6px;">{badge_res}</div>
                        <div style="font-size: 13px; color: #475569;">
                            <span style="background: #160e91; color: white; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{local_casa_fora_u}</span> 
                            &nbsp;📍 {ult_jogo['Local']} &nbsp;|&nbsp; Jogo #{ult_jogo['Jogo']}
                        </div>
                    </div>
                </div>
            </div>
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 10px;">
                <div style="text-align: left; flex: 1;">
                    <div style="font-size: 15px; font-weight: 800; color: #160e91;">{ult_jogo['Mandante']}</div>
                    <div style="font-size: 10px; color: #64748b; font-weight: bold; margin-top: 2px;">MANDANTE</div>
                </div>
                <div style="font-size: 28px; font-weight: 900; color: #160e91; background: #f1f5f9; padding: 8px 24px; border-radius: 8px; letter-spacing: 2px;">
                    {placar_u}
                </div>
                <div style="text-align: right; flex: 1;">
                    <div style="font-size: 15px; font-weight: 800; color: #160e91;">{ult_jogo['Visitante']}</div>
                    <div style="font-size: 10px; color: #64748b; font-weight: bold; margin-top: 2px;">VISITANTE</div>
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )
    else:
        st.info("Nenhum resultado anterior encontrado.")

# 1. TABELA DE CLASSIFICAÇÃO
elif aba_atual == "Classificação":
    st.subheader(f"Tabela de Classificação - {fase_selecionada}")

    def aplicar_filtro_equipe(df):
        if equipe_selecionada != "Todas as Equipes" and "Equipe" in df.columns:
            return df[df["Equipe"] == equipe_selecionada]
        return df

    if fase_selecionada == "Classificação Geral":
        df_geral_view = aplicar_filtro_equipe(df_geral_oficial)
        st.markdown(
            "### 🌐 **Classificação Geral Oficial (Do 1º ao 28º Colocado)**"
        )
        st.dataframe(df_geral_view, use_container_width=True, hide_index=True)

    else:
        if grupo_selecionado == "Grupo A":
            st.markdown("### 🅰️ **Grupo A**")
            st.dataframe(
                aplicar_filtro_equipe(df_grupo_a),
                use_container_width=True,
                hide_index=True,
            )
        elif grupo_selecionado == "Grupo B":
            st.markdown("### 🅱️ **Grupo B**")
            st.dataframe(
                aplicar_filtro_equipe(df_grupo_b),
                use_container_width=True,
                hide_index=True,
            )
        else:
            col_g1, col_g2 = st.columns(2)
            with col_g1:
                st.markdown("### 🅰️ **Grupo A**")
                st.dataframe(
                    aplicar_filtro_equipe(df_grupo_a),
                    use_container_width=True,
                    hide_index=True,
                )
            with col_g2:
                st.markdown("### 🅱️ **Grupo B**")
                st.dataframe(
                    aplicar_filtro_equipe(df_grupo_b),
                    use_container_width=True,
                    hide_index=True,
                )

# 2. PRÓXIMOS JOGOS
elif aba_atual == "Próximos Jogos":
    st.subheader("Próximos Confrontos Agendados")
    if not df_jogos.empty:
        df_prox = df_jogos[df_jogos["Status"] == "Agendado"].copy()
        if equipe_selecionada != "Todas as Equipes":
            df_prox = df_prox[
                (df_prox["Mandante"] == equipe_selecionada)
                | (df_prox["Visitante"] == equipe_selecionada)
            ]

        if not df_prox.empty:
            for _, j in df_prox.iterrows():
                num_jogo = f"Jogo #{j['Jogo']} | " if j.get("Jogo") != "-" else ""
                st.markdown(
                    f"""
                    <div class="card-jogo">
                        <div style="font-size:13px; color:#64748b; margin-bottom: 8px;">
                            <b>{num_jogo}</b>📅 <b>Data:</b> {j['Data']} &nbsp;|&nbsp; ⏰ <b>Horário:</b> {j['Horário']} &nbsp;|&nbsp; 📍 <b>Local:</b> {j['Local']}
                        </div>
                        <div style="font-size:17px; font-weight: 700; color: #160e91;">
                            {j['Mandante']} <span class="placar-badge">VS</span> {j['Visitante']}
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Nenhum próximo jogo agendado para o filtro selecionado.")
    else:
        st.info("Nenhuma agenda de partidas localizada no momento.")

# 3. JOGOS ANTERIORES
elif aba_atual == "Jogos Anteriores":
    st.subheader("Resultados das Partidas")
    if not df_jogos.empty:
        df_ant = df_jogos[df_jogos["Status"] == "Finalizado"].copy()
        if equipe_selecionada != "Todas as Equipes":
            df_ant = df_ant[
                (df_ant["Mandante"] == equipe_selecionada)
                | (df_ant["Visitante"] == equipe_selecionada)
            ]

        if not df_ant.empty:
            for _, j in df_ant.iterrows():
                num_jogo = f"Jogo #{j['Jogo']} | " if j.get("Jogo") != "-" else ""
                st.markdown(
                    f"""
                    <div class="card-jogo" style="border-left-color: #28a745;">
                        <div style="font-size:13px; color:#64748b; margin-bottom: 8px;">
                            <b>{num_jogo}</b>📅 <b>Data:</b> {j['Data']} &nbsp;|&nbsp; ⏰ <b>Horário:</b> {j['Horário']} &nbsp;|&nbsp; 📍 <b>Local:</b> {j['Local']}
                        </div>
                        <div style="font-size:18px; font-weight: 700; color: #160e91;">
                            {j['Mandante']} <span class="placar-badge-final">{j['Placar']}</span> {j['Visitante']}
                        </div>
                    </div>
                """,
                    unsafe_allow_html=True,
                )
        else:
            st.warning("Nenhum resultado registrado para o filtro selecionado.")
    else:
        st.info("Nenhum resultado de partida localizado até o momento.")

# 4. ARTILHARIA
elif aba_atual == "Artilharia":
    st.subheader("Artilharia - Sub-13 Masculino")
    df_art_view = df_artilharia_oficial.copy()
    if equipe_selecionada != "Todas as Equipes":
        df_art_view = df_art_view[df_art_view["Equipe"] == equipe_selecionada]
    st.dataframe(df_art_view, use_container_width=True, hide_index=True)

# 5. CARTÕES AMARELOS E VERMELHOS (COM SUB-ABAS)
elif aba_atual == "Cartões Amarelos e Vermelhos":
    st.subheader("Controle Disciplinar (Cartões)")

    sub_aba_amarelos, sub_aba_vermelhos = st.tabs(["Cartões Amarelos", "Cartões Vermelhos"])

    with sub_aba_amarelos:
        df_car_amarelos_view = df_cartoes_amarelos.copy()
        if equipe_selecionada != "Todas as Equipes":
            df_car_amarelos_view = df_car_amarelos_view[
                df_car_amarelos_view["Equipe"] == equipe_selecionada
            ]
        if not df_car_amarelos_view.empty:
            st.dataframe(df_car_amarelos_view, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cartão amarelo registrado para o filtro selecionado.")

    with sub_aba_vermelhos:
        df_car_vermelhos_view = df_cartoes_vermelhos.copy()
        if equipe_selecionada != "Todas as Equipes":
            df_car_vermelhos_view = df_car_vermelhos_view[
                df_car_vermelhos_view["Equipe"] == equipe_selecionada
            ]
        if not df_car_vermelhos_view.empty:
            st.dataframe(df_car_vermelhos_view, use_container_width=True, hide_index=True)
        else:
            st.info("Nenhum cartão vermelho registrado para o filtro selecionado.")