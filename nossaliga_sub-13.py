import io
import re
import pandas as pd
import requests
import streamlit as st
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE ECRÃ
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nossa Liga Futsal 2026 - Sub-13 Masculino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS customizada (Fundo cinza grafite, abas e menus visíveis no mobile)
st.markdown(
    """
    <style>
    /* FIXAR A BARRA LATERAL (ESCONDE BOTÃO DE RECOLHER) */
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    [data-testid="collapsedControl"] {
        display: none !important;
    }
    section[data-testid="stSidebar"] {
        min-width: 280px !important;
        max-width: 280px !important;
    }

    /* FUNDO DA PÁGINA EM CINZA GRAFITE */
    .stApp { background-color: #2b2b2b !important; }
    
    /* ELIMINAÇÃO TOTAL DE SOMBRAS E FANTASMAS NAS FONTES */
    * {
        text-shadow: none !important;
        -webkit-font-smoothing: antialiased !important;
    }

    .header-box {
        background: linear-gradient(135deg, #160e91, #215ea0);
        padding: 24px;
        border-radius: 12px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .header-title { font-size: 28px; font-weight: 800; margin: 0; color: #ffffff !important; }
    .header-subtitle { font-size: 14px; color: #f8f063; margin-top: 4px; font-weight: 600; }
    
    /* CAIXA DE TÍTULO DE SEÇÃO COM FUNDO AZUL SÓLIDO */
    .section-header-box {
        background-color: #110888 !important;
        color: #ffffff !important;
        padding: 14px 20px !important;
        border-radius: 8px !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        margin-bottom: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1) !important;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .section-header-box span, .section-header-box div {
        color: #ffffff !important;
    }

    /* Metrics Cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
    }
    .metric-value { font-size: 24px; font-weight: 800; color: #160e91; }
    .metric-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-top: 4px; }
    
    /* Match Card Container */
    .match-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 12px 10px;
        border: 1px solid #cbd5e1;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .match-header {
        font-size: 12px;
        font-weight: 800;
        color: #f8f063;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    .team-name { 
        font-size: 11.5px; 
        font-weight: 800; 
        color: #0f172a; 
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 100%;
    }
    .team-logo {
        width: 15px;
        height: 15px;
        object-fit: contain;
        flex-shrink: 0;
    }
    .score-badge {
        font-size: 15px;
        font-weight: 800;
        color: #160e91;
        background: #f1f5f9;
        padding: 4px 8px;
        border-radius: 6px;
        display: inline-block;
    }
    .status-vitoria {
        background-color: #22c55e;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 800;
        font-size: 10px;
    }
    .status-derrota {
        background-color: #ef4444;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 800;
        font-size: 10px;
    }
    .status-empate {
        background-color: #64748b;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-weight: 800;
        font-size: 10px;
    }

    /* CORREÇÃO DEFINITIVA DAS ABAS (ST.TABS) */
    div.stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: transparent !important;
        border-bottom: none !important;
        margin-bottom: 20px !important;
    }

    div.stTabs [data-baseweb="tab"] {
        background-color: #ffffff !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        border: 1px solid #cbd5e1 !important;
        height: auto !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05) !important;
    }

    div.stTabs [data-baseweb="tab"][aria-selected="false"],
    div.stTabs [data-baseweb="tab"][aria-selected="false"] p, 
    div.stTabs [data-baseweb="tab"][aria-selected="false"] div, 
    div.stTabs [data-baseweb="tab"][aria-selected="false"] span,
    div.stTabs button[data-baseweb="tab"][aria-selected="false"] * {
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        font-weight: 800 !important;
        font-size: 13px !important;
        text-shadow: none !important;
    }

    div.stTabs [data-baseweb="tab"]:hover {
        background-color: #f1f5f9 !important;
    }

    div.stTabs [data-baseweb="tab"][aria-selected="true"] {
        background-color: #110888 !important;
        border: 2px solid #110888 !important;
    }

    div.stTabs [data-baseweb="tab"][aria-selected="true"],
    div.stTabs [data-baseweb="tab"][aria-selected="true"] p,
    div.stTabs [data-baseweb="tab"][aria-selected="true"] div,
    div.stTabs [data-baseweb="tab"][aria-selected="true"] span,
    div.stTabs button[data-baseweb="tab"][aria-selected="true"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
    }

    div.stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* ESTILIZAÇÃO DOS FILTROS (ST.SELECTBOX) COM ALTO CONTRASTE */
    div[data-testid="stSelectbox"] label {
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #ffffff !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 4px !important;
    }

    div[data-testid="stSelectbox"] > div > div {
        background-color: #110888 !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        border: 2px solid #ffffff !important;
        font-weight: 800 !important;
        min-height: 40px !important;
        height: 40px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }

    div[data-testid="stSelectbox"] svg {
        fill: #ffffff !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] *,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] div {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* CORREÇÃO DO MENU DROPDOWN (LISTA DE OPÇÕES DO SELECTBOX NO MOBILE) */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #ffffff !important;
    }
    div[data-baseweb="popover"] div, div[data-baseweb="menu"] div, ul[role="listbox"] li, ul[role="listbox"] li span {
        color: #110888 !important;
        -webkit-text-fill-color: #110888 !important;
        font-weight: 700 !important;
    }
    ul[role="listbox"] li:hover {
        background-color: #f1f5f9 !important;
    }

    .btn-limpar-container {
        display: flex;
        align-items: flex-end;
        height: 100%;
        padding-bottom: 2px;
    }
    
    /* TABELAS EM AZUL NEGRITO (COMPACTADAS) */
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    .custom-table th {
        background-color: #110888;
        color: #ffffff;
        font-weight: 800;
        text-align: left;
        padding: 6px 8px;
        font-size: 11px;
    }
    .custom-table td {
        padding: 5px 8px;
        border-bottom: 1px solid #e2e8f0;
        font-size: 11px;
        color: #110888 !important;
        font-weight: 800 !important;
        white-space: nowrap;
    }
    .custom-table tr:hover {
        background-color: #f8fafc;
    }
    .team-cell {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        font-weight: 800;
        color: #110888 !important;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ENDEREÇOS E HEADERS
# -----------------------------------------------------------------------------
URL_CATEGORIA = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978"
URL_ARTILHARIA = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978/estatisticas/artilharia"
URL_CARTOES = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978/estatisticas/cartoes"
URL_SUSPENSOES = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978/estatisticas/suspensoes"
URL_JOGOS = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/impressao/categoria/19978/0"
URL_CLASSIFICACAO_GERAL = f"{URL_CATEGORIA}/classificacao/geral/0"
URL_EQUIPE_SANTA_MARIA_BASE = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/equipe/colegio-santa-maria/42735"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# -----------------------------------------------------------------------------
# FUNÇÕES DE RASPAGEM E UTILITÁRIOS
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def carregar_dados_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        if resp.status_code != 200:
            return None
        soup = BeautifulSoup(resp.content, "html.parser")
        return soup
    except Exception:
        return None

def renderizar_cabecalho_secao(titulo):
    st.markdown(f'<div class="section-header-box">{titulo}</div>', unsafe_allow_html=True)

def extrair_tabela_unica(table):
    rows = []
    for tr in table.find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    if not rows:
        return pd.DataFrame()
    try:
        primeira_linha_str = " ".join(rows[0]).lower()
        tem_cabecalho = any(k in primeira_linha_str for k in ["classificação", "equipe", "clube", "j", "v", "e", "d", "gp", "gc", "p"])
        
        if tem_cabecalho and len(rows) > 1:
            header = rows[0]
            data = rows[1:]
            max_len = max(len(r) for r in data) if data else len(header)
            while len(header) < max_len:
                header.append(f"Col_{len(header)}")
            return pd.DataFrame(data, columns=header[:max_len])
        else:
            if len(rows) > 1 and len(rows[0]) == len(rows[1]):
                return pd.DataFrame(rows[1:], columns=rows[0])
            else:
                return pd.DataFrame(rows)
    except Exception:
        return pd.DataFrame()

def extrair_tabelas_soup(soup):
    dfs = []
    if not soup:
        return dfs
    for table in soup.find_all("table"):
        df = extrair_tabela_unica(table)
        if not df.empty:
            dfs.append(df)
    return dfs

def limpar_colunas_df(df):
    if df.empty:
        return df
    
    if all(str(c).isdigit() for c in df.columns) and len(df) > 0:
        primeira_linha = [str(val).lower() for val in df.iloc[0].values]
        if any(k in " ".join(primeira_linha) for k in ["classificação", "equipe", "clube", "j", "v", "e", "d", "gp", "gc", "p"]):
            df.columns = df.iloc[0]
            df = df.iloc[1:].reset_index(drop=True)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(str(c) for c in col if 'unnamed' not in str(c).lower()).strip() for col in df.columns]
    else:
        df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(ttl=300)
def obter_links_classificacao_dinamicos():
    soup = carregar_dados_url(URL_CATEGORIA)
    links = {
        "geral": URL_CLASSIFICACAO_GERAL,
        "grupo_a": f"{URL_CATEGORIA}/classificacao/grupo-a/0",
        "grupo_b": f"{URL_CATEGORIA}/classificacao/grupo-b/0"
    }
    if soup:
        for a in soup.find_all("a", href=True):
            href = a['href']
            texto = a.get_text(strip=True).lower()
            if "classificacao" in href or "classificação" in href:
                full_url = href if href.startswith("http") else f"https://www.nossaliga.com.br{href}"
                if "geral" in href:
                    links["geral"] = full_url
                elif "grupo-a" in href or "grupo a" in texto or "grupo_a" in href:
                    links["grupo_a"] = full_url
                elif "grupo-b" in href or "grupo b" in texto or "grupo_b" in href:
                    links["grupo_b"] = full_url
    return links

def filtrar_tabela_valida(df):
    if df.empty:
        return False
    texto = df.to_string().lower()
    if "vencedor do jogo" in texto or "semifinal" in texto or "final" in texto:
        return False
    if len(df.columns) < 3 or len(df) <= 1:
        return False
    return True

@st.cache_data(ttl=300)
def obter_classificacao_geral_oficial():
    soup_geral = carregar_dados_url(URL_CLASSIFICACAO_GERAL)
    if soup_geral:
        dfs = extrair_tabelas_soup(soup_geral)
        for d in dfs:
            d_limpo = limpar_colunas_df(d)
            if filtrar_tabela_valida(d_limpo):
                return d_limpo
    return pd.DataFrame()

@st.cache_data(ttl=300)
def obter_todas_tabelas_classificacao():
    df_geral = obter_classificacao_geral_oficial()
    soup_cat = carregar_dados_url(URL_CATEGORIA)
    df_grupo_a = pd.DataFrame()
    df_grupo_b = pd.DataFrame()
    
    if soup_cat:
        for tag in soup_cat.find_all(["h2", "h3", "h4", "div", "span"], string=re.compile(r"grupo\s*a|grupo\s*b", re.IGNORECASE)):
            texto_tag = tag.get_text(strip=True).lower()
            tabela = tag.find_next("table")
            if tabela:
                df = extrair_tabela_unica(tabela)
                df_limpo = limpar_colunas_df(df)
                if filtrar_tabela_valida(df_limpo):
                    if "grupo a" in texto_tag and df_grupo_a.empty:
                        df_grupo_a = df_limpo
                    elif "grupo b" in texto_tag and df_grupo_b.empty:
                        df_grupo_b = df_limpo

    if df_grupo_a.empty or df_grupo_b.empty:
        dfs_cat = extrair_tabelas_soup(soup_cat) if soup_cat else []
        tabelas_validas = [limpar_colunas_df(d) for d in dfs_cat if filtrar_tabela_valida(limpar_colunas_df(d))]
        
        if df_grupo_a.empty and len(tabelas_validas) > 0:
            df_grupo_a = tabelas_validas[0]
        if df_grupo_b.empty and len(tabelas_validas) > 1:
            for t in tabelas_validas[1:]:
                if not t.equals(df_grupo_a):
                    df_grupo_b = t
                    break

    if df_grupo_a.empty or df_grupo_b.empty:
        links = obter_links_classificacao_dinamicos()
        if df_grupo_a.empty:
            soup_ga = carregar_dados_url(links["grupo_a"])
            dfs_ga = extrair_tabelas_soup(soup_ga) if soup_ga else []
            for d in dfs_ga:
                d_limpo = limpar_colunas_df(d)
                if filtrar_tabela_valida(d_limpo):
                    df_grupo_a = d_limpo
                    break
                    
        if df_grupo_b.empty:
            soup_gb = carregar_dados_url(links["grupo_b"])
            dfs_gb = extrair_tabelas_soup(soup_gb) if soup_gb else []
            for d in dfs_gb:
                d_limpo = limpar_colunas_df(d)
                if filtrar_tabela_valida(d_limpo) and not d_limpo.equals(df_grupo_a):
                    df_grupo_b = d_limpo
                    break

    return df_geral, df_grupo_a, df_grupo_b

@st.cache_data(ttl=300)
def obter_mapeamento_escudos():
    soup = carregar_dados_url(URL_CLASSIFICACAO_GERAL)
    mapa = {}
    if soup:
        imgs = soup.find_all("img")
        for img in imgs:
            src = img.get("src", "")
            title = img.get("title", "") or img.get("alt", "")
            if src and title:
                if not src.startswith("http"):
                    src = f"https://www.nossaliga.com.br{src}"
                mapa[title.strip().lower()] = src
    return mapa

def formatar_equipe_com_escudo(nome_equipe, mapa_escudos):
    if not nome_equipe or pd.isna(nome_equipe):
        return ""
    
    nome_clean = str(nome_equipe).strip()
    nome_lower = nome_clean.lower()
    url_escudo = ""
    
    for k, v in mapa_escudos.items():
        if k in nome_lower or nome_lower in k:
            url_escudo = v
            break

    if url_escudo:
        return f'<div class="team-cell"><img src="{url_escudo}" class="team-logo" /><span style="color: #110888 !important; font-weight: 800 !important; white-space: nowrap;">{nome_clean}</span></div>'
    return f'<span style="color: #110888 !important; font-weight: 800 !important; white-space: nowrap;">{nome_clean}</span>'

def formatar_tabela_classificacao_oficial(df, mapa_escudos, reatribuir_posicao=False):
    if df.empty:
        return df
    
    df = limpar_colunas_df(df)
    novas_linhas = []
    
    for idx, row in df.iterrows():
        if len(row) >= 2:
            if reatribuir_posicao:
                pos_str = f"{idx + 1}º"
            else:
                pos = str(row.iloc[0]).strip()
                pos_clean = re.sub(r'[ºª°]', '', pos).strip()
                pos_str = f"{pos_clean}º" if pos_clean.isdigit() else pos

            nome_equipe = str(row.iloc[1]).strip()
            if not nome_equipe or nome_equipe.lower() in ["none", "nan"] or nome_equipe.isdigit():
                if len(row) > 2:
                    nome_equipe = str(row.iloc[2]).strip()

            eq_fmt = formatar_equipe_com_escudo(nome_equipe, mapa_escudos)

            celula_classificacao = (
                f'<div style="display: flex; align-items: center; gap: 6px;">'
                f'<span style="font-weight: 800 !important; color: #110888 !important; min-width: 18px;">{pos_str}</span>'
                f'{eq_fmt}'
                f'</div>'
            )

            nova_linha = [celula_classificacao]
            valores_estatisticas = []
            for i in range(2, len(row)):
                val = str(row.iloc[i]).strip()
                if val and val.lower() not in ["none", "nan"]:
                    valores_estatisticas.append(val)

            nova_linha.extend(valores_estatisticas)
            novas_linhas.append(nova_linha)

    colunas_oficiais = ["Classificação", "P", "J", "V", "E", "D", "GP", "GC", "SG", "Avg", "%A"]
    if novas_linhas:
        linhas_ajustadas = []
        max_cols = max(len(nl) for nl in novas_linhas) if novas_linhas else len(colunas_oficiais)
        cols_final = colunas_oficiais[:max_cols] if max_cols <= len(colunas_oficiais) else colunas_oficiais + [f"Col_{i}" for i in range(len(colunas_oficiais), max_cols)]
        
        for nl in novas_linhas:
            while len(nl) < len(cols_final):
                nl.append("")
            linhas_ajustadas.append(nl[:len(cols_final)])
        return pd.DataFrame(linhas_ajustadas, columns=cols_final)

    return df

def renderizar_tabela_html(df):
    st.markdown(df.to_html(escape=False, index=False, classes="custom-table"), unsafe_allow_html=True)

def obter_df_jogos():
    soup = carregar_dados_url(URL_JOGOS)
    if not soup:
        return pd.DataFrame()
    
    linhas = soup.find_all("tr")
    jogos_dados = []
    
    for tr in linhas:
        tds = tr.find_all("td")
        if len(tds) >= 7:
            textos = [td.get_text(strip=True) for td in tds]
            if re.match(r"^\d+$", textos[0]):
                jogos_dados.append({
                    "Nº Jogo": textos[0],
                    "Data": textos[1],
                    "Horário": textos[2],
                    "Mandante": textos[3],
                    "Placar": textos[4],
                    "Visitante": textos[5],
                    "Local": textos[6]
                })
    return pd.DataFrame(jogos_dados)

def obter_posicoes_santa_maria():
    pos_geral = "N/I"
    pos_grupo = "N/I"
    
    df_geral, df_ga, df_gb = obter_todas_tabelas_classificacao()
        
    if not df_geral.empty:
        col_eq = [c for c in df_geral.columns if any(k in str(c).lower() for k in ["equipe", "clube", "times", "nome"])]
        target_col = col_eq[0] if col_eq else df_geral.columns[1] if len(df_geral.columns) > 1 else df_geral.columns[0]
        
        for idx, row in df_geral.iterrows():
            if "santa maria" in str(row[target_col]).lower():
                col_pos = df_geral.columns[0]
                val_pos = re.sub(r'[ºª°]', '', str(row[col_pos])).strip()
                pos_geral = f"{val_pos}º" if val_pos.isdigit() else f"{row[col_pos]}º"
                break

    for df_g_grupo in [df_ga, df_gb]:
        if not df_g_grupo.empty:
            df_gp_limpo = limpar_colunas_df(df_g_grupo)
            col_eq_gp = [c for c in df_gp_limpo.columns if any(k in str(c).lower() for k in ["equipe", "clube", "times", "nome"])]
            t_col = col_eq_gp[0] if col_eq_gp else df_gp_limpo.columns[1] if len(df_gp_limpo.columns) > 1 else df_gp_limpo.columns[0]
            for idx, row in df_gp_limpo.iterrows():
                if "santa maria" in str(row[t_col]).lower():
                    col_pos = df_gp_limpo.columns[0]
                    val_pos = re.sub(r'[ºª°]', '', str(row[col_pos])).strip()
                    pos_grupo = f"{val_pos}º" if val_pos.isdigit() else f"{row[col_pos]}º"
                    break
        if pos_grupo != "N/I":
            break

    return pos_geral, pos_grupo

def ir_para_inicio():
    st.session_state["aba_radio"] = "Início"

def botao_voltar_inicio(key_suffix=""):
    st.button("🏠 Ir para a Página Inicial", key=f"btn_inicio_{key_suffix}", on_click=ir_para_inicio)

def limpar_filtro(key):
    st.session_state[key] = "Todas as Equipes"

def criar_filtro_equipe(lista_equipes, key):
    equipes_unicas = sorted([str(e).strip() for e in lista_equipes if pd.notna(e) and str(e).strip() != ""])
    opcoes = ["Todas as Equipes"] + equipes_unicas
    
    if key not in st.session_state:
        st.session_state[key] = "Todas as Equipes"
        
    col_sel, col_btn, col_vazia = st.columns([2, 1, 2])
    with col_sel:
        selecionado = st.selectbox("🔍 Selecionar Filtro por Equipe:", opcoes, key=key)
    with col_btn:
        st.markdown("<div class='btn-limpar-container'>", unsafe_allow_html=True)
        st.button("🧹 Limpar Filtro", key=f"btn_limpar_{key}", on_click=limpar_filtro, args=(key,))
        st.markdown("</div>", unsafe_allow_html=True)
        
    return selecionado

mapa_escudos = obter_mapeamento_escudos()
links_classificacao = obter_links_classificacao_dinamicos()

# -----------------------------------------------------------------------------
# INTERFACE PRINCIPAL
# -----------------------------------------------------------------------------
st.markdown(
    """
    <div class="header-box">
        <h1 class="header-title">NOSSA LIGA FUTSAL 2026</h1>
        <div class="header-subtitle">16ª EDIÇÃO — PAINEL OFICIAL SUB-13 MASCULINO</div>
    </div>
""",
    unsafe_allow_html=True,
)

if st.sidebar.button("🔄 Atualizar Dados Agora"):
    st.cache_data.clear()
    st.rerun()

opcoes_menu = [
    "Início", 
    "Classificação Sub-13", 
    "Jogos", 
    "Artilharia", 
    "Cartões Amarelos e Vermelhos", 
    "Suspensão", 
    "Atletas Sub-13 Santa Maria"
]

if "aba_radio" not in st.session_state:
    st.session_state["aba_radio"] = "Início"

opcao = st.sidebar.radio(
    "Navegue pelas abas:",
    opcoes_menu,
    key="aba_radio"
)

# -----------------------------------------------------------------------------
# PROCESSAMENTO DAS ABAS
# -----------------------------------------------------------------------------
if opcao == "Início":
    df_todos_jogos = obter_df_jogos()
    pos_geral, pos_grupo = obter_posicoes_santa_maria()
    
    if not df_todos_jogos.empty:
        cond_santa_maria = (
            (df_todos_jogos["Mandante"].str.strip().str.lower() == "colégio santa maria") | 
            (df_todos_jogos["Visitante"].str.strip().str.lower() == "colégio santa maria")
        )
        df_sm = df_todos_jogos[cond_santa_maria].copy()
        
        is_realizado = df_sm["Placar"].str.contains(r"\d", regex=True)
        df_sm_realizados = df_sm[is_realizado].copy()
        df_sm_restantes = df_sm[~is_realizado].copy()
        
        total_realizados = len(df_sm_realizados)
        total_restantes = len(df_sm_restantes)
    else:
        df_sm_realizados = pd.DataFrame()
        df_sm_restantes = pd.DataFrame()
        total_realizados = 0
        total_restantes = 0

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value" style="font-size:15px; padding-top:6px;">
                    {formatar_equipe_com_escudo("Colégio Santa Maria", mapa_escudos)}
                </div>
                <div class="metric-label">NOME DA EQUIPE</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{pos_geral}</div>
                <div class="metric-label">POSIÇÃO GERAL</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{pos_grupo}</div>
                <div class="metric-label">POSIÇÃO NO GRUPO</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_realizados}</div>
                <div class="metric-label">JOGOS REALIZADOS</div>
            </div>
        """, unsafe_allow_html=True)
    with c5:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_restantes}</div>
                <div class="metric-label">JOGOS RESTANTES</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_esq, col_dir = st.columns([1.3, 1.0])

    with col_esq:
        st.markdown("<div class='match-header'>PRÓXIMO JOGO - COLÉGIO SANTA MARIA</div>", unsafe_allow_html=True)
        if not df_sm_restantes.empty:
            prox = df_sm_restantes.iloc[0]
            mandante_formatted = formatar_equipe_com_escudo(prox['Mandante'], mapa_escudos)
            visitante_formatted = formatar_equipe_com_escudo(prox['Visitante'], mapa_escudos)
            
            st.markdown(f"""
                <div class="match-box">
                    <div style="font-size:11.5px; color:#475569; margin-bottom:8px; font-weight:600;">
                        📅 <b>Data:</b> {prox['Data']} às {prox['Horário']} &nbsp;|&nbsp; 📍 <b>Local:</b> {prox['Local']} &nbsp;|&nbsp; 🏷️ <b>Jogo #{prox['Nº Jogo']}</b>
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; text-align:center; gap: 2px;">
                        <div style="flex:1; min-width:0; overflow:hidden;">
                            <div class="team-name">{mandante_formatted}</div>
                            <div style="font-size:9.5px; color:#94a3b8; font-weight:700; margin-top:2px;">MANDANTE</div>
                        </div>
                        <div style="padding: 0 4px; flex-shrink:0;">
                            <span class="score-badge">X</span>
                        </div>
                        <div style="flex:1; min-width:0; overflow:hidden;">
                            <div class="team-name">{visitante_formatted}</div>
                            <div style="font-size:9.5px; color:#94a3b8; font-weight:700; margin-top:2px;">VISITANTE</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Não há próximos jogos agendados no momento.")

        st.markdown("<div class='match-header' style='margin-top: 15px;'>ÚLTIMO RESULTADO - COLÉGIO SANTA MARIA</div>", unsafe_allow_html=True)
        if not df_sm_realizados.empty:
            ult_sm = df_sm_realizados.iloc[-1]
            mandante_sm = formatar_equipe_com_escudo(ult_sm['Mandante'], mapa_escudos)
            visitante_sm = formatar_equipe_com_escudo(ult_sm['Visitante'], mapa_escudos)
            
            tag_status = ""
            try:
                p_mand, p_vis = [int(x.strip()) for x in ult_sm['Placar'].split('x')]
                is_mandante = ult_sm['Mandante'].strip().lower() == "colégio santa maria"
                
                if p_mand == p_vis:
                    tag_status = '<span class="status-empate">EMPATE</span>'
                elif (is_mandante and p_mand > p_vis) or (not is_mandante and p_vis > p_mand):
                    tag_status = '<span class="status-vitoria">VITÓRIA</span>'
                else:
                    tag_status = '<span class="status-derrota">DERROTA</span>'
            except Exception:
                tag_status = ""

            st.markdown(f"""
                <div class="match-box">
                    <div style="font-size:11.5px; color:#475569; margin-bottom:8px; font-weight:600;">
                        📅 <b>Data:</b> {ult_sm['Data']} às {ult_sm['Horário']} &nbsp;|&nbsp; 📍 <b>Local:</b> {ult_sm['Local']} &nbsp;|&nbsp; 🏷️ <b>Jogo #{ult_sm['Nº Jogo']}</b> &nbsp; {tag_status}
                    </div>
                    <div style="display:flex; justify-content:space-between; align-items:center; text-align:center; gap: 2px;">
                        <div style="flex:1; min-width:0; overflow:hidden;">
                            <div class="team-name">{mandante_sm}</div>
                            <div style="font-size:9.5px; color:#94a3b8; font-weight:700; margin-top:2px;">MANDANTE</div>
                        </div>
                        <div style="padding: 0 4px; flex-shrink:0;">
                            <span class="score-badge">{ult_sm['Placar']}</span>
                        </div>
                        <div style="flex:1; min-width:0; overflow:hidden;">
                            <div class="team-name">{visitante_sm}</div>
                            <div style="font-size:9.5px; color:#94a3b8; font-weight:700; margin-top:2px;">VISITANTE</div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("Nenhum resultado anterior registrado até o momento.")

    with col_dir:
        st.markdown("<div class='match-header'>RESULTADOS DA ÚLTIMA RODADA</div>", unsafe_allow_html=True)
        if not df_todos_jogos.empty:
            is_realizado_geral = df_todos_jogos["Placar"].str.contains(r"\d", regex=True)
            df_realizados_geral = df_todos_jogos[is_realizado_geral].copy()
            
            if not df_realizados_geral.empty:
                ultima_data = df_realizados_geral.iloc[-1]['Data']
                df_ultima_rodada = df_realizados_geral[df_realizados_geral['Data'] == ultima_data].copy()
                
                st.markdown(f"<div style='font-size: 13px; color: #f8f063; font-weight: 700; margin-bottom: 12px;'>📅 Data da Rodada: {ultima_data}</div>", unsafe_allow_html=True)
                
                for _, ult in df_ultima_rodada.iterrows():
                    m_fmt = formatar_equipe_com_escudo(ult['Mandante'], mapa_escudos)
                    v_fmt = formatar_equipe_com_escudo(ult['Visitante'], mapa_escudos)
                    
                    st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#ffffff; padding:8px 10px; border-radius:8px; border:1px solid #cbd5e1; margin-bottom:8px; box-shadow:0 2px 6px rgba(0,0,0,0.08);">
                            <div style="flex:2; text-align:left; font-size:11px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{m_fmt}</div>
                            <div style="flex:1; text-align:center;"><span style="background:#f1f5f9; padding:3px 6px; border-radius:4px; font-weight:800; color:#160e91; font-size:10px;">{ult['Placar']}</span></div>
                            <div style="flex:2; text-align:right; font-size:11px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{v_fmt}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum resultado registrado.")
        else:
            st.info("Erro ao carregar os jogos.")

elif opcao == "Classificação Sub-13":
    botao_voltar_inicio("classificacao")
    renderizar_cabecalho_secao("📊 Classificação — Sub-13 Masculino")
    
    df_geral_raw, df_ga_raw, df_gb_raw = obter_todas_tabelas_classificacao()
    
    tab_geral, tab_grupos = st.tabs(["🌐 Classificação Geral", "🏆 Classificação por Grupos"])
    
    with tab_geral:
        if not df_geral_raw.empty:
            df_g_fmt = formatar_tabela_classificacao_oficial(df_geral_raw, mapa_escudos)
            renderizar_tabela_html(df_g_fmt)
        else:
            st.warning("Não foi possível carregar a tabela de classificação geral oficial.")

    with tab_grupos:
        col_g1, col_g2 = st.columns(2, gap="medium")
        with col_g1:
            st.markdown("<h3 style='color: #ffffff;'>🅰️ Grupo A</h3>", unsafe_allow_html=True)
            if not df_ga_raw.empty:
                df_ga_fmt = formatar_tabela_classificacao_oficial(df_ga_raw, mapa_escudos)
                renderizar_tabela_html(df_ga_fmt)
            else:
                st.info("Dados do Grupo A indisponíveis no momento.")
                
        with col_g2:
            st.markdown("<h3 style='color: #ffffff;'>🅱️ Grupo B</h3>", unsafe_allow_html=True)
            if not df_gb_raw.empty:
                df_gb_fmt = formatar_tabela_classificacao_oficial(df_gb_raw, mapa_escudos)
                renderizar_tabela_html(df_gb_fmt)
            else:
                st.info("Dados do Grupo B indisponíveis no momento.")

elif opcao == "Jogos":
    botao_voltar_inicio("jogos")
    renderizar_cabecalho_secao("📅 Tabela de Jogos — Sub-13 Masculino")
    df_jogos_todos = obter_df_jogos()
    
    if not df_jogos_todos.empty:
        todas_equipes = pd.concat([df_jogos_todos["Mandante"], df_jogos_todos["Visitante"]]).unique()
        equipe_sel = criar_filtro_equipe(todas_equipes, key="filtro_jogos")
        
        if equipe_sel != "Todas as Equipes":
            cond = (df_jogos_todos["Mandante"].str.strip() == equipe_sel) | (df_jogos_todos["Visitante"].str.strip() == equipe_sel)
            df_jogos_filtrados = df_jogos_todos[cond].copy()
        else:
            df_jogos_filtrados = df_jogos_todos.copy()

        df_jogos_filtrados["Mandante"] = df_jogos_filtrados["Mandante"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
        df_jogos_filtrados["Visitante"] = df_jogos_filtrados["Visitante"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))

        tab_anteriores, tab_proximos = st.tabs(["⏪ Jogos Anteriores", "⏩ Próximos Jogos"])
        
        is_realizado = df_jogos_filtrados["Placar"].str.contains(r"\d", regex=True)
        df_anteriores = df_jogos_filtrados[is_realizado].copy()
        df_proximos = df_jogos_filtrados[~is_realizado].copy()
        
        with tab_anteriores:
            st.markdown("<h3 style='color: #ffffff; font-size: 15px;'>⏪ Jogos Anteriores (Com Resultado)</h3>", unsafe_allow_html=True)
            if not df_anteriores.empty:
                renderizar_tabela_html(df_anteriores)
            else:
                st.info("Nenhum jogo anterior encontrado para a seleção.")
                
        with tab_proximos:
            st.markdown("<h3 style='color: #ffffff; font-size: 15px;'>⏩ Próximos Jogos (A Realizar)</h3>", unsafe_allow_html=True)
            if not df_proximos.empty:
                renderizar_tabela_html(df_proximos)
            else:
                st.info("Nenhum próximo jogo pendente para a seleção.")
    else:
        st.error("Erro na comunicação com o servidor da liga ou extração de jogos.")

elif opcao == "Artilharia":
    botao_voltar_inicio("artilharia")
    renderizar_cabecalho_secao("🎯 Artilharia — Sub-13 Masculino")
    soup = carregar_dados_url(URL_ARTILHARIA)
    if soup:
        dfs_art = extrair_tabelas_soup(soup)
        if dfs_art:
            df_art_raw = limpar_colunas_df(dfs_art[0])
            
            novas_linhas = []
            for index, row in df_art_raw.iterrows():
                colocacao = row.iloc[0] if len(row) > 0 else (index + 1)
                texto_misto = str(row.iloc[1]) if len(row) > 1 else ""
                gols = row.iloc[2] if len(row) > 2 else ""

                padrao_separacao = r"\b(colégio|colegio|escola|mackenzie|sport|náutico|nautico|santa cruz|cruz|america|américa|retrô|retro|flamengo|vasco|botafogo|fluminense|bahia|vitória|vitoria|ceará|ceara|fortaleza)\b"
                match = re.search(padrao_separacao, texto_misto, re.IGNORECASE)

                if match:
                    ponto_corte = match.start()
                    atleta = texto_misto[:ponto_corte].strip().title()
                    equipe = texto_misto[ponto_corte:].strip().title()
                else:
                    equipe_encontrada = "Não identificada"
                    atleta = texto_misto.strip().title()
                    for k in mapa_escudos.keys():
                        if k in texto_misto.lower():
                            idx_k = texto_misto.lower().find(k)
                            atleta = texto_misto[:idx_k].strip().title()
                            equipe_encontrada = texto_misto[idx_k:].strip().title()
                            break
                    equipe = equipe_encontrada

                novas_linhas.append({
                    "Colocação": colocacao,
                    "Nome do Atleta": atleta,
                    "Nome da Equipe": equipe,
                    "Quantidade de gols": gols
                })

            df_art = pd.DataFrame(novas_linhas)

            equipe_sel = criar_filtro_equipe(df_art["Nome da Equipe"].unique(), key="filtro_artilharia")
            if equipe_sel != "Todas as Equipes":
                df_art = df_art[df_art["Nome da Equipe"].astype(str).str.strip() == equipe_sel]

            df_art["Nome da Equipe"] = df_art["Nome da Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
            renderizar_tabela_html(df_art)
        else:
            st.warning("Nenhuma tabela de artilharia foi encontrada.")
    else:
        st.error("Erro na comunicação com o servidor da liga.")

elif opcao == "Cartões Amarelos e Vermelhos":
    botao_voltar_inicio("cartoes")
    renderizar_cabecalho_secao("📋 Controle Oficial de Cartões — Sub-13 Masculino")
    soup = carregar_dados_url(URL_CARTOES)
    
    amarelos_list = []
    vermelhos_list = []
    
    if soup:
        dfs_cartoes = extrair_tabelas_soup(soup)
        for df in dfs_cartoes:
            df_limpo = limpar_colunas_df(df)
            cols = [str(c).lower() for c in df_limpo.columns]
            
            if any("amarel" in c for c in cols):
                amarelos_list.append(df_limpo)
            elif any("vermelh" in c for c in cols):
                vermelhos_list.append(df_limpo)
            elif len(amarelos_list) == 0:
                amarelos_list.append(df_limpo)
            elif len(vermelhos_list) == 0:
                vermelhos_list.append(df_limpo)

        df_amarelos = pd.concat(amarelos_list, ignore_index=True) if amarelos_list else pd.DataFrame()
        df_vermelhos = pd.concat(vermelhos_list, ignore_index=True) if vermelhos_list else pd.DataFrame()
        
        for df_c in [df_amarelos, df_vermelhos]:
            if not df_c.empty:
                for col in df_c.columns:
                    if col.lower() in ["clube", "equipe/clube"]:
                        df_c.rename(columns={col: "Equipe"}, inplace=True)

        eqs_amarelos = df_amarelos["Equipe"].dropna().unique() if not df_amarelos.empty and "Equipe" in df_amarelos.columns else []
        eqs_vermelhos = df_vermelhos["Equipe"].dropna().unique() if not df_vermelhos.empty and "Equipe" in df_vermelhos.columns else []
        todas_eqs = list(set(list(eqs_amarelos) + list(eqs_vermelhos)))
        
        equipe_sel = criar_filtro_equipe(todas_eqs, key="filtro_cartoes")
        
        if equipe_sel != "Todas as Equipes":
            if not df_amarelos.empty and "Equipe" in df_amarelos.columns:
                df_amarelos = df_amarelos[df_amarelos["Equipe"].astype(str).str.strip() == equipe_sel]
            if not df_vermelhos.empty and "Equipe" in df_vermelhos.columns:
                df_vermelhos = df_vermelhos[df_vermelhos["Equipe"].astype(str).str.strip() == equipe_sel]

        for df_c in [df_amarelos, df_vermelhos]:
            if not df_c.empty and "Equipe" in df_c.columns:
                df_c["Equipe"] = df_c["Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))

        tab_amarelos, tab_vermelhos = st.tabs(["🟨 Cartões Amarelos", "🟥 Cartões Vermelhos"])

        with tab_amarelos:
            st.markdown("<h3 style='color: #ffffff;'>Cartões Amarelos</h3>", unsafe_allow_html=True)
            if not df_amarelos.empty:
                renderizar_tabela_html(df_amarelos)
            else:
                st.info("Nenhum registro de cartão amarelo para esta seleção.")

        with tab_vermelhos:
            st.markdown("<h3 style='color: #ffffff;'>Cartões Vermelhos</h3>", unsafe_allow_html=True)
            if not df_vermelhos.empty:
                renderizar_tabela_html(df_vermelhos)
            else:
                st.info("Nenhum registro de cartão vermelho para esta seleção.")
    else:
        st.error("Erro na comunicação com o servidor da liga.")

elif opcao == "Suspensão":
    botao_voltar_inicio("suspensao")
    renderizar_cabecalho_secao("🚫 Controle de Suspensões e Penalizações — Sub-13 Masculino")
    soup = carregar_dados_url(URL_SUSPENSOES)
    
    if soup:
        dfs_susp = extrair_tabelas_soup(soup)
        
        if dfs_susp:
            dfs_susp_limpos = [limpar_colunas_df(d) for d in dfs_susp]
            df_bruto = pd.concat(dfs_susp_limpos, ignore_index=True)
            
            for col in df_bruto.columns:
                if col.lower() in ["clube", "equipe/clube"]:
                    df_bruto.rename(columns={col: "Equipe"}, inplace=True)

            cols_equipe = [c for c in df_bruto.columns if "equipe" in str(c).lower() or "clube" in str(c).lower()]
            todas_eqs = []
            for c in cols_equipe:
                todas_eqs.extend(df_bruto[c].dropna().unique())
            
            equipe_sel = criar_filtro_equipe(todas_eqs, key="filtro_suspensao")
            
            if equipe_sel != "Todas as Equipes":
                cond = pd.Series([False] * len(df_bruto))
                for c in cols_equipe:
                    cond = cond | (df_bruto[c].astype(str).str.strip() == equipe_sel)
                df_bruto = df_bruto[cond].copy()

            tab_atletas, tab_comissao, tab_equipes = st.tabs([
                "🏃 Penalização de Atletas", 
                "📋 Penalização de Comissão Técnica", 
                "🛡️ Penalização de Equipes"
            ])

            with tab_atletas:
                st.markdown("<h3 style='color: #ffffff;'>Penalização de Atletas</h3>", unsafe_allow_html=True)
                if "Atleta" in df_bruto.columns:
                    df_atl = df_bruto[
                        df_bruto["Atleta"].notna() & 
                        (~df_bruto["Atleta"].astype(str).str.lower().isin(["none", "nan", ""]))
                    ].copy()
                    
                    if not df_atl.empty:
                        if "Equipe" in df_atl.columns:
                            df_atl["Equipe"] = df_atl["Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                        cols_desejadas = ["Equipe", "Atleta", "Penalização", "Situação"]
                        cols_finais = [c for c in cols_desejadas if c in df_atl.columns]
                        renderizar_tabela_html(df_atl[cols_finais])
                    else:
                        st.info("Nenhuma penalização de atleta encontrada para o filtro selecionado.")
                else:
                    st.info("Nenhuma penalização de atleta encontrada.")

            with tab_comissao:
                st.markdown("<h3 style='color: #ffffff;'>Penalização de Comissão Técnica</h3>", unsafe_allow_html=True)
                
                cols_brutas = list(df_bruto.columns)
                col_eq_comissao = None
                col_membro_nome = None
                
                for c in cols_brutas:
                    c_str = str(c).lower()
                    if "membro da comissão - equipe" in c_str and "1" not in c_str and "unnamed" not in c_str:
                        col_eq_comissao = c
                    elif "membro" in c_str or "unnamed: 4" in c_str or ".1" in c_str:
                        col_membro_nome = c
                        
                if not col_membro_nome and len(cols_brutas) >= 5:
                    col_membro_nome = cols_brutas[4]
                if not col_eq_comissao and len(cols_brutas) >= 4:
                    col_eq_comissao = cols_brutas[3]

                if col_membro_nome:
                    df_com = df_bruto[
                        df_bruto[col_membro_nome].notna() & 
                        (~df_bruto[col_membro_nome].astype(str).str.lower().isin(["none", "nan", ""]))
                    ].copy()
                    
                    if not df_com.empty:
                        df_com_exibir = pd.DataFrame()
                        
                        if col_eq_comissao and col_eq_comissao in df_com.columns:
                            df_com_exibir["Equipe"] = df_com[col_eq_comissao].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                        elif "Equipe" in df_com.columns:
                            df_com_exibir["Equipe"] = df_com["Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                            
                        df_com_exibir["Membro da Comissão"] = df_com[col_membro_nome]
                        
                        if "Penalização" in df_com.columns:
                            df_com_exibir["Penalização"] = df_com["Penalização"]
                        if "Situação" in df_com.columns:
                            df_com_exibir["Situação"] = df_com["Situação"]
                            
                        renderizar_tabela_html(df_com_exibir)
                    else:
                        st.info("Nenhuma penalização de comissão técnica encontrada para o filtro selecionado.")
                else:
                    st.info("Nenhuma penalização de comissão técnica encontrada.")

            with tab_equipes:
                st.markdown("<h3 style='color: #ffffff;'>Penalização de Equipes</h3>", unsafe_allow_html=True)
                df_eq = df_bruto.copy()
                
                if "Atleta" in df_eq.columns:
                    df_eq = df_eq[df_eq["Atleta"].isna() | df_eq["Atleta"].astype(str).str.lower().isin(["none", "nan", ""])]
                
                if col_membro_nome and col_membro_nome in df_eq.columns:
                    df_eq = df_eq[df_eq[col_membro_nome].isna() | df_eq[col_membro_nome].astype(str).str.lower().isin(["none", "nan", ""])]
                
                if "Equipe" in df_eq.columns:
                    df_eq = df_eq[df_eq["Equipe"].notna() & (~df_eq["Equipe"].astype(str).str.lower().isin(["none", "nan", ""]))]
                
                if not df_eq.empty:
                    col_desc = [c for c in df_eq.columns if "descrição" in str(c).lower() or "ocorrencia" in str(c).lower()]
                    
                    if "Equipe" in df_eq.columns:
                        df_eq["Equipe"] = df_eq["Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                    cols_eq = ["Equipe"] if "Equipe" in df_eq.columns else []
                    renomear_eq = {}
                    
                    if col_desc:
                        cols_eq.append(col_desc[0])
                        renomear_eq[col_desc[0]] = "Descrição da ocorrência"
                        
                    df_eq_exibir = df_eq[cols_eq].rename(columns=renomear_eq)
                    df_eq_exibir = df_eq_exibir.loc[:, ~df_eq_exibir.columns.duplicated()]
                    renderizar_tabela_html(df_eq_exibir)
                else:
                    st.info("Nenhuma penalização direta aplicada a equipes para o filtro selecionado.")
        else:
            tab_atletas, tab_comissao, tab_equipes = st.tabs([
                "🏃 Penalização de Atletas", 
                "📋 Penalização de Comissão Técnica", 
                "🛡️ Penalização de Equipes"
            ])
            with tab_atletas:
                st.info("Nenhum dado encontrado.")
            with tab_comissao:
                st.info("Nenhum dado encontrado.")
            with tab_equipes:
                st.info("Nenhum dado encontrado.")
    else:
        st.error("Erro na comunicação com o servidor da liga.")

elif opcao == "Atletas Sub-13 Santa Maria":
    botao_voltar_inicio("atletas_sub13_sm")
    renderizar_cabecalho_secao("👥 Atletas da Categoria Sub-13 — Colégio Santa Maria")
    
    # 1. Carrega a página principal da equipe para encontrar o link direto da guia/aba Sub-13
    soup_equipe_base = carregar_dados_url(URL_EQUIPE_SANTA_MARIA_BASE)
    url_guia_sub13 = URL_EQUIPE_SANTA_MARIA_BASE
    
    if soup_equipe_base:
        for a in soup_equipe_base.find_all("a", href=True):
            texto_link = a.get_text(strip=True).lower()
            href_link = a['href'].lower()
            if ("sub-13" in texto_link or "sub13" in texto_link or "sub-13" in href_link or "sub13" in href_link) and "categoria" in href_link:
                url_guia_sub13 = a['href']
                if not url_guia_sub13.startswith("http"):
                    url_guia_sub13 = f"https://www.nossaliga.com.br{url_guia_sub13}"
                break

    # 2. Acessa a guia específica do Sub-13 da equipe
    soup_sub13 = carregar_dados_url(url_guia_sub13)
    
    if soup_sub13:
        dfs_atletas = extrair_tabelas_soup(soup_sub13)
        df_final_atletas = pd.DataFrame()
        
        if dfs_atletas:
            frames_filtrados = []
            for d in dfs_atletas:
                df_limpo = limpar_colunas_df(d)
                if not df_limpo.empty:
                    # Verifica se a tabela contém nomes de atletas ou dados relevantes de elenco
                    texto_df = df_limpo.astype(str).agg(' '.join, axis=1).str.lower()
                    if len(df_limpo) > 1 or any(k in texto_df.values[0] for k in ["nome", "atleta", "jogador", "nº", "numero"]):
                        frames_filtrados.append(df_limpo)
                        
            if frames_filtrados:
                df_final_atletas = pd.concat(frames_filtrados, ignore_index=True)
                
                # Remove colunas duplicadas se houver
                df_final_atletas = df_final_atletas.loc[:, ~df_final_atletas.columns.duplicated()]
                
                if not df_final_atletas.empty:
                    st.markdown(f"<div style='font-size: 13px; color: #f8f063; font-weight: 700; margin-bottom: 12px;'>📋 Elenco oficial extraído da guia Sub-13</div>", unsafe_allow_html=True)
                    renderizar_tabela_html(df_final_atletas)
                else:
                    st.info("Nenhum atleta encontrado na tabela da guia Sub-13.")
            else:
                st.info("Nenhuma tabela válida de atletas localizada na guia Sub-13.")
        else:
            # Caso os atletas estejam listados em cartões ou blocos de texto na guia Sub-13
            cards_atletas = soup_sub13.find_all(["div", "section"], class_=re.compile(r"atleta|jogador|elenco|card", re.IGNORECASE))
            encontrou = False
            if cards_atletas:
                for card in cards_atletas:
                    texto_card = card.get_text(strip=True)
                    if len(texto_card) > 3:
                        st.markdown(f"<div style='background:#ffffff; color:#110888; padding:10px; border-radius:8px; margin-bottom:8px; font-weight:800; font-size:12px;'>{texto_card}</div>", unsafe_allow_html=True)
                        encontrou = True
            
            if not encontrou:
                for p in soup_sub13.find_all(["p", "li", "span", "div"]):
                    t = p.get_text(strip=True)
                    if len(t) > 5 and ("atleta" in t.lower() or "jogador" in t.lower()):
                        st.markdown(f"<div style='background:#ffffff; color:#110888; padding:10px; border-radius:8px; margin-bottom:8px; font-weight:800; font-size:12px;'>{t}</div>", unsafe_allow_html=True)
                        encontrou = True
            
            if not encontrou:
                st.info("Nenhum registro de atleta foi localizado diretamente na guia Sub-13 desta equipe.")
    else:
        st.error("Erro na comunicação com o servidor da liga ao carregar a guia Sub-13 do Colégio Santa Maria.")