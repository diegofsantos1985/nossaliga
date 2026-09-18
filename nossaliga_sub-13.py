import io
import re
import pandas as pd
import requests
import streamlit as st
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# -----------------------------------------------------------------------------
# CONFIGURAÇÃO DE TELA
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Nossa Liga Futsal 2026 - Sub-13 Masculino",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Estilização CSS customizada
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

    .stApp { background-color: #f4f6f9; }
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
    
    /* Metrics Cards */
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }
    .metric-value { font-size: 24px; font-weight: 800; color: #160e91; }
    .metric-label { font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-top: 4px; }
    
    /* Match Card Container */
    .match-box {
        background: #ffffff;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .match-header {
        font-size: 12px;
        font-weight: 800;
        color: #475569;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 15px;
    }
    .team-name { 
        font-size: 18px; 
        font-weight: 800; 
        color: #0f172a; 
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }
    .score-badge {
        font-size: 22px;
        font-weight: 800;
        color: #160e91;
        background: #f1f5f9;
        padding: 8px 18px;
        border-radius: 8px;
        display: inline-block;
    }
    .status-vitoria {
        background-color: #22c55e;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 800;
        font-size: 11px;
    }
    .status-derrota {
        background-color: #ef4444;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 800;
        font-size: 11px;
    }
    .status-empate {
        background-color: #64748b;
        color: white;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 800;
        font-size: 11px;
    }

    /* ESTILIZAÇÃO DAS SUB-ABAS (ST.TABS) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: transparent;
        border-bottom: none !important;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #110888 !important;
        color: #ffffff !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15) !important;
        transition: all 0.2s ease-in-out !important;
        height: auto !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #1a0fb3 !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 14px rgba(0, 0, 0, 0.25) !important;
    }

    .stTabs [aria-selected="true"] {
        background-color: #080352 !important;
        color: #ffffff !important;
        border: 2px solid #3b82f6 !important;
        box-shadow: 0 4px 12px rgba(17, 8, 136, 0.4) !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* ESTILIZAÇÃO DOS FILTROS (ST.SELECTBOX) */
    div[data-testid="stSelectbox"] label {
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #110888 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        margin-bottom: 4px !important;
    }

    div[data-testid="stSelectbox"] > div > div {
        background-color: #ffffff !important;
        color: #110888 !important;
        border-radius: 8px !important;
        border: 2px solid #110888 !important;
        font-weight: 800 !important;
        min-height: 38px !important;
        height: 38px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }

    div[data-testid="stSelectbox"] > div > div:hover {
        border-color: #1a0fb3 !important;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.12) !important;
    }

    div[data-testid="stSelectbox"] svg {
        fill: #110888 !important;
    }

    div[data-testid="stSelectbox"] [data-baseweb="select"] * {
        color: #110888 !important;
        font-weight: 800 !important;
    }

    .btn-limpar-container {
        display: flex;
        align-items: flex-end;
        height: 100%;
        padding-bottom: 2px;
    }
    
    .custom-table {
        width: 100%;
        border-collapse: collapse;
        background-color: #ffffff;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }
    .custom-table th {
        background-color: #110888;
        color: #ffffff;
        font-weight: 700;
        text-align: left;
        padding: 10px 14px;
        font-size: 13px;
    }
    .custom-table td {
        padding: 8px 14px;
        border-bottom: 1px solid #e2e8f0;
        font-size: 13px;
        color: #1e293b;
    }
    .custom-table tr:hover {
        background-color: #f8fafc;
    }
    .team-cell {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
    }
    .team-logo {
        width: 22px;
        height: 22px;
        object-fit: contain;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ENDEREÇOS E HEADERS
# -----------------------------------------------------------------------------
URL_CLASSIFICACAO = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978"
URL_ARTILHARIA = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978/estatisticas/artilharia"
URL_CARTOES = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/estatisticas/cartoes"
URL_SUSPENSOES = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/categoria/sub-13-masculino/19978/estatisticas/suspensoes"
URL_JOGOS = "https://www.nossaliga.com.br/futsal/nossa-liga-futsal-2026/16-edicao-edicao-ano-2026/5361/impressao/categoria/19978/0"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# -----------------------------------------------------------------------------
# FUNÇÕES DE RASPAGEM E UTILITÁRIOS (ROBUSTA SEM DEPENDER DE LXML)
# -----------------------------------------------------------------------------
@st.cache_data(ttl=60)
def carregar_dados_url(url):
    try:
        resp = requests.get(url, headers=HEADERS, verify=False, timeout=15)
        if resp.status_code != 200:
            st.error(f"O servidor bloqueou o acesso ou retornou erro. Código HTTP: {resp.status_code} para o URL: {url}")
            return None
        soup = BeautifulSoup(resp.content, "html.parser")
        return soup
    except Exception as e:
        st.error(f"Erro de ligação ao servidor: {e}")
        return None

def extrair_tabelas_soup(soup):
    """Extrai tabelas HTML usando puro BeautifulSoup, eliminando erros do lxml."""
    dfs = []
    if not soup:
        return dfs
    for table in soup.find_all("table"):
        rows = []
        for tr in table.find_all("tr"):
            cells = [td.get_text(strip=True) for td in tr.find_all(["th", "td"])]
            if cells:
                rows.append(cells)
        if rows:
            try:
                if len(rows) > 1 and len(rows[0]) == len(rows[1]):
                    df = pd.DataFrame(rows[1:], columns=rows[0])
                else:
                    df = pd.DataFrame(rows)
                dfs.append(df)
            except Exception:
                pass
    return dfs

def limpar_colunas_df(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = ['_'.join(str(c) for c in col if 'unnamed' not in str(c).lower()).strip() for col in df.columns]
    else:
        df.columns = [str(c).strip() for c in df.columns]
    return df

@st.cache_data(ttl=300)
def obter_mapeamento_escudos():
    soup = carregar_dados_url(URL_CLASSIFICACAO)
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
        return f'<div class="team-cell"><img src="{url_escudo}" class="team-logo" /><span>{nome_clean}</span></div>'
    return f'<span>{nome_clean}</span>'

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
    
    soup = carregar_dados_url(URL_CLASSIFICACAO)
    dfs = extrair_tabelas_soup(soup) if soup else []
        
    if dfs:
        df_geral = limpar_colunas_df(dfs[0])
        col_eq = [c for c in df_geral.columns if any(k in str(c).lower() for k in ["equipe", "clube", "times", "nome"])]
        target_col = col_eq[0] if col_eq else df_geral.columns[1] if len(df_geral.columns) > 1 else df_geral.columns[0]
        
        for idx, row in df_geral.iterrows():
            if "santa maria" in str(row[target_col]).lower():
                col_pos = df_geral.columns[0]
                val_pos = re.sub(r'[ºª°]', '', str(row[col_pos])).strip()
                pos_geral = f"{val_pos}º" if val_pos.isdigit() else f"{row[col_pos]}º"
                break

        if len(dfs) >= 2:
            df_g2 = limpar_colunas_df(dfs[1])
            col_eq2 = [c for c in df_g2.columns if any(k in str(c).lower() for k in ["equipe", "clube", "times", "nome"])]
            target_col2 = col_eq2[0] if col_eq2 else df_g2.columns[1] if len(df_g2.columns) > 1 else df_g2.columns[0]
            
            for idx, row in df_g2.iterrows():
                if "santa maria" in str(row[target_col2]).lower():
                    col_pos = df_g2.columns[0]
                    val_pos = re.sub(r'[ºª°]', '', str(row[col_pos])).strip()
                    pos_grupo = f"{val_pos}º" if val_pos.isdigit() else f"{row[col_pos]}º"
                    break
        else:
            pos_grupo = pos_geral
            
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

opcoes_menu = ["Início", "Classificação Sub-13", "Jogos", "Artilharia", "Cartões Amarelos e Vermelhos", "Suspensão"]

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
                <div class="metric-value" style="font-size:18px; padding-top:6px;">
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
                    <div style="font-size:13px; color:#64748b; margin-bottom:12px; font-weight:600;">
                        📅 <b>Data:</b> {prox['Data']} às {prox['Horário']} &nbsp;|&nbsp; 📍 <b>Local:</b> {prox['Local']} &nbsp;|&nbsp; 🏷️ <b>Jogo #{prox['Nº Jogo']}</b>
                    </div>
                    <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
                        <div style="flex:1;">
                            <div class="team-name">{mandante_formatted}</div>
                            <div style="font-size:11px; color:#94a3b8; font-weight:700; margin-top:2px;">MANDANTE</div>
                        </div>
                        <div style="padding: 0 20px;">
                            <span class="score-badge">X</span>
                        </div>
                        <div style="flex:1;">
                            <div class="team-name">{visitante_formatted}</div>
                            <div style="font-size:11px; color:#94a3b8; font-weight:700; margin-top:2px;">VISITANTE</div>
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
                    <div style="font-size:13px; color:#64748b; margin-bottom:12px; font-weight:600;">
                        📅 <b>Data:</b> {ult_sm['Data']} às {ult_sm['Horário']} &nbsp;|&nbsp; 📍 <b>Local:</b> {ult_sm['Local']} &nbsp;|&nbsp; 🏷️ <b>Jogo #{ult_sm['Nº Jogo']}</b> &nbsp; {tag_status}
                    </div>
                    <div style="display:flex; justify-content:space-around; align-items:center; text-align:center;">
                        <div style="flex:1;">
                            <div class="team-name">{mandante_sm}</div>
                            <div style="font-size:11px; color:#94a3b8; font-weight:700; margin-top:2px;">MANDANTE</div>
                        </div>
                        <div style="padding: 0 20px;">
                            <span class="score-badge">{ult_sm['Placar']}</span>
                        </div>
                        <div style="flex:1;">
                            <div class="team-name">{visitante_sm}</div>
                            <div style="font-size:11px; color:#94a3b8; font-weight:700; margin-top:2px;">VISITANTE</div>
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
                
                st.markdown(f"<div style='font-size: 13px; color: #475569; font-weight: 700; margin-bottom: 12px;'>📅 Data da Rodada: {ultima_data}</div>", unsafe_allow_html=True)
                
                for _, ult in df_ultima_rodada.iterrows():
                    m_fmt = formatar_equipe_com_escudo(ult['Mandante'], mapa_escudos)
                    v_fmt = formatar_equipe_com_escudo(ult['Visitante'], mapa_escudos)
                    
                    st.markdown(f"""
                        <div style="display:flex; justify-content:space-between; align-items:center; background:#ffffff; padding:10px 14px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:8px; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                            <div style="flex:2; text-align:left; font-size:12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{m_fmt}</div>
                            <div style="flex:1; text-align:center;"><span style="background:#f1f5f9; padding:4px 8px; border-radius:4px; font-weight:800; color:#160e91; font-size:11px;">{ult['Placar']}</span></div>
                            <div style="flex:2; text-align:right; font-size:12px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{v_fmt}</div>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Nenhum resultado registrado.")
        else:
            st.info("Erro ao carregar os jogos.")

elif opcao == "Classificação Sub-13":
    botao_voltar_inicio("classificacao")
    st.subheader("📊 Classificação — Sub-13 Masculino")
    
    soup_teste = carregar_dados_url(URL_CLASSIFICACAO)
    
    if soup_teste:
        dfs = extrair_tabelas_soup(soup_teste)
        tab_geral, tab_grupos = st.tabs(["🌐 Classificação Geral", "🏆 Classificação por Grupos"])
        
        if dfs:
            dfs_formatadas = []
            for df in dfs:
                df_fmt = limpar_colunas_df(df)
                col_equipe = [c for c in df_fmt.columns if any(k in str(c).lower() for k in ["equipe", "clube", "times", "nome"])]
                if col_equipe:
                    df_fmt[col_equipe[0]] = df_fmt[col_equipe[0]].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                elif len(df_fmt.columns) >= 2:
                    col_target = df_fmt.columns[1]
                    df_fmt[col_target] = df_fmt[col_target].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                dfs_formatadas.append(df_fmt)

            with tab_geral:
                if dfs_formatadas:
                    df_geral = pd.concat(dfs_formatadas, ignore_index=True)
                    renderizar_tabela_html(df_geral)
                else:
                    st.warning("Não foi possível processar a tabela de classificação geral.")

            with tab_grupos:
                if len(dfs_formatadas) >= 2:
                    col_g1, col_g2 = st.columns(2)
                    with col_g1:
                        st.markdown("### 🅰️ Grupo A")
                        renderizar_tabela_html(dfs_formatadas[0])
                    with col_g2:
                        st.markdown("### 🅱️ Grupo B")
                        renderizar_tabela_html(dfs_formatadas[1])
                elif len(dfs_formatadas) == 1:
                    st.markdown("### 🅰️ Grupo A")
                    renderizar_tabela_html(dfs_formatadas[0])
                else:
                    st.warning("Tabelas de grupos não encontradas no momento.")
        else:
            st.warning("A página foi descarregada, mas nenhuma tabela HTML estruturada foi encontrada na página da classificação.")
    else:
        st.error("Não foi possível aceder ao link da classificação devido a um bloqueio ou falha de rede no servidor de origem.")

elif opcao == "Jogos":
    botao_voltar_inicio("jogos")
    st.subheader("📅 Tabela de Jogos — Sub-13 Masculino")
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
            st.markdown("### ⏪ Jogos Anteriores (Com Resultado)")
            if not df_anteriores.empty:
                renderizar_tabela_html(df_anteriores)
            else:
                st.info("Nenhum jogo anterior encontrado para a seleção.")
                
        with tab_proximos:
            st.markdown("### ⏩ Próximos Jogos (A Realizar)")
            if not df_proximos.empty:
                renderizar_tabela_html(df_proximos)
            else:
                st.info("Nenhum próximo jogo pendente para a seleção.")
    else:
        st.error("Erro na comunicação com o servidor da liga ou extração de jogos.")

elif opcao == "Artilharia":
    botao_voltar_inicio("artilharia")
    st.subheader("🎯 Artilharia — Sub-13 Masculino")
    soup = carregar_dados_url(URL_ARTILHARIA)
    if soup:
        dfs_art = extrair_tabelas_soup(soup)
        if dfs_art:
            df_art_raw = dfs_art[0]
            
            novas_linhas = []
            
            for index, row in df_art_raw.iterrows():
                colocacao = row.iloc[0] if len(row) > 0 else (index + 1)
                texto_misto = str(row.iloc[1]) if len(row) > 1 else ""
                gols = row.iloc[2] if len(row) > 2 else ""

                padrao_separacao = r"\b(colégio|colegio|escola|mackenzie)\b"
                match = re.search(padrao_separacao, texto_misto, re.IGNORECASE)

                if match:
                    ponto_corte = match.start()
                    atleta = texto_misto[:ponto_corte].strip().title()
                    equipe = texto_misto[ponto_corte:].strip().title()
                else:
                    atleta = texto_misto.strip().title()
                    equipe = "Não identificada"

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
    st.subheader("📋 Controle Oficial de Cartões — Sub-13 Masculino")
    soup = carregar_dados_url(URL_CARTOES)
    
    amarelos_list = []
    vermelhos_list = []
    
    if soup:
        dfs_cartoes = extrair_tabelas_soup(soup)
        for df in dfs_cartoes:
            cols = [str(c).lower() for c in df.columns]
            
            if any("amarel" in c for c in cols):
                amarelos_list.append(df)
            elif any("vermelh" in c for c in cols):
                vermelhos_list.append(df)
            elif len(amarelos_list) == 0:
                amarelos_list.append(df)
            elif len(vermelhos_list) == 0:
                vermelhos_list.append(df)

        df_amarelos = pd.concat(amarelos_list, ignore_index=True) if amarelos_list else pd.DataFrame()
        df_vermelhos = pd.concat(vermelhos_list, ignore_index=True) if vermelhos_list else pd.DataFrame()
        
        eqs_amarelos = df_amarelos["Equipe"].dropna().unique() if "Equipe" in df_amarelos.columns else []
        eqs_vermelhos = df_vermelhos["Equipe"].dropna().unique() if "Equipe" in df_vermelhos.columns else []
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
            st.markdown("### Cartões Amarelos")
            if not df_amarelos.empty:
                renderizar_tabela_html(df_amarelos)
            else:
                st.info("Nenhum registro de cartão amarelo para esta seleção.")

        with tab_vermelhos:
            st.markdown("### Cartões Vermelhos")
            if not df_vermelhos.empty:
                renderizar_tabela_html(df_vermelhos)
            else:
                st.info("Nenhum registro de cartão vermelho para esta seleção.")
    else:
        st.error("Erro na comunicação com o servidor da liga.")

elif opcao == "Suspensão":
    botao_voltar_inicio("suspensao")
    st.subheader("🚫 Controle de Suspensões e Penalizações — Sub-13 Masculino")
    soup = carregar_dados_url(URL_SUSPENSOES)
    
    if soup:
        dfs_susp = extrair_tabelas_soup(soup)
        
        if dfs_susp:
            df_bruto = pd.concat(dfs_susp, ignore_index=True)
            
            cols_equipe = [c for c in df_bruto.columns if "equipe" in str(c).lower()]
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
                st.markdown("### Penalização de Atletas")
                if "Atleta" in df_bruto.columns:
                    df_atl = df_bruto[
                        df_bruto["Atleta"].notna() & 
                        (~df_bruto["Atleta"].astype(str).str.lower().isin(["none", "nan", ""]))
                    ].copy()
                    
                    if not df_atl.empty:
                        df_atl["Equipe"] = df_atl["Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                        cols_desejadas = ["Equipe", "Atleta", "Penalização", "Situação"]
                        cols_finais = [c for c in cols_desejadas if c in df_atl.columns]
                        renderizar_tabela_html(df_atl[cols_finais])
                    else:
                        st.info("Nenhuma penalização de atleta encontrada para o filtro selecionado.")
                else:
                    st.info("Nenhuma penalização de atleta encontrada.")

            with tab_comissao:
                st.markdown("### Penalização de Comissão Técnica")
                
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
                st.markdown("### Penalização de Equipes")
                df_eq = df_bruto.copy()
                
                if "Atleta" in df_eq.columns:
                    df_eq = df_eq[df_eq["Atleta"].isna() | df_eq["Atleta"].astype(str).str.lower().isin(["none", "nan", ""])]
                
                if col_membro_nome and col_membro_nome in df_eq.columns:
                    df_eq = df_eq[df_eq[col_membro_nome].isna() | df_eq[col_membro_nome].astype(str).str.lower().isin(["none", "nan", ""])]
                
                if "Equipe" in df_eq.columns:
                    df_eq = df_eq[df_eq["Equipe"].notna() & (~df_eq["Equipe"].astype(str).str.lower().isin(["none", "nan", ""]))]
                
                if not df_eq.empty:
                    col_desc = [c for c in df_eq.columns if "descrição" in str(c).lower() or "ocorrencia" in str(c).lower()]
                    
                    df_eq["Equipe"] = df_eq["Equipe"].apply(lambda e: formatar_equipe_com_escudo(e, mapa_escudos))
                    cols_eq = ["Equipe"]
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