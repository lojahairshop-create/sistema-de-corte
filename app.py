import streamlit as st
import math
import pandas as pd
from datetime import datetime, timedelta
import io, json, os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from calculos import *
from estilos import CSS
from dxf_utils import processar_dxf, calcular_nesting_simples, EZDXF_DISPONIVEL

st.set_page_config(page_title="Orçamento Industrial Unificado", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")
st.markdown(CSS, unsafe_allow_html=True)

CONFIG_PATH = "config_orcamento.json"

def load_config():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_config(params):
    config = load_config()
    config.update(params)
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4)
    except:
        pass

def save_s(key):
    if key in st.session_state:
        save_config({key: st.session_state[key]})

cfg = load_config()

def card_resultado(label, valor, classe=""):
    st.markdown(f'<div class="result-card {classe}"><div class="label">{label}</div><div class="value">{valor}</div></div>', unsafe_allow_html=True)

# State initialization
if 'itens' not in st.session_state:
    st.session_state.itens = []
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = []

st.markdown('<div class="main-header"><h1>🏭 Orçamento Industrial Unificado</h1><p>Planilha de Custo • Importação DXF • Dobra • Solda • Montagem</p></div>', unsafe_allow_html=True)

# === SIDEBAR ===
with st.sidebar:
    st.markdown("## ⚙️ Configurações Globais")
    
    with st.expander("📊 Impostos (%)", expanded=True):
        tx_icms = st.number_input("ICMS", value=float(cfg.get("tx_icms", 18.0)), step=0.5, format="%.2f", key="tx_icms", on_change=save_s, args=("tx_icms",)) / 100
        tx_ipi = st.number_input("IPI", value=float(cfg.get("tx_ipi", 5.0)), step=0.5, format="%.2f", key="tx_ipi", on_change=save_s, args=("tx_ipi",)) / 100
        tx_pis = st.number_input("PIS", value=float(cfg.get("tx_pis", 0.65)), step=0.05, format="%.2f", key="tx_pis", on_change=save_s, args=("tx_pis",)) / 100
        tx_cofins = st.number_input("COFINS", value=float(cfg.get("tx_cofins", 3.0)), step=0.1, format="%.2f", key="tx_cofins", on_change=save_s, args=("tx_cofins",)) / 100
        tx_csll = st.number_input("CSLL", value=float(cfg.get("tx_csll", 1.08)), step=0.1, format="%.2f", key="tx_csll", on_change=save_s, args=("tx_csll",)) / 100
        tx_irpj = st.number_input("IRPJ", value=float(cfg.get("tx_irpj", 1.2)), step=0.1, format="%.2f", key="tx_irpj", on_change=save_s, args=("tx_irpj",)) / 100
        fator = calcular_fator_impostos(tx_icms, tx_pis, tx_cofins, tx_csll, tx_irpj)
        st.info(f"Cascata: {(1-fator)*100:.2f}% | Fator: {fator:.4f}")
        
    with st.expander("💰 Margem e Comissão", expanded=True):
        margem_lucro = st.number_input("Margem de Lucro (%)", value=float(cfg.get("margem", 30.0)), step=5.0, format="%.1f", key="margem", on_change=save_s, args=("margem",)) / 100
        taxa_comissao = st.number_input("Comissão (%)", value=float(cfg.get("comissao", 3.0)), step=0.5, format="%.1f", key="comissao", on_change=save_s, args=("comissao",)) / 100
        ajuste_comercial = st.number_input("Acréscimo (+) / Desconto (-) (%)", value=float(cfg.get("ajuste_comercial", 0.0)), step=1.0, format="%.1f", key="ajuste_comercial", on_change=save_s, args=("ajuste_comercial",))
        
    with st.expander("🛠️ Tarifas Hora-Máquina (R$/h)", expanded=False):
        tar_corte = st.number_input("Corte Laser", value=float(cfg.get("tar_corte", 450.0)), step=10.0, key="tar_corte", on_change=save_s, args=("tar_corte",))
        tar_setup = st.number_input("SET-UP", value=float(cfg.get("tar_setup", 60.0)), step=10.0, key="tar_setup", on_change=save_s, args=("tar_setup",))
        tar_dobra = st.number_input("Dobra", value=float(cfg.get("tar_dobra", 100.0)), step=10.0, key="tar_dobra", on_change=save_s, args=("tar_dobra",))
        tar_caldeiraria = st.number_input("Caldeiraria", value=float(cfg.get("tar_cald", 100.0)), step=10.0, key="tar_cald", on_change=save_s, args=("tar_cald",))
        tar_solda = st.number_input("Solda", value=float(cfg.get("tar_solda", 100.0)), step=10.0, key="tar_solda", on_change=save_s, args=("tar_solda",))
        tar_guilhotina = st.number_input("Guilhotina", value=float(cfg.get("tar_guil", 68.0)), step=10.0, key="tar_guil", on_change=save_s, args=("tar_guil",))
        tar_usinagem = st.number_input("Usinagem Interna", value=float(cfg.get("tar_usin", 80.0)), step=10.0, key="tar_usin", on_change=save_s, args=("tar_usin",))
        tar_montagem = st.number_input("Montagem", value=float(cfg.get("tar_mont", 80.0)), step=10.0, key="tar_mont", on_change=save_s, args=("tar_mont",))
        
    with st.expander("⚙️ Material e Chapa Padrão", expanded=False):
        chapa_l_pad = st.number_input("Largura Chapa (mm)", value=float(cfg.get("ch_l", 1200.0)), step=100.0, key="ch_l", on_change=save_s, args=("ch_l",))
        chapa_c_pad = st.number_input("Comprimento Chapa (mm)", value=float(cfg.get("ch_c", 2400.0)), step=100.0, key="ch_c", on_change=save_s, args=("ch_c",))
        preco_aco = st.number_input("Preço Aço Carbono (R$/kg)", value=float(cfg.get("p_aco", 8.50)), step=0.5, format="%.2f", key="p_aco", on_change=save_s, args=("p_aco",))
        preco_inox = st.number_input("Preço Inox (R$/kg)", value=float(cfg.get("p_inox", 32.0)), step=1.0, format="%.2f", key="p_inox", on_change=save_s, args=("p_inox",))
        preco_alum = st.number_input("Preço Alumínio (R$/kg)", value=float(cfg.get("p_alum", 25.0)), step=1.0, format="%.2f", key="p_alum", on_change=save_s, args=("p_alum",))

    with st.expander("📄 Configurações do PDF (Emissor/Logo)", expanded=False):
        if 'logo_uploader_key' not in st.session_state:
            st.session_state.logo_uploader_key = 0

        logo_bytes = None
        if os.path.exists("logo_customizado.bin"):
            try:
                with open("logo_customizado.bin", "rb") as f:
                    logo_bytes = f.read()
            except:
                pass

        logo_uploaded = st.file_uploader("Logo da Empresa (PNG/JPG)", type=["png", "jpg", "jpeg"], key=f"logo_uploader_{st.session_state.logo_uploader_key}")
        if logo_uploaded is not None:
            new_logo_bytes = logo_uploaded.getvalue()
            if new_logo_bytes != logo_bytes:
                logo_bytes = new_logo_bytes
                try:
                    with open("logo_customizado.bin", "wb") as f:
                        f.write(logo_bytes)
                except:
                    pass
                st.rerun()

        if logo_bytes is not None:
            st.image(logo_bytes, caption="Logotipo do PDF", width=150)
            if st.button("🗑️ Remover Logotipo Customizado", key="btn_remove_logo"):
                if os.path.exists("logo_customizado.bin"):
                    try:
                        os.remove("logo_customizado.bin")
                    except:
                        pass
                st.session_state.logo_uploader_key += 1
                st.rerun()

        emissor_nome = st.text_input("Nome da Empresa", value=cfg.get("em_nome", "2R CORTE LASER"), key="em_nome", on_change=save_s, args=("em_nome",))
        emissor_resp = st.text_input("Responsável / Vendedor", value=cfg.get("em_resp", "Wellington Rafael"), key="em_resp", on_change=save_s, args=("em_resp",))
        emissor_end = st.text_area("Endereço", value=cfg.get("em_end", "Av. Alexandre José Barbosa, 215 - Jardim São Luiz II\nItatiba - SP, 13.253-080"), key="em_end", on_change=save_s, args=("em_end",))
        emissor_tel = st.text_input("Telefone", value=cfg.get("em_tel", "(11) 4524-3463 – Ramal: 219"), key="em_tel", on_change=save_s, args=("em_tel",))
        emissor_cel = st.text_input("Celular", value=cfg.get("em_cel", "(11) 98994-4136"), key="em_cel", on_change=save_s, args=("em_cel",))
        emissor_email = st.text_input("E-mail", value=cfg.get("em_email", "comercial@2rcortelaser.com.br"), key="em_email", on_change=save_s, args=("em_email",))

    with st.expander("📜 Termos e Condições do PDF", expanded=False):
        cond_prazo = st.text_input("Prazo de Entrega", value=cfg.get("cond_prazo", "7 Dias úteis após recebimento do pedido de compra"), key="cond_prazo", on_change=save_s, args=("cond_prazo",))
        cond_pgto = st.text_input("Forma de Pagamento", value=cfg.get("cond_pgto", "A Combinar"), key="cond_pgto", on_change=save_s, args=("cond_pgto",))
        cond_minimo = st.number_input("Pedido Mínimo (R$)", value=float(cfg.get("cond_minimo", 500.0)), step=50.0, key="cond_minimo", on_change=save_s, args=("cond_minimo",))
        cond_frete = st.text_input("Frete", value=cfg.get("cond_frete", "FOB"), key="cond_frete", on_change=save_s, args=("cond_frete",))
        cond_impostos = st.text_area("Impostos Descrição", value=cfg.get("cond_impostos", "ICMS INCLUSO - PIS/COFINS INCLUSO\nIPI: 3.25% A INCLUIR"), key="cond_impostos", on_change=save_s, args=("cond_impostos",))
        cond_comentarios = st.text_area("Mensagem de Observações / Totais", value=cfg.get("cond_coment", "Venda IPI - 3,25% / Benef. Isento"), key="cond_coment", on_change=save_s, args=("cond_coment",))
        
        st.markdown("**Texto das Condições Gerais (7 Itens):**")
        c1 = st.text_area("Item 1", value=cfg.get("c1", "Os desenhos deverão ser fornecidos no formato .DXF ou .DWG em escala 1:1 com a respectiva indicação de revisão. Peças cortadas fora da sua verdadeira grandeza serão de responsabilidade do cliente."), key="c1", on_change=save_s, args=("c1",))
        c2 = st.text_area("Item 2", value=cfg.get("c2", "TOLERANCIA CORTE <=0,2mm e <=1,00mm | TOLERÂNCIA DOBRA: +/- 1,5mm."), key="c2", on_change=save_s, args=("c2",))
        c3 = st.text_area("Item 3", value=cfg.get("c3", "Furos com diâmetro menor que a espessura da chapa serão somente marcados."), key="c3", on_change=save_s, args=("c3",))
        c4 = st.text_area("Item 4", value=cfg.get("c4", "A produção somente será iniciada quando:\n* Recebido pedido do cliente E / OU recebimento da matéria-prima (no caso de beneficiamento).\n* Recebido a confirmação por e-mail aprovando a proposta comercial."), key="c4", on_change=save_s, args=("c4",))
        c5 = st.text_area("Item 5", value=cfg.get("c5", "Horário para entrega e retirada de mercadorias: 08h às 12h | 14h às 17h."), key="c5", on_change=save_s, args=("c5",))
        c6 = st.text_area("Item 6", value=cfg.get("c6", "No processo de corte pode haver empenamento das peças (algo normal devida a alta temperatura). O cliente deve especificar no ato da cotação a necessidade de mantê-las planas."), key="c6", on_change=save_s, args=("c6",))
        c7 = st.text_area("Item 7", value=cfg.get("c7", "Prezados clientes, concluído o pedido de BENEFICIAMENTO, a sucata gerada será mantida em até, no máximo, 4 dias úteis. Após este período será descartada junto com outras sucatas pelo motivo de logística e espaço. Dessa forma, tornando-se de propriedade da empresa."), key="c7", on_change=save_s, args=("c7",))

taxas_impostos = {'icms': tx_icms, 'ipi': tx_ipi, 'pis': tx_pis, 'cofins': tx_cofins, 'csll': tx_csll, 'irpj': tx_irpj}
tarifas = {'corte_laser': tar_corte, 'setup': tar_setup, 'dobra': tar_dobra, 'caldeiraria': tar_caldeiraria, 'solda': tar_solda, 'guilhotina': tar_guilhotina, 'usinagem_int': tar_usinagem, 'montagem': tar_montagem}
precos_material = {'Aço Carbono': preco_aco, 'Aço Inox': preco_inox, 'Alumínio': preco_alum}
config_global = {
    'gap': 5.0,
    'margem_lucro': margem_lucro,
    'taxa_comissao': taxa_comissao,
    'taxas_impostos': taxas_impostos,
    'tarifas': tarifas,
    'precos_material': precos_material,
    'ajuste_comercial': ajuste_comercial
}

# === DADOS DO PROJETO ===
st.markdown('<div class="section-title">📋 Dados do Orçamento</div>', unsafe_allow_html=True)
pc1, pc2, pc3, pc4 = st.columns([2, 2, 1, 1])
with pc1:
    nome_projeto = st.text_input("Projeto / Orçamento Nº", cfg.get("nome_proj", "Orçamento 001"), key="nome_proj", on_change=save_s, args=("nome_proj",))
with pc2:
    nome_cliente = st.text_input("Cliente", cfg.get("nome_cli", ""), key="nome_cli", on_change=save_s, args=("nome_cli",))
with pc3:
    orcamentista = st.text_input("Orçamentista", cfg.get("orcam", ""), key="orcam", on_change=save_s, args=("orcam",))
with pc4:
    tipo_venda = st.selectbox("Tipo de Venda", ["Revenda", "Venda Direta", "Industrialização"], index=["Revenda", "Venda Direta", "Industrialização"].index(cfg.get("tipo_venda", "Revenda")), key="tipo_venda", on_change=save_s, args=("tipo_venda",))

pc5, pc6, pc7, pc8 = st.columns([2.5, 1.5, 1, 1])
with pc5:
    cliente_endereco = st.text_input("Endereço do Cliente", cfg.get("cliente_end", "Singapura"), key="cliente_end", on_change=save_s, args=("cliente_end",))
with pc6:
    cliente_telefone = st.text_input("Telefone do Cliente", cfg.get("cliente_tel", ""), key="cliente_tel", on_change=save_s, args=("cliente_tel",))
with pc7:
    data_criacao_input = st.date_input("Data de Criação", value=datetime.now())
with pc8:
    validade_dias = st.number_input("Validade (dias)", min_value=1, value=int(cfg.get("validade_dias", 7)), key="validade_dias", on_change=save_s, args=("validade_dias",))

data_vencimento_input = data_criacao_input + timedelta(days=validade_dias)
data_criacao_str = data_criacao_input.strftime('%d/%m/%Y')
data_vencimento_str = data_vencimento_input.strftime('%d/%m/%Y')

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# === IMPORTAÇÃO DE DESENHOS / ENTRADAS ===
st.markdown('<div class="section-title">📥 Entrada de Peças</div>', unsafe_allow_html=True)

tab_dxf, tab_manual = st.tabs(["📂 Importar Arquivos DXF", "✍️ Adicionar Peça Manual (Formulário)"])

with tab_dxf:
    up_col, actions_col = st.columns([2, 1])
    
    with up_col:
        uploaded_files = st.file_uploader(
            "Arraste múltiplos arquivos DXF aqui para carregar as geometrias automaticamente",
            type=["dxf"],
            accept_multiple_files=True,
            key="dxf_uploader"
        )
        
        if uploaded_files:
            if not EZDXF_DISPONIVEL:
                st.error("Biblioteca ezdxf não instalada. Execute: pip install ezdxf")
            else:
                novo_item_adicionado = False
                for dxf_file in uploaded_files:
                    if dxf_file.name not in st.session_state.processed_files:
                        # process DXF geometry with default speeds/peck
                        res = processar_dxf(dxf_file, 3528.0, 1.0)
                        if res:
                            st.session_state.itens.append({
                                'descricao': os.path.splitext(dxf_file.name)[0],
                                'qtd': 1,
                                'material': "Aço Carbono",
                                'espessura': 3.18,
                                'largura': round(res.get('largura_x', 100.0), 1),
                                'compr': round(res.get('altura_y', 100.0), 1),
                                'perimetro': round(res.get('perimetro', 400.0), 1),
                                'n_entradas': int(res.get('furos', 4)),
                                'preco_kg': 0.0, # Uses default
                                'dxf_bytes': dxf_file.getvalue(),
                                'tempos': {
                                    'corte_laser': 0.0, # uses formula
                                    'setup': 0.0,
                                    'dobra': 0.0,
                                    'caldeiraria': 0.0,
                                    'solda': 0.0,
                                    'guilhotina': 0.0,
                                    'usinagem_int': 0.0,
                                    'montagem': 0.0
                                },
                                'custos_extras': {
                                    'usin_ext': 0.0
                                }
                            })
                            st.session_state.processed_files.append(dxf_file.name)
                            st.success(f"✅ Arquivo '{dxf_file.name}' importado com sucesso!")
                            novo_item_adicionado = True
                # Trigger rerun ONLY if a new file was actually processed
                if novo_item_adicionado:
                    st.rerun()
                
    with actions_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Adicionar Peça Rápida (100x100)", use_container_width=True, key="quick_add_btn"):
            st.session_state.itens.append({
                'descricao': f"Peça Manual {len(st.session_state.itens)+1}",
                'qtd': 1,
                'material': "Aço Carbono",
                'espessura': 3.18,
                'largura': 100.0,
                'compr': 100.0,
                'perimetro': 400.0,
                'n_entradas': 4,
                'preco_kg': 0.0, # Uses default
                'dxf_bytes': None,
                'tempos': {
                    'corte_laser': 0.0,
                    'setup': 0.0,
                    'dobra': 0.0,
                    'caldeiraria': 0.0,
                    'solda': 0.0,
                    'guilhotina': 0.0,
                    'usinagem_int': 0.0,
                    'montagem': 0.0
                },
                'custos_extras': {
                    'usin_ext': 0.0
                }
            })
            st.rerun()
            
        if st.button("🗑️ Limpar Todos os Itens", use_container_width=True, key="clear_all_btn"):
            st.session_state.itens = []
            st.session_state.processed_files = []
            st.rerun()

with tab_manual:
    st.info("💡 **Preencha os dados essenciais abaixo.** Os tempos de corte serão calculados automaticamente baseado na espessura e perímetro informados.")
    with st.form("form_peca_manual", clear_on_submit=True):
        m_col1, m_col2, m_col3 = st.columns(3)
        with m_col1:
            m_desc = st.text_input("Descrição da Peça", value=f"Peça Manual {len(st.session_state.itens)+1}", key="m_desc")
            m_qtd = st.number_input("Quantidade", min_value=1, value=1, step=1, key="m_qtd")
            m_mat = st.selectbox("Material", ["Aço Carbono", "Aço Inox", "Alumínio"], key="m_mat")
        with m_col2:
            m_espe = st.number_input("Espessura (mm)", min_value=0.1, value=3.18, step=0.01, format="%.2f", key="m_espe")
            m_larg = st.number_input("Largura (mm)", min_value=0.1, value=100.0, step=1.0, format="%.1f", key="m_larg")
            m_compr = st.number_input("Comprimento (mm)", min_value=0.1, value=100.0, step=1.0, format="%.1f", key="m_compr")
        with m_col3:
            m_perim = st.number_input("Perímetro (mm) (0 = Auto)", min_value=0.0, value=0.0, step=10.0, format="%.1f", key="m_perim",
                                      help="Se deixado em 0.0, o perímetro será calculado automaticamente como 2 * (Largura + Comprimento) + perímetro dos furos.")
            m_entr = st.number_input("Entradas (Furos)", min_value=0, value=0, step=1, key="m_entr")
            m_pr_kg = st.number_input("Preço R$/kg (0 = Padrão)", min_value=0.0, value=0.0, step=0.5, format="%.2f", key="m_pr_kg",
                                      help="Se deixado em 0.0, será usado o preço padrão configurado na barra lateral.")
            
        st.markdown("**Tempos de Processo Unitários (Opcional - em minutos):**")
        t_col1, t_col2, t_col3, t_col4 = st.columns(4)
        with t_col1:
            m_setup = st.number_input("Setup (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_setup")
            m_dobra = st.number_input("Dobra (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_dobra")
        with t_col2:
            m_calde = st.number_input("Caldeiraria (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_calde")
            m_solda = st.number_input("Solda (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_solda")
        with t_col3:
            m_guil = st.number_input("Guilhotina (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_guil")
            m_usin = st.number_input("Usinagem (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_usin")
        with t_col4:
            m_mont = st.number_input("Montagem (min)", min_value=0.0, value=0.0, step=0.5, format="%.1f", key="m_mont")
            m_extra = st.number_input("Custo Extra Unitário (R$)", min_value=0.0, value=0.0, step=1.0, format="%.2f", key="m_extra")
            
        submitted = st.form_submit_button("➕ Adicionar Peça Manual ao Orçamento", use_container_width=True)
        if submitted:
            if m_perim == 0.0:
                m_perim = 2.0 * (m_larg + m_compr) + m_entr * 31.4
            
            st.session_state.itens.append({
                'descricao': m_desc,
                'qtd': m_qtd,
                'material': m_mat,
                'espessura': m_espe,
                'largura': m_larg,
                'compr': m_compr,
                'perimetro': round(m_perim, 1),
                'n_entradas': m_entr,
                'preco_kg': m_pr_kg,
                'dxf_bytes': None,
                'tempos': {
                    'corte_laser': 0.0,
                    'setup': m_setup,
                    'dobra': m_dobra,
                    'caldeiraria': m_calde,
                    'solda': m_solda,
                    'guilhotina': m_guil,
                    'usinagem_int': m_usin,
                    'montagem': m_mont
                },
                'custos_extras': {
                    'usin_ext': m_extra
                }
            })
            st.success(f"✅ Peça '{m_desc}' adicionada com sucesso!")
            st.rerun()

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# === MAIN WORKSPACE TABS ===
if st.session_state.itens:
    tab_editor, tab_resultados, tab_nesting = st.tabs([
        "📝 1. Editar Peças (Planilha)",
        "📊 2. Resultados de Custos e Impostos",
        "🧩 3. Arranjo de Chapas (Nesting)"
    ])
    
    # --- TAB 1: SPREADSHEET EDITOR ---
    with tab_editor:
        st.info("💡 **Dica:** Edite os valores diretamente na tabela abaixo. Você pode alterar a Quantidade, Material, Espessura, Preços e Tempos de Operação. A planilha e as fórmulas se recalculam de forma automática!")
        
        # Prepare input dataframe
        input_rows = []
        for it in st.session_state.itens:
            input_rows.append({
                'Descrição': it.get('descricao', ''),
                'Qtd': int(it.get('qtd', 1)),
                'Material': it.get('material', 'Aço Carbono'),
                'Espessura (mm)': float(it.get('espessura', 3.18)),
                'Largura (mm)': float(it.get('largura', 0.0)),
                'Comprimento (mm)': float(it.get('compr', 0.0)),
                'Perímetro (mm)': float(it.get('perimetro', 0.0)),
                'Entradas': int(it.get('n_entradas', 0)),
                'Preço R$/kg': float(it.get('preco_kg', 0.0)),
                'Setup (min)': float(it.get('tempos', {}).get('setup', 0.0)),
                'Dobra (min)': float(it.get('tempos', {}).get('dobra', 0.0)),
                'Caldeiraria (min)': float(it.get('tempos', {}).get('caldeiraria', 0.0)),
                'Solda (min)': float(it.get('tempos', {}).get('solda', 0.0)),
                'Guilhotina (min)': float(it.get('tempos', {}).get('guilhotina', 0.0)),
                'Usinagem (min)': float(it.get('tempos', {}).get('usinagem_int', 0.0)),
                'Montagem (min)': float(it.get('tempos', {}).get('montagem', 0.0)),
                'Custo Extra (R$)': float(it.get('custos_extras', {}).get('usin_ext', 0.0)),
                'Corte Override (min)': float(it.get('tempos', {}).get('corte_laser', 0.0)),
            })
            
        df_input = pd.DataFrame(input_rows)
        
        # Render the interactive grid
        edited_df = st.data_editor(
            df_input,
            use_container_width=True,
            column_config={
                "Material": st.column_config.SelectboxColumn("Material", options=["Aço Carbono", "Aço Inox", "Alumínio"], required=True),
                "Qtd": st.column_config.NumberColumn("Qtd", min_value=1, step=1, required=True),
                "Espessura (mm)": st.column_config.NumberColumn("Espessura (mm)", min_value=0.1, step=0.01, format="%.2f"),
                "Largura (mm)": st.column_config.NumberColumn("Largura (mm)", min_value=0.0, step=1.0),
                "Comprimento (mm)": st.column_config.NumberColumn("Comprimento (mm)", min_value=0.0, step=1.0),
                "Perímetro (mm)": st.column_config.NumberColumn("Perímetro (mm)", min_value=0.0, step=1.0),
                "Entradas": st.column_config.NumberColumn("Entradas", min_value=0, step=1),
                "Preço R$/kg": st.column_config.NumberColumn("Preço R$/kg (0=Default)", min_value=0.0, step=0.5, format="%.2f"),
                "Setup (min)": st.column_config.NumberColumn("Setup (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Dobra (min)": st.column_config.NumberColumn("Dobra (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Caldeiraria (min)": st.column_config.NumberColumn("Caldeiraria (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Solda (min)": st.column_config.NumberColumn("Solda (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Guilhotina (min)": st.column_config.NumberColumn("Guilhotina (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Usinagem (min)": st.column_config.NumberColumn("Usinagem (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Montagem (min)": st.column_config.NumberColumn("Montagem (min)", min_value=0.0, step=0.5, format="%.1f"),
                "Custo Extra (R$)": st.column_config.NumberColumn("Custo Extra (R$)", min_value=0.0, step=1.0, format="%.2f"),
                "Corte Override (min)": st.column_config.NumberColumn("Corte Override (min)", min_value=0.0, step=0.5, format="%.1f"),
            },
            num_rows="fixed", # row addition/deletion handled by buttons
            key="grid_itens_editor"
        )
        
        # Save back the grid edits to the session state
        updated_itens = []
        for idx, r in edited_df.iterrows():
            orig_item = st.session_state.itens[idx] if idx < len(st.session_state.itens) else {}
            updated_itens.append({
                'descricao': str(r['Descrição']),
                'qtd': int(r['Qtd']),
                'material': str(r['Material']),
                'espessura': float(r['Espessura (mm)']),
                'largura': float(r['Largura (mm)']),
                'compr': float(r['Comprimento (mm)']),
                'perimetro': float(r['Perímetro (mm)']),
                'n_entradas': int(r['Entradas']),
                'preco_kg': float(r['Preço R$/kg']),
                'dxf_bytes': orig_item.get('dxf_bytes', None),
                'tempos': {
                    'corte_laser': float(r['Corte Override (min)']),
                    'setup': float(r['Setup (min)']),
                    'dobra': float(r['Dobra (min)']),
                    'caldeiraria': float(r['Caldeiraria (min)']),
                    'solda': float(r['Solda (min)']),
                    'guilhotina': float(r['Guilhotina (min)']),
                    'usinagem_int': float(r['Usinagem (min)']),
                    'montagem': float(r['Montagem (min)'])
                },
                'custos_extras': {
                    'usin_ext': float(r['Custo Extra (R$)'])
                }
            })
        st.session_state.itens = updated_itens

        # Seção para remover peças individualmente
        st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
        st.markdown('<div class="section-title" style="font-size: 1.2rem;">🗑️ Remover Peças do Orçamento</div>', unsafe_allow_html=True)
        del_col1, del_col2 = st.columns([3, 1])
        with del_col1:
            items_to_del = st.multiselect(
                "Selecione as peças que deseja remover:",
                options=range(len(st.session_state.itens)),
                format_func=lambda idx: f"{idx+1}. {st.session_state.itens[idx]['descricao']} ({st.session_state.itens[idx]['qtd']} un - {st.session_state.itens[idx]['material']})",
                key="multiselect_delete_items"
            )
        with del_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Remover Selecionadas", use_container_width=True, disabled=not items_to_del, key="btn_delete_selected"):
                for idx in sorted(items_to_del, reverse=True):
                    desc = st.session_state.itens[idx]['descricao']
                    for f in list(st.session_state.processed_files):
                        if os.path.splitext(f)[0] == desc or f == desc:
                            st.session_state.processed_files.remove(f)
                    st.session_state.itens.pop(idx)
                st.success("✅ Peças removidas com sucesso!")
                st.rerun()

    # --- TAB 2: CALCULATED RESULTS & SUMMARIES ---
    with tab_resultados:
        tabela_resultados = []
        tot_peso = 0.0
        tot_mp = 0.0
        tot_fab = 0.0
        tot_basico = 0.0
        tot_nf = 0.0
        tot_comissao = 0.0
        
        tot_imp = {k: 0.0 for k in taxas_impostos}
        
        for i, item in enumerate(st.session_state.itens):
            calc = calcular_item_completo(item, config_global)
            item['calc'] = calc
            
            dim_str = f"{item['largura']:.1f} x {item['compr']:.1f}"
            tabela_resultados.append({
                '#': i+1,
                'Descrição': item['descricao'],
                'Qtd': item['qtd'],
                'Material': item['material'],
                'Esp.(mm)': item['espessura'],
                'Dimensões (mm)': dim_str,
                'Peso Un.(kg)': round(calc['peso_unit'], 3),
                'Peso Tot.(kg)': round(calc['peso_total'], 3),
                'Pçs/Chapa': calc['pcs_chapa'],
                'Qtd Chapas': calc['qtd_chapas'],
                'Sobra (pçs)': calc['sobra'],
                'Retalho (kg)': round(calc['retalho'], 3),
                'Tempo Corte (min)': calc['corte_laser_time'],
                'Custo MP (R$)': round(calc['custo_mp'], 2),
                'Total Fab (R$)': round(calc['total_fab'], 2),
                'Custo Básico (R$)': round(calc['custo_basico'], 2),
                'Venda s/Imp (R$)': round(calc['venda_sem_imp'], 2),
                'Preço c/Imp (R$)': round(calc['preco_com_imp'], 2),
                'NF Total (R$)': round(calc['valor_nf_total'], 2),
            })
            
            tot_peso += calc['peso_total']
            tot_mp += calc['custo_mp']
            tot_fab += calc['total_fab']
            tot_basico += calc['custo_basico']
            tot_nf += calc['valor_nf_total']
            tot_comissao += calc['comissao']
            
            for k in taxas_impostos:
                tot_imp[k] += calc['impostos'].get(k, 0.0)
                
        df_resultados = pd.DataFrame(tabela_resultados)
        
        # Display main computed table
        st.markdown('<div class="section-title">📊 Planilha de Custos Calculada</div>', unsafe_allow_html=True)
        st.dataframe(df_resultados, use_container_width=True, hide_index=True)
        
        # Display grand totals cards
        st.markdown('<div class="section-title">💰 Totais Gerais do Orçamento</div>', unsafe_allow_html=True)
        tot_tributos = sum(tot_imp.values())
        
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            card_resultado("Peso Total", f"{tot_peso:.2f} kg")
            card_resultado("Custo Mat. Prima", f"R$ {tot_mp:,.2f}", "result-card-blue")
        with r2:
            card_resultado("Total Fabricação", f"R$ {tot_fab:,.2f}")
            card_resultado("Custo Básico Geral", f"R$ {tot_basico:,.2f}")
        with r3:
            card_resultado("Impostos Totais (com IPI)", f"R$ {tot_tributos:,.2f}", "result-card-orange")
            card_resultado("Comissão Geral", f"R$ {tot_comissao:,.2f}")
        with r4:
            card_resultado("VALOR TOTAL NF", f"R$ {tot_nf:,.2f}", "result-card-green")
            if tot_peso > 0:
                card_resultado("R$/kg Final", f"R$ {tot_nf/tot_peso:,.2f}")
                
        # Detailed Expanders
        with st.expander("📊 Detalhamento dos Impostos do Lote"):
            imp_data = {'Imposto': [], 'Taxa (%)': [], 'Valor Total (R$)': []}
            for k, v in tot_imp.items():
                imp_data['Imposto'].append(k.upper())
                imp_data['Taxa (%)'].append(f"{taxas_impostos[k]*100:.2f}%")
                imp_data['Valor Total (R$)'].append(f"R$ {v:,.2f}")
            st.dataframe(pd.DataFrame(imp_data), use_container_width=True, hide_index=True)
            
        with st.expander("📋 Detalhamento Individual de Cada Peça"):
            for i, item in enumerate(st.session_state.itens):
                c = item['calc']
                st.markdown(f"**Item {i+1}: {item['descricao']}** ({item['qtd']} un. - {item['material']} e={item['espessura']}mm)")
                det = {
                    'Campo': ['Área', 'Peso Unit.', 'Peso Total', 'Peso Chapa', 'Pçs/Chapa', 'Qtd Chapas', 'Sobra', 'Retalho',
                              'Custo MP', 'Tempo Corte', 'Total Fab.', 'Custo Básico', 'Venda s/Imp', 'Preço c/Imp (s/IPI)', 'Valor NF Unit.', 'Comissão'],
                    'Valor': [f"{c['area']:.4f} m²", f"{c['peso_unit']:.3f} kg", f"{c['peso_total']:.3f} kg",
                              f"{c['peso_chapa']:.2f} kg", str(c['pcs_chapa']), str(c['qtd_chapas']),
                              str(c['sobra']), f"{c['retalho']:.3f} kg", f"R$ {c['custo_mp']:.2f}",
                              f"{c['corte_laser_time']} min", f"R$ {c['total_fab']:.2f}", f"R$ {c['custo_basico']:.2f}", f"R$ {c['venda_sem_imp']:.2f}",
                              f"R$ {c['preco_unit_com_imp']:.2f}", f"R$ {c['valor_nf']:.2f}", f"R$ {c['comissao']:.2f}"]
                }
                st.dataframe(pd.DataFrame(det), use_container_width=True, hide_index=True)
                st.markdown("---")
                
        # Export tools
        st.markdown('<div class="section-title">📥 Exportar Orçamento</div>', unsafe_allow_html=True)
        txt_rel = f"""{'='*60}
ORÇAMENTO INDUSTRIAL AUTOMATIZADO
{'='*60}
Projeto:      {nome_projeto}
Cliente:      {nome_cliente}
Orçamentista: {orcamentista}
Tipo Venda:   {tipo_venda}
Data/Hora:    {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*60}
ITENS DO ORÇAMENTO:
{df_resultados.to_string(index=False)}
{'='*60}
RESUMO DOS TOTAIS:
  Peso Total:         {tot_peso:.2f} kg
  Custo Mat. Prima:   R$ {tot_mp:,.2f}
  Total Fabricação:   R$ {tot_fab:,.2f}
  Custo Básico Geral: R$ {tot_basico:,.2f}
  Impostos Totais:    R$ {tot_tributos:,.2f}
  Comissão Geral:     R$ {tot_comissao:,.2f}
  VALOR TOTAL NF:     R$ {tot_nf:,.2f}
{'='*60}
"""
        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            st.download_button("📄 Baixar TXT", txt_rel, f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
        with ex2:
            try:
                buf = io.BytesIO()
                with pd.ExcelWriter(buf, engine='openpyxl') as w:
                    df_resultados.to_excel(w, sheet_name='Itens', index=False)
                    pd.DataFrame(imp_data).to_excel(w, sheet_name='Impostos', index=False)
                    pd.DataFrame({'Total': ['Peso Total','Custo MP','Total Fab','Custo Básico','Impostos','Comissão','VALOR NF'], 'Valor': [tot_peso, tot_mp, tot_fab, tot_basico, tot_tributos, tot_comissao, tot_nf]}).to_excel(w, sheet_name='Resumo', index=False)
                st.download_button("📊 Baixar Excel", buf.getvalue(), f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao gerar Excel: {e}")
        with ex3:
            try:
                from gerador_pdf import gerar_orcamento_pdf
                pdf_logo_bytes = None
                if os.path.exists("logo_customizado.bin"):
                    try:
                        with open("logo_customizado.bin", "rb") as f:
                            pdf_logo_bytes = f.read()
                    except:
                        pass
                if logo_uploaded is not None:
                    pdf_logo_bytes = logo_uploaded.getvalue()
                client_dict = {
                    'nome': nome_cliente,
                    'endereco': cliente_endereco,
                    'telefone': cliente_telefone,
                    'num_orcamento': nome_projeto,
                    'data_criacao': data_criacao_str,
                    'data_vencimento': data_vencimento_str
                }
                emissor_dict = {
                    'nome': emissor_nome,
                    'responsavel': emissor_resp,
                    'endereco': emissor_end,
                    'telefone': emissor_tel,
                    'celular': emissor_cel,
                    'email': emissor_email
                }
                prazos_dict = {
                    'prazo_entrega': cond_prazo,
                    'forma_pagamento': cond_pgto,
                    'pedido_minimo': cond_minimo,
                    'frete': cond_frete,
                    'impostos_descricao': cond_impostos,
                    'comentarios': cond_comentarios,
                    'condicoes_texto': [c1, c2, c3, c4, c5, c6, c7]
                }
                pdf_data = gerar_orcamento_pdf(st.session_state.itens, config_global, client_dict, emissor_dict, prazos_dict, pdf_logo_bytes)
                st.download_button("📄 Baixar PDF do Orçamento", pdf_data, f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
            except Exception as e:
                st.warning(f"Erro ao gerar PDF: {e}")
                import traceback
                traceback.print_exc()

    # --- TAB 3: NESTING SIMULATION ---
    with tab_nesting:
        st.markdown('<div class="section-title">🧩 Nesting de Chapas</div>', unsafe_allow_html=True)
        st.info("Selecione um item da lista abaixo para simular o aproveitamento de chapas padrão.")
        
        item_names = [f"{idx+1}. {it['descricao']}" for idx, it in enumerate(st.session_state.itens)]
        selected_idx_str = st.selectbox("Selecione a peça", item_names)
        
        if selected_idx_str:
            selected_idx = int(selected_idx_str.split(".")[0]) - 1
            item = st.session_state.itens[selected_idx]
            
            n_w = st.number_input("Largura Chapa Nesting (mm)", value=chapa_l_pad, step=100.0)
            n_c = st.number_input("Comprimento Chapa Nesting (mm)", value=chapa_c_pad, step=100.0)
            
            best, aprov, rw, rh = calcular_nesting_simples(
                item['largura'],
                item['compr'],
                n_w,
                n_c,
                5.0, # margem
                item['espessura'], # gap = thickness of part
                True, # rotacionar
                item['qtd']
            )
            
            if best:
                st.success(f"Nesting calculado! Aproveitamento: **{aprov:.1f}%** | Layout: **{best['desc']}** | Peças acomodadas: **{best['qtd']} / {item['qtd']}**")
                
                # Plot layout in Neobrutalist style
                fig, ax = plt.subplots(figsize=(10, 6), facecolor='#FFFDF5')
                ax.set_facecolor('#FFFDF5')
                
                # Plate outline (White fill with heavy Black border)
                ax.add_patch(patches.Rectangle((0, 0), n_w, n_c, edgecolor='#000000', facecolor='#ffffff', linewidth=3, label='Chapa'))
                
                # Nested parts in Yellow with thick Black borders
                for r in best['rects']:
                    ax.add_patch(patches.Rectangle(
                        (r['x'], r['y']), r['w'], r['h'], 
                        edgecolor='#000000', facecolor='#FFD93D', alpha=1.0, linewidth=2
                    ))
                    
                ax.set_xlim(-100, n_w + 100)
                ax.set_ylim(-100, n_c + 100)
                ax.set_aspect('equal')
                
                # Style ticks and labels to look clean and high-contrast
                ax.tick_params(colors='#000000')
                ax.xaxis.label.set_color('#000000')
                ax.yaxis.label.set_color('#000000')
                for spine in ax.spines.values():
                    spine.set_color('#000000')
                    spine.set_linewidth(2.5)
                    
                st.pyplot(fig)
            else:
                st.error("Não foi possível realizar o nesting (peça maior que a chapa ou quantidade zero).")

else:
    st.info("Nenhum item adicionado ainda. Faça upload de arquivos DXF ou adicione uma peça manual acima para iniciar o orçamento.")

st.markdown('<div style="text-align:center; padding: 2rem 0 1rem; opacity: 0.5; font-size: 0.8rem;">🏭 Orçamento Industrial Unificado v3.0 — Excelência em Paridade Industrial</div>', unsafe_allow_html=True)
