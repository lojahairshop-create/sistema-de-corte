"""
Módulo de Cálculos — Fórmulas da Planilha de Custo Industrial
Todas as fórmulas foram reverse-engineered da planilha original.
"""
import math

DENSIDADE_PADRAO = 7860  # kg/m³ (confirmado da planilha)
GAP_PADRAO = 5  # mm entre peças
MARGEM_AREA = 10  # mm cada lado para cálculo de área


def calcular_area_peca(largura_mm, compr_mm):
    """Área com margem de 10mm cada lado (m²). Fórmula da planilha col 13."""
    return ((largura_mm + 2 * MARGEM_AREA) / 1000) * ((compr_mm + 2 * MARGEM_AREA) / 1000)


def calcular_peso_unitario(largura_mm, compr_mm, espessura_mm, densidade=DENSIDADE_PADRAO):
    """Peso unitário da peça pura (kg). Fórmula da planilha col 14."""
    return largura_mm * compr_mm * espessura_mm * densidade / 1e9


def calcular_peso_total(largura_mm, compr_mm, espessura_mm, qtd, gap=GAP_PADRAO, densidade=DENSIDADE_PADRAO):
    """Peso total incluindo gap (kg). Fórmula da planilha col 18."""
    return (largura_mm + gap) * (compr_mm + gap) * espessura_mm * densidade / 1e9 * qtd


def calcular_peso_chapa(chapa_l_mm, chapa_c_mm, espessura_mm, densidade=DENSIDADE_PADRAO):
    """Peso da chapa inteira (kg). Fórmula da planilha col 19."""
    return chapa_l_mm * chapa_c_mm * espessura_mm * densidade / 1e9


def calcular_pecas_por_chapa(largura_mm, compr_mm, chapa_l_mm, chapa_c_mm, gap=GAP_PADRAO):
    """Peças por chapa (arranjo retangular). Fórmula da planilha col 20."""
    arranjo1 = int(chapa_l_mm / (largura_mm + gap)) * int(chapa_c_mm / (compr_mm + gap))
    arranjo2 = int(chapa_l_mm / (compr_mm + gap)) * int(chapa_c_mm / (largura_mm + gap))
    return max(arranjo1, arranjo2)


def calcular_qtd_chapas(qtd_pecas, pecas_por_chapa):
    """Quantidade de chapas necessárias. Fórmula da planilha col 21."""
    if pecas_por_chapa <= 0:
        return 0
    return math.ceil(qtd_pecas / pecas_por_chapa)


def calcular_sobra_chapa(qtd_pecas, pecas_por_chapa, qtd_chapas):
    """Sobra de peças na chapa. Fórmula da planilha col 22."""
    return pecas_por_chapa * qtd_chapas - qtd_pecas


def calcular_retalho_kg(sobra, peso_unitario):
    """Retalho em kg. Fórmula da planilha col 23."""
    return sobra * peso_unitario


def calcular_custo_mp(peso_total, preco_kg):
    """Custo matéria prima. Fórmula da planilha col 25."""
    return peso_total * preco_kg


def calcular_total_fabricacao(tempos, tarifas):
    """
    Total de fabricação em R$.
    tempos: dict com chaves 'corte_laser', 'setup', 'dobra', 'caldeiraria', 
            'solda', 'guilhotina', 'usinagem_int', 'montagem' (em minutos)
    tarifas: dict com as mesmas chaves (R$/hora)
    """
    total = 0.0
    for op in tempos:
        t_min = tempos.get(op, 0) or 0
        tarifa_h = tarifas.get(op, 0) or 0
        total += (t_min / 60.0) * tarifa_h
    return total


def calcular_custo_basico(custo_mp, total_fabricacao, custos_extras=None):
    """Custo básico total (col 45) = Custo MP + Total Fabricação + extras."""
    extras = 0.0
    if custos_extras:
        extras = sum(v for v in custos_extras.values() if v)
    return custo_mp + total_fabricacao + extras


def calcular_fator_impostos(icms, pis, cofins, csll, irpj):
    """Fator de cálculo de impostos (SEM IPI). Fórmula da planilha."""
    total_cascata = icms + pis + cofins + csll + irpj
    return 1 - total_cascata


def calcular_preco_venda(custo_basico, margem_lucro, fator_impostos):
    """
    Preço de venda com impostos (sem IPI).
    venda_sem_imp = custo_basico * (1 + margem)
    preco = venda_sem_imp / fator
    """
    venda_sem_imp = custo_basico * (1 + margem_lucro)
    if fator_impostos <= 0.05:
        fator_impostos = 0.05
    preco_com_imp = venda_sem_imp / fator_impostos
    return venda_sem_imp, preco_com_imp


def calcular_impostos_detalhados(preco_com_imp, taxas):
    """
    Calcula cada imposto individualmente.
    taxas: dict com 'icms', 'ipi', 'pis', 'cofins', 'csll', 'irpj'
    Retorna dict com valores em R$.
    """
    result = {}
    for nome, taxa in taxas.items():
        result[nome] = preco_com_imp * taxa
    return result


def calcular_valor_nf(preco_com_imp, valor_ipi):
    """Valor total da NF = Preço + IPI (IPI somado por fora)."""
    return preco_com_imp + valor_ipi


def calcular_comissao(venda_sem_imp, taxa_comissao):
    """Comissão = Venda sem impostos × taxa."""
    return venda_sem_imp * taxa_comissao


def calcular_item_completo(item_data, config):
    """
    Calcula TODOS os campos de um item, replicando a planilha inteira.
    
    item_data: dict com campos de entrada do item
    config: dict com configurações globais (impostos, tarifas, etc.)
    
    Retorna: dict com todos os campos calculados
    """
    # Extrair dados do item
    qtd = item_data.get('qtd', 1) or 1
    largura = item_data.get('largura', 0) or 0
    compr = item_data.get('compr', 0) or 0
    espessura = item_data.get('espessura', 0) or 0
    chapa_l = item_data.get('chapa_l', 1200) or 1200
    chapa_c = item_data.get('chapa_c', 2400) or 2400
    preco_kg = item_data.get('preco_kg', 0) or 0
    densidade = config.get('densidade', DENSIDADE_PADRAO)
    gap = config.get('gap', GAP_PADRAO)
    
    # Cálculos geométricos
    area = calcular_area_peca(largura, compr) if largura > 0 and compr > 0 else 0
    peso_unit = calcular_peso_unitario(largura, compr, espessura, densidade) if largura > 0 else 0
    peso_total = calcular_peso_total(largura, compr, espessura, qtd, gap, densidade) if largura > 0 else 0
    peso_chapa = calcular_peso_chapa(chapa_l, chapa_c, espessura, densidade) if espessura > 0 else 0
    
    pcs_chapa = calcular_pecas_por_chapa(largura, compr, chapa_l, chapa_c, gap) if largura > 0 and compr > 0 else 0
    qtd_chapas = calcular_qtd_chapas(qtd, pcs_chapa)
    sobra = calcular_sobra_chapa(qtd, pcs_chapa, qtd_chapas) if pcs_chapa > 0 else 0
    retalho = calcular_retalho_kg(sobra, peso_unit)
    
    # Custos
    custo_mp = calcular_custo_mp(peso_total, preco_kg)
    
    tempos = item_data.get('tempos', {})
    tarifas = config.get('tarifas', {})
    total_fab = calcular_total_fabricacao(tempos, tarifas)
    
    custos_extras = item_data.get('custos_extras', {})
    custo_basico = calcular_custo_basico(custo_mp, total_fab, custos_extras)
    
    # Preço de venda
    margem = config.get('margem_lucro', 0.30)
    taxas_imp = config.get('taxas_impostos', {})
    fator = calcular_fator_impostos(
        taxas_imp.get('icms', 0.18), taxas_imp.get('pis', 0.0065),
        taxas_imp.get('cofins', 0.03), taxas_imp.get('csll', 0.0108),
        taxas_imp.get('irpj', 0.012)
    )
    
    venda_sem_imp, preco_com_imp = calcular_preco_venda(custo_basico, margem, fator)
    preco_total = preco_com_imp * qtd
    
    impostos = calcular_impostos_detalhados(preco_com_imp, taxas_imp)
    valor_nf = calcular_valor_nf(preco_com_imp, impostos.get('ipi', 0))
    valor_nf_total = valor_nf * qtd
    
    taxa_comissao = config.get('taxa_comissao', 0.03)
    comissao = calcular_comissao(venda_sem_imp, taxa_comissao)
    
    total_tributos = sum(v for k, v in impostos.items() if k != 'csll' and k != 'irpj')
    
    return {
        'area': area,
        'peso_unit': peso_unit,
        'peso_total': peso_total,
        'peso_chapa': peso_chapa,
        'pcs_chapa': pcs_chapa,
        'qtd_chapas': qtd_chapas,
        'sobra': sobra,
        'retalho': retalho,
        'custo_mp': custo_mp,
        'total_fab': total_fab,
        'custo_basico': custo_basico,
        'venda_sem_imp': venda_sem_imp,
        'preco_com_imp': preco_com_imp,
        'preco_total': preco_total,
        'impostos': impostos,
        'total_tributos': total_tributos,
        'valor_nf': valor_nf,
        'valor_nf_total': valor_nf_total,
        'comissao': comissao,
        'fator_impostos': fator,
    }
