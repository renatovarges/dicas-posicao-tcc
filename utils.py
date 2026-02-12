import pandas as pd
import unicodedata
import os
import base64
import requests
import json
import streamlit as st

# Mapeamento de IDs de Clubes (2024/2025 - Série A e B)
CLUB_MAP = {
    '262': 'Flamengo',
    '263': 'Botafogo',
    '264': 'Corinthians',
    '265': 'Bahia',
    '266': 'Fluminense',
    '267': 'Vasco',
    '275': 'Palmeiras',
    '276': 'São Paulo',
    '282': 'Atlético-MG',
    '283': 'Cruzeiro',
    '284': 'Grêmio',
    '285': 'Internacional',
    '287': 'Vitória',
    '315': 'Chapecoense', # Antes era Vitória? Agora parece ser CHA
    '364': 'Remo',
    '317': 'Joinville', # JEC
    '327': 'América-RN', # AME? Ou Paysandu? Output says 327: AME. 291: PAY
    '291': 'Paysandu',
    '351': 'Fortaleza',
    '356': 'Goiás',
    '373': 'Atlético-GO',
    '292': 'Sport',
    '354': 'Ceará',
    '280': 'Bragantino',
    '290': 'Goiás', # Duplicate in list? 290 is GOI, 356 is FOR? No 356 is FOR? 
    # Let's trust the fetch_clubs output more carefully.
    # 356: FOR (Fortaleza?) No, 351 is AME? 
    # Let's stick to the ones we confirmed: Remo, Vitoria.
    # 287: VIT -> Vitória
    # 364: REM -> Remo
    # 315: CHA -> Chapecoense
    '293': 'Athletico-PR',
    '294': 'Coritiba',
    '303': 'Ponte Preta',
    '2305': 'Mirassol',
    '2305': 'Mirassol',
    '306': 'Santos', # Legacy/Alt
    '277': 'Santos', # Active Market ID
    '316': 'Figueirense',
    '316': 'Figueirense',
    '340': 'CRB',
    '319': 'Londrina',
    '321': 'Operário-PR', # OPE
    '393': 'América-MG',
    '296': 'Botafogo-SP',
    '373': 'Atlético-GO',
    '356': 'Fortaleza', # Check overlap/conflict from before? No, 351 was AME? Fix this.
    '314': 'Avaí',
    '344': 'Guarani',
    '303': 'Ponte Preta',
    '286': 'Juventude',
    '291': 'Paysandu',
    '354': 'Ceará',
    '292': 'Sport',
    '280': 'Bragantino',
    '1371': 'Cuiabá',
    '204': 'Criciúma',
    '315': 'Chapecoense',
    '364': 'Remo',
    '287': 'Vitória',
    '317': 'Joinville',
    '327': 'América-RN',
}

@st.cache_data(ttl=300) # Cache for 5 minutes
def fetch_mercado_data():
    """
    Busca dados do mercado atual do Cartola API.
    Retorna uma lista de dicionários com atletas.
    """
    url = "https://api.cartola.globo.com/atletas/mercado"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data.get('atletas', [])
        else:
            print(f"Erro API Mercado: {response.status_code}")
            return []
    except Exception as e:
        print(f"Erro Request Mercado: {e}")
        return []

def validate_gato_mestre_token(token):
    """
    Valida se o token do Gato Mestre está ativo e retornando dados.
    Tenta múltiplos formatos de header.
    """
    if not token:
        return False, "Token vazio"
        
    # Remove prefixo Bearer se existir e limpa
    clean_token = token.strip().strip('"').strip("'")
    if clean_token.lower().startswith("bearer "):
        clean_token = clean_token[7:].strip()
    
    url = "https://api.cartola.globo.com/auth/gatomestre/atletas"
    
    # Tentativa 1: X-GLB-Token
    headers_1 = {
        "User-Agent": "Mozilla/5.0",
        "X-GLB-Token": clean_token
    }
    
    # Tentativa 2: Bearer
    headers_2 = {
        "User-Agent": "Mozilla/5.0",
        "Authorization": f"Bearer {clean_token}"
    }

    try:
        # Try Method 1
        response = requests.get(url, headers=headers_1)
        if response.status_code == 200:
            return True, "Token Válido (X-GLB-Token)"
        
        # If 401/403, Try Method 2
        if response.status_code in [401, 403]:
            response2 = requests.get(url, headers=headers_2)
            if response2.status_code == 200:
                return True, "Token Válido (Bearer)"
            else:
                return False, f"Token Inválido (401) - Verifique se copiou corretamente."
        else:
            return False, f"Erro API: {response.status_code}"
            
    except Exception as e:
        return False, f"Erro de Conexão: {e}"

@st.cache_data(ttl=300, show_spinner=False)
def fetch_gato_mestre_data(token):
    """
    Busca dados do Gato Mestre (Mínimo para Valorizar) usando token.
    Tenta múltiplos endpoints e suporta formato de Dicionário (ID -> Dados).
    """
    if not token:
        return {}
        
    clean_token = token.strip().strip('"').strip("'")
    if clean_token.lower().startswith("bearer "):
        clean_token = clean_token[7:].strip()

    # Endpoints to try
    endpoints = [
        "https://api.cartola.globo.com/auth/gatomestre/atletas",
        "https://api.cartola.globo.com/auth/mercado/atleta/gatomestre"
    ]
    
    # Headers mimicking the user's browser
    headers_base = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "x-glb-app-name": "cartola-web"
    }
    
    for url in endpoints:
        # Auth: Bearer is standard for this endpoint based on user logs
        headers = headers_base.copy()
        headers["Authorization"] = f"Bearer {clean_token}"
        
        try:
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                mpv_map = {}
                
                # CASE 1: Response is a Dict of IDs -> Info (User's log format)
                # {"100084": {"minimo_para_valorizar": 3.18, ...}, ...}
                if isinstance(data, dict):
                    # Check if it's the specific format (keys are IDs, values have 'minimo_para_valorizar')
                    sample_key = next(iter(data), None)
                    if sample_key and isinstance(data[sample_key], dict) and 'minimo_para_valorizar' in data[sample_key]:
                         for aid_str, info in data.items():
                            try:
                                aid = int(aid_str)
                                mpv_map[aid] = float(info.get('minimo_para_valorizar', 0.0))
                            except:
                                pass
                         if mpv_map:
                             st.toast(f"GM: {len(mpv_map)} mínimos carregados (Dict)!", icon="💰")
                             return mpv_map

                    # CASE 2: Response has 'atletas' key (Legacy/Alternative)
                    elif 'atletas' in data:
                        atletas_list = data['atletas']
                        for a in atletas_list:
                             if 'atleta_id' in a and 'minimo_para_valorizar' in a:
                                 mpv_map[int(a['atleta_id'])] = float(a['minimo_para_valorizar'])
                        if mpv_map:
                             st.toast(f"GM: {len(mpv_map)} mínimos carregados (List)!", icon="💰")
                             return mpv_map

                # CASE 3: List of objects
                elif isinstance(data, list):
                     for a in data:
                         if 'atleta_id' in a and 'minimo_para_valorizar' in a:
                             mpv_map[int(a['atleta_id'])] = float(a['minimo_para_valorizar'])
                     if mpv_map:
                         st.toast(f"GM: {len(mpv_map)} mínimos carregados (Direct List)!", icon="💰")
                         return mpv_map
                         
        except Exception as e:
            print(f"Erro GM ({url}): {e}")
            continue

    st.toast("GM: Dados não encontrados ou estrutura desconhecida.", icon="⚠️")
    return {}

def get_team_logo_path(team_name):
    """
    Retorna o caminho para o logo do time em assets/logos/.
    Tenta mapear o nome para o arquivo correspondente.
    """
    if not team_name:
        return ""
        
    # Normalização simples para encontrar arquivo
    # Ex: "Atlético-MG" -> "atletico-mg.png" ou "atleticomg.png"
    # User tem assets/logos/
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logos_dir = os.path.join(base_dir, "assets", "teams")
    
    if not os.path.exists(logos_dir):
        return ""
        
    # Tenta encontrar arquivo com match aproximado
    # Remove acentos e lower, e remove hifens/underscores para garantir match
    clean_name = normalize_name(team_name).lower().replace(" ", "").replace("-", "").replace("_", "")
    
    # Lista arquivos
    try:
        files = os.listdir(logos_dir)
        for f in files:
            f_clean = f.lower().replace("_", "").replace("-", "").replace(" ", "").split(".")[0]
            if f_clean == clean_name or clean_name in f_clean:
                 return os.path.join(logos_dir, f)
                 
        # Fallback: tentar direto nome ex: Flamengo.png
        direct_path = os.path.join(logos_dir, f"{team_name}.png")
        if os.path.exists(direct_path):
            return direct_path
            
    except Exception:
        pass
        
    return ""

def get_file_base64(file_path):
    """
    Lê um arquivo e retorna sua representação base64 para embedding em HTML/CSS.
    """
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

def normalize_name(name):
    """
    Normaliza nomes removendo acentos e convertendo para maiúsculas.
    """
    if pd.isna(name):
        return ""
    nfkd_form = unicodedata.normalize('NFKD', str(name))
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper().strip()

def load_data(file_path):
    """
    Carrega os dados da planilha Excel do usuário (Aba 'Por jogo').
    Realiza a limpeza inicial e garante os tipos de dados corretos.
    """
    try:
        df = pd.read_excel(file_path, sheet_name='Por jogo')
        
        # Parse Data
        if 'Data' in df.columns:
            # Tenta inferir formato, assumindo dia primeiro (DD/MM/AAAA)
            df['Data_dt'] = pd.to_datetime(df['Data'], dayfirst=True, errors='coerce')
        else:
            raise ValueError("Coluna 'Data' não encontrada.")
            
        if 'Nome2' in df.columns:
            target_col = 'Nome2'
        elif 'Jogador' in df.columns:
            target_col = 'Jogador'
        else:
            raise ValueError("Coluna de nome do jogador (Nome2 ou Jogador) não encontrada.")

        df['Jogador_Norm'] = df[target_col].apply(normalize_name)
        df['Jogador_Original'] = df[target_col]
        
        if 'Time' in df.columns:
            # As vezes o time vem como ID ou Nome. Inspect mostrou 'Time'.
            df['Time_Norm'] = df['Time'].apply(normalize_name)
        
        if 'PosReal' in df.columns:
             df['Posicao_Norm'] = df['PosReal'].apply(normalize_name)

        # Converter colunas numéricas
        numeric_cols = ['Pts', 'Básica', 'G', 'A', 'DE', 'SG', 'FS', 'FF', 'FD', 'DS', 'CA', 'CV', 'GS', 'PP', 'PC', 'FC', 'I', 'PI']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
        return df
    except Exception as e:
        raise ValueError(f"Erro ao carregar arquivo de dados: {e}")


def load_classificacao(file_path):
    """
    Carrega o arquivo de classificação de Meias/Volantes (CSV ou Excel).
    """
    try:
        if file_path.endswith('.xlsx'):
            # Ler Excel, buscando cabeçalho correto
            # O arquivo parece ter cabeçalho na linha 0 ou 1
            df = pd.read_excel(file_path, header=None)
            
            # Encontrar linha de cabeçalho
            header_idx = -1
            for i, row in df.iterrows():
                row_vals = [str(x).upper() for x in row.values]
                if 'JOGADOR' in row_vals and ('CLASSIFICACAO' in row_vals or 'CLASSIFICAÇÃO' in row_vals):
                    header_idx = i
                    break
            
            if header_idx != -1:
                df = pd.read_excel(file_path, header=header_idx)
            else:
                # Tenta fallback para header=1 (comum em planilhas formatadas)
                try:
                    df_h1 = pd.read_excel(file_path, header=1)
                    cols_h1 = [str(c).upper() for c in df_h1.columns]
                    if '1º VOLANTE' in cols_h1 or 'MEIA' in cols_h1:
                        df = df_h1
                    else:
                         df = pd.read_excel(file_path)
                except:
                     df = pd.read_excel(file_path)

        else:
            df = pd.read_csv(file_path, sep=None, engine='python')
            
        # Normalizar Colunas
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # LOGICA 1: Coluna 'CLASSIFICACAO' explícita
        col_jogador = next((c for c in df.columns if 'JOGADOR' in c), None)
        col_class = next((c for c in df.columns if 'CLASSIFICA' in c), None)
        
        mapping = {}
        
        if col_jogador:
            # Iterar rows para preencher mapping
            for _, row in df.iterrows():
                nome = normalize_name(str(row[col_jogador]))
                if not nome: continue
                
                # Check 1: Coluna Classificacao
                if col_class and pd.notna(row[col_class]):
                    mapping[nome] = normalize_name(str(row[col_class]))
                    continue
                
                # Check 2: Formato Wide (1º VOLANTE, 2º VOLANTE, MEIA)
                # Verifica marcadores nas colunas específicas
                is_volante = False
                if '1º VOLANTE' in df.columns and pd.notna(row['1º VOLANTE']): is_volante = True
                if '2º VOLANTE' in df.columns and pd.notna(row['2º VOLANTE']): is_volante = True
                
                if is_volante:
                    mapping[nome] = 'VOLANTE'
                    continue
                    
                if 'MEIA' in df.columns and pd.notna(row['MEIA']):
                    mapping[nome] = 'MEIA'
                    continue
        
        return mapping
            
    except Exception as e:
        print(f"Aviso: Classificação externa não carregada: {e}")
        return {}

def parse_rodadas(file_path):
    """
    Lê o arquivo RODADAS_BRASILEIRAO_2026.txt e estrutura os dados.
    """
    rodadas_data = {}
    current_rodada = None
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            line = line.strip()
            if not line: continue
            
            if "RODADA" in line.upper():
                parts = line.split()
                for p in parts:
                    if p.isdigit():
                        current_rodada = int(p)
                        break
                continue
            
            if " x " in line:
                times = line.split(" x ")
                if len(times) == 2:
                    time_casa = normalize_name(times[0])
                    time_fora = normalize_name(times[1])
                    
                    if current_rodada is not None:
                        if time_casa not in rodadas_data: rodadas_data[time_casa] = []
                        if time_fora not in rodadas_data: rodadas_data[time_fora] = []
                        
                        rodadas_data[time_casa].append({'rodada': current_rodada, 'oponente': time_fora, 'mando': 'CASA'})
                        rodadas_data[time_fora].append({'rodada': current_rodada, 'oponente': time_casa, 'mando': 'FORA'})
                        
        return rodadas_data
    except Exception as e:
        print(f"Erro ao ler rodadas: {e}")
        return {}

def map_pos_id_to_name(pos_id):
    """
    Mapeia ID numérico do Cartola para Nome.
    """
    try:
        pid = int(float(pos_id))
        mapping = {
            1: 'GOLEIRO',
            2: 'LATERAL', # Laterais podem vir como 2 ou subcats?
            3: 'ZAGUEIRO',
            4: 'MEIA',
            5: 'ATACANTE',
            6: 'TECNICO'
        }
        return mapping.get(pid, 'OUTROS')
    except:
        return 'OUTROS'

def get_next_match_info(team_name, rodadas_data, target_round):
    team_clean = normalize_name(team_name)
    if team_clean in rodadas_data:
        for match in rodadas_data[team_clean]:
            if match['rodada'] == target_round:
                return match
    return None

def process_ranking(df, n_jogos, filter_type, target_round, rodadas_data, top_n_players, posicao_filter=None, pos_map=None):
    """
    Processa o ranking baseado nos filtros.
    """
    player_data = {}
    times = df['Time_Norm'].unique()
    
    # Mapeamento do filtro de posição para nomes normalizados possíveis
    target_positions = []
    if posicao_filter:
        if isinstance(posicao_filter, str):
            target_positions = [normalize_name(posicao_filter)]
        else:
             target_positions = [normalize_name(p) for p in posicao_filter]

    for time in times:
        df_time = df[df['Time_Norm'] == time].copy()
        
        # REGRA DE OURO: Ordenação por DATA decrescente
        df_time = df_time.sort_values(by='Data_dt', ascending=False)
        
        # Identificar Jogos do Time que entram
        eligible_dates = []
        
        if filter_type == "Todas":
            # Pega datas únicas dos últimos N jogos
            unique_dates = df_time['Data_dt'].unique()
            # unique já retorna sorted se veio do df sorted? 
            # NÃO, unique devolve appearance order. Como df tá sorted clean, deve funfar.
            # Melhor garantir:
            unique_dates_sorted = sorted(unique_dates, reverse=True)
            eligible_dates = unique_dates_sorted[:n_jogos]
            
        elif filter_type == "Por Mando":
            next_match = get_next_match_info(time, rodadas_data, target_round)
            if next_match:
                target_mando = next_match['mando']
                # Filtrar coluna 'Mand'
                # 'C' ou 'Casa' ou 'M'
                # Vamos normalizar a coluna Mand para garantir
                df_time['Mand_Norm'] = df_time['Mand'].apply(lambda x: str(x).upper().strip())
                
                if target_mando == 'CASA':
                    df_mando = df_time[df_time['Mand_Norm'].isin(['C', 'CASA', 'M', 'MANDANTE'])]
                else:
                    df_mando = df_time[df_time['Mand_Norm'].isin(['F', 'FORA', 'V', 'VISITANTE'])]
                
                unique_dates_sorted = sorted(df_mando['Data_dt'].unique(), reverse=True)
                eligible_dates = unique_dates_sorted[:n_jogos]
            else:
                eligible_dates = []

        # Pegar linhas desses jogos
        df_selected = df_time[df_time['Data_dt'].isin(eligible_dates)]
        
        for _, row in df_selected.iterrows():
            nome_norm = row['Jogador_Norm']
            
            # Detecção de Posição
            # 1. Tenta pegar do mapa externo (Meia/Volante)
            pos_real = None
            if pos_map and nome_norm in pos_map:
                pos_real = pos_map[nome_norm]
            
            # 2. Se não achou ou não é Meia/Volante, usa o ID da planilha convertido
            if not pos_real:
                # Usa 'PosReal' ou 'Posicao' ou 'PosID'
                target_pos_col = 'PosReal' if 'PosReal' in row else 'PosID'
                val_pos = row.get(target_pos_col, 0)
                pos_real = map_pos_id_to_name(val_pos)
            
            # Filtro Posição
            if target_positions:
                if normalize_name(pos_real) not in target_positions:
                    continue
            
            if nome_norm not in player_data:
                player_data[nome_norm] = {
                    'Nome': row.get('Jogador_Original', row.get('Nome2', 'Unknown')),
                    'Time': row['Time'],
                    'Posicao': pos_real,
                    'Jogos': [],
                    'Total_Pontos': 0.0,
                    'Total_Media_Basica': 0.0,
                    'Scouts': {}
                }
            
            p = player_data[nome_norm]
            
            # Info do Jogo
            mando_str = str(row['Mand']).upper()
            is_casa = mando_str in ['C', 'CASA', 'M']
            
            game_scouts = {}
            for col in ['G', 'A', 'SG', 'DE', 'FS', 'FF', 'FD', 'DS', 'CA', 'CV', 'GS', 'PP', 'PC', 'FC', 'I', 'PI']:
                val = row.get(col, 0)
                if val > 0:
                    game_scouts[col] = int(val)
                    p['Scouts'][col] = p['Scouts'].get(col, 0) + int(val)
            
            p['Jogos'].append({
                'Data': row['Data_dt'],
                'Adversario': row.get('Adversário', '??'),
                'Casa': is_casa,
                'Pontos': row.get('Pts', 0),
                'Basica': row.get('Básica', 0),
                'Scouts': game_scouts
            })
            
            # Totais temporários (serão recalculados após o corte)
            p['Total_Pontos'] += row.get('Pts', 0)
            p['Total_Media_Basica'] += row.get('Básica', 0)
            
    # Finalizar Lista e Aplicar "Safety Net"
    ranking = []
    for nome, data in player_data.items():
        # 1. Garantir ordem cronológica
        data['Jogos'].sort(key=lambda x: x['Data'], reverse=True)
        
        # 2. Cortar excedentes (Safety Net)
        if len(data['Jogos']) > n_jogos:
            data['Jogos'] = data['Jogos'][:n_jogos]
            
            # 3. Recalcular Totais Baseado no Corte
            data['Total_Pontos'] = sum(j['Pontos'] for j in data['Jogos'])
            data['Total_Media_Basica'] = sum(j['Basica'] for j in data['Jogos'])
            
            # 4. Recalcular Scouts Totais
            data['Scouts'] = {}
            for j in data['Jogos']:
                for s_key, s_val in j['Scouts'].items():
                    data['Scouts'][s_key] = data['Scouts'].get(s_key, 0) + s_val

        # Calcular Médias Finais
        # Divisão sempre pelo n_jogos TEÓRICO ou REAL?
        # Regra user: "Média" = Total / N
        # Se o jogador jogou MENOS que N, divide por N ou pelo real?
        # Geralmente em ranking "Média" é pelo N jogos disputados ou N do filtro?
        # Código anterior usava `n_jogos` (filtro). Manterei para consistência.
        # Mas se ele jogou 2 e filtro é 3?
        # User disse "O número pequeno 'Média' será... Total / N".
        # Vamos manter divisão por `n_jogos` se > 0 else 1.
        
        divisor = n_jogos if n_jogos > 0 else 1
        data['Media_Pontos'] = data['Total_Pontos'] / divisor
        data['Media_Basica'] = data['Total_Media_Basica'] / divisor
        
        ranking.append(data)
        
    # Validar ordenação final do ranking
    ranking.sort(key=lambda x: x['Total_Pontos'], reverse=True)
    
    return ranking[:top_n_players]
