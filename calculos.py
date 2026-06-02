"""
Módulo de Cálculos — Fórmulas da Planilha de Custo Industrial
Todas as fórmulas foram reverse-engineered da planilha original.
"""
import math

# Lookup tables for cutting speed (velocidade) and peck (tempo de furo)
# Format: thickness_mm -> (speed_mm_min, peck_seconds)
TABELA_INOX = {
    1.0: (7800.0, 1.0),
    1.5: (6300.0, 1.1),
    2.0: (5300.0, 1.1),
    2.5: (4500.0, 1.2),
    3.0: (3800.0, 1.2),
    3.18: (3528.0, 1.3),
    4.0: (2450.0, 1.4),
    4.75: (2000.0, 1.5),
    5.0: (1600.0, 1.8),
    6.35: (1200.0, 2.0),
    8.0: (500.0, 2.5),
    10.0: (350.0, 3.0),
    12.7: (225.0, 4.0),
    15.87: (0.0, 0.0),
    19.0: (0.0, 0.0)
}

TABELA_ACO_CARBONO = {
    1.0: (6500.0, 1.0),
    1.5: (5800.0, 1.0),
    2.0: (4900.0, 1.0),
    2.5: (3724.0, 1.0),
    3.0: (3600.0, 1.0),
    3.18: (3528.0, 1.0),
    4.0: (2646.0, 1.0),
    4.75: (2352.0, 1.5),
    6.35: (2058.0, 2.0),
    8.0: (1666.0, 2.5),
    10.0: (1200.0, 3.0),
    12.7: (1078.0, 3.0),
    15.87: (780.0, 6.0),
    19.0: (600.0, 10.0)
}

TABELA_ALUMINIO = {
    1.0: (8750.0, 1.0),
    1.5: (6600.0, 1.0),
    2.0: (5390.0, 1.0),
    2.5: (3724.0, 1.0),
    3.18: (2450.0, 1.0),
    4.0: (1764.0, 1.2),
    4.75: (1274.0, 1.2),
    6.35: (882.0, 1.5),
    8.0: (300.0, 1.5),
    10.0: (0.0, 0.0),
    12.7: (0.0, 0.0),
    15.87: (0.0, 0.0),
    19.0: (0.0, 0.0)
}


def get_densidade_material(material):
    """Retorna a densidade correta baseada no material (g/cm³)."""
    mat_lower = str(material).lower()
    if 'inox' in mat_lower:
        return 8.2
    elif 'alum' in mat_lower:
        return 3.2
    else:
        return 7.86  # Aço Carbono ou padrão


def lookup_velocidade_e_peck(material, espessura):
    """Realiza a busca aproximada (tipo VLOOKUP True) para velocidade e peck."""
    mat_lower = str(material).lower()
    if 'inox' in mat_lower:
        tabela = TABELA_INOX
    elif 'alum' in mat_lower:
        tabela = TABELA_ALUMINIO
    else:
        tabela = TABELA_ACO_CARBONO
        
    keys = sorted(tabela.keys())
    matched_key = keys[0]
    for k in keys:
        if k <= espessura:
            matched_key = k
        else:
            break
            
    return tabela[matched_key]


def calcular_area_peca(largura_mm, compr_mm):
    """Área com margem de 10mm em cada lado (m²). Fórmula da planilha col 21 (V)."""
    return ((largura_mm + 20) / 1000.0) * ((compr_mm + 20) / 1000.0)


def calcular_peso_unitario(largura_mm, compr_mm, espessura_mm, material):
    """Peso unitário da peça (kg). Fórmula da planilha col 22 (W)."""
    dens = get_densidade_material(material)
    return espessura_mm * (largura_mm + espessura_mm) * (compr_mm + espessura_mm) * dens / 1000000.0


def calcular_peso_total(largura_mm, compr_mm, espessura_mm, qtd, material):
    """Peso total considerando gap/margem (kg). Fórmula da planilha col 26 (AA)."""
    dens = get_densidade_material(material)
    margin = espessura_mm if espessura_mm > 5.0 else 5.0
    return qtd * (espessura_mm * (largura_mm + margin) * (compr_mm + margin) * dens / 1000000.0)


def calcular_peso_chapa(chapa_l_mm, chapa_c_mm, espessura_mm):
    """Peso da chapa (kg). Fórmula da planilha col 27 (AB)."""
    return (espessura_mm * chapa_l_mm * chapa_c_mm * 7.86 / 1000000.0)


def calcular_pecas_por_chapa(largura_mm, compr_mm, espessura_mm, chapa_l_mm, chapa_c_mm):
    """Peças por chapa. Fórmula da planilha col 28 (AC)."""
    if (largura_mm + espessura_mm) <= 0 or (compr_mm + espessura_mm) <= 0:
        return 0
    val = math.floor((chapa_l_mm - 10) / (largura_mm + espessura_mm)) * math.floor((chapa_c_mm - 10) / (compr_mm + espessura_mm))
    return max(0, val)


def calcular_item_completo(item_data, config):
    """Calcula todos os campos de um item de acordo com a planilha."""
    qtd = float(item_data.get('qtd', 1.0) or 1.0)
    largura = float(item_data.get('largura', 0.0) or 0.0)
    compr = float(item_data.get('compr', 0.0) or 0.0)
    espessura = float(item_data.get('espessura', 3.18) or 3.18)
    perimetro = float(item_data.get('perimetro', 0.0) or 0.0)
    n_entradas = float(item_data.get('n_entradas', 0.0) or 0.0)
    material = str(item_data.get('material', 'Aço Carbono') or 'Aço Carbono')
    preco_kg = float(item_data.get('preco_kg', 0.0) or 0.0)
    if preco_kg == 0.0:
        precos_mat = config.get('precos_material', {})
        mat_key = 'Aço Carbono'
        if 'inox' in material.lower():
            mat_key = 'Aço Inox'
        elif 'alum' in material.lower():
            mat_key = 'Alumínio'
        preco_kg = precos_mat.get(mat_key, 0.0)
    
    chapa_l = float(item_data.get('chapa_l', 1200.0) or 1200.0)
    chapa_c = float(item_data.get('chapa_c', 2400.0) or 2400.0)
    
    # Velocidade e Peck automático
    speed, peck = lookup_velocidade_e_peck(material, espessura)
    
    # Área
    area = calcular_area_peca(largura, compr)
    
    # Pesos
    peso_unit = calcular_peso_unitario(largura, compr, espessura, material)
    peso_total = calcular_peso_total(largura, compr, espessura, qtd, material)
    peso_chapa = calcular_peso_chapa(chapa_l, chapa_c, espessura)
    
    # Rendimento de Chapas
    pcs_chapa = calcular_pecas_por_chapa(largura, compr, espessura, chapa_l, chapa_c)
    qtd_chapas = math.ceil(qtd / pcs_chapa) if pcs_chapa > 0 else 0
    sobra = (qtd_chapas * pcs_chapa) - qtd if pcs_chapa > 0 else 0
    retalho = sobra * peso_unit
    
    # Custo de Matéria Prima (com IPI)
    taxas_imp = config.get('taxas_impostos', {})
    ipi_rate = taxas_imp.get('ipi', 0.05)
    custo_mp = peso_total * preco_kg * (1.0 + ipi_rate)
    
    # Tempo de Corte (AI)
    # Se já vier preenchido e for diferente de zero, respeita a entrada do usuário
    tempos = item_data.get('tempos', {})
    corte_user = tempos.get('corte_laser')
    if corte_user is not None and corte_user > 0.0:
        corte_laser_time = float(corte_user)
    else:
        if speed > 0 and perimetro > 0:
            corte_laser_time = math.ceil((((perimetro / speed) * 60.0 + n_entradas * peck) * qtd) / 60.0)
        else:
            corte_laser_time = 0.0
            
    # Tempos operacionais (unitários, multiplicados pela quantidade no cálculo final)
    op_times = {
        'setup': float(tempos.get('setup', 0.0) or 0.0),
        'dobra': float(tempos.get('dobra', 0.0) or 0.0),
        'caldeiraria': float(tempos.get('caldeiraria', 0.0) or 0.0),
        'solda': float(tempos.get('solda', 0.0) or 0.0),
        'guilhotina': float(tempos.get('guilhotina', 0.0) or 0.0),
        'usinagem_int': float(tempos.get('usinagem_int', 0.0) or 0.0),
        'montagem': float(tempos.get('montagem', 0.0) or 0.0)
    }
    
    # Total Fabricação (corte + operações unitárias * qtd)
    tarifas = config.get('tarifas', {})
    corte_rate = tarifas.get('corte_laser', 450.0)
    setup_rate = tarifas.get('setup', 60.0)
    dobra_rate = tarifas.get('dobra', 100.0)
    cald_rate = tarifas.get('caldeiraria', 100.0)
    solda_rate = tarifas.get('solda', 100.0)
    guil_rate = tarifas.get('guilhotina', 68.0)
    usin_rate = tarifas.get('usinagem_int', 80.0)
    mont_rate = tarifas.get('montagem', 80.0)
    
    total_fab = (
        corte_laser_time * corte_rate +
        qtd * (
            op_times['setup'] * setup_rate +
            op_times['dobra'] * dobra_rate +
            op_times['caldeiraria'] * cald_rate +
            op_times['solda'] * solda_rate +
            op_times['guilhotina'] * guil_rate +
            op_times['usinagem_int'] * usin_rate +
            op_times['montagem'] * mont_rate
        )
    ) / 60.0
    
    # Custos Extras
    custos_extras = item_data.get('custos_extras', {})
    extras = sum(float(v or 0.0) for v in custos_extras.values())
    
    # Custo Básico Total
    custo_basico = custo_mp + total_fab + extras
    
    # Preço de Venda
    margem = config.get('margem_lucro', 0.30)
    venda_sem_imp = custo_basico * (1.0 + margem)
    
    # Aplicar acréscimo / desconto comercial
    ajuste = config.get('ajuste_comercial', 0.0) / 100.0
    venda_sem_imp = venda_sem_imp * (1.0 + ajuste)
    
    icms_rate = taxas_imp.get('icms', 0.18)
    pis_rate = taxas_imp.get('pis', 0.0065)
    cofins_rate = taxas_imp.get('cofins', 0.03)
    csll_rate = taxas_imp.get('csll', 0.0108)
    irpj_rate = taxas_imp.get('irpj', 0.012)
    
    fator = 1.0 - (icms_rate + pis_rate + cofins_rate + csll_rate + irpj_rate)
    if fator <= 0.05:
        fator = 0.05
        
    preco_com_imp = venda_sem_imp / fator  # Preço total com impostos sem IPI
    preco_unit = preco_com_imp / qtd
    
    # Detalhamento de impostos
    icms_val = preco_com_imp * icms_rate
    pis_val = preco_com_imp * pis_rate
    cofins_val = preco_com_imp * cofins_rate
    csll_val = preco_com_imp * csll_rate
    irpj_val = preco_com_imp * irpj_rate
    ipi_val = preco_com_imp * ipi_rate
    
    total_tributos = icms_val + ipi_val + pis_val + cofins_val
    
    # NF (IPI adicionado por fora)
    valor_nf_total = preco_com_imp * (1.0 + ipi_rate)
    valor_nf_unit = valor_nf_total / qtd
    
    # Comissão
    commission_rate = config.get('taxa_comissao', 0.03)
    comissao = venda_sem_imp * commission_rate
    
    return {
        'speed': speed,
        'peck': peck,
        'area': area,
        'peso_unit': peso_unit,
        'peso_total': peso_total,
        'peso_chapa': peso_chapa,
        'pcs_chapa': pcs_chapa,
        'qtd_chapas': qtd_chapas,
        'sobra': sobra,
        'retalho': retalho,
        'custo_mp': custo_mp,
        'corte_laser_time': corte_laser_time,
        'total_fab': total_fab,
        'custo_basico': custo_basico,
        'venda_sem_imp': venda_sem_imp,
        'preco_com_imp': preco_com_imp,
        'preco_unit_com_imp': preco_unit,
        'impostos': {
            'icms': icms_val,
            'ipi': ipi_val,
            'pis': pis_val,
            'cofins': cofins_val,
            'csll': csll_val,
            'irpj': irpj_val
        },
        'total_tributos': total_tributos,
        'valor_nf': valor_nf_unit,
        'valor_nf_total': valor_nf_total,
        'comissao': comissao,
        'fator_impostos': fator,
    }


def calcular_item_completo_v2(item_data, config):
    """Alias para compatibilidade com os testes unitários."""
    return calcular_item_completo(item_data, config)


def calcular_fator_impostos(icms, pis, cofins, csll, irpj):
    """Calcula o fator divisor de impostos em cascata."""
    return 1.0 - (icms + pis + cofins + csll + irpj)
