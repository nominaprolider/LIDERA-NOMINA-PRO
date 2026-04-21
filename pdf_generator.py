"""
pdf_generator.py — Generador de comprobante de nómina en PDF
Usa ReportLab para crear documentos profesionales con cláusula de paz y salvo.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

C_VERDE       = HexColor("#009E76")
C_VERDE_DARK  = HexColor("#006B52")
C_VERDE_LIGHT = HexColor("#E0F7F1")
C_GRIS_CLARO  = HexColor("#F5F7FA")
C_GRIS_MEDIO  = HexColor("#C8D2DC")
C_GRIS_TEXTO  = HexColor("#5A6473")
C_NEGRO       = HexColor("#141923")
C_ROJO        = HexColor("#C83232")
C_BLANCO      = white


def _fmt(n) -> str:
    return f"${int(n):,}".replace(",", ".")


def generar_pdf(res: dict) -> bytes:
    buf = io.BytesIO()
    periodo_str = (
        f"{res['periodo_inicio'].strftime('%d/%m/%Y')} — "
        f"{res['periodo_fin'].strftime('%d/%m/%Y')}"
    )

    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        rightMargin=15*mm, leftMargin=15*mm,
        topMargin=12*mm, bottomMargin=15*mm,
        title=f"Comprobante Nómina — {res['empleado']}",
    )

    W = 180 * mm

    # — ESTILOS —
    def sty(name, **kw):
        base = dict(fontName="Helvetica", fontSize=9, leading=13, textColor=C_NEGRO)
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_hdr  = sty("hdr",  fontSize=17, textColor=C_BLANCO, fontName="Helvetica-Bold", leading=22)
    s_hsub = sty("hsub", fontSize=8.5, textColor=HexColor("#A8E6D0"), alignment=TA_RIGHT, leading=13)
    s_sec  = sty("sec",  fontSize=9, textColor=C_BLANCO, fontName="Helvetica-Bold", leftIndent=4)
    s_lbl  = sty("lbl",  textColor=C_GRIS_TEXTO)
    s_val  = sty("val",  fontName="Helvetica-Bold")
    s_vg   = sty("vg",   fontName="Helvetica-Bold", textColor=C_VERDE_DARK, alignment=TA_RIGHT)
    s_vr   = sty("vr",   fontName="Helvetica-Bold", textColor=C_ROJO, alignment=TA_RIGHT)
    s_vb   = sty("vb",   fontName="Helvetica-Bold", alignment=TA_RIGHT)
    s_nl   = sty("nl",   fontSize=12, textColor=C_BLANCO, fontName="Helvetica-Bold", leading=16)
    s_nv   = sty("nv",   fontSize=20, textColor=HexColor("#B4FEE0"), fontName="Helvetica-Bold",
                         alignment=TA_RIGHT, leading=24)
    s_paz  = sty("paz",  fontSize=8, fontName="Helvetica-Oblique", alignment=TA_JUSTIFY, leading=12)
    s_fn   = sty("fn",   fontSize=8.5, fontName="Helvetica-Bold", alignment=TA_CENTER)
    s_fs   = sty("fs",   fontSize=7.5, textColor=C_GRIS_TEXTO, alignment=TA_CENTER)
    s_th   = sty("th",   fontSize=7, textColor=C_BLANCO, fontName="Helvetica-Bold", alignment=TA_CENTER, leading=9)
    s_tc   = sty("tc",   fontSize=7, alignment=TA_CENTER, leading=9)
    s_foot = sty("foot", fontSize=6.5, textColor=C_GRIS_TEXTO, fontName="Helvetica-Oblique",
                         alignment=TA_CENTER, leading=10)

    story = []

    # — HEADER —
    ht = Table([[
        Paragraph("🍽️  COMPROBANTE DE NÓMINA", s_hdr),
        Paragraph(
            f"{res['empresa']}<br/>NIT/CC: {res.get('nit','—')}<br/>Colombia 2026",
            s_hsub
        )
    ]], colWidths=[W*0.6, W*0.4])
    ht.setStyle(TableStyle([
        ("BACKGROUND",     (0,0),(-1,-1), C_VERDE_DARK),
        ("TOPPADDING",     (0,0),(-1,-1), 12),
        ("BOTTOMPADDING",  (0,0),(-1,-1), 12),
        ("LEFTPADDING",    (0,0),(0,-1),  14),
        ("RIGHTPADDING",   (1,0),(1,-1),  12),
        ("VALIGN",         (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(ht)

    banda = Table([[""]], colWidths=[W], rowHeights=[5*mm])
    banda.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),C_VERDE)]))
    story.append(banda)
    story.append(Spacer(1, 5*mm))

    # — HELPERS —
    def sec_tit(txt):
        t = Table([[Paragraph(f"  {txt}", s_sec)]], colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0,0),(-1,-1), C_VERDE),
            ("TOPPADDING", (0,0),(-1,-1), 5),
            ("BOTTOMPADDING",(0,0),(-1,-1), 5),
        ]))
        return t

    def fila_d(label, valor, alt=False):
        bg = C_GRIS_CLARO if alt else C_BLANCO
        r = Table([[Paragraph(f"  {label}", s_lbl), Paragraph(f"  {valor}", s_val)]],
                  colWidths=[W*0.45, W*0.55])
        r.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), bg),
            ("TOPPADDING",(0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
        ]))
        return r

    def fila_m(label, monto, ded=False, alt=False, bold=False):
        bg = C_GRIS_CLARO if alt else C_BLANCO
        signo = "−" if ded else "+"
        sval = s_vr if ded else s_vg
        slbl = s_val if bold else s_lbl
        r = Table([[Paragraph(f"  {label}", slbl),
                    Paragraph(f"{signo} {_fmt(monto)} COP", sval)]],
                  colWidths=[W*0.68, W*0.32])
        r.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,-1), bg),
            ("TOPPADDING",(0,0),(-1,-1), 4),
            ("BOTTOMPADDING",(0,0),(-1,-1), 4),
            ("RIGHTPADDING",(1,0),(1,-1), 6),
        ]))
        return r

    # — DATOS GENERALES —
    story.append(sec_tit("👤 INFORMACIÓN DEL EMPLEADO Y PERÍODO"))
    story.append(Spacer(1, 1*mm))
    alt = True
    for lbl, val in [
        ("Empleado", res["empleado"]),
        ("Cédula", res["cedula"]),
        ("Empresa / Restaurante", res["empresa"]),
        ("Tipo de Salario", res["tipo_salario"]),
        ("Período Liquidado", periodo_str),
        ("Días Laborados", str(res["dias_laborados"])),
    ]:
        story.append(fila_d(lbl, val, alt)); alt = not alt
    story.append(Spacer(1, 4*mm))

    # — DEVENGADO —
    story.append(sec_tit("📈 CONCEPTOS DEVENGADOS"))
    story.append(Spacer(1, 1*mm))
    alt = True
    items = [
        (f"Salario Base / Horas Ordinarias", res["salario_base_calc"]),
        (f"Auxilio de Transporte (proporcional a {res['dias_laborados']} días)", res["aux_transporte"]),
    ]
    if res["comisiones"]:
        items.append(("Comisiones / Bonificaciones", res["comisiones"]))
    if res["recargo_nocturno"]:
        items.append((f"Recargo Nocturno (35%) · {res['horas_nocturnas']:.1f}h desde 19:00", res["recargo_nocturno"]))
    if res["recargo_dominical"]:
        items.append((f"Recargo Dominical/Festivo (100%) · {res['horas_dominical']:.1f}h", res["recargo_dominical"]))
    if res["he_diurnas_valor"]:
        items.append((f"H.E. Diurnas (25%) · {res['he_diurnas_horas']:.1f}h", res["he_diurnas_valor"]))
    if res["he_nocturnas_valor"]:
        items.append((f"H.E. Nocturnas (75%) · {res['he_nocturnas_horas']:.1f}h", res["he_nocturnas_valor"]))

    for lbl, val in items:
        story.append(fila_m(lbl, val, alt=alt)); alt = not alt

    story.append(HRFlowable(width="100%", thickness=1, color=C_VERDE, spaceAfter=2))
    story.append(fila_m("TOTAL DEVENGADO", res["total_devengado"], bold=True))
    story.append(Spacer(1, 4*mm))

    # — DEDUCCIONES —
    story.append(sec_tit("📉 DEDUCCIONES DE LEY (Seguridad Social)"))
    story.append(Spacer(1, 1*mm))
    alt = True
    story.append(fila_m(f"Salud (4%) sobre base {_fmt(res['base_ss'])}", res["salud"], ded=True, alt=alt)); alt = not alt
    story.append(fila_m(f"Pensión (4%) sobre base {_fmt(res['base_ss'])}", res["pension"], ded=True, alt=alt))
    story.append(HRFlowable(width="100%", thickness=1, color=C_ROJO, spaceAfter=2))
    story.append(fila_m("TOTAL DEDUCCIONES", res["total_deducciones"], ded=True, bold=True))
    story.append(Spacer(1, 4*mm))

    # — NETO —
    nt = Table([[
        Paragraph("💵  NETO A PAGAR", s_nl),
        Paragraph(f"{_fmt(res['neto_a_pagar'])} COP", s_nv),
    ]], colWidths=[W*0.45, W*0.55])
    nt.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_VERDE_DARK),
        ("TOPPADDING",    (0,0),(-1,-1), 14),
        ("BOTTOMPADDING", (0,0),(-1,-1), 14),
        ("LEFTPADDING",   (0,0),(0,-1),  14),
        ("RIGHTPADDING",  (1,0),(1,-1),  12),
        ("VALIGN",        (0,0),(-1,-1), "MIDDLE"),
    ]))
    story.append(nt)
    story.append(Spacer(1, 5*mm))

    # — DESGLOSE TURNOS —
    if res.get("detalle_turnos"):
        story.append(sec_tit("📋 DESGLOSE DE TURNOS TRABAJADOS"))
        story.append(Spacer(1, 1.5*mm))
        headers = ["Fecha","Tipo","Entrada","Salida","Hs Ord","Hs Noc","Dom/F","HE D.","HE N.","Valor"]
        cws = [22*mm,28*mm,15*mm,15*mm,12*mm,12*mm,12*mm,12*mm,12*mm,20*mm]
        td = [[Paragraph(h, s_th) for h in headers]]
        for row in res["detalle_turnos"]:
            tr = []
            for i, cell in enumerate(row):
                if i == 9 and isinstance(cell, (int, float)):
                    tr.append(Paragraph(_fmt(int(cell)), s_tc))
                else:
                    tr.append(Paragraph(str(cell), s_tc))
            td.append(tr)
        tt = Table(td, colWidths=cws, repeatRows=1)
        tstyles = [
            ("BACKGROUND",    (0,0),(-1,0),  C_VERDE_DARK),
            ("GRID",          (0,0),(-1,-1), 0.3, C_GRIS_MEDIO),
            ("TOPPADDING",    (0,0),(-1,-1), 3),
            ("BOTTOMPADDING", (0,0),(-1,-1), 3),
        ]
        for i in range(1, len(td)):
            if i % 2 == 0:
                tstyles.append(("BACKGROUND",(0,i),(-1,i), C_GRIS_CLARO))
        tt.setStyle(TableStyle(tstyles))
        story.append(tt)
        story.append(Spacer(1, 5*mm))

    # — PAZ Y SALVO —
    story.append(sec_tit("📋 CLÁUSULA DE PAZ Y SALVO (Art. 65 C.S.T.)"))
    story.append(Spacer(1, 2*mm))
    texto_paz = (
        f"Yo, <b>{res['empleado']}</b>, identificado(a) como aparece al pie de mi firma, "
        f"declaro que he recibido a entera satisfacción la suma de <b>{_fmt(res['neto_a_pagar'])} COP</b> "
        f"por concepto de liquidación de nómina/turno del periodo <b>{periodo_str}</b>. "
        f"Acepto que los cálculos de recargos nocturnos, dominicales y horas extras se ajustan "
        f"a la realidad laborada y a la normativa vigente al año 2026. Con este pago, me declaro a "
        f"<b>PAZ Y SALVO</b> con mi empleador por salarios, prestaciones y recargos del periodo "
        f"mencionado, renunciando a cualquier reclamación posterior por estos conceptos."
    )
    pb = Table([[Paragraph(texto_paz, s_paz)]], colWidths=[W])
    pb.setStyle(TableStyle([
        ("BACKGROUND",    (0,0),(-1,-1), C_VERDE_LIGHT),
        ("TOPPADDING",    (0,0),(-1,-1), 10),
        ("BOTTOMPADDING", (0,0),(-1,-1), 10),
        ("LEFTPADDING",   (0,0),(-1,-1), 12),
        ("RIGHTPADDING",  (0,0),(-1,-1), 12),
        ("BOX",           (0,0),(-1,-1), 1, C_VERDE),
    ]))
    story.append(pb)
    story.append(Spacer(1, 6*mm))

    # — FIRMAS —
    story.append(sec_tit("✍️ FIRMAS Y ACEPTACIÓN"))
    story.append(Spacer(1, 8*mm))
    fw = W * 0.40
    hw = W * 0.10
    sp = W * 0.10

    t_emp = Table([
        [Paragraph("_" * 44, s_fn)],
        [Paragraph(res["empleado"], s_fn)],
        [Paragraph(f"C.C. {res['cedula']}", s_fs)],
        [Paragraph("EMPLEADO(A)", s_fs)],
    ], colWidths=[fw])

    t_hue = Table([
        [Paragraph(" ", s_fn)],
        [Paragraph(" ", s_fn)],
        [Paragraph("HUELLA\nDACTILAR", s_fs)],
    ], colWidths=[hw])
    t_hue.setStyle(TableStyle([
        ("BOX",        (0,0),(-1,-1), 0.8, C_GRIS_MEDIO),
        ("BACKGROUND", (0,0),(-1,-1), C_GRIS_CLARO),
        ("TOPPADDING", (0,0),(-1,-1), 14),
        ("BOTTOMPADDING",(0,0),(-1,-1), 14),
    ]))

    t_emp2 = Table([
        [Paragraph("_" * 44, s_fn)],
        [Paragraph(res["empresa"][:35], s_fn)],
        [Paragraph("Representante Legal", s_fs)],
        [Paragraph("EMPLEADOR", s_fs)],
    ], colWidths=[fw])

    firmas = Table([[t_emp, t_hue, Table([[""]], colWidths=[sp]), t_emp2]],
                   colWidths=[fw, hw, sp, fw])
    firmas.setStyle(TableStyle([("VALIGN",(0,0),(-1,-1),"BOTTOM")]))
    story.append(firmas)
    story.append(Spacer(1, 8*mm))

    # — PIE —
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_GRIS_MEDIO, spaceAfter=3))
    story.append(Paragraph(
        "NóminaRest · Colombia 2026 · Ley 2101/2021 · Decreto 2910/2024 (SMLMV $1.512.000) · "
        "Decreto 2911/2024 (Aux. Transporte $182.000) · CST Art. 168, 177, 65. "
        "Este documento no reemplaza la asesoría de un contador o abogado laboral certificado.",
        s_foot
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()
