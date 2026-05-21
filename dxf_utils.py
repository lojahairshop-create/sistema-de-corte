"""Funções de processamento DXF e Nesting."""
import math
import streamlit as st

try:
    import ezdxf
    EZDXF_DISPONIVEL = True
except ImportError:
    EZDXF_DISPONIVEL = False


def processar_dxf(arquivo_dxf, velocidade_mm_min, tempo_furo_seg):
    if not EZDXF_DISPONIVEL:
        st.error("Biblioteca ezdxf não instalada. Execute: pip install ezdxf")
        return None
    import tempfile, os
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
            tmp.write(arquivo_dxf.getvalue())
            tmp_path = tmp.name
        try:
            doc = ezdxf.readfile(tmp_path)
        except ezdxf.DXFStructureError:
            try:
                from ezdxf import recover
                doc, auditor = recover.readfile(tmp_path)
            except Exception as e:
                os.remove(tmp_path)
                raise e
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        msp = doc.modelspace()
        perimetro_total, qtd_furos = 0.0, 0
        for entity in msp:
            tipo = entity.dxftype()
            comp = 0.0
            if tipo == 'LINE':
                s, e = entity.dxf.start, entity.dxf.end
                comp = math.dist((s.x, s.y), (e.x, e.y))
            elif tipo == 'CIRCLE':
                comp = 2 * math.pi * entity.dxf.radius
            elif tipo == 'ARC':
                r = entity.dxf.radius
                a1, a2 = math.radians(entity.dxf.start_angle), math.radians(entity.dxf.end_angle)
                if a2 < a1: a2 += 2 * math.pi
                comp = r * (a2 - a1)
            elif tipo == 'LWPOLYLINE':
                pts = list(entity.get_points('xy'))
                for i in range(len(pts)-1): comp += math.dist(pts[i], pts[i+1])
                if entity.closed: comp += math.dist(pts[-1], pts[0])
            elif tipo == 'POLYLINE':
                pts = [(v.dxf.location.x, v.dxf.location.y) for v in entity.vertices]
                for i in range(len(pts)-1): comp += math.dist(pts[i], pts[i+1])
                if entity.is_closed: comp += math.dist(pts[-1], pts[0])
            elif tipo == 'ELLIPSE':
                try:
                    a = entity.dxf.major_axis.magnitude
                    b = a * entity.dxf.ratio
                    comp = math.pi * (3*(a+b) - math.sqrt((3*a+b)*(a+3*b)))
                except: pass
            elif tipo == 'SPLINE':
                try:
                    pts = list(entity.flattening(0.5))
                    for i in range(len(pts)-1):
                        comp += math.dist((pts[i].x, pts[i].y), (pts[i+1].x, pts[i+1].y))
                except: pass
            if comp > 0:
                perimetro_total += comp
                qtd_furos += 1
        lx, ly = 0.0, 0.0
        try:
            from ezdxf import bbox
            ext = bbox.extents(msp)
            if ext.has_data:
                lx = ext.extmax.x - ext.extmin.x
                ly = ext.extmax.y - ext.extmin.y
        except: pass
        tc = perimetro_total / velocidade_mm_min if velocidade_mm_min > 0 else 0
        tf = (qtd_furos * tempo_furo_seg) / 60.0
        return {"perimetro": perimetro_total, "furos": qtd_furos, "tempo_corte_min": tc,
                "tempo_furo_min": tf, "tempo_total_min": tc + tf, "largura_x": lx, "altura_y": ly}
    except Exception as e:
        st.error(f"Erro ao processar DXF: {e}")
        return None


def calcular_nesting_simples(w_peca, h_peca, w_chapa, h_chapa, margem, espaco, permitir_rotacao, qtd_desejada=0):
    if w_peca <= 0 or h_peca <= 0: return None, 0, 0, 0
    W_util, H_util = w_chapa - 2*margem, h_chapa - 2*margem
    if W_util <= 0 or H_util <= 0: return None, 0, 0, 0
    layouts = []
    def pack(wp, hp, sx, sy, mw, mh):
        rects = []
        cols, rows = int((mw+espaco)/(wp+espaco)), int((mh+espaco)/(hp+espaco))
        if cols > 0 and rows > 0:
            for r in range(rows):
                for c in range(cols):
                    rects.append({'x': sx+c*(wp+espaco), 'y': sy+r*(hp+espaco), 'w': wp, 'h': hp})
        return rects
    r0 = pack(w_peca, h_peca, margem, margem, W_util, H_util)
    layouts.append({'desc': '0°', 'qtd': len(r0), 'rects': r0})
    if permitir_rotacao:
        r90 = pack(h_peca, w_peca, margem, margem, W_util, H_util)
        layouts.append({'desc': '90°', 'qtd': len(r90), 'rects': r90})
    valid = []
    for l in layouts:
        if qtd_desejada > 0 and l['qtd'] >= qtd_desejada:
            l['rects'] = l['rects'][:qtd_desejada]; l['qtd'] = qtd_desejada
        if l['qtd'] > 0:
            mx = max(r['x']+r['w'] for r in l['rects'])+margem
            my = max(r['y']+r['h'] for r in l['rects'])+margem
            l['retalho_w'], l['retalho_h'], l['retalho_area'] = mx, my, mx*my
            valid.append(l)
    if not valid: return None, 0, 0, 0
    if qtd_desejada > 0:
        alvos = [l for l in valid if l['qtd'] == qtd_desejada]
        best = min(alvos, key=lambda l: l['retalho_area']) if alvos else max(valid, key=lambda l: l['qtd'])
    else:
        best = max(valid, key=lambda l: l['qtd'])
    area_usada = best['qtd'] * w_peca * h_peca
    rw, rh = best['retalho_w'], best['retalho_h']
    if qtd_desejada > 0 and best['qtd'] == qtd_desejada:
        aprov = (area_usada / best['retalho_area'])*100 if best['retalho_area'] > 0 else 0
    else:
        aprov = (area_usada / (w_chapa*h_chapa))*100 if w_chapa*h_chapa > 0 else 0
    return best, aprov, rw, rh
