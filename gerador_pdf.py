import os
import io
import math
from matplotlib.figure import Figure
import matplotlib.patches as patches

# Try to import ezdxf
try:
    import ezdxf
    from ezdxf import bbox
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False

# ReportLab Imports
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

def gerar_preview_geometria(item, dxf_bytes=None):
    """
    Gera uma imagem PNG (em bytes) contendo o contorno da peça.
    Se dxf_bytes for fornecido e ezdxf estiver disponível, desenha a geometria do DXF.
    Caso contrário, desenha um retângulo com as dimensões de largura e comprimento.
    """
    fig = Figure(figsize=(1.2, 1.2), dpi=100)
    ax = fig.subplots()
    ax.set_aspect('equal')
    ax.axis('off')
    
    plotted = False
    
    if dxf_bytes and EZDXF_DISPONIVEL:
        import tempfile
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
                tmp.write(dxf_bytes)
                tmp_path = tmp.name
            
            doc = ezdxf.readfile(tmp_path)
            msp = doc.modelspace()
            
            for entity in msp:
                tipo = entity.dxftype()
                if tipo == 'LINE':
                    s, e = entity.dxf.start, entity.dxf.end
                    ax.plot([s.x, e.x], [s.y, e.y], color='#0f172a', linewidth=0.8)
                    plotted = True
                elif tipo == 'CIRCLE':
                    c = entity.dxf.center
                    r = entity.dxf.radius
                    circle = plt.Circle((c.x, c.y), r, fill=False, color='#0f172a', linewidth=0.8)
                    ax.add_patch(circle)
                    plotted = True
                elif tipo == 'ARC':
                    # Approximate arc drawing
                    r = entity.dxf.radius
                    c = entity.dxf.center
                    a1 = entity.dxf.start_angle
                    a2 = entity.dxf.end_angle
                    # Draw using a patch
                    arc = patches.Arc((c.x, c.y), r*2, r*2, angle=0, theta1=a1, theta2=a2, color='#0f172a', linewidth=0.8)
                    ax.add_patch(arc)
                    plotted = True
                elif tipo == 'LWPOLYLINE':
                    pts = list(entity.get_points('xy'))
                    if pts:
                        xs = [p[0] for p in pts]
                        ys = [p[1] for p in pts]
                        if entity.closed:
                            xs.append(pts[0][0])
                            ys.append(pts[0][1])
                        ax.plot(xs, ys, color='#0f172a', linewidth=0.8)
                        plotted = True
                elif tipo == 'POLYLINE':
                    pts = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
                    if pts:
                        xs = [p[0] for p in pts]
                        ys = [p[1] for p in pts]
                        if entity.is_closed:
                            xs.append(pts[0][0])
                            ys.append(pts[0][1])
                        ax.plot(xs, ys, color='#0f172a', linewidth=0.8)
                        plotted = True
        except Exception as e:
            # Fallback quietly to rectangular drawing if dxf rendering fails
            pass
        finally:
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except:
                    pass

    if not plotted:
        # Fallback rectangular drawing
        w = item.get('largura', 100.0)
        h = item.get('compr', 100.0)
        if w <= 0: w = 100.0
        if h <= 0: h = 100.0
        # Draw a clean rectangle
        rect = patches.Rectangle((0, 0), w, h, fill=False, edgecolor='#4f46e5', linewidth=1.2)
        ax.add_patch(rect)
        ax.set_xlim(-w*0.05, w*1.05)
        ax.set_ylim(-h*0.05, h*1.05)
        
    # Save plot as bytes
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=100, bbox_inches='tight', pad_inches=0.05, transparent=True)
    fig.clear()
    buf.seek(0)
    return buf.getvalue()


class NumberedCanvas(canvas.Canvas):
    """
    Canvas customizado de duas passagens para desenhar o cabeçalho e rodapé
    dinâmicos em todas as páginas, sabendo o total exato de páginas.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_elements(num_pages)
            super().showPage()
        super().save()

    def draw_page_elements(self, page_count):
        self.saveState()
        
        # 1. CABEÇALHO (Em todas as páginas)
        # Logo
        logo_data = getattr(self, 'logo_data', None)
        if logo_data:
            try:
                logo_io = io.BytesIO(logo_data)
                # Draw logo image
                self.drawImage(logo_io, 36, 750, width=120, height=50, preserveAspectRatio=True, mask='auto')
            except Exception as e:
                # Text fallback if image loading fails
                self.setFont("Helvetica-Bold", 16)
                self.setFillColor(colors.HexColor("#0f172a"))
                self.drawString(36, 765, getattr(self, 'company_name', "ORÇAMENTO INDUSTRIAL"))
        else:
            self.setFont("Helvetica-Bold", 16)
            self.setFillColor(colors.HexColor("#0f172a"))
            self.drawString(36, 765, getattr(self, 'company_name', "ORÇAMENTO INDUSTRIAL"))
            
        # Número do Orçamento
        num_orcamento = getattr(self, 'num_orcamento', '0001')
        self.setFont("Helvetica-Bold", 14)
        self.setFillColor(colors.HexColor("#0f172a"))
        self.drawRightString(559, 765, f"Nº Orçamento : {num_orcamento}")
        
        # Linha do Cabeçalho
        self.setStrokeColor(colors.HexColor("#cbd5e1"))
        self.setLineWidth(0.8)
        self.line(36, 740, 559, 740)
        
        # 2. RODAPÉ (Em todas as páginas)
        self.line(36, 40, 559, 40)
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(36, 25, f"{getattr(self, 'company_name', 'Orçamento')} — Todos os direitos reservados.")
        
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(559, 25, page_text)
        
        self.restoreState()


def gerar_orcamento_pdf(itens, config_global, cliente_info, emissor_info, prazos_condicoes, logo_bytes=None):
    """
    Gera o PDF de orçamento no padrão do modelo de 2 páginas.
    Retorna os bytes do PDF gerado.
    """
    pdf_buffer = io.BytesIO()
    
    # 1. Configurações básicas de layout
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=120, # Espaço para o cabeçalho
        bottomMargin=55 # Espaço para o rodapé
    )
    
    # Injeta dados dinâmicos no document para o NumberedCanvas ler
    doc.num_orcamento = cliente_info.get('num_orcamento', '0001')
    doc.company_name = emissor_info.get('nome', '2R CORTE LASER')
    doc.logo_data = logo_bytes

    styles = getSampleStyleSheet()
    
    # Estilos customizados
    style_normal = ParagraphStyle('Normal_Custom', parent=styles['Normal'], fontSize=8, leading=10, textColor=colors.HexColor("#334155"))
    style_bold = ParagraphStyle('Bold_Custom', parent=style_normal, fontName='Helvetica-Bold')
    style_h2 = ParagraphStyle('H2_Custom', parent=styles['Heading2'], fontSize=11, leading=14, fontName='Helvetica-Bold', textColor=colors.HexColor("#0f172a"), spaceBefore=10, spaceAfter=6)
    style_cell = ParagraphStyle('Cell_Custom', parent=style_normal, fontSize=8, leading=9)
    style_cell_center = ParagraphStyle('Cell_Center_Custom', parent=style_cell, alignment=1)
    style_cell_bold = ParagraphStyle('Cell_Bold_Custom', parent=style_cell, fontName='Helvetica-Bold')
    style_cell_bold_center = ParagraphStyle('Cell_Bold_Center_Custom', parent=style_cell_center, fontName='Helvetica-Bold')
    
    story = []
    
    # === SEÇÃO 1: METADADOS (CLIENTE E EMISSOR) ===
    meta_data = [
        [
            Paragraph("<b>Cliente:</b>", style_cell),
            Paragraph("<b>Preparado Por:</b>", style_cell)
        ],
        [
            Paragraph(f"{cliente_info.get('nome', '')}<br/>"
                      f"{cliente_info.get('endereco', '')}<br/>"
                      f"Telefone: {cliente_info.get('telefone', '-')}", style_cell),
            Paragraph(f"{emissor_info.get('responsavel', '')}<br/>"
                      f"<b>{emissor_info.get('nome', '')}</b><br/>"
                      f"{emissor_info.get('endereco', '')}<br/>"
                      f"Tel.: {emissor_info.get('telefone', '')}<br/>"
                      f"Cel.: {emissor_info.get('celular', '')}<br/>"
                      f"Email: {emissor_info.get('email', '')}", style_cell)
        ],
        [
            Paragraph(f"<b>Data de Criação:</b> {cliente_info.get('data_criacao', '')}<br/>"
                      f"<b>Data de Vencimento:</b> {cliente_info.get('data_vencimento', '')}", style_cell),
            ""
        ]
    ]
    
    meta_table = Table(meta_data, colWidths=[260, 263])
    meta_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 1),
        ('BOTTOMPADDING', (0,0), (-1,-1), 1),
        ('LEFTPADDING', (0,0), (-1,-1), 0),
        ('RIGHTPADDING', (0,0), (-1,-1), 0),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # === SEÇÃO 2: TABELA DE ITENS ===
    # A4 printable area width is 595 - 72 = 523
    col_widths = [20, 75, 120, 50, 100, 30, 64, 64]
    table_data = [[
        Paragraph("<b>ITEM</b>", style_cell_bold_center),
        Paragraph("<b>DIMENSÃO</b>", style_cell_bold_center),
        Paragraph("<b>PRODUTO / DESCRIÇÃO</b>", style_cell_bold),
        Paragraph("<b>PESO (Kg)</b>", style_cell_bold_center),
        Paragraph("<b>MATERIAL</b>", style_cell_bold),
        Paragraph("<b>QTDE.</b>", style_cell_bold_center),
        Paragraph("<b>VALOR UNIT.</b>", style_cell_bold_center),
        Paragraph("<b>VALOR TOTAL</b>", style_cell_bold_center)
    ]]
    
    total_peso = 0.0
    total_itens_qtd = 0
    total_nf = 0.0
    
    for i, it in enumerate(itens):
        calc = it.get('calc', {})
        total_peso += calc.get('peso_total', 0.0)
        total_itens_qtd += it.get('qtd', 1)
        total_nf += calc.get('valor_nf_total', 0.0)
        
        # 1. Gera imagem da peça
        dxf_b = it.get('dxf_bytes', None)
        img_bytes = gerar_preview_geometria(it, dxf_b)
        img_io = io.BytesIO(img_bytes)
        img_flowable = Image(img_io, width=45, height=45)
        
        # 2. Constrói a coluna DIMENSÃO (Imagem + Texto)
        dim_text = f"{it.get('largura', 0.0):.2f} X {it.get('compr', 0.0):.2f}"
        dim_cell = [
            Spacer(1, 2),
            img_flowable,
            Spacer(1, 2),
            Paragraph(dim_text, style_cell_center)
        ]
        
        # 3. Processos executados
        procs_list = ["Laser"] # Laser is default
        tempos = it.get('tempos', {})
        if tempos.get('dobra', 0.0) > 0.0: procs_list.append("Dobra")
        if tempos.get('solda', 0.0) > 0.0: procs_list.append("Solda")
        if tempos.get('caldeiraria', 0.0) > 0.0: procs_list.append("Caldeiraria")
        if tempos.get('usinagem_int', 0.0) > 0.0: procs_list.append("Usinagem")
        if tempos.get('guilhotina', 0.0) > 0.0: procs_list.append("Guilhotina")
        if tempos.get('montagem', 0.0) > 0.0: procs_list.append("Montagem")
        procs_str = f"<b>Processos:</b> {', '.join(procs_list)}"
        
        desc_cell = [
            Paragraph(it.get('descricao', ''), style_cell_bold),
            Spacer(1, 4),
            Paragraph(procs_str, style_cell)
        ]
        
        # 4. Detalhes de preço e peso
        peso_tot_val = calc.get('peso_total', 0.0)
        v_unit = calc.get('valor_nf_total', 0.0) / it.get('qtd', 1) if it.get('qtd', 1) > 0 else 0.0
        v_tot = calc.get('valor_nf_total', 0.0)
        mat_str = f"{it.get('material', '')} {it.get('espessura', 0.0):.2f}mm"
        
        table_data.append([
            Paragraph(str(i+1), style_cell_center),
            dim_cell,
            desc_cell,
            Paragraph(f"{peso_tot_val:.2f}", style_cell_center),
            Paragraph(mat_str, style_cell),
            Paragraph(str(it.get('qtd', 1)), style_cell_center),
            Paragraph(f"R$ {v_unit:,.2f}", style_cell_center),
            Paragraph(f"R$ {v_tot:,.2f}", style_cell_center)
        ])
        
    items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('ALIGN', (3,1), (3,-1), 'CENTER'),
        ('ALIGN', (5,1), (-1,-1), 'CENTER'),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 15))
    
    # === SEÇÃO 3: TOTAIS E COMENTÁRIOS ===
    comentarios = prazos_condicoes.get('comentarios', '')
    coment_cell = [
        Paragraph("<b>Comentários:</b>", style_cell_bold),
        Spacer(1, 4),
        Paragraph(comentarios.replace('\n', '<br/>'), style_normal)
    ]
    
    # IPI info text
    tx_ipi_desc = f"Venda IPI - {config_global.get('taxas_impostos', {}).get('ipi', 0.05)*100:.2f}%"
    totais_cell = [
        Paragraph(f"<b>VALOR TOTAL : R$ {total_nf:,.2f}</b>", ParagraphStyle('TotalVal', parent=style_cell_bold, fontSize=12, leading=14, alignment=2, textColor=colors.HexColor("#1e293b"))),
        Paragraph(f"({tx_ipi_desc} / Benef. Isento)", ParagraphStyle('TotalValSub', parent=style_cell, alignment=2, textColor=colors.HexColor("#475569"))),
        Spacer(1, 4),
        Paragraph(f"Total de {total_itens_qtd} peças", ParagraphStyle('TotalQty', parent=style_cell, alignment=2)),
        Paragraph(f"Peso total do orçamento {total_peso:.2f} Kg", ParagraphStyle('TotalWeight', parent=style_cell, alignment=2))
    ]
    
    summary_data = [
        [coment_cell, totais_cell]
    ]
    
    summary_table = Table(summary_data, colWidths=[300, 223])
    summary_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.8, colors.HexColor("#94a3b8")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
    ]))
    
    story.append(KeepTogether(summary_table))
    
    # === PÁGINA 2: CONDIÇÕES GERAIS DE FORNECIMENTO ===
    story.append(PageBreak())
    
    story.append(Paragraph("CONDIÇÕES GERAIS DE FORNECIMENTO", style_h2))
    story.append(Spacer(1, 5))
    
    # 7 Tópicos de condições
    terms_list = prazos_condicoes.get('condicoes_texto', [])
    if not terms_list:
        # Default terms if none are saved
        terms_list = [
            "Os desenhos deverão ser fornecidos no formato .DXF ou .DWG em escala 1:1 com a respectiva indicação de revisão. Peças cortadas fora da sua verdadeira grandeza serão de responsabilidade do cliente.",
            "TOLERANCIA CORTE <=0,2mm e <=1,00mm | TOLERÂNCIA DOBRA: +/- 1,5mm.",
            "Furos com diâmetro menor que a espessura da chapa serão somente marcados.",
            "A produção somente será iniciada quando:\n* Recebido pedido do cliente E / OU recebimento da matéria-prima (no caso de beneficiamento).\n* Recebido a confirmação por e-mail aprovando a proposta comercial.",
            "Horário para entrega e retirada de mercadorias: 08h às 12h | 14h às 17h.",
            "No processo de corte pode haver empenamento das peças (algo normal devida a alta temperatura). O cliente deve especificar no ato da cotação a necessidade de mantê-las planas.",
            "Prezados clientes, concluído o pedido de BENEFICIAMENTO, a sucata gerada será mantida em até, no máximo, 4 dias úteis. Após este período será descartada junto com outras sucatas pelo motivo de logística e espaço. Dessa forma, tornando-se de propriedade da empresa."
        ]
        
    for index, term in enumerate(terms_list):
        term_p = Paragraph(f"<b>{index+1}.</b> {term.replace('\n', '<br/>')}", style_normal)
        story.append(term_p)
        story.append(Spacer(1, 8))
        
    story.append(Spacer(1, 15))
    
    # Tabela de Condições Gerais de Venda
    terms_grid_data = [
        [Paragraph("<b>Prazo de Entrega:</b>", style_cell_bold), Paragraph(prazos_condicoes.get('prazo_entrega', '7 Dias úteis após recebimento do pedido'), style_normal)],
        [Paragraph("<b>Forma de Pagamento:</b>", style_cell_bold), Paragraph(prazos_condicoes.get('forma_pagamento', 'A Combinar'), style_normal)],
        [Paragraph("<b>Pedido Mínimo:</b>", style_cell_bold), Paragraph(f"R$ {prazos_condicoes.get('pedido_minimo', 500.0):,.2f}", style_normal)],
        [Paragraph("<b>Frete:</b>", style_cell_bold), Paragraph(prazos_condicoes.get('frete', 'FOB'), style_normal)],
        [Paragraph("<b>Impostos:</b>", style_cell_bold), Paragraph(prazos_condicoes.get('impostos_descricao', 'ICMS INCLUSO - PIS/COFINS INCLUSO | IPI A INCLUIR'), style_normal)],
    ]
    
    terms_grid_table = Table(terms_grid_data, colWidths=[130, 393])
    terms_grid_table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#cbd5e1")),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor("#f1f5f9")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    story.append(KeepTogether(terms_grid_table))
    
    # Define a custom drawPage function to apply custom attributes to canvas
    def apply_canvas_data(canvas, doc):
        canvas.num_orcamento = doc.num_orcamento
        canvas.company_name = doc.company_name
        canvas.logo_data = doc.logo_data

    # Build the document
    doc.build(story, canvasmaker=NumberedCanvas, onFirstPage=apply_canvas_data, onLaterPages=apply_canvas_data)
    
    pdf_buffer.seek(0)
    return pdf_buffer.getvalue()
