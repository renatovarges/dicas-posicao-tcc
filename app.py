import streamlit as st
import pandas as pd
import os
import utils
try:
    import screenshot_utils  # Módulo de Screenshot Server-Side (requer Playwright)
    HAS_PLAYWRIGHT = True
except Exception:
    HAS_PLAYWRIGHT = False
import base64

# Configuração da Página
st.set_page_config(layout="wide", page_title="Dicas do Cartola", page_icon="🎩")

# CSS Global para corrigir contraste de textos
st.markdown("""
<style>
    /* Forçar textos brancos em todo o app */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
        color: #ffffff !important;
    }
    
    /* Labels de inputs */
    label, .stTextInput label, .stSelectbox label, .stNumberInput label {
        color: #ffffff !important;
    }
    
    /* Textos de caption e helper */
    .stCaption, small {
        color: #cccccc !important;
    }
</style>
""", unsafe_allow_html=True)

# --- PIN Protection ---
def check_pin():
    """Verifica PIN se configurado nos Secrets."""
    try:
        pin_correto = st.secrets["PIN"]
    except (KeyError, FileNotFoundError):
        return True  # Sem PIN configurado = acesso livre (uso local)

    if st.session_state.get("autenticado", False):
        return True

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown("## 🔒 Acesso Restrito")
        st.markdown("Digite o PIN para acessar o sistema **TCC**.")
        pin_input = st.text_input("PIN:", type="password", max_chars=4, placeholder="****")

        if st.button("Entrar", type="primary", use_container_width=True):
            if pin_input == pin_correto:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ PIN incorreto! Tente novamente.")

    return False

if not check_pin():
    st.stop()

# --- Helper Assets (Cached) ---
@st.cache_data(show_spinner=False)
def get_base64_encoded(file_path):
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_data(show_spinner=False)
def get_team_logo_b64(team_name):
    path = utils.get_team_logo_path(team_name)
    if path and os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""

@st.cache_data(show_spinner=False)
def render_custom_css():
    # Caminhos
    font_bold_path = os.path.join("assets", "fonts", "Decalotype-ExtraBold.otf")
    font_real_bold_path = os.path.join("assets", "fonts", "Decalotype-Bold.otf")
    font_med_path = os.path.join("assets", "fonts", "Decalotype-Medium.otf")
    bg_path = os.path.join("assets", "logos", "background.jpg")
    
    font_bold_b64 = get_base64_encoded(font_bold_path)
    font_real_bold_b64 = get_base64_encoded(font_real_bold_path)
    font_med_b64 = get_base64_encoded(font_med_path)
    bg_b64 = get_base64_encoded(bg_path)
    
    css = f"""
    /* Fonts Global import */
    @font-face {{
        font-family: 'Decalotype';
        src: url(data:font/otf;base64,{font_bold_b64}) format('opentype');
        font-weight: 800;
        font-style: normal;
        font-display: block;
    }}
    @font-face {{
        font-family: 'Decalotype';
        src: url(data:font/otf;base64,{font_real_bold_b64}) format('opentype');
        font-weight: 700;
        font-style: normal;
        font-display: block;
    }}
    @font-face {{
        font-family: 'Decalotype';
        src: url(data:font/otf;base64,{font_med_b64}) format('opentype');
        font-weight: 500;
        font-style: normal;
        font-display: block;
    }}
    
    /* REPORT CONTAINER */
    .report-container {{
        font-family: 'Decalotype', sans-serif;
        width: 1200px; /* FIXED WIDTH for consistent export */
        margin: 0 auto;
        background-color: #ffffff;
        background-image: url(data:image/jpeg;base64,{bg_b64});
        background-size: cover;
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        padding: 40px; 
        padding-bottom: 0; /* Footer vai até a borda */
        box-sizing: border-box;
        min-height: 1200px;
        color: white;
        -webkit-font-smoothing: antialiased;
        display: flex;
        flex-direction: column;
    }}
    
    /* HEADER V2 */
    .tcc-header {{
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 30px;
        padding: 0 10px;
    }}
    
    .header-logo {{
        height: 100px; /* Slightly smaller to fit better */
        width: auto;
        object-fit: contain;
    }}
    
    .header-title-box {{
        background-color: #0d3b2a;
        color: white;
        padding: 10px 30px; /* Reduced padding */
        border-radius: 12px;
        font-size: 38px; /* Reduced font size to fit one line */
        font-weight: 800;
        text-transform: uppercase;
        border: 2px solid white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
        flex-grow: 1; /* Allow to grow */
        margin: 0 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.4);
        white-space: nowrap; /* Force single line */
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    /* GRID LAYOUT */
    .grid-container {{
        display: flex;
        gap: 30px;
        align-items: flex-start;
    }}
    
    .col-left, .col-right {{
        flex: 1;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }}
    
    /* POSITION TITLE V2 */
    .position-group {{
        width: 100%;
        margin-bottom: 0;
        text-align: center; /* Centers the inline-block title */
    }}

    .pos-title-bar {{
        background-color: #ffffff;
        color: #0d3b2a;
        padding: 6px 30px; /* Wider padding */
        border-radius: 8px;
        font-size: 32px;
        font-weight: 800;
        text-transform: uppercase;
        border: 2px solid #0d3b2a;
        display: inline-block;
        margin-bottom: 12px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }}
    
    /* PLAYER CARD COMPACT */
    .player-card {{
        background-color: #0d3b2a;
        border: 2px solid #1E7C5C;
        border-radius: 16px;
        padding: 12px 18px;
        margin-bottom: 12px;
        box-shadow: 0 3px 6px rgba(0,0,0,0.3);
        color: white;
        display: flex;
        justify-content: space-between;
        align-items: center;
        text-align: left; /* Reset text align from parent */
    }}
    
    .card-left {{
        display: flex;
        align-items: center;
        gap: 12px;
    }}
    
    .team-circle {{
        width: 68px; /* Slightly larger default */
        height: 68px;
        background: white;
        border-radius: 50%;
        display: flex;
        justify-content: center;
        align-items: center;
        border: 3px solid white;
        box-shadow: 0 6px 12px rgba(0,0,0,0.6);
        flex-shrink: 0;
    }}
    
    .team-circle.sm {{
        width: 60px; /* Smaller for specific teams */
        height: 60px;
    }}
    
    .team-logo {{
        width: 96%; /* Increase size to reduce white padding */
        height: 96%;
        object-fit: contain;
        filter: drop-shadow(0px 2px 2px rgba(0,0,0,0.2));
    }}

    .p-name {{
        font-size: 24px;
        font-weight: 800;
        text-transform: uppercase;
        /* allow wrapping */
        display: block; 
        line-height: 1.1;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
    }}
    
    .name-text {{
        margin-right: 6px;
        vertical-align: middle;
    }}
    
    /* ICONS */
    .icon-badge {{
        display: inline-flex;
        align-items: center;
        justify-content: center;
        border-radius: 50%;
        color: white;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
        margin: 2px 3px; 
        vertical-align: middle;
        position: relative;
        top: -1px; /* Visual tweak for alignment */
    }}
    
    .icon-star {{
        color: #f1c40f; 
        font-size: 26px; /* Slightly larger */
        background-color: transparent !important; /* Force Clear */
        box-shadow: none !important; /* Force Clear */
        filter: drop-shadow(0px 1px 1px rgba(0,0,0,0.5));
    }}
    
    .icon-c {{
        width: 24px; 
        height: 24px;
        background-color: #2ecc71; 
        font-size: 16px;
        border: 2px solid white;
    }}
    
    .icon-rl {{
        width: 24px; 
        height: 24px;
        background-color: #e67e22; 
        font-size: 12px;
        border: 2px solid white;
    }}
    
    /* STATS & COLORS */
    .stats-row {{
        display: flex;
        gap: 12px; /* Close gap between stats */
        align-items: flex-start; /* Align top */
    }}
    
    .stat-box {{
        text-align: center;
        min-width: 55px;
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Top align */
        height: 100%;
    }}
    
    .stat-label {{
        font-size: 14px; /* Default larger */
        color: #ffffff;
        font-weight: 800;
        margin-bottom: 8px;
        letter-spacing: 0.5px;
        text-shadow: 0 1px 2px rgba(0,0,0,0.5);
        align-self: center;
        text-transform: uppercase;
    }}
    
    .lbl-price {{ font-size: 15px; }} /* Slightly larger for C$ */
    
    .stat-value {{
        font-size: 22px;
        font-weight: 800;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        line-height: 1;
        margin-top: auto; 
        padding-top: 8px; /* Pushes value down to align with Conf Circle */
    }}
    
    .conf-circle {{
        width: 32px;
        height: 32px;
        border-radius: 50%;
        color: #0d3b2a;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 900;
        font-size: 18px;
        margin: 0 auto;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        border: 2px solid rgba(255,255,255,0.2);
    }}
    
    /* CONFIDENCE COLORS */
    .bg-conf-a {{ background-color: #2ecc71; }} /* Strong Green */
    .bg-conf-b {{ background-color: #cddc39; }} /* Lime/Green Yellow */
    .bg-conf-c {{ background-color: #f1c40f; }} /* Yellow */
    .bg-conf-d {{ background-color: #e74c3c; }} /* Red */
    
    .val-green {{ color: #2ecc71; }}
    .val-red {{ color: #ff5252; }}
    .val-white {{ color: #ffffff; }}

    /* FOOTER V3 - Duas linhas */
    .tcc-footer {{
        background-color: #0d3b2a;
        margin-top: auto; /* EMPURRA pro fundo da arte */
        margin-left: -40px; /* Compensa o padding do container */
        margin-right: -40px;
        padding: 0;
        display: flex;
        align-items: center;
        border-top: 3px solid #a3e635;
        font-size: 16px;
        font-weight: 700;
        color: white;
        border-radius: 0;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.2);
        min-height: 90px;
    }}
    
    .footer-left {{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        padding: 10px 20px;
    }}
    
    .footer-center {{
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px 0;
        gap: 6px;
    }}
    
    .footer-right {{
        flex: 0 0 auto;
        display: flex;
        align-items: center;
        padding: 10px 20px;
    }}
    
    .footer-logo-img {{
        height: 60px;
        width: auto;
    }}
    
    .footer-exclusive-text {{
        font-size: 14px;
        font-weight: 700;
        letter-spacing: 1px;
        color: #ffffff;
        text-transform: uppercase;
    }}
    
    .legend-box {{
        display: flex;
        gap: 25px;
        font-size: 14px;
        align-items: center;
        font-weight: 600;
    }}
    """
    return css

# --- Session State Management ---
if 'players' not in st.session_state:
    st.session_state['players'] = {
        'Goleiros': [],
        'Laterais': [],
        'Zagueiros': [],
        'Meias': [],
        'Atacantes': [],
        'Técnicos': []
    }

def add_player(pos, player_dict):
    st.session_state['players'][pos].append(player_dict)

def remove_player(pos, idx):
    if 0 <= idx < len(st.session_state['players'][pos]):
        st.session_state['players'][pos].pop(idx)

def reset_inputs():
    """Resets input widgets to default values."""
    st.session_state['new_p_name'] = ""
    st.session_state['new_p_team'] = ""
    st.session_state['new_p_price'] = 0.0
    st.session_state['new_p_mpv'] = 0.0
    st.session_state['new_conf'] = "A"
    st.session_state['new_is_una'] = False
    st.session_state['new_is_cap'] = False
    st.session_state['new_is_rl'] = False
    st.session_state['player_selector'] = "" # Clear search too

def submit_new_player(pos):
    """Callback to add player and reset inputs."""
    name = st.session_state.get('new_p_name', '').strip()
    if not name:
        st.error("Nome do jogador é obrigatório.")
        return

    new_p = {
        "name": name,
        "team": st.session_state.get('new_p_team', ''),
        "price": st.session_state.get('new_p_price', 0.0),
        "mpv": st.session_state.get('new_p_mpv', 0.0),
        "conf": st.session_state.get('new_conf', 'A'),
        "badges": {
            "unanimidade": st.session_state.get('new_is_una', False),
            "bom_capitao": st.session_state.get('new_is_cap', False),
            "reserva_luxo": st.session_state.get('new_is_rl', False)
        }
    }
    
    add_player(pos, new_p)
    # Use toast for success message since we are in a callback
    st.toast(f"{name} adicionado!", icon="✅")
    reset_inputs()

# --- Sidebar ---
st.sidebar.title("Configurações")

st.sidebar.header("1. API Cartola 🎩")
use_api = st.sidebar.toggle("Usar Dados da API", value=True)
gm_token = st.sidebar.text_input("Token Gato Mestre (Opcional)", help="Para obter o 'Mínimo para Valorizar'")

if st.sidebar.button("🔄 Atualizar Mercado"):
    # Clear cache to force new data fetch/mapping
    st.cache_data.clear()
    
    with st.spinner("Buscando dados do Cartola..."):
        api_data = utils.fetch_mercado_data()
        
        # Validate GM Token
        is_valid, msg = utils.validate_gato_mestre_token(gm_token)
        if gm_token:
            if is_valid:
                st.toast(f"Gato Mestre: {msg}", icon="🐱")
            else:
                st.error(f"Erro Gato Mestre: {msg}")
        
        gm_data = utils.fetch_gato_mestre_data(gm_token) if is_valid else {}
        
        if api_data:
            # Merge GM Data
            processed_data = []
            for atleta in api_data:
                aid = atleta.get('atleta_id')
                mpv = 0.0
                if aid and aid in gm_data:
                    mpv = gm_data[aid]
                
                # Get Team Name
                club_id = str(atleta.get('clube_id'))
                team_name = utils.CLUB_MAP.get(club_id, 'Outros')
                
                # Get Position Name
                pos_id = atleta.get('posicao_id')
                pos_name = utils.map_pos_id_to_name(pos_id)
                
                # Create standardized dict
                processed_data.append({
                    'id': aid,
                    'Jogador_Original': atleta.get('apelido', atleta.get('nome', 'N/A')),
                    'Jogador_Norm': utils.normalize_name(atleta.get('apelido', atleta.get('nome', 'N/A'))),
                    'Time': team_name,
                    'Posicao': pos_name, # Normalized name
                    'Preco': float(atleta.get('preco_num', 0)),
                    'MinValorizar': float(mpv)
                })
            
            st.session_state['data_api'] = pd.DataFrame(processed_data)
            st.toast(f"Mercado Atualizado: {len(processed_data)} jogadores!", icon="✅")
        else:
            st.error("Falha ao buscar dados do Mercado.")

st.sidebar.divider()
st.sidebar.header("2. Upload Manual (Opcional)")
uploaded_api = st.sidebar.file_uploader("Planilha API (Excel)", type=["xlsx"])
rodada_atual = st.sidebar.number_input("Rodada", 1, 38, 2)

# Load Data logic
data_api = None

# Priority: Session State API > Uploaded Excel
if 'data_api' in st.session_state and not st.session_state['data_api'].empty:
    data_api = st.session_state['data_api']
elif uploaded_api:
    try:
        data_api = utils.load_data(uploaded_api)
        st.sidebar.success(f"{len(data_api)} jogadores carregados (Excel)!")
    except Exception as e:
        st.sidebar.error(f"Erro no upload: {e}")

# --- Main Area ---
tab_editor, tab_preview = st.tabs(["📝 Editor", "🎨 Visualização"])

# === EDITOR TAB ===
with tab_editor:
    st.header("Editor de Dicas")
    
    selected_pos = st.selectbox("Selecione a Posição", list(st.session_state['players'].keys()))
    
    # Mapping Display Position to Data Position
    POS_MAPPING = {
        'Goleiros': 'GOLEIRO',
        'Laterais': 'LATERAL', # API returns LATERAL for both?
        'Zagueiros': 'ZAGUEIRO',
        'Meias': 'MEIA',
        'Atacantes': 'ATACANTE',
        'Técnicos': 'TECNICO'
    }
    
    target_pos_api = POS_MAPPING.get(selected_pos, "")
    
    # Initialize inputs if necessary
    if 'new_p_name' not in st.session_state:
        reset_inputs()

    # Form to Add Player
    with st.expander(f"➕ Adicionar Jogador em {selected_pos}", expanded=True):
        col_search, col_manual = st.columns([3, 1])
        
        # Search (if API loaded)
        if data_api is not None:
            # Filter by Position FIRST
            if target_pos_api:
                filtered_pos = data_api[data_api['Posicao'] == target_pos_api].copy()
            else:
                filtered_pos = data_api.copy()
            
            filtered_pos = filtered_pos.sort_values(by='Jogador_Original')
            
            if not filtered_pos.empty:
                filtered_pos['Preco_Fmt'] = filtered_pos['Preco'].apply(lambda x: f"{float(x):.2f}")
                filtered_pos['Display_Str'] = (
                    filtered_pos['Jogador_Original'].astype(str) + 
                    " - " + 
                    filtered_pos['Time'].astype(str) + 
                    " (C$ " + 
                    filtered_pos['Preco_Fmt'] + 
                    ")"
                )
                display_options = filtered_pos['Display_Str'].tolist()
                cols_to_keep = ['Jogador_Original', 'Time', 'Preco', 'MinValorizar']
                filtered_pos.set_index('Display_Str', inplace=True)
                player_map = filtered_pos[cols_to_keep].to_dict('index')
            else:
                display_options = []
                player_map = {}
            
            with col_search:
                # Key 'player_selector' allows us to reset it via session_state
                selected_display = st.selectbox("Selecione o Jogador:", [""] + display_options, key="player_selector")
            
            with col_manual:
                st.write("") # Spacer
                st.write("")
                if st.button("🧹 Limpar Busca"):
                    reset_inputs() # clears everything
                    st.rerun()

            # Logic to populate inputs from selection
            # We check if selection changed or if it's set
            if selected_display and selected_display in player_map:
                row = player_map[selected_display]
                # Check if 'player_selector' changed value.
                if 'last_player_selector' not in st.session_state: st.session_state['last_player_selector'] = ""
                
                if st.session_state['player_selector'] != st.session_state['last_player_selector']:
                     st.session_state['last_player_selector'] = st.session_state['player_selector']
                     st.session_state['new_p_name'] = row['Jogador_Original']
                     st.session_state['new_p_team'] = row.get('Time', 'Unknown')
                     st.session_state['new_p_price'] = float(row.get('Preco', 0))
                     st.session_state['new_p_mpv'] = float(row.get('MinValorizar', 0.0))
                     st.rerun()

        else:
            st.info("Carregue os dados da API para buscar jogadores.")
        
        # Inputs
        c1, c2, c3 = st.columns(3)
        # BIND to session state keys
        p_name = c1.text_input("Nome", key="new_p_name")
        p_team = c2.text_input("Time", key="new_p_team")
        p_price = c3.number_input("Preço (C$)", format="%.2f", key="new_p_price")
        
        c4, c5 = st.columns(2)
        p_mpv = c4.number_input("Mín. P/ Valorizar", format="%.2f", key="new_p_mpv")
        p_conf = c5.select_slider("Confiança", options=["A", "B", "C", "D", "E"], key="new_conf")
        
        # Bagdes
        st.caption("Marcadores Especiais:")
        b1, b2, b3, b4 = st.columns(4)
        is_cap = b1.checkbox("Unanimidade (⭐)", key="new_is_una")
        is_bom_cap = b2.checkbox("Bom Capitão (©)", key="new_is_cap")
        is_rl = b3.checkbox("Reserva Luxo (RL)", key="new_is_rl")

        # Use on_click callback to avoid "modified after instantiation" error
        st.button("Adicionar à Lista", on_click=submit_new_player, args=(selected_pos,))

    # List Current Players
    st.divider()
    st.subheader(f"Lista Atual: {selected_pos}")
    
    current_list = st.session_state['players'][selected_pos]
    if not current_list:
        st.info("Nenhum jogador adicionado nesta posição.")
    else:
        for idx, p in enumerate(current_list):
            c_info, c_action = st.columns([5, 1])
            badges_str = " | ".join([k for k,v in p['badges'].items() if v])
            c_info.markdown(f"**{p['name']}** ({p['team']}) - C$ {p['price']} - Conf: {p['conf']} {f'[{badges_str}]' if badges_str else ''}")
            if c_action.button("🗑️", key=f"del_{selected_pos}_{idx}"):
                remove_player(selected_pos, idx)
                st.rerun()

# === VISUALIZATION TAB ===
with tab_preview:
    st.header("Pré-visualização da Arte")
    
    # Session state for HTML to avoid re-calc
    if 'preview_html' not in st.session_state:
        st.session_state['preview_html'] = None
        
    st.info("⚠️ Otimização: A pré-visualização só é gerada ao clicar no botão abaixo para evitar lentidão durante a edição.")
    
    st.info("⚠️ Otimização: A pré-visualização só é gerada ao clicar no botão abaixo para evitar lentidão durante a edição.")
    
    if st.button("🎨 Gerar/Atualizar Visualização", type="primary"):
        # Render HTML
        bg_css = render_custom_css()
        
        # logo tcc header
        logo_tcc = os.path.join("assets", "logos", "logo_tcc.png") # Main logo
        logo_tcc_b64 = ""
        if os.path.exists(logo_tcc):
            with open(logo_tcc, "rb") as f: logo_tcc_b64 = base64.b64encode(f.read()).decode()

        # logo tcc footer (White)
        logo_tcc_white = os.path.join("assets", "logos", "logo_tcc_branco.png") 
        logo_tcc_white_b64 = ""
        # Fallback to main logo if white doesn't exist, but try white first
        if os.path.exists(logo_tcc_white):
            with open(logo_tcc_white, "rb") as f: logo_tcc_white_b64 = base64.b64encode(f.read()).decode()
        else:
            logo_tcc_white_b64 = logo_tcc_b64
        
        # Build HTML Content - Split Columns
        groups_left = ['Técnicos', 'Laterais', 'Meias']
        groups_right = ['Goleiros', 'Zagueiros', 'Atacantes']
        
        def generate_pos_block(pos_key):
            players = st.session_state['players'].get(pos_key, [])
            if not players: return ""
            
            # SORTING LOGIC:
            # 1. Unanimidade (True < False -> Reverse? No, use not)
            # 2. Capitão
            # 3. Confiança (A < B < C...)
            # 4. Nome
            
            # We want Unanimidade (True) first. Integer(True)=1, Integer(False)=0.
            # So if we sort ascending, 0 comes first (False).
            # We want 1 first. So use 'not' val (False < True).
            
            players.sort(key=lambda x: (
                not x['badges']['unanimidade'],
                not x['badges']['bom_capitao'],
                x['conf'],
                x['name']
            ))

            block_html = f"""
            <div class="position-group">
                <div class="pos-title-bar">{pos_key}</div>
            """
            
            for p in players:
                t_logo = get_team_logo_b64(p['team'])
                t_img = f'<img src="data:image/png;base64,{t_logo}" class="team-logo"/>' if t_logo else ''
                
                # Logic for Team Circle Size
                # Standard is large (68px). Exceptions are normal (60px).
                # Exceptions: São Paulo, Athletico-PR (check actual string), Flamengo
                # Using 'raw' name from input or mapped? p['team'] matches CLUB_MAP values.
                # Common names: "São Paulo", "Athletico-PR", "Flamengo"
                
                team_circle_class = "team-circle"
                if p['team'] in ['São Paulo', 'Athletico-PR', 'Flamengo']:
                    team_circle_class += " sm"

                # ICONS Logic
                icons_html = ""
                if p['badges']['unanimidade']: icons_html += '<span class="icon-badge icon-star">★</span>'
                if p['badges']['reserva_luxo']: icons_html += '<span class="icon-badge icon-rl">RL</span>'
                if p['badges']['bom_capitao']: icons_html += '<span class="icon-badge icon-c">C</span>'
                
                # Confidence Color
                conf_class = "bg-conf-a"
                if p['conf'] == 'B': conf_class = "bg-conf-b"
                if p['conf'] == 'C': conf_class = "bg-conf-c"
                if p['conf'] == 'D': conf_class = "bg-conf-d"
                
                # Valorizar Color Logic (Fixed)
                mpv = float(p.get('mpv', 0.0))
                val_class = "val-white"
                
                if pos_key == 'Técnicos':
                    if mpv <= 2.00: val_class = "val-green"
                    elif mpv > 6.00: val_class = "val-red"
                else: 
                    if mpv <= 3.00: val_class = "val-green"
                    elif mpv > 6.00: val_class = "val-red"

                block_html += f"""
                <div class="player-card">
                    <div class="card-left">
                        <div class="{team_circle_class}">
                            {t_img}
                        </div>
                        <div class="p-name"><span class="name-text">{p['name']}</span>{icons_html}</div>
                    </div>
                        
                    <div class="stats-row">
                        <div class="stat-box">
                            <div class="stat-label lbl-price">C$</div>
                            <div class="stat-value">{p['price']:.1f}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">MPV</div>
                            <div class="stat-value {val_class}">{mpv:.1f}</div>
                        </div>
                        <div class="stat-box">
                            <div class="stat-label">CONF</div>
                            <div class="conf-circle {conf_class}" style="box-shadow: 0 4px 8px rgba(0,0,0,0.5);">{p['conf']}</div>
                        </div>
                    </div>
                </div>
                """
            block_html += "</div>"
            return block_html

        html_left = ""
        for pos in groups_left: html_left += generate_pos_block(pos)
            
        html_right = ""
        for pos in groups_right: html_right += generate_pos_block(pos)

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>{render_custom_css()}</style>
            <!-- REVERT TO HTML-TO-IMAGE (More efficient for large DOMs if configured right) -->
        </head>
        <body>
    <div id="ui-controls" style="position:fixed; top:10px; right:10px; z-index:9999; display:flex; flex-direction:column; gap:8px; align-items:flex-end;">
        <div style="background:rgba(13, 59, 42, 0.9); padding:8px 12px; border-radius:8px; border:1px solid #a3e635; display:flex; flex-direction:column; gap:4px; box-shadow:0 4px 6px rgba(0,0,0,0.3);">
            <div style="display:flex; align-items:center; gap:10px;">
                <span style="color:white; font-weight:bold; font-family:sans-serif; font-size:14px;">Qualidade:</span>
                <select id="resSelect" style="padding:5px; border-radius:4px; border:none; font-weight:bold; cursor:pointer;">
                    <option value="2.0">2.0x (2400px - Padrão)</option>
                    <option value="3.0">3.0x (3600px - Print A3)</option>
                    <option value="4.0">4.0x (4800px - Máxima)</option>
                    <option value="6.0">6.0x (~7200px - 600 DPI)</option>
                </select>
            </div>
            <div style="color:#a3e635; font-family:sans-serif; font-size:11px; max-width:200px; line-height:1.2;">
                * 6.0x é a qualidade "600 DPI" antiga. Só use se seu PC aguentar!
            </div>
        </div>
        <button onclick="window.downloadHighRes()" style="padding:12px 24px; background-color:#0d3b2a; color:white; border:2px solid #a3e635; border-radius:8px; cursor:pointer; font-weight:bold; font-size:16px; box-shadow:0 4px 10px rgba(0,0,0,0.3); transition:all 0.2s; display:flex; align-items:center; gap:8px;">
            ⬇️ BAIXAR PNG
        </button>
    </div>
            <div class="report-container" id="capture">
                <!-- HEADER V2 -->
                <div class="tcc-header">
                    <img src="data:image/png;base64,{logo_tcc_b64}" class="header-logo">
                    <div class="header-title-box">DICAS POR POSIÇÃO &ndash; TCC &ndash; RODADA {rodada_atual}</div>
                    <img src="data:image/png;base64,{logo_tcc_b64}" class="header-logo">
                </div>
                
                <!-- BODY -->
                <div class="grid-container">
                    <div class="col-left">{html_left}</div>
                    <div class="col-right">{html_right}</div>
                </div>
                
                <!-- FOOTER V3 -->
                <div class="tcc-footer">
                    <div class="footer-left">
                         <img src="data:image/png;base64,{logo_tcc_white_b64}" class="footer-logo-img">
                    </div>
                    <div class="footer-center">
                        <div class="legend-box">
                            <span style="display:flex; align-items:center; gap:5px;"><span class="icon-badge icon-rl">RL</span> Luxo</span>
                            <span style="display:flex; align-items:center; gap:5px;"><span class="icon-badge icon-star" style="background:transparent; color:#f1c40f; box-shadow:none;">★</span> Unanimidade</span>
                            <span style="display:flex; align-items:center; gap:5px;"><span class="icon-badge icon-c">C</span> Bom Capitão</span>
                            <span style="display:flex; align-items:center; gap:5px;"><span class="icon-badge bg-conf-a" style="width:15px;height:15px;"></span> Nível de Confiança</span>
                        </div>
                        <div class="footer-exclusive-text">MATERIAL EXCLUSIVO &ndash; TREINANDO CAMPEÕES DE CARTOLA</div>
                    </div>
                    <div class="footer-right">
                        <img src="data:image/png;base64,{logo_tcc_white_b64}" class="footer-logo-img">
                    </div>
                </div>
            </div>

            <!-- SCRIPTS LOADED AT END OF BODY -->
            <script src="https://cdnjs.cloudflare.com/ajax/libs/html-to-image/1.11.11/html-to-image.min.js"></script>
            <script>
                // Make functions global
                window.downloadHighRes = function() {{
                    var node = document.getElementById('capture');
                    document.body.style.cursor = 'wait';
                    
                    
                    // FIXED DIMENSIONS: The container is 1200px.
                    // Instead of trust scrollWidth (which changes with zoom), we force it.
                    // We add a horizontal buffer (40px) to prevent right-edge cuts.
                    // FIXED DIMENSIONS: The container is 1200px.
                    // Instead of trust scrollWidth (which changes with zoom), we force it.
                    // We add a horizontal buffer (40px) to prevent right-edge cuts.
                    var fixedWidth = 1200;
                    var w = fixedWidth + 40; 
                    
                    // Add buffer to height to prevent footer cuts at different zoom levels
                    var h = Math.max(node.scrollHeight, node.offsetHeight) + 150;
                    
                    // GET USER SELECTION FROM HTML
                    var sel = document.getElementById('resSelect');
                    var targetScale = parseFloat(sel.value);
                    
                    // Cap scale to browser limits (approx 30k pixels height for modern browsers)
                    var MAX_PIXELS = 30000;
                    if (h * targetScale > MAX_PIXELS) {{
                        var safeScale = MAX_PIXELS / h;
                        if (safeScale < targetScale) {{
                            targetScale = safeScale;
                            alert("⚠️ ALERTA DE LIMITE:\\n\\nA lista é muito grande (" + h + "px de altura).\\nPara 600 DPI, ela teria " + (h*6) + "px, o que trava o navegador.\\n\\nA escala foi ajustada automaticamente para " + targetScale.toFixed(2) + "x (Máximo Seguro).");
                            sel.value = "2.0"; // Visual reset
                        }}
                    }}
                    
                    console.log("Starting capture at scale: " + targetScale);
                    
                    htmlToImage.toBlob(node, {{
                        backgroundColor: '#ffffff',
                        width: w,
                        height: h,
                        pixelRatio: targetScale,
                        style: {{
                            transform: 'none',
                            visibility: 'visible',
                            maxHeight: 'none',
                            maxWidth: 'none',
                            height: 'auto',
                            overflow: 'visible',
                            // FORCE WIDTH and CENTER to avoid cut
                            width: fixedWidth + 'px',
                            marginLeft: '20px', // Center in the w+40 canvas
                            marginRight: '20px'
                        }}
                    }})
                    .then(function(blob) {{
                        if (!blob) {{
                            throw new Error("Blob vazio gerado.");
                        }}
                        var url = URL.createObjectURL(blob);
                        var link = document.createElement('a');
                        link.download = 'Dicas_Rodada_TCC_v' + targetScale.toFixed(1) + 'x.png';
                        link.href = url;
                        link.click();
                        
                        setTimeout(function() {{ URL.revokeObjectURL(url); }}, 100);
                        document.body.style.cursor = 'default';
                        
                        // Show success feedback
                        var btn = document.querySelector('button[onclick="window.downloadHighRes()"]');
                        var originalText = btn.innerText;
                        btn.innerText = "✅ SUCESSO!";
                        setTimeout(() => btn.innerText = originalText, 2000);
                    }})
                    .catch(function(error) {{
                        console.error('Capture failed:', error);
                        alert('❌ ERRO ao gerar imagem ' + targetScale + 'x.\\n\\nO navegador não aguentou essa resolução. Tente selecionar uma qualidade MENOR no menu (ex: 1.5x ou 2.0x).');
                        document.body.style.cursor = 'default';
                    }});
                }};
            </script>
        </body>
        </html>
        """
        
        st.session_state['preview_html'] = full_html

    # Display if exists
    if st.session_state['preview_html']:
        st.components.v1.html(st.session_state['preview_html'], height=1400, scrolling=True)
        
        st.divider()
        st.subheader("📥 Exportação")
        
        c_dl_1, c_dl_2 = st.columns(2)
        
        # Opção 1: Download HTML (Para Debug ou Print Manual)
        with c_dl_1:
            b64 = base64.b64encode(st.session_state['preview_html'].encode()).decode()
            href = f'<a href="data:text/html;base64,{b64}" download="Dicas_Rodada_{rodada_atual}.html" style="text-decoration:none;"><button style="background-color:transparent; border:1px solid #ccc; padding:8px 16px; border-radius:4px; cursor:pointer;">📄 Baixar HTML (Debug)</button></a>'
            st.markdown(href, unsafe_allow_html=True) 
        
        # Opção 2: Server-Side Screenshot (Playwright/Chromium)
        with c_dl_2:
            st.write("### 📸 Alta Qualidade (Recomendado)")
            st.caption("Usa Playwright (Chromium) para gerar uma imagem perfeita, independente do zoom do seu navegador.")
            
            # Selector de Qualidade
            qualidade = st.select_slider("Qualidade:", options=[2.0, 3.0, 4.0], value=3.0, format_func=lambda x: f"{x}x ({int(1200*x)}px largura)")
            
            if st.button("🚀 Gerar PNG (Alta Definição)", type="primary"):
                with st.spinner("⏳ Renderizando via Playwright... (pode levar ~10s)"):
                    try:
                        png_bytes = screenshot_utils.capture_html_to_image(
                            st.session_state['preview_html'], 
                            scale=qualidade
                        )
                        
                        if png_bytes:
                            size_mb = len(png_bytes) / (1024 * 1024)
                            st.success(f"✅ Imagem gerada! ({size_mb:.1f} MB)")
                            st.download_button(
                                label="⬇️ CLIQUE PARA BAIXAR PNG",
                                data=png_bytes,
                                file_name=f"Dicas_TCC_Rodada_{rodada_atual}_HQ.png",
                                mime="image/png"
                            )
                        else:
                            st.error("Falha ao gerar imagem. Verifique os logs do terminal.")
                    except Exception as e:
                        st.error(f"Erro: {e}")
                        
    else:
        st.warning("Clique em 'Gerar/Atualizar Visualização' para ver o resultado.")
