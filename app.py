import streamlit as st
import math
import pandas as pd
from datetime import datetime
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
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f: return json.load(f)
        except: return {}
    return {}
def save_config(params):
    config = load_config(); config.update(params)
    try:
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f: json.dump(config, f, indent=4)
    except: pass
def save_s(key):
    if key in st.session_state: save_config({key: st.session_state[key]})
cfg = load_config()

def card_resultado(label, valor, classe=""):
    st.markdown(f'<div class="result-card {classe}"><div class="label">{label}</div><div class="value">{valor}</div></div>', unsafe_allow_html=True)

if 'itens' not in st.session_state: st.session_state.itens = []
if 'dxf_resultado' not in st.session_state: st.session_state.dxf_resultado = None

st.markdown('<div class="main-header"><h1>🏭 Orçamento Industrial Unificado</h1><p>Planilha de Custo • Corte Laser • Dobra • Caldeiraria • Solda • Usinagem</p></div>', unsafe_allow_html=True)

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
    with st.expander("🛠️ Tarifas Hora-Máquina (R$/h)", expanded=False):
        tar_corte = st.number_input("Corte Laser", value=float(cfg.get("tar_corte", 370.0)), step=10.0, key="tar_corte", on_change=save_s, args=("tar_corte",))
        tar_setup = st.number_input("SET-UP", value=float(cfg.get("tar_setup", 120.0)), step=10.0, key="tar_setup", on_change=save_s, args=("tar_setup",))
        tar_dobra = st.number_input("Dobra", value=float(cfg.get("tar_dobra", 190.0)), step=10.0, key="tar_dobra", on_change=save_s, args=("tar_dobra",))
        tar_caldeiraria = st.number_input("Caldeiraria", value=float(cfg.get("tar_cald", 150.0)), step=10.0, key="tar_cald", on_change=save_s, args=("tar_cald",))
        tar_solda = st.number_input("Solda", value=float(cfg.get("tar_solda", 120.0)), step=10.0, key="tar_solda", on_change=save_s, args=("tar_solda",))
        tar_guilhotina = st.number_input("Guilhotina", value=float(cfg.get("tar_guil", 100.0)), step=10.0, key="tar_guil", on_change=save_s, args=("tar_guil",))
        tar_usinagem = st.number_input("Usinagem Interna", value=float(cfg.get("tar_usin", 120.0)), step=10.0, key="tar_usin", on_change=save_s, args=("tar_usin",))
        tar_montagem = st.number_input("Montagem", value=float(cfg.get("tar_mont", 100.0)), step=10.0, key="tar_mont", on_change=save_s, args=("tar_mont",))
    with st.expander("⚙️ Material e Chapa", expanded=False):
        densidade = st.number_input("Densidade (kg/m³)", value=float(cfg.get("dens", 7860.0)), step=10.0, key="dens", on_change=save_s, args=("dens",))
        gap_pecas = st.number_input("Gap entre peças (mm)", value=float(cfg.get("gap", 5.0)), step=1.0, key="gap", on_change=save_s, args=("gap",))
        chapa_l_pad = st.number_input("Chapa Largura padrão (mm)", value=float(cfg.get("ch_l", 1200.0)), step=100.0, key="ch_l", on_change=save_s, args=("ch_l",))
        chapa_c_pad = st.number_input("Chapa Comprimento padrão (mm)", value=float(cfg.get("ch_c", 2400.0)), step=100.0, key="ch_c", on_change=save_s, args=("ch_c",))
        preco_aco = st.number_input("Preço Aço Carbono (R$/kg)", value=float(cfg.get("p_aco", 8.50)), step=0.5, format="%.2f", key="p_aco", on_change=save_s, args=("p_aco",))
        preco_inox = st.number_input("Preço Inox (R$/kg)", value=float(cfg.get("p_inox", 32.0)), step=1.0, format="%.2f", key="p_inox", on_change=save_s, args=("p_inox",))
        preco_alum = st.number_input("Preço Alumínio (R$/kg)", value=float(cfg.get("p_alum", 25.0)), step=1.0, format="%.2f", key="p_alum", on_change=save_s, args=("p_alum",))

taxas_impostos = {'icms': tx_icms, 'ipi': tx_ipi, 'pis': tx_pis, 'cofins': tx_cofins, 'csll': tx_csll, 'irpj': tx_irpj}
tarifas = {'corte_laser': tar_corte, 'setup': tar_setup, 'dobra': tar_dobra, 'caldeiraria': tar_caldeiraria, 'solda': tar_solda, 'guilhotina': tar_guilhotina, 'usinagem_int': tar_usinagem, 'montagem': tar_montagem}
config_global = {'densidade': densidade, 'gap': gap_pecas, 'margem_lucro': margem_lucro, 'taxa_comissao': taxa_comissao, 'taxas_impostos': taxas_impostos, 'tarifas': tarifas}
precos_material = {'Aço Carbono': preco_aco, 'Aço Inox': preco_inox, 'Alumínio': preco_alum}

# === DADOS DO PROJETO ===
st.markdown('<div class="section-title">📋 Dados do Projeto</div>', unsafe_allow_html=True)
pc1, pc2, pc3, pc4 = st.columns([2, 2, 1, 1])
with pc1: nome_projeto = st.text_input("Projeto / Orçamento Nº", "Orçamento 001", key="nome_proj")
with pc2: nome_cliente = st.text_input("Cliente", "", key="nome_cli")
with pc3: orcamentista = st.text_input("Orçamentista", "", key="orcam")
with pc4: tipo_venda = st.selectbox("Tipo de Venda", ["Revenda", "Venda Direta", "Industrialização"], key="tipo_venda")
st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

tabela_3kw = {
    "Aço Carbono": {1.0:(12000,0.2),1.2:(10000,0.2),1.5:(8000,0.3),2.0:(6000,0.3),3.0:(4500,0.4),3.18:(3528,0.4),4.75:(3000,0.6),6.35:(2500,0.8),8.0:(1800,1.0),9.5:(1300,1.2),12.7:(900,1.5),16.0:(700,2.0),19.05:(500,3.0),22.2:(400,4.0),25.4:(300,5.0)},
    "Aço Inox": {1.0:(15000,0.2),1.2:(12000,0.2),1.5:(9000,0.3),2.0:(7000,0.4),3.0:(4000,0.5),4.75:(2000,0.8),6.35:(1200,1.2),8.0:(800,1.5),9.5:(500,2.0),12.7:(300,3.0),16.0:(150,4.0)}
}

# === ADICIONAR ITEM ===
st.markdown('<div class="section-title">➕ Adicionar Item ao Orçamento</div>', unsafe_allow_html=True)
with st.expander("📝 Formulário de Novo Item", expanded=True):
    g1, g2, g3, g4 = st.columns([2, 1, 1, 1])
    with g1: descricao = st.text_input("Descrição", "Peça 01", key="f_desc")
    with g2: qtd = st.number_input("Quantidade", min_value=1, value=1, key="f_qtd")
    with g3: material = st.selectbox("Material", ["Aço Carbono", "Aço Inox", "Alumínio"], key="f_mat")
    with g4: tipo_mat = st.text_input("Tipo / Liga", "S 1020", key="f_tipo")

    d1, d2, d3, d4, d5 = st.columns(5)
    with d1: espessura = st.number_input("Espessura (mm)", value=3.18, step=0.1, format="%.2f", key="f_esp")
    with d2: largura = st.number_input("Largura (mm)", value=122.0, step=1.0, key="f_larg")
    with d3: comprimento = st.number_input("Comprimento (mm)", value=111.0, step=1.0, key="f_comp")
    with d4: perimetro = st.number_input("Perímetro de corte (mm)", value=0.0, step=1.0, key="f_perim")
    with d5: n_entradas = st.number_input("Nº Entradas", value=0, step=1, key="f_entr")

    c1, c2, c3, c4 = st.columns(4)
    with c1: f_chapa_l = st.number_input("Chapa L (mm)", value=chapa_l_pad, step=100.0, key="f_ch_l")
    with c2: f_chapa_c = st.number_input("Chapa C (mm)", value=chapa_c_pad, step=100.0, key="f_ch_c")
    vel_default, furo_default = tabela_3kw.get(material, {}).get(espessura, (2000, 1.0))
    with c3: vel_corte = st.number_input("Vel. Corte (mm/min)", value=float(vel_default), step=100.0, key="f_vel")
    with c4:
        preco_kg = precos_material.get(material, preco_aco)
        preco_kg_item = st.number_input("R$/kg", value=preco_kg, step=0.5, format="%.2f", key="f_pkg")

    st.markdown("###### ⏱️ Tempos de Operação (minutos)")
    t1, t2, t3, t4, t5, t6, t7, t8 = st.columns(8)
    with t1: tempo_corte = st.number_input("Corte", value=0.0, step=0.5, key="f_t_corte", format="%.1f")
    with t2: tempo_setup = st.number_input("SET-UP", value=6.0, step=1.0, key="f_t_setup", format="%.1f")
    with t3: tempo_dobra = st.number_input("Dobra", value=0.0, step=1.0, key="f_t_dobra", format="%.1f")
    with t4: tempo_cald = st.number_input("Caldeirar.", value=0.0, step=1.0, key="f_t_cald", format="%.1f")
    with t5: tempo_solda = st.number_input("Solda", value=0.0, step=1.0, key="f_t_solda", format="%.1f")
    with t6: tempo_guil = st.number_input("Guilhot.", value=0.0, step=1.0, key="f_t_guil", format="%.1f")
    with t7: tempo_usin = st.number_input("Usinagem", value=0.0, step=1.0, key="f_t_usin", format="%.1f")
    with t8: tempo_mont = st.number_input("Montagem", value=0.0, step=1.0, key="f_t_mont", format="%.1f")

    st.markdown("###### 💲 Custos Extras (R$)")
    e1, e2, e3, e4 = st.columns(4)
    with e1: custo_usin_ext = st.number_input("Usin. Externa", value=0.0, step=10.0, key="f_usin_ext")
    with e2: custo_trat = st.number_input("Trat. Térmico", value=0.0, step=10.0, key="f_trat")
    with e3: custo_emb = st.number_input("Embalagem", value=0.0, step=5.0, key="f_emb")
    with e4: custo_transp = st.number_input("Transporte", value=0.0, step=10.0, key="f_transp")

    item_preview = {
        'qtd': qtd, 'largura': largura, 'compr': comprimento, 'espessura': espessura,
        'chapa_l': f_chapa_l, 'chapa_c': f_chapa_c, 'preco_kg': preco_kg_item,
        'tempos': {'corte_laser': tempo_corte, 'setup': tempo_setup, 'dobra': tempo_dobra,
                   'caldeiraria': tempo_cald, 'solda': tempo_solda, 'guilhotina': tempo_guil,
                   'usinagem_int': tempo_usin, 'montagem': tempo_mont},
        'custos_extras': {'usin_ext': custo_usin_ext, 'trat_termico': custo_trat, 'embalagem': custo_emb, 'transporte': custo_transp}
    }
    calc = calcular_item_completo(item_preview, config_global)
    info_html = f'''
    <div class="info-box">
        📐 Área: <b>{calc['area']:.4f} m²</b> |
        ⚖️ Peso Unit: <b>{calc['peso_unit']:.3f} kg</b> |
        📦 Peso Total: <b>{calc['peso_total']:.3f} kg</b> |
        🏭 Pçs/Chapa: <b>{calc['pcs_chapa']}</b> |
        💰 Custo Básico: <b>R$ {calc['custo_basico']:.2f}</b> |
        🏷️ Preço c/ Imp: <b>R$ {calc['preco_com_imp']:.2f}</b> |
        📄 Valor NF: <b>R$ {calc['valor_nf']:.2f}</b>
    </div>
    '''
    st.markdown(info_html, unsafe_allow_html=True)

    if st.button("✅ ADICIONAR ITEM AO ORÇAMENTO", type="primary", key="btn_add_item"):
        novo_item = {
            'descricao': descricao, 'qtd': qtd, 'material': material, 'tipo': tipo_mat,
            'espessura': espessura, 'largura': largura, 'compr': comprimento,
            'perimetro': perimetro, 'n_entradas': n_entradas,
            'vel_corte': vel_corte, 'chapa_l': f_chapa_l, 'chapa_c': f_chapa_c,
            'preco_kg': preco_kg_item,
            'tempos': dict(item_preview['tempos']),
            'custos_extras': dict(item_preview['custos_extras']),
            'calc': calc
        }
        st.session_state.itens.append(novo_item)
        st.success(f"✅ '{descricao}' adicionado! ({qtd} un. → NF: R$ {calc['valor_nf_total']:.2f})")
        st.rerun()

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# === DXF ===
st.markdown('<div class="section-title">📐 Importar DXF</div>', unsafe_allow_html=True)
with st.expander("Upload de arquivo DXF", expanded=False):
    arquivo_dxf = st.file_uploader("Carregue um .dxf", type=["dxf"], key="dxf_up")
    if arquivo_dxf:
        mat_dxf = st.selectbox("Material", ["Aço Carbono", "Aço Inox"], key="mat_dxf")
        esp_dxf = st.selectbox("Espessura (mm)", list(tabela_3kw.get(mat_dxf, {}).keys()), key="esp_dxf")
        vp, fp = tabela_3kw.get(mat_dxf, {}).get(esp_dxf, (2000, 1.0))
        if st.button("⚡ Processar DXF", type="primary"):
            res = processar_dxf(arquivo_dxf, vp, fp)
            if res:
                st.session_state.dxf_resultado = res
                st.success(f"DXF processado! Perímetro: {res['perimetro']:.1f}mm | Tempo: {res['tempo_total_min']:.2f}min")
    if st.session_state.dxf_resultado:
        res = st.session_state.dxf_resultado
        st.info(f"📐 Perímetro: {res['perimetro']:.1f}mm | Larg: {res.get('largura_x',0):.1f}mm | Alt: {res.get('altura_y',0):.1f}mm | Tempo: {res['tempo_total_min']:.2f}min")

st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

# === TABELA DE ITENS ===
st.markdown('<div class="section-title">📋 Itens do Orçamento</div>', unsafe_allow_html=True)

if st.session_state.itens:
    for i, item in enumerate(st.session_state.itens):
        item_data = {
            'qtd': item['qtd'], 'largura': item['largura'], 'compr': item['compr'],
            'espessura': item['espessura'], 'chapa_l': item['chapa_l'], 'chapa_c': item['chapa_c'],
            'preco_kg': item['preco_kg'], 'tempos': item['tempos'], 'custos_extras': item['custos_extras']
        }
        item['calc'] = calcular_item_completo(item_data, config_global)

    tabela = []
    for i, item in enumerate(st.session_state.itens):
        c = item['calc']
        tabela.append({
            '#': i+1, 'Descrição': item['descricao'], 'Qtd': item['qtd'],
            'Material': item['material'], 'Esp.(mm)': item['espessura'],
            'Larg.(mm)': item['largura'], 'Comp.(mm)': item['compr'],
            'Peso Un.(kg)': round(c['peso_unit'], 3), 'Peso Tot.(kg)': round(c['peso_total'], 3),
            'Pçs/Chapa': c['pcs_chapa'], 'Custo MP': round(c['custo_mp'], 2),
            'Total Fab.': round(c['total_fab'], 2), 'Custo Básico': round(c['custo_basico'], 2),
            'Venda s/Imp': round(c['venda_sem_imp'], 2), 'Preço c/Imp': round(c['preco_com_imp'], 2),
            'Valor NF': round(c['valor_nf'], 2), 'NF Total': round(c['valor_nf_total'], 2),
        })
    df = pd.DataFrame(tabela)
    st.dataframe(df, use_container_width=True, hide_index=True)

    ac1, ac2, ac3 = st.columns([1, 1, 2])
    with ac1: del_idx = st.number_input("Item p/ remover", min_value=1, max_value=len(st.session_state.itens), value=1, key="del_idx")
    with ac2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Remover Item", key="btn_del"):
            st.session_state.itens.pop(del_idx - 1); st.rerun()
    with ac3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🗑️ Limpar Todos", key="btn_clear"):
            st.session_state.itens = []; st.rerun()

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # === RESUMO ===
    st.markdown('<div class="section-title">💰 Resumo do Orçamento</div>', unsafe_allow_html=True)
    tot_peso = sum(it['calc']['peso_total'] for it in st.session_state.itens)
    tot_mp = sum(it['calc']['custo_mp'] for it in st.session_state.itens)
    tot_fab = sum(it['calc']['total_fab'] for it in st.session_state.itens)
    tot_basico = sum(it['calc']['custo_basico'] for it in st.session_state.itens)
    tot_nf = sum(it['calc']['valor_nf_total'] for it in st.session_state.itens)
    tot_comissao = sum(it['calc']['comissao'] for it in st.session_state.itens)
    tot_imp = {k: sum(it['calc']['impostos'].get(k, 0) * it['qtd'] for it in st.session_state.itens) for k in taxas_impostos}
    tot_tributos = sum(tot_imp.values())

    r1, r2, r3, r4 = st.columns(4)
    with r1:
        card_resultado("Peso Total", f"{tot_peso:.2f} kg")
        card_resultado("Custo Mat. Prima", f"R$ {tot_mp:,.2f}", "result-card-blue")
    with r2:
        card_resultado("Total Fabricação", f"R$ {tot_fab:,.2f}")
        card_resultado("Custo Básico", f"R$ {tot_basico:,.2f}")
    with r3:
        card_resultado("Impostos Totais", f"R$ {tot_tributos:,.2f}", "result-card-orange")
        card_resultado("Comissão", f"R$ {tot_comissao:,.2f}")
    with r4:
        card_resultado("VALOR TOTAL NF", f"R$ {tot_nf:,.2f}", "result-card-green")
        if tot_peso > 0: card_resultado("R$/kg Final", f"R$ {tot_nf/tot_peso:,.2f}")

    with st.expander("📊 Detalhamento de Impostos"):
        imp_data = {'Imposto': [], 'Taxa': [], 'Valor Total (R$)': []}
        for k, v in tot_imp.items():
            imp_data['Imposto'].append(k.upper())
            imp_data['Taxa'].append(f"{taxas_impostos[k]*100:.2f}%")
            imp_data['Valor Total (R$)'].append(f"R$ {v:,.2f}")
        st.dataframe(pd.DataFrame(imp_data), use_container_width=True, hide_index=True)

    with st.expander("📋 Detalhamento por Item"):
        for i, item in enumerate(st.session_state.itens):
            c = item['calc']
            st.markdown(f"**Item {i+1}: {item['descricao']}** ({item['qtd']} un. - {item['material']} {item['tipo']})")
            det = {
                'Campo': ['Área', 'Peso Unit.', 'Peso Total', 'Peso Chapa', 'Pçs/Chapa', 'Qtd Chapas', 'Sobra', 'Retalho',
                          'Custo MP', 'Total Fab.', 'Custo Básico', 'Venda s/Imp', 'Preço c/Imp', 'Valor NF', 'Comissão'],
                'Valor': [f"{c['area']:.4f} m²", f"{c['peso_unit']:.3f} kg", f"{c['peso_total']:.3f} kg",
                          f"{c['peso_chapa']:.2f} kg", str(c['pcs_chapa']), str(c['qtd_chapas']),
                          str(c['sobra']), f"{c['retalho']:.3f} kg", f"R$ {c['custo_mp']:.2f}",
                          f"R$ {c['total_fab']:.2f}", f"R$ {c['custo_basico']:.2f}", f"R$ {c['venda_sem_imp']:.2f}",
                          f"R$ {c['preco_com_imp']:.2f}", f"R$ {c['valor_nf']:.2f}", f"R$ {c['comissao']:.4f}"]
            }
            st.dataframe(pd.DataFrame(det), use_container_width=True, hide_index=True)
            st.markdown("---")

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    # === EXPORTAÇÃO ===
    st.markdown('<div class="section-title">📥 Exportar Orçamento</div>', unsafe_allow_html=True)
    txt_rel = f"""{'='*60}
    ORÇAMENTO INDUSTRIAL UNIFICADO
{'='*60}
Projeto:  {nome_projeto}
Cliente:  {nome_cliente}
Orçamentista: {orcamentista}
Tipo Venda: {tipo_venda}
Data:     {datetime.now().strftime('%d/%m/%Y %H:%M')}
{'='*60}
ITENS:
{df.to_string(index=False)}
{'='*60}
RESUMO:
  Peso Total:         {tot_peso:.2f} kg
  Custo Mat. Prima:    R$ {tot_mp:,.2f}
  Total Fabricação:    R$ {tot_fab:,.2f}
  Custo Básico:        R$ {tot_basico:,.2f}
  Impostos Totais:     R$ {tot_tributos:,.2f}
  Comissão:            R$ {tot_comissao:,.2f}
  VALOR TOTAL NF:      R$ {tot_nf:,.2f}
{'='*60}
"""
    ex1, ex2 = st.columns(2)
    with ex1:
        st.download_button("📄 Baixar TXT", txt_rel, f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.txt", mime="text/plain", use_container_width=True)
    with ex2:
        try:
            buf = io.BytesIO()
            with pd.ExcelWriter(buf, engine='openpyxl') as w:
                df.to_excel(w, sheet_name='Itens', index=False)
                pd.DataFrame(imp_data).to_excel(w, sheet_name='Impostos', index=False)
                pd.DataFrame({'Item': ['Peso Total','Custo MP','Total Fab','Custo Básico','Impostos','Comissão','VALOR NF'], 'Valor': [tot_peso, tot_mp, tot_fab, tot_basico, tot_tributos, tot_comissao, tot_nf]}).to_excel(w, sheet_name='Resumo', index=False)
            st.download_button("📊 Baixar Excel", buf.getvalue(), f"Orcamento_{nome_projeto}_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        except Exception as e:
            st.warning(f"Erro Excel: {e}")

else:
    st.info("Nenhum item adicionado. Use o formulário acima para começar.")

st.markdown('<div style="text-align:center; padding: 2rem 0 1rem; opacity: 0.5; font-size: 0.8rem;">🏭 Orçamento Industrial Unificado v2.0 — Planilha + Software de Corte</div>', unsafe_allow_html=True)
