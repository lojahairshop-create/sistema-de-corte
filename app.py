import streamlit as st
import math
import pandas as pd
from datetime import datetime
import io
import json
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches


# Tentativa de importar ezdxf (para processamento de arquivos DXF)
try:
    import ezdxf
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================
st.set_page_config(
    page_title="Orçamento Industrial - Corte, Dobra, Usinagem, Solda & Pintura",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS CUSTOMIZADO
# ============================================================
st.markdown("""
<style>
    /* --- Tipografia Moderna --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* --- Fundo Geral e Minimalismo --- */
    .stApp {
        background-color: #f8fafc; /* Fundo leve e limpo cinza-azulado */
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* --- Main Header / Banner --- */
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    .main-header::after {
        content: '';
        position: absolute;
        top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 60%);
        transform: rotate(30deg);
        pointer-events: none;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin: 0.5rem 0 0;
        opacity: 0.8;
        font-size: 1rem;
        font-weight: 400;
    }
    
    /* --- Sidebar Premium --- */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 20px rgba(0,0,0,0.03);
    }
    
    /* --- Inputs e SelectBoxes Arredondados e Elegantes --- */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    div[data-baseweb="select"] {
        border-radius: 8px !important;
        border: 1px solid #cbd5e1 !important;
        background-color: white;
        transition: border 0.3s, box-shadow 0.3s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02) !important;
    }
    .stTextInput>div>div>input:focus,
    .stNumberInput>div>div>input:focus,
    div[data-baseweb="select"]:focus-within {
        border-color: #2563eb !important;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
    }

    /* --- Botões Atraentes --- */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 2rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        width: 100%;
    }
    div.stButton > button:first-child:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.4);
        background: linear-gradient(135deg, #1d4ed8 0%, #1e3a8a 100%);
    }

    /* --- Uploader de Arquivo Estilizado --- */
    section[data-testid="stFileUploader"] {
        border-radius: 12px;
        border: 2px dashed #94a3b8;
        background-color: #f8fafc;
        padding: 1.5rem;
        transition: all 0.2s;
    }
    section[data-testid="stFileUploader"]:hover {
        border-color: #2563eb;
        background-color: #eff6ff;
    }
    
    /* --- Cards de Resultado com Sombras Suaves --- */
    .result-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        color: #1e293b;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .result-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .result-card .label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    .result-card .value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #0f172a;
    }
    
    /* Variações de Cores para Cards */
    .result-card-green {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border-color: #bbf7d0;
    }
    .result-card-green .value { color: #166534; }
    
    .result-card-orange {
        background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
        border-color: #fed7aa;
    }
    .result-card-orange .value { color: #9a3412; }
    
    .result-card-blue {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-color: #bfdbfe;
    }
    .result-card-blue .value { color: #1e40af; }
    
    /* --- Seções e Divisores --- */
    .section-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 2rem 0 1.5rem;
    }
    .section-title::before {
        content: '';
        display: block;
        width: 5px;
        height: 24px;
        background-color: #2563eb;
        border-radius: 4px;
    }
    .custom-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #cbd5e1, transparent);
        margin: 2rem 0;
    }
    
    /* --- Info Boxes (Alertas Suaves) --- */
    .info-box {
        background: #eff6ff;
        border-left: 4px solid #2563eb;
        padding: 1rem 1.2rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        font-size: 0.95rem;
        color: #1e3a8a;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# PERSISTÊNCIA DE CONFIGURAÇÕES
# ============================================================
CONFIG_PATH = "config_orcamento.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(params):
    config = load_config()
    config.update(params)
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except Exception:
        pass

def save_setting(key_name):
    """Callback para salvar configurações no JSON imediatamente quando alteradas."""
    if key_name in st.session_state:
        save_config({key_name: st.session_state[key_name]})

cfg = load_config()

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def processar_dxf(arquivo_dxf, velocidade_mm_min, tempo_furo_seg):
    """
    Processa um arquivo DXF e calcula perímetro total, quantidade de furos
    e tempo de corte estimado.
    """
    if not EZDXF_DISPONIVEL:
        st.error("Biblioteca ezdxf não está instalada. Execute: pip install ezdxf")
    import tempfile
    import os
    
    try:
        # Salva num arquivo temporário para usar o readfile nativo do ezdxf, que gerencia encodings perfeitamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(arquivo_dxf.getvalue())
            tmp_path = tmp.name

        try:
            doc = ezdxf.readfile(tmp_path)
        except ezdxf.DXFStructureError:
            # Em caso de pequenos erros estruturais ou binários no DXF, tentamos o módulo de recuperação
            try:
                from ezdxf import recover
                doc, auditor = recover.readfile(tmp_path)
            except Exception as e:
                os.remove(tmp_path)
                raise e
        
        # Limpa o arquivo temporário
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

        msp = doc.modelspace()

        perimetro_total = 0.0
        qtd_furos = 0

        for entity in msp:
            tipo = entity.dxftype()
            comp_atual = 0.0

            if tipo == 'LINE':
                start = entity.dxf.start
                end = entity.dxf.end
                comp_atual = math.dist((start.x, start.y), (end.x, end.y))

            elif tipo == 'CIRCLE':
                comp_atual = 2 * math.pi * entity.dxf.radius

            elif tipo == 'ARC':
                raio = entity.dxf.radius
                ang_inicio = math.radians(entity.dxf.start_angle)
                ang_fim = math.radians(entity.dxf.end_angle)
                if ang_fim < ang_inicio:
                    ang_fim += 2 * math.pi
                comp_atual = raio * (ang_fim - ang_inicio)

            elif tipo == 'LWPOLYLINE':
                pontos = list(entity.get_points('xy'))
                for i in range(len(pontos) - 1):
                    comp_atual += math.dist(pontos[i], pontos[i + 1])
                if entity.closed:
                    comp_atual += math.dist(pontos[-1], pontos[0])

            elif tipo == 'POLYLINE':
                pontos = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
                for i in range(len(pontos) - 1):
                    comp_atual += math.dist(pontos[i], pontos[i + 1])
                if entity.is_closed:
                    comp_atual += math.dist(pontos[-1], pontos[0])

            elif tipo == 'ELLIPSE':
                # Aproximação de comprimento de elipse
                try:
                    a = entity.dxf.major_axis.magnitude
                    ratio = entity.dxf.ratio
                    b = a * ratio
                    # Aproximação de Ramanujan
                    comp_atual = math.pi * (3*(a+b) - math.sqrt((3*a+b)*(a+3*b)))
                except:
                    pass

            elif tipo == 'SPLINE':
                try:
                    pontos = list(entity.flattening(0.5))
                    for i in range(len(pontos) - 1):
                        comp_atual += math.dist(
                            (pontos[i].x, pontos[i].y),
                            (pontos[i+1].x, pontos[i+1].y)
                        )
                except:
                    pass

            if comp_atual > 0:
                perimetro_total += comp_atual
                qtd_furos += 1

        # Cálculos de Bounding Box (Dimensões X e Y)
        largura_x = 0.0
        altura_y = 0.0
        try:
            from ezdxf import bbox
            ext = bbox.extents(msp)
            if ext.has_data:
                largura_x = ext.extmax.x - ext.extmin.x
                altura_y = ext.extmax.y - ext.extmin.y
        except Exception:
            pass

        # Cálculos de Tempo
        tempo_corte_min = perimetro_total / velocidade_mm_min if velocidade_mm_min > 0 else 0
        tempo_furo_min = (qtd_furos * tempo_furo_seg) / 60.0
        tempo_total_min = tempo_corte_min + tempo_furo_min

        return {
            "perimetro": perimetro_total,
            "furos": qtd_furos,
            "tempo_corte_min": tempo_corte_min,
            "tempo_furo_min": tempo_furo_min,
            "tempo_total_min": tempo_total_min,
            "largura_x": largura_x,
            "altura_y": altura_y
        }

    except Exception as e:
        st.error(f"Erro ao processar DXF: {e}")
        return None

def calcular_nesting_simples(w_peca, h_peca, w_chapa, h_chapa, margem, espaco, permitir_rotacao, qtd_desejada=0):
    """Calcula arranjo simples de Bounding Boxes em uma chapa, retornando propriedades, rects e retalho necessário."""
    if w_peca <= 0 or h_peca <= 0: return None, 0, 0, 0
    
    W_util = w_chapa - 2*margem
    H_util = h_chapa - 2*margem
    
    if W_util <= 0 or H_util <= 0: return None, 0, 0, 0

    layouts = []

    def pack_grid(wp, hp, start_x, start_y, max_w, max_h):
        rects = []
        cols = int((max_w + espaco) / (wp + espaco))
        rows = int((max_h + espaco) / (hp + espaco))
        if cols > 0 and rows > 0:
            for r in range(rows):
                for c in range(cols):
                    x = start_x + c * (wp + espaco)
                    y = start_y + r * (hp + espaco)
                    rects.append({'x': x, 'y': y, 'w': wp, 'h': hp})
        return rects

    # 1. Orientação 0 Graus
    rects_0 = pack_grid(w_peca, h_peca, margem, margem, W_util, H_util)
    layouts.append({'desc': '0° (Horizontal)', 'qtd': len(rects_0), 'rects': rects_0})

    # 2. Orientação 90 Graus
    if permitir_rotacao:
        rects_90 = pack_grid(h_peca, w_peca, margem, margem, W_util, H_util)
        layouts.append({'desc': '90° (Vertical)', 'qtd': len(rects_90), 'rects': rects_90})

        # 3. Layout Misto (0° embaixo, 90° em cima)
        max_rows_0 = int((H_util + espaco) / (h_peca + espaco))
        for r_0 in range(1, max_rows_0):
            altura_0 = r_0 * (h_peca + espaco) - espaco
            altura_restante = H_util - altura_0 - espaco
            if altura_restante >= w_peca: # lembre-se: a 90° a altura é w_peca
                r_mixed = pack_grid(w_peca, h_peca, margem, margem, W_util, altura_0)
                r_mixed += pack_grid(h_peca, w_peca, margem, margem + altura_0 + espaco, W_util, altura_restante)
                if len(r_mixed) > 0:
                    layouts.append({'desc': f'Misto ({r_0} filas horizontais)', 'qtd': len(r_mixed), 'rects': r_mixed})
                    
        # 4. Layout Misto (90° embaixo, 0° em cima)
        max_rows_90 = int((H_util + espaco) / (w_peca + espaco))
        for r_90 in range(1, max_rows_90):
            altura_90 = r_90 * (w_peca + espaco) - espaco
            altura_restante = H_util - altura_90 - espaco
            if altura_restante >= h_peca:
                r_mixed = pack_grid(h_peca, w_peca, margem, margem, W_util, altura_90)
                r_mixed += pack_grid(w_peca, h_peca, margem, margem + altura_90 + espaco, W_util, altura_restante)
                if len(r_mixed) > 0:
                    layouts.append({'desc': f'Misto ({r_90} filas verticais)', 'qtd': len(r_mixed), 'rects': r_mixed})

    # Processar Layouts: Aplicar limite, calcular retalho
    valid_layouts = []
    for l in layouts:
        if qtd_desejada > 0 and l['qtd'] >= qtd_desejada:
            l['rects'] = l['rects'][:qtd_desejada]
            l['qtd'] = qtd_desejada
            
        if l['qtd'] > 0:
            max_x = max([r['x'] + r['w'] for r in l['rects']]) + margem
            max_y = max([r['y'] + r['h'] for r in l['rects']]) + margem
            l['retalho_w'] = max_x
            l['retalho_h'] = max_y
            l['retalho_area'] = max_x * max_y
            valid_layouts.append(l)

    if not valid_layouts: return None, 0, 0, 0

    if qtd_desejada > 0:
        alvos = [l for l in valid_layouts if l['qtd'] == qtd_desejada]
        if alvos:
            best_layout = min(alvos, key=lambda l: l['retalho_area'])
        else:
            best_layout = max(valid_layouts, key=lambda l: l['qtd'])
    else:
        best_layout = max(valid_layouts, key=lambda l: l['qtd'])
    
    area_usada = best_layout['qtd'] * (w_peca * h_peca)
    ret_w = best_layout['retalho_w']
    ret_h = best_layout['retalho_h']
    
    if qtd_desejada > 0 and best_layout['qtd'] == qtd_desejada:
        aproveitamento = (area_usada / best_layout['retalho_area']) * 100 if best_layout['retalho_area'] > 0 else 0
    else:
        area_total = w_chapa * h_chapa
        aproveitamento = (area_usada / area_total) * 100 if area_total > 0 else 0
        
    return best_layout, aproveitamento, ret_w, ret_h



def card_resultado(label, valor, classe_extra=""):
    """Renderiza um card de resultado estilizado."""
    st.markdown(f"""
    <div class="result-card {classe_extra}">
        <div class="label">{label}</div>
        <div class="value">{valor}</div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# SESSION STATE (MEMÓRIA)
# ============================================================
if 'lista_materiais' not in st.session_state:
    st.session_state.lista_materiais = []
if 'lista_servicos' not in st.session_state:
    st.session_state.lista_servicos = []
if 'dxf_resultado' not in st.session_state:
    st.session_state.dxf_resultado = None


# ============================================================
# HEADER
# ============================================================
st.markdown("""
<div class="main-header">
    <h1>🏭 Orçamento Industrial</h1>
    <p>Corte • Dobra • Usinagem • Solda • Pintura</p>
</div>
""", unsafe_allow_html=True)


# ============================================================
# BARRA LATERAL — CONFIGURAÇÕES GERAIS
# ============================================================
with st.sidebar:
    st.markdown("## ⚙️ Configurações")

    # --- Tarifas Hora-Máquina ---
    with st.expander("🛠️ Tarifas Hora-Máquina (R$/h)", expanded=True):
        tarifa_corte_carbono = st.number_input(
            "Corte Aço Carbono", value=float(cfg.get("tar_cc", 370.0)), step=10.0, format="%.2f", key="tar_cc", on_change=save_setting, args=("tar_cc",)
        )
        tarifa_corte_inox = st.number_input(
            "Corte Aço Inox", value=float(cfg.get("tar_ci", 410.0)), step=10.0, format="%.2f", key="tar_ci", on_change=save_setting, args=("tar_ci",)
        )
        tarifa_dobra = st.number_input(
            "Dobra", value=float(cfg.get("tar_dobra", 190.0)), step=10.0, format="%.2f", key="tar_dobra", on_change=save_setting, args=("tar_dobra",)
        )
        tarifa_solda = st.number_input(
            "Solda", value=float(cfg.get("tar_solda", 120.0)), step=10.0, format="%.2f", key="tar_solda", on_change=save_setting, args=("tar_solda",)
        )
        tarifa_usinagem = st.number_input(
            "Usinagem", value=float(cfg.get("tar_usin", 120.0)), step=10.0, format="%.2f", key="tar_usin", on_change=save_setting, args=("tar_usin",)
        )

    # --- Insumos ---
    with st.expander("💰 Preços de Insumos", expanded=False):
        preco_aco_kg = st.number_input(
            "Preço Aço (R$/kg)", value=float(cfg.get("preco_aco", 8.50)), step=0.50, format="%.2f", key="preco_aco", on_change=save_setting, args=("preco_aco",)
        )
        preco_inox_kg = st.number_input(
            "Preço Inox (R$/kg)", value=float(cfg.get("preco_inox", 32.00)), step=1.0, format="%.2f", key="preco_inox", on_change=save_setting, args=("preco_inox",)
        )
        preco_pintura_kg = st.number_input(
            "Preço Pintura (R$/kg)", value=float(cfg.get("preco_pintura", 5.00)), step=0.50, format="%.2f", key="preco_pintura", on_change=save_setting, args=("preco_pintura",)
        )

    # --- Impostos ---
    with st.expander("📊 Impostos Totais (%)", expanded=False):
        imposto_venda = st.number_input(
            "Venda (%)", value=float(cfg.get("imp_venda", 30.50)), step=0.5, format="%.2f", key="imp_venda", on_change=save_setting, args=("imp_venda",)
        ) / 100
        imposto_beneficiamento = st.number_input(
            "Beneficiamento (%)", value=float(cfg.get("imp_benef", 20.75)), step=0.5, format="%.2f", key="imp_benef", on_change=save_setting, args=("imp_benef",)
        ) / 100
        imposto_servico = st.number_input(
            "Serviço (%)", value=float(cfg.get("imp_serv", 14.75)), step=0.5, format="%.2f", key="imp_serv", on_change=save_setting, args=("imp_serv",)
        ) / 100

    # --- Margem de Lucro ---
    with st.expander("📈 Margem de Lucro (%)", expanded=False):
        margem_material = st.number_input(
            "Sobre Material (%)", value=float(cfg.get("marg_mat", 30.0)), step=5.0, format="%.2f", key="marg_mat", on_change=save_setting, args=("marg_mat",)
        ) / 100
        margem_servico = st.number_input(
            "Sobre Serviço (%)", value=float(cfg.get("marg_serv", 30.0)), step=5.0, format="%.2f", key="marg_serv", on_change=save_setting, args=("marg_serv",)
        ) / 100

# ============================================================
# DADOS DO PROJETO
# ============================================================
st.markdown('<div class="section-title">📋 Dados do Projeto</div>', unsafe_allow_html=True)

proj_c1, proj_c2, proj_c3 = st.columns([2, 2, 1])
with proj_c1:
    nome_projeto = st.text_input("Nome do Projeto", "Estrutura Metálica 01", key="nome_proj")
with proj_c2:
    nome_cliente = st.text_input("Cliente", "Cliente Padrão", key="nome_cli")
with proj_c3:
    opt_impostos = {
        "Venda": imposto_venda,
        "Beneficiamento": imposto_beneficiamento,
        "Serviço": imposto_servico
    }
    # Resgata o que foi salvo ou usa 'Venda'
    trib_salva = cfg.get("tipo_trib", "Venda")
    idx_trib = list(opt_impostos.keys()).index(trib_salva) if trib_salva in opt_impostos else 0
    
    tipo_tributacao = st.selectbox(
        "Tributação",
        options=list(opt_impostos.keys()),
        index=idx_trib,
        format_func=lambda x: f"{x} ({opt_impostos[x]*100:.2f}%)",
        key="tipo_trib",
        on_change=save_setting,
        args=("tipo_trib",)
    )

# Lógica de imposto aplicado
imposto_aplicado = opt_impostos[tipo_tributacao]

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ============================================================
# 1. PROCESSAMENTO DE ARQUIVO DXF
# ============================================================
st.markdown('<div class="section-title">📐 Importar Arquivo DXF (Corte)</div>', unsafe_allow_html=True)

dxf_c1, dxf_c2 = st.columns([1, 1])

with dxf_c1:
    arquivo_dxf = st.file_uploader(
        "Carregue um arquivo .dxf para calcular o corte automaticamente",
        type=["dxf"],
        key="dxf_upload"
    )
    if arquivo_dxf is not None:
        st.markdown("###### ⚙️ Configurações da Máquina (Ref: 3000W)")
        
        # Tabela (Velocidade mm/min, Tempo Furo seg)
        tabela_3kw = {
            "Aço Carbono": {
                1.0: (12000, 0.2), 1.2: (10000, 0.2), 1.5: (8000, 0.3), 2.0: (6000, 0.3), 
                3.0: (4500, 0.4), 4.75: (3000, 0.6), 6.35: (2500, 0.8), 8.0: (1800, 1.0),
                9.5: (1300, 1.2), 12.7: (900, 1.5), 16.0: (700, 2.0),
                19.05: (500, 3.0), 22.2: (400, 4.0), 25.4: (300, 5.0), 28.5: (200, 6.5), 31.75: (150, 8.0)
            },
            "Aço Inox": {
                1.0: (15000, 0.2), 1.2: (12000, 0.2), 1.5: (9000, 0.3), 2.0: (7000, 0.4), 
                3.0: (4000, 0.5), 4.75: (2000, 0.8), 6.35: (1200, 1.2), 8.0: (800, 1.5),
                9.5: (500, 2.0), 12.7: (300, 3.0), 16.0: (150, 4.0),
                19.05: (100, 5.0), 22.2: (80, 6.0), 25.4: (50, 8.0), 28.5: (40, 10.0), 31.75: (30, 12.0)
            }
        }

        def reset_laser_params():
            m = st.session_state.mat_dxf
            e = st.session_state.esp_dxf
            vel, furo = tabela_3kw.get(m, {}).get(e, (2000, 1.0))
            st.session_state.vel_corte = float(vel)
            st.session_state.t_furo = float(furo)
            
        p1, p2 = st.columns(2)
        mat_dxf = p1.selectbox("Material alvo", ["Aço Carbono", "Aço Inox"], key="mat_dxf", on_change=reset_laser_params)
        
        opcoes_esp = [1.0, 1.2, 1.5, 2.0, 3.0, 4.75, 6.35, 8.0, 9.5, 12.7, 16.0, 19.05, 22.2, 25.4, 28.5, 31.75]
        esp_dxf = p2.selectbox(
            "Espessura (mm)", 
            opcoes_esp, 
            key="esp_dxf", 
            index=3, 
            format_func=lambda x: f"{x} mm (1.1/4\")" if x == 31.75 else f"{x} mm (1\")" if x == 25.4 else f"{x} mm",
            on_change=reset_laser_params
        )
        
        vel_padrao, furo_padrao = tabela_3kw.get(mat_dxf, {}).get(esp_dxf, (2000, 1.0))

        v1, v2 = st.columns(2)
        velocidade_corte = v1.number_input(
            "Corte (mm/min)", value=float(vel_padrao), step=100.0, format="%.0f", key="vel_corte", help="Velocidade da tabela"
        )
        tempo_furo_seg = v2.number_input(
            "Furo (seg)", value=float(furo_padrao), step=0.1, format="%.1f", key="t_furo", help="Tempo de piercing da tabela"
        )
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("⚡ Confirmar Material e Processar DXF", key="btn_process_dxf", type="primary"):
            with st.spinner("Processando arquivo DXF e simulando corte..."):
                resultado = processar_dxf(arquivo_dxf, velocidade_corte, tempo_furo_seg)
                if resultado:
                    st.session_state.dxf_resultado = resultado
                    st.success("DXF processado com sucesso!")

with dxf_c2:
    if st.session_state.dxf_resultado:
        res = st.session_state.dxf_resultado
        st.markdown("##### Resultado do DXF")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Perímetro", f"{res['perimetro']:.1f} mm")
        m2.metric("Comprimento (X)", f"{res.get('largura_x', 0):.1f} mm")
        m3.metric("Altura (Y)", f"{res.get('altura_y', 0):.1f} mm")
        m4.metric("Tempo Total", f"{res['tempo_total_min']:.2f} min")

        st.markdown(f"""
        <div class="info-box">
            ⏱️ Corte: <b>{res['tempo_corte_min']:.2f} min</b> |
            🔥 Furos: <b>{res['furos']} ({res['tempo_furo_min']:.2f} min)</b>
        </div>
        """, unsafe_allow_html=True)

# Nova Sub-seção de Nesting/Arranjo de Chapas
if st.session_state.dxf_resultado:
    res = st.session_state.dxf_resultado
    if res.get('largura_x', 0) > 0 and res.get('altura_y', 0) > 0:
        st.markdown('##### 🧩 Arranjo de Chapas (Nesting) - *Estimativa*')
        with st.expander("Abrir Calculadora de Estudo de Arranjo", expanded=True):
            n_c1, n_c2 = st.columns([1, 2])
            
            with n_c1:
                st.markdown("###### Propriedades do Arranjo")
                ch_w = st.number_input("Largura da Chapa (X) mm", value=1500.0, step=10.0, key="nest_ch_w")
                ch_h = st.number_input("Comprimento da Chapa (Y) mm", value=3000.0, step=10.0, key="nest_ch_h")
                n_espaco = st.number_input("Distância entre peças (mm)", value=10.0, step=1.0, key="nest_esp")
                n_margem = st.number_input("Distância para bordas (mm)", value=10.0, step=1.0, key="nest_marg")
                n_qtd_desejada = st.number_input("Quantidade Desejada (0 = Encher Chapa)", value=0, step=1, key="nest_qtd")
                n_rot = st.checkbox("Rotacionar peças em 90° visando max. aproveitamento", value=True, key="nest_rot")
                
                # Dimensões da peça (com override de segurança minimal case)
                w_p = res['largura_x']
                h_p = res['altura_y']
                
                gerar_arranjo = st.button("📊 Calcular Arranjo")
                
            with n_c2:
                if gerar_arranjo:
                    with st.spinner("Calculando o melhor arranjo matemático (Bounding Box)..."):
                        best_layout, aprov, ret_w, ret_h = calcular_nesting_simples(w_p, h_p, ch_w, ch_h, n_margem, n_espaco, n_rot, n_qtd_desejada)
                        
                        if best_layout and best_layout['qtd'] > 0:
                            if n_qtd_desejada > 0 and best_layout['qtd'] == n_qtd_desejada:
                                st.success(f"Foram encaixadas **{best_layout['qtd']} peças**. Retalho necessário: **{ret_w:.1f} x {ret_h:.1f} mm** (Ap: **{aprov:.1f}%** do retalho)")
                            else:
                                st.success(f"Cabem **{best_layout['qtd']} peças** (Aproveitamento: **{aprov:.1f}%** da chapa inteira)")
                            
                            st.caption(f"Estratégia usada: {best_layout['desc']}")
                            
                            # Gráfico de visualização
                            fig, ax = plt.subplots(figsize=(6, 6 * (ch_h / ch_w) if ch_w > 0 else 6))
                            
                            # Desenha Chapa Total
                            ax.add_patch(patches.Rectangle((0, 0), ch_w, ch_h, linewidth=2, edgecolor='black', facecolor='#e0e0e0', label='Chapa'))
                            
                            # Se há um retalho menor específico e bateu a meta, desenha o contorno do retalho
                            if n_qtd_desejada > 0 and best_layout['qtd'] == n_qtd_desejada:
                                ax.add_patch(patches.Rectangle((0, 0), ret_w, ret_h, linewidth=2, edgecolor='orange', facecolor='#ffe0b2', hatch='//', alpha=0.9, zorder=0))
                                ax.text(ret_w/2, ret_h, f"Retalho: {ret_w:.0f}x{ret_h:.0f}mm", color='red', ha='center', va='bottom', fontsize=9, weight='bold')
                            
                            # Desenha Área Útil (Tracejado)
                            ax.add_patch(patches.Rectangle((n_margem, n_margem), ch_w - 2*n_margem, ch_h - 2*n_margem, 
                                                           linewidth=1, edgecolor='red', linestyle='--', facecolor='none'))
                            
                            # Desenha as Peças
                            for i, rect in enumerate(best_layout['rects']):
                                # Usa cor alternada para estética
                                cor = '#1f77b4' if i % 2 == 0 else '#2ca02c'
                                ax.add_patch(patches.Rectangle((rect['x'], rect['y']), rect['w'], rect['h'], 
                                                               linewidth=1, edgecolor='white', facecolor=cor, alpha=0.8, zorder=2))
                                # Texto no centro da peça (apenas se couber minimamente)
                                if rect['w'] > ch_w * 0.05 and rect['h'] > ch_h * 0.05:
                                    ax.text(rect['x'] + rect['w']/2, rect['y'] + rect['h']/2, str(i+1), 
                                            color='white', weight='bold', ha='center', va='center', fontsize=8, zorder=3)
                            
                            ax.set_xlim(0, ch_w)
                            ax.set_ylim(0, ch_h)
                            ax.set_aspect('equal')
                            ax.set_xlabel("Largura (mm)")
                            ax.set_ylabel("Comprimento (mm)")
                            ax.set_title("Visualização do Arranjo - Bounding Box")
                            st.pyplot(fig)
                            
                            # Um botão para transferir quantidade para o form de material? (Opcional, apenas UX extra)
                            if st.button("Copiar Qtd para Form de Material (Abaixo)", icon="⬇️"):
                                st.session_state["qtd_mat_temp"] = best_layout['qtd']
                                st.rerun()

                        else:
                            st.warning("⚠️ Nenhuma peça cabe com estas configurações.")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# ============================================================
# 2. CALCULADORA DE MATERIAIS
# ============================================================
st.markdown('<div class="section-title">🧱 Adicionar Materiais</div>', unsafe_allow_html=True)

mat_col1, mat_col2 = st.columns([1, 2])

DENSIDADE_ACO = 7850  # kg/m³

with mat_col1:
    st.markdown("##### Seleção do Item")
    tipo_material = st.selectbox(
        "Tipo de Material",
        ["Chapa", "Tubo Quadrado", "Tubo Redondo", "Barra Quadrada", "Barra Redonda", "Manual"],
        key="tipo_mat"
    )
    tipo_aco = st.selectbox("Tipo de Aço", ["Aço Carbono", "Aço Inox"], key="tipo_aco_mat")
    
    # Se a quantidade veio do form de nesting, preenche, senão usa 1
    val_qtd = st.session_state.get("qtd_mat_temp", 1)
    qtd_material = st.number_input("Quantidade", min_value=1, value=val_qtd, step=1, key="qtd_mat")
    if "qtd_mat_temp" in st.session_state and st.session_state.qtd_mat_temp == qtd_material:
        # Mostra pequeno aviso verde e limpa memory
        st.success("Quantidade preenchida do Nesting!")
        del st.session_state["qtd_mat_temp"]

with mat_col2:
    st.markdown("##### Dimensões")
    peso_calculado = 0.0
    desc_item = ""

    if tipo_material == "Chapa":
        c1, c2, c3 = st.columns(3)
        ch_l = c1.number_input("Largura (mm)", value=1000.0, key="ch_l") / 1000
        ch_c = c2.number_input("Comprimento (mm)", value=2000.0, key="ch_c") / 1000
        ch_e = c3.number_input("Espessura (mm)", value=4.75, step=0.25, key="ch_e") / 1000
        peso_calculado = (ch_l * ch_c * ch_e) * DENSIDADE_ACO
        desc_item = f"Chapa {ch_e*1000:.2f}mm ({ch_l*1000:.0f}x{ch_c*1000:.0f})"

    elif tipo_material == "Tubo Quadrado":
        c1, c2, c3, c4 = st.columns(4)
        tq_l = c1.number_input("Largura (mm)", value=50.0, key="tq_l") / 1000
        tq_a = c2.number_input("Altura (mm)", value=50.0, key="tq_a") / 1000
        tq_e = c3.number_input("Parede (mm)", value=2.0, step=0.1, key="tq_e") / 1000
        tq_c = c4.number_input("Comp. (m)", value=6.0, key="tq_c")
        area = ((tq_l * tq_a) - ((tq_l - 2*tq_e) * (tq_a - 2*tq_e))) * 0.96
        peso_calculado = area * tq_c * DENSIDADE_ACO
        desc_item = f"Tubo Quad. {tq_l*1000:.0f}x{tq_a*1000:.0f} #{tq_e*1000:.1f}mm L={tq_c:.1f}m"

    elif tipo_material == "Tubo Redondo":
        c1, c2, c3 = st.columns(3)
        tr_d = c1.number_input("Diâmetro (mm)", value=50.0, key="tr_d") / 1000
        tr_e = c2.number_input("Parede (mm)", value=2.0, step=0.1, key="tr_e") / 1000
        tr_c = c3.number_input("Comp. (m)", value=6.0, key="tr_c")
        area = math.pi * ((tr_d/2)**2 - ((tr_d - 2*tr_e)/2)**2)
        peso_calculado = area * tr_c * DENSIDADE_ACO
        desc_item = f"Tubo Red. Ø{tr_d*1000:.0f}mm #{tr_e*1000:.1f}mm L={tr_c:.1f}m"

    elif tipo_material == "Barra Quadrada":
        c1, c2 = st.columns(2)
        bq_l = c1.number_input("Lado (mm)", value=20.0, key="bq_l") / 1000
        bq_c = c2.number_input("Comp. (m)", value=6.0, key="bq_c")
        peso_calculado = (bq_l ** 2) * bq_c * DENSIDADE_ACO
        desc_item = f"Barra Quad. {bq_l*1000:.0f}mm L={bq_c:.1f}m"

    elif tipo_material == "Barra Redonda":
        c1, c2 = st.columns(2)
        br_d = c1.number_input("Diâmetro (mm)", value=10.0, key="br_d") / 1000
        br_c = c2.number_input("Comp. (m)", value=6.0, key="br_c")
        peso_calculado = (math.pi * (br_d/2)**2 * br_c) * DENSIDADE_ACO
        desc_item = f"Barra Red. Ø{br_d*1000:.1f}mm L={br_c:.1f}m"

    elif tipo_material == "Manual":
        c1, c2 = st.columns(2)
        nome_manual = c1.text_input("Descrição", "Item personalizado", key="man_nome")
        peso_manual = c2.number_input("Peso Total (kg)", value=10.0, key="man_peso")
        peso_calculado = peso_manual
        desc_item = f"{nome_manual} (Manual)"

    # Preço unitário do material
    preco_kg_selecionado = preco_inox_kg if tipo_aco == "Aço Inox" else preco_aco_kg
    peso_total_linha = peso_calculado * qtd_material
    custo_material_linha = peso_total_linha * preco_kg_selecionado

    st.markdown(f"""
    <div class="info-box">
        ⚖️ Peso Unit.: <b>{peso_calculado:.2f} kg</b> |
        📦 Peso Total: <b>{peso_total_linha:.2f} kg</b> |
        💲 Custo Material: <b>R$ {custo_material_linha:.2f}</b>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕ ADICIONAR MATERIAL", key="btn_add_mat"):
        st.session_state.lista_materiais.append({
            'Qtd': qtd_material,
            'Descrição': desc_item,
            'Tipo Aço': tipo_aco,
            'Peso Unit. (kg)': round(peso_calculado, 2),
            'Peso Total (kg)': round(peso_total_linha, 2),
            'R$/kg': round(preco_kg_selecionado, 2),
            'Custo (R$)': round(custo_material_linha, 2)
        })
        st.success(f"✅ '{desc_item}' adicionado!")
        st.rerun()


# --- Tabela de Materiais ---
if st.session_state.lista_materiais:
    st.markdown("##### 📋 Lista de Materiais")
    df_mat = pd.DataFrame(st.session_state.lista_materiais)
    st.dataframe(df_mat, use_container_width=True, hide_index=True)

    tot_col1, tot_col2, tot_col3 = st.columns(3)
    with tot_col1:
        peso_total_mat = sum(i['Peso Total (kg)'] for i in st.session_state.lista_materiais)
        st.metric("⚖️ Peso Total Materiais", f"{peso_total_mat:.2f} kg")
    with tot_col2:
        custo_total_mat = sum(i['Custo (R$)'] for i in st.session_state.lista_materiais)
        st.metric("💰 Custo Total Materiais", f"R$ {custo_total_mat:,.2f}")
    with tot_col3:
        if st.button("🗑️ Limpar Materiais", key="btn_limpar_mat"):
            st.session_state.lista_materiais = []
            st.rerun()
else:
    peso_total_mat = 0.0
    custo_total_mat = 0.0


st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ============================================================
# 3. MÃO DE OBRA / SERVIÇOS
# ============================================================
st.markdown('<div class="section-title">⏱️ Mão de Obra e Serviços</div>', unsafe_allow_html=True)

serv_c1, serv_c2, serv_c3 = st.columns(3)

with serv_c1:
    with st.container(border=True):
        st.markdown("##### ✂️ Corte")
        tec_corte = st.radio("Tecnologia", ["Aço Carbono", "Aço Inox / Laser"], key="tec_corte")
        tarifa_corte_sel = tarifa_corte_inox if "Inox" in tec_corte else tarifa_corte_carbono

        # Se veio do DXF, preenche automaticamente
        tempo_dxf = 0.0
        if st.session_state.dxf_resultado:
            tempo_dxf = st.session_state.dxf_resultado['tempo_total_min']

        t_corte = st.number_input(
            "Minutos de CORTE",
            value=round(tempo_dxf, 2),
            step=1.0,
            format="%.2f",
            key="t_corte",
            help="Se processou um DXF, o valor é preenchido automaticamente."
        )

    with st.container(border=True):
        st.markdown("##### 🔧 Dobra")
        t_dobra = st.number_input("Minutos de DOBRA", value=0.0, step=1.0, format="%.2f", key="t_dobra")

with serv_c2:
    with st.container(border=True):
        st.markdown("##### ⚙️ Usinagem")
        t_usinagem = st.number_input("Minutos de USINAGEM", value=0.0, step=1.0, format="%.2f", key="t_usin")

    with st.container(border=True):
        st.markdown("##### 🔥 Solda")
        t_solda = st.number_input("Minutos de SOLDA", value=0.0, step=1.0, format="%.2f", key="t_solda")

with serv_c3:
    with st.container(border=True):
        st.markdown("##### 🎨 Pintura")
        aplicar_pintura = st.checkbox("Incluir Pintura", value=False, key="chk_pintura")
        if aplicar_pintura:
            peso_pintura = st.number_input(
                "Peso para Pintura (kg)",
                value=peso_total_mat,
                step=1.0,
                format="%.2f",
                key="peso_pintura"
            )
        else:
            peso_pintura = 0.0

    with st.container(border=True):
        st.markdown("##### 📦 Extras")
        valor_extras = st.number_input(
            "R$ Extras (Frete/Terceiros)", value=0.0, step=10.0, format="%.2f", key="extras"
        )


# ============================================================
# 4. CÁLCULOS FINANCEIROS
# ============================================================
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
st.markdown('<div class="section-title">💰 Resultado do Orçamento</div>', unsafe_allow_html=True)

# --- Custos de Mão de Obra ---
custo_corte = (t_corte / 60) * tarifa_corte_sel
custo_dobra = (t_dobra / 60) * tarifa_dobra
custo_usinagem = (t_usinagem / 60) * tarifa_usinagem
custo_solda = (t_solda / 60) * tarifa_solda
custo_pintura = peso_pintura * preco_pintura_kg if aplicar_pintura else 0.0

custo_total_servicos = custo_corte + custo_dobra + custo_usinagem + custo_solda + custo_pintura

# --- Custo Direto Total ---
custo_direto = custo_total_mat + custo_total_servicos + valor_extras

# --- Aplicando Margens ---
lucro_material = custo_total_mat * margem_material
lucro_servico = custo_total_servicos * margem_servico
lucro_extras = valor_extras * margem_servico

lucro_total = lucro_material + lucro_servico + lucro_extras

# --- Sub-total (custo + lucro) ---
subtotal = custo_direto + lucro_total

# --- Preço de Venda (com impostos "por dentro") ---
divisor_imposto = 1 - imposto_aplicado
if divisor_imposto <= 0.05:
    divisor_imposto = 0.05

preco_venda = subtotal / divisor_imposto
valor_imposto = preco_venda * imposto_aplicado


# --- EXIBIÇÃO DOS RESULTADOS ---
res_c1, res_c2, res_c3, res_c4 = st.columns(4)

with res_c1:
    card_resultado("Custo Material", f"R$ {custo_total_mat:,.2f}", "result-card-blue")
    card_resultado("Custo Serviços", f"R$ {custo_total_servicos:,.2f}")

with res_c2:
    card_resultado("Custo Direto Total", f"R$ {custo_direto:,.2f}")
    card_resultado("Extras", f"R$ {valor_extras:,.2f}")

with res_c3:
    card_resultado("Lucro Projetado", f"R$ {lucro_total:,.2f}", "result-card-orange")
    card_resultado("Impostos", f"R$ {valor_imposto:,.2f}")

with res_c4:
    card_resultado("PREÇO DE VENDA", f"R$ {preco_venda:,.2f}", "result-card-green")
    if peso_total_mat > 0:
        card_resultado("R$/kg Final", f"R$ {preco_venda/peso_total_mat:,.2f}")


# --- Detalhamento ---
with st.expander("📊 Detalhamento Completo", expanded=False):
    det_c1, det_c2 = st.columns(2)

    with det_c1:
        st.markdown("##### Composição de Custos")
        dados_custos = {
            "Item": ["Material", "Corte", "Dobra", "Usinagem", "Solda", "Pintura", "Extras"],
            "Tempo (min)": ["-", f"{t_corte:.2f}", f"{t_dobra:.2f}", f"{t_usinagem:.2f}", f"{t_solda:.2f}", "-", "-"],
            "Tarifa (R$/h)": ["-", f"{tarifa_corte_sel:.2f}", f"{tarifa_dobra:.2f}", f"{tarifa_usinagem:.2f}", f"{tarifa_solda:.2f}", f"{preco_pintura_kg:.2f}/kg", "-"],
            "Custo (R$)": [
                f"{custo_total_mat:,.2f}",
                f"{custo_corte:,.2f}",
                f"{custo_dobra:,.2f}",
                f"{custo_usinagem:,.2f}",
                f"{custo_solda:,.2f}",
                f"{custo_pintura:,.2f}",
                f"{valor_extras:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(dados_custos), use_container_width=True, hide_index=True)

    with det_c2:
        st.markdown("##### Formação do Preço de Venda")
        
        lbl_trib = f"Impostos ({tipo_tributacao})"
        
        dados_preco = {
            "Etapa": [
                "Custo Direto",
                f"Lucro Material ({margem_material*100:.0f}%)",
                f"Lucro Serviço ({margem_servico*100:.0f}%)",
                "Subtotal",
                lbl_trib,
                "PREÇO FINAL"
            ],
            "Valor (R$)": [
                f"{custo_direto:,.2f}",
                f"{lucro_material:,.2f}",
                f"{lucro_servico + lucro_extras:,.2f}",
                f"{subtotal:,.2f}",
                f"{valor_imposto:,.2f}",
                f"{preco_venda:,.2f}"
            ]
        }
        st.dataframe(pd.DataFrame(dados_preco), use_container_width=True, hide_index=True)


st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)


# ============================================================
# 5. EXPORTAÇÃO
# ============================================================
st.markdown('<div class="section-title">📥 Exportar Orçamento</div>', unsafe_allow_html=True)

exp_c1, exp_c2 = st.columns(2)

# --- Relatório TXT ---
txt_relatorio = f"""
{'='*60}
    ORÇAMENTO INDUSTRIAL
{'='*60}
Projeto:  {nome_projeto}
Cliente:  {nome_cliente}
Data:     {datetime.now().strftime("%d/%m/%Y %H:%M")}
{'='*60}

MATERIAIS:
{pd.DataFrame(st.session_state.lista_materiais).to_string(index=False) if st.session_state.lista_materiais else "Nenhum item adicionado"}

{'='*60}
SERVIÇOS:
  Corte:      {t_corte:.2f} min  →  R$ {custo_corte:,.2f}  ({tec_corte})
  Dobra:      {t_dobra:.2f} min  →  R$ {custo_dobra:,.2f}
  Usinagem:   {t_usinagem:.2f} min  →  R$ {custo_usinagem:,.2f}
  Solda:      {t_solda:.2f} min  →  R$ {custo_solda:,.2f}
  Pintura:    {peso_pintura:.2f} kg  →  R$ {custo_pintura:,.2f}
  Extras:                        →  R$ {valor_extras:,.2f}

{'='*60}
RESUMO FINANCEIRO:
  Custo Material:       R$ {custo_total_mat:,.2f}
  Custo Serviços:       R$ {custo_total_servicos:,.2f}
  Custo Direto Total:   R$ {custo_direto:,.2f}
  Lucro Projetado:      R$ {lucro_total:,.2f}
  Impostos ({tipo_tributacao}): R$ {valor_imposto:,.2f}

  ╔══════════════════════════════════════╗
  ║  PREÇO FINAL DE VENDA: R$ {preco_venda:>10,.2f}  ║
  ╚══════════════════════════════════════╝
  
  Peso Total: {peso_total_mat:.2f} kg
  {'R$/kg: R$ ' + f'{preco_venda/peso_total_mat:,.2f}' if peso_total_mat > 0 else ''}
{'='*60}
"""

with exp_c1:
    st.download_button(
        "📄 Baixar Orçamento (TXT)",
        txt_relatorio,
        f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain",
        use_container_width=True
    )

with exp_c2:
    # --- Exportação Excel ---
    try:
        buffer_excel = io.BytesIO()
        with pd.ExcelWriter(buffer_excel, engine='openpyxl') as writer:
            # Aba de Materiais
            if st.session_state.lista_materiais:
                df_mat_export = pd.DataFrame(st.session_state.lista_materiais)
                df_mat_export.to_excel(writer, sheet_name='Materiais', index=False)

            # Aba de Serviços
            df_serv = pd.DataFrame({
                "Serviço": ["Corte", "Dobra", "Usinagem", "Solda", "Pintura", "Extras"],
                "Tempo (min)": [t_corte, t_dobra, t_usinagem, t_solda, 0, 0],
                "Custo (R$)": [custo_corte, custo_dobra, custo_usinagem, custo_solda, custo_pintura, valor_extras]
            })
            df_serv.to_excel(writer, sheet_name='Serviços', index=False)

            # Aba Resumo
            df_resumo = pd.DataFrame({
                "Item": ["Custo Material", "Custo Serviços", "Extras", "Custo Direto",
                         "Lucro Material", "Lucro Serviço", "Subtotal", "Impostos", "PREÇO VENDA"],
                "Valor (R$)": [custo_total_mat, custo_total_servicos, valor_extras, custo_direto,
                               lucro_material, lucro_servico + lucro_extras, subtotal, valor_imposto, preco_venda]
            })
            df_resumo.to_excel(writer, sheet_name='Resumo', index=False)

        st.download_button(
            "📊 Baixar Orçamento (Excel)",
            buffer_excel.getvalue(),
            f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"Não foi possível gerar Excel: {e}")


# ============================================================
# RODAPÉ
# ============================================================
st.markdown("""
<div style="text-align:center; padding: 2rem 0 1rem; opacity: 0.5; font-size: 0.8rem;">
    🏭 Orçamento Industrial v1.0 — Desenvolvido para cálculo de corte, dobra, usinagem, solda e pintura
</div>
""", unsafe_allow_html=True)
