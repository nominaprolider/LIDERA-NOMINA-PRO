"""
pdf_generator.py — Comprobante de nómina · Asistente de Nómina Blindada
Diseño Verde Oscuro Profesional · ReportLab · Colombia 2026.
"""

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ── PALETA VERDE OSCURO PROFESIONAL ────────────────────────────────
C_VERDE_OSC = HexColor("#1B5E20")
C_VERDE_MED = HexColor("#2E7D32")
C_VERDE_SUAVE = HexColor("#43A047")
C_VERDE_CLARO = HexColor("#E8F5E9")
C_VERDE_INPUT = HexColor("#F1F8F4")
C_GRIS_SEDA = HexColor("#F5F7F4")
C_GRIS_BORDE = HexColor("#C5D8C8")
C_TEXTO = HexColor("#1B3A1F")
C_TEXTO_SOFT = HexColor("#4F6B53")
C_ROJO = HexColor("#C62828")
C_ROJO_SOFT = HexColor("#FFEBEE")
C_AMBAR = HexColor("#F9A825")
C_AMBAR_SOFT = HexColor("#FFF8E1")
C_BLANCO = white


def _fmt(n) -> str:
    return f"${int(n):,}".replace(",", ".")


def generar_pdf(res: dict) -> bytes:
    buf = io.BytesIO()
    periodo_str = (
        f"{res['periodo_inicio'].strftime('%d/%m/%Y')} — "
        f"{res['periodo_fin'].strftime('%d/%m/%Y')}"
    )

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=12 * mm,
        bottomMargin=15 * mm,
        title=f"Comprobante de Nómina — {res['empleado']}",
    )
    W = 180 * mm

    def sty(name, **kw):
        base = dict(fontName="Helvetica", fontSize=9, leading=13, textColor=C_TEXTO)
        base.update(kw)
        return ParagraphStyle(name, **base)

    s_hdr = sty(
        "hdr", fontSize=18, textColor=C_BLANCO, fontName="Helvetica-Bold", leading=22
    )
    s_hsub = sty(
        "hsub",
        fontSize=8.5,
        textColor=HexColor("#C8E6C9"),
        alignment=TA_RIGHT,
        leading=13,
    )
    s_sec = sty(
        "sec", fontSize=9.5, textColor=C_BLANCO, fontName="Helvetica-Bold", leftIndent=4
    )
    s_lbl = sty("lbl", textColor=C_TEXTO_SOFT)
    s_val = sty("val", fontName="Helvetica-Bold")
    s_nl = sty(
        "nl", fontSize=12.5, textColor=C_BLANCO, fontName="Helvetica-Bold", leading=16
    )
    s_nv = sty(
        "nv",
        fontSize=22,
        textColor=HexColor("#C8E6C9"),
        fontName="Helvetica-Bold",
        alignment=TA_RIGHT,
        leading=26,
    )
    s_paz = sty(
        "paz",
        fontSize=9,
        fontName="Helvetica-Oblique",
        alignment=TA_JUSTIFY,
        leading=13.5,
    )
    s_fn = sty("fn", fontSize=8.5, fontName="Helvetica-Bold", alignment=TA_CENTER)
    s_fs = sty("fs", fontSize=7.5, textColor=C_TEXTO_SOFT, alignment=TA_CENTER)
    s_th = sty(
        "th",
        fontSize=8.5,
        textColor=C_BLANCO,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        leading=11,
    )
    s_th_d = sty(
        "thd",
        fontSize=8.5,
        textColor=C_BLANCO,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        leading=11,
    )
    s_tcell_l = sty("tcl", fontSize=8, textColor=C_TEXTO, alignment=TA_LEFT, leading=11)
    s_tcell_r = sty(
        "tcr",
        fontSize=8,
        fontName="Helvetica-Bold",
        textColor=C_VERDE_OSC,
        alignment=TA_RIGHT,
        leading=11,
    )
    s_tcell_rd = sty(
        "trd",
        fontSize=8,
        fontName="Helvetica-Bold",
        textColor=C_ROJO,
        alignment=TA_RIGHT,
        leading=11,
    )
    s_tot_l = sty(
        "totl",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=C_BLANCO,
        alignment=TA_LEFT,
        leading=12,
    )
    s_tot_r = sty(
        "totr",
        fontSize=9,
        fontName="Helvetica-Bold",
        textColor=C_BLANCO,
        alignment=TA_RIGHT,
        leading=12,
    )
    s_t_th = sty(
        "tth",
        fontSize=7,
        textColor=C_BLANCO,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
        leading=9,
    )
    s_t_tc = sty("ttc", fontSize=7, alignment=TA_CENTER, leading=9)
    s_foot = sty(
        "foot",
        fontSize=6.8,
        textColor=C_TEXTO_SOFT,
        fontName="Helvetica-Oblique",
        alignment=TA_CENTER,
        leading=10,
    )
    s_saldo = sty(
        "saldo",
        fontSize=10,
        fontName="Helvetica-Bold",
        textColor=C_TEXTO,
        alignment=TA_LEFT,
        leading=14,
    )
    s_incap = sty("incap", fontSize=8.5, textColor=C_TEXTO, leading=12)

    story = []

    # ── HEADER ───────────────────────────────────────────────
    ht = Table(
        [
            [
                Paragraph("COMPROBANTE DE NÓMINA", s_hdr),
                Paragraph(
                    f"{res['empresa']}<br/>NIT/CC: {res.get('nit', '—')}<br/>Colombia 2026",
                    s_hsub,
                ),
            ]
        ],
        colWidths=[W * 0.6, W * 0.4],
    )
    ht.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_VERDE_OSC),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (0, -1), 14),
                ("RIGHTPADDING", (1, 0), (1, -1), 12),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(ht)

    banda = Table([[""]], colWidths=[W], rowHeights=[5 * mm])
    banda.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), C_VERDE_SUAVE)]))
    story.append(banda)
    story.append(Spacer(1, 5 * mm))

    def sec_tit(txt):
        t = Table([[Paragraph(f"  {txt}", s_sec)]], colWidths=[W])
        t.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), C_VERDE_OSC),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        return t

    def fila_d(label, valor, alt=False):
        bg = C_GRIS_SEDA if alt else C_BLANCO
        r = Table(
            [[Paragraph(f"  {label}", s_lbl), Paragraph(f"  {valor}", s_val)]],
            colWidths=[W * 0.45, W * 0.55],
        )
        r.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, -1), bg),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ]
            )
        )
        return r

    # ── INFORMACIÓN GENERAL ──────────────────────────────────
    story.append(sec_tit("INFORMACIÓN DEL TRABAJADOR Y EL PERÍODO"))
    story.append(Spacer(1, 1 * mm))
    alt = True
    for lbl, val in [
        ("Trabajador", res["empleado"]),
        ("Cédula", res["cedula"]),
        ("Empresa / Restaurante", res["empresa"]),
        ("Tipo de Salario", res["tipo_salario"]),
        ("Período Liquidado", periodo_str),
        ("Días del Período", str(res["dias_laborados"])),
        ("Días Efectivamente Trabajados", str(res["dias_efectivos"])),
        ("Días que Faltó (sin justificación)", str(res["dias_no_laborados"])),
        ("Días que Estuvo Enfermo", str(res["incapacidades"])),
    ]:
        story.append(fila_d(lbl, val, alt))
        alt = not alt
    story.append(Spacer(1, 4 * mm))

    # ════════════════════════════════════════════════════════
    # TABLA: LO QUE RECIBE / DESCUENTOS REALIZADOS
    # ════════════════════════════════════════════════════════
    devengados = [("Salario base del período", res["salario_base_calc"])]
    if res["aux_transporte"]:
        devengados.append(
            (
                f"Auxilio de Transporte (proporcional · {res['dias_efectivos']}d)",
                res["aux_transporte"],
            )
        )
    if res["comisiones"]:
        devengados.append(("Comisiones (suman al salario)", res["comisiones"]))
    if res["bonif_no_salariales"]:
        devengados.append(
            ("Bonificaciones (no salariales)", res["bonif_no_salariales"])
        )
    if res.get("auxilio_incapacidad", 0):
        tag = (
            " · 100% (mín. protegido)"
            if res.get("devenga_smlmv") and res.get("dias_incap_eps", 0) > 0
            else ""
        )
        devengados.append(
            (
                f"Pago días enfermo ({res['dias_incap_empleador']}d emp.+{res['dias_incap_eps']}d EPS){tag}",
                res["auxilio_incapacidad"],
            )
        )
    if res["recargo_nocturno"]:
        devengados.append(
            (
                f"Recargo Nocturno (35%) {res['horas_nocturnas']:.1f}h",
                res["recargo_nocturno"],
            )
        )
    if res["recargo_dominical"]:
        devengados.append(
            (
                f"Recargo Domingo/Festivo (100%) {res['horas_dominical']:.1f}h",
                res["recargo_dominical"],
            )
        )
    if res["he_diurnas_valor"]:
        devengados.append(
            (
                f"Horas Extra Diurnas (25%) {res['he_diurnas_horas']:.1f}h",
                res["he_diurnas_valor"],
            )
        )
    if res["he_nocturnas_valor"]:
        devengados.append(
            (
                f"Horas Extra Nocturnas (75%) {res['he_nocturnas_horas']:.1f}h",
                res["he_nocturnas_valor"],
            )
        )

    deducciones = [
        (f"Salud (4% sobre {_fmt(res['base_ss'])})", res["salud"]),
        (f"Pensión (4% sobre {_fmt(res['base_ss'])})", res["pension"]),
    ]
    if res.get("desc_falta_dominical", 0):
        deducciones.append(
            ("Descuento por el domingo perdido (Art. 173)", res["desc_falta_dominical"])
        )
    if res["prestamos"]:
        deducciones.append(("Préstamo / Adelanto", res["prestamos"]))
    if res["sanciones"]:
        deducciones.append(("Multa o sanción disciplinaria", res["sanciones"]))

    n_filas = max(len(devengados), len(deducciones))

    rows = [
        [
            Paragraph("LO QUE EL TRABAJADOR RECIBE", s_th),
            Paragraph("VALOR", s_th),
            Paragraph("DESCUENTOS REALIZADOS", s_th_d),
            Paragraph("VALOR", s_th_d),
        ]
    ]
    for i in range(n_filas):
        d = devengados[i] if i < len(devengados) else ("", 0)
        de = deducciones[i] if i < len(deducciones) else ("", 0)
        rows.append(
            [
                Paragraph(d[0], s_tcell_l) if d[0] else Paragraph("", s_tcell_l),
                Paragraph(f"+ {_fmt(d[1])}", s_tcell_r)
                if d[0]
                else Paragraph("", s_tcell_r),
                Paragraph(de[0], s_tcell_l) if de[0] else Paragraph("", s_tcell_l),
                Paragraph(f"− {_fmt(de[1])}", s_tcell_rd)
                if de[0]
                else Paragraph("", s_tcell_rd),
            ]
        )
    rows.append(
        [
            Paragraph("TOTAL QUE RECIBE", s_tot_l),
            Paragraph(f"+ {_fmt(res['total_devengado'])}", s_tot_r),
            Paragraph("TOTAL DESCONTADO", s_tot_l),
            Paragraph(f"− {_fmt(res['total_deducciones'])}", s_tot_r),
        ]
    )

    cw = [W * 0.32, W * 0.18, W * 0.32, W * 0.18]
    tbl = Table(rows, colWidths=cw, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (1, 0), C_VERDE_OSC),
        ("BACKGROUND", (2, 0), (3, 0), C_ROJO),
        ("BACKGROUND", (0, -1), (1, -1), C_VERDE_OSC),
        ("BACKGROUND", (2, -1), (3, -1), C_ROJO),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, C_BLANCO),
        ("GRID", (0, 1), (-1, -2), 0.3, C_GRIS_BORDE),
        ("BOX", (0, 0), (-1, -1), 0.5, C_GRIS_BORDE),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for r in range(1, len(rows) - 1):
        if r % 2 == 0:
            ts.append(("BACKGROUND", (0, r), (1, r), C_VERDE_CLARO))
            ts.append(("BACKGROUND", (2, r), (3, r), C_ROJO_SOFT))
    tbl.setStyle(TableStyle(ts))
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))

    # ── DESGLOSE DE INCAPACIDAD (¿Quién paga cada día?) ──────
    if res["incapacidades"] > 0:
        story.append(sec_tit("DETALLE DE PAGO POR INCAPACIDAD (¿QUIÉN PAGA CADA DÍA?)"))
        story.append(Spacer(1, 1.5 * mm))

        if res.get("devenga_smlmv") and res.get("dias_incap_eps", 0) > 0:
            nota_smlmv = (
                "<b>⚠ Protección al Salario Mínimo:</b> al ganar el SMLMV, "
                "todos los días de incapacidad se pagan al <b>100%</b> del salario "
                "diario (no se aplica la reducción al 66.67%), garantizando el mínimo vital."
            )
        else:
            nota_smlmv = ""

        i_rows = [
            [
                Paragraph("DÍAS", s_t_th),
                Paragraph("RESPONSABLE", s_t_th),
                Paragraph("PORCENTAJE", s_t_th),
                Paragraph("VALOR PAGADO", s_t_th),
            ]
        ]
        if res["dias_incap_empleador"] > 0:
            i_rows.append(
                [
                    Paragraph(f"Día 1 a {res['dias_incap_empleador']}", s_t_tc),
                    Paragraph("EMPLEADOR", s_t_tc),
                    Paragraph("100%", s_t_tc),
                    Paragraph(_fmt(res["auxilio_incap_empleador"]), s_t_tc),
                ]
            )
        if res["dias_incap_eps"] > 0:
            pct_str = "100% (mín. protegido)" if res.get("devenga_smlmv") else "66.67%"
            i_rows.append(
                [
                    Paragraph(
                        f"Día 3 a {res['dias_incap_empleador'] + res['dias_incap_eps']}",
                        s_t_tc,
                    ),
                    Paragraph("EPS", s_t_tc),
                    Paragraph(pct_str, s_t_tc),
                    Paragraph(_fmt(res["auxilio_incap_eps"]), s_t_tc),
                ]
            )
        i_tbl = Table(
            i_rows, colWidths=[W * 0.18, W * 0.27, W * 0.27, W * 0.28], repeatRows=1
        )
        i_tbl.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), C_VERDE_OSC),
                    ("GRID", (0, 0), (-1, -1), 0.3, C_GRIS_BORDE),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_BLANCO, C_VERDE_CLARO]),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        story.append(i_tbl)
        if nota_smlmv:
            story.append(Spacer(1, 2 * mm))
            nb = Table([[Paragraph(nota_smlmv, s_incap)]], colWidths=[W])
            nb.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), C_AMBAR_SOFT),
                        ("BOX", (0, 0), (-1, -1), 0.8, C_AMBAR),
                        ("LEFTPADDING", (0, 0), (-1, -1), 10),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                        ("TOPPADDING", (0, 0), (-1, -1), 8),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                    ]
                )
            )
            story.append(nb)
        story.append(Spacer(1, 5 * mm))

    # ── NETO A PAGAR ─────────────────────────────────────────
    nt = Table(
        [
            [
                Paragraph("NETO A PAGAR AL TRABAJADOR", s_nl),
                Paragraph(f"{_fmt(res['neto_a_pagar'])} COP", s_nv),
            ]
        ],
        colWidths=[W * 0.5, W * 0.5],
    )
    nt.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_VERDE_OSC),
                ("TOPPADDING", (0, 0), (-1, -1), 16),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 16),
                ("LEFTPADDING", (0, 0), (0, -1), 14),
                ("RIGHTPADDING", (1, 0), (1, -1), 14),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(nt)
    story.append(Spacer(1, 4 * mm))

    # ── SALDO PRÉSTAMO ───────────────────────────────────────
    saldo_box = Table(
        [
            [
                Paragraph(
                    f"Saldo de Préstamo Pendiente:  <font color='#C62828'>"
                    f"<b>{_fmt(res['saldo_prestamo_pendiente'])} COP</b></font>",
                    s_saldo,
                )
            ]
        ],
        colWidths=[W],
    )
    saldo_box.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_AMBAR_SOFT),
                ("BOX", (0, 0), (-1, -1), 0.8, C_AMBAR),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(saldo_box)
    story.append(Spacer(1, 5 * mm))

    # ── DESGLOSE DE TURNOS ──────────────────────────────────
    if res.get("detalle_turnos"):
        story.append(sec_tit("DESGLOSE DE TURNOS TRABAJADOS"))
        story.append(Spacer(1, 1.5 * mm))
        headers = [
            "Fecha",
            "Tipo",
            "Entrada",
            "Salida",
            "Hs Ord",
            "Hs Noc",
            "Dom/F",
            "HE D.",
            "HE N.",
            "Valor",
        ]
        cws = [
            22 * mm,
            28 * mm,
            15 * mm,
            15 * mm,
            12 * mm,
            12 * mm,
            12 * mm,
            12 * mm,
            12 * mm,
            20 * mm,
        ]
        td = [[Paragraph(h, s_t_th) for h in headers]]
        for row in res["detalle_turnos"]:
            tr = []
            for i, cell in enumerate(row):
                if i == 9 and isinstance(cell, (int, float)):
                    tr.append(Paragraph(_fmt(int(cell)), s_t_tc))
                else:
                    tr.append(Paragraph(str(cell), s_t_tc))
            td.append(tr)
        tt = Table(td, colWidths=cws, repeatRows=1)
        tt.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), C_VERDE_OSC),
                    ("GRID", (0, 0), (-1, -1), 0.3, C_GRIS_BORDE),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [C_BLANCO, C_GRIS_SEDA]),
                    ("TOPPADDING", (0, 0), (-1, -1), 3),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ]
            )
        )
        story.append(tt)
        story.append(Spacer(1, 5 * mm))

    # ── PRESTACIONES SOCIALES (COSTO MENSUAL EMPLEADOR) ─────
    story.append(
        sec_tit("PRESTACIONES SOCIALES Y COSTO TOTAL MENSUAL (A CARGO DEL EMPLEADOR)")
    )
    story.append(Spacer(1, 1.5 * mm))

    p_rows = [
        [
            Paragraph("CONCEPTO", s_t_th),
            Paragraph("BASE / TASA", s_t_th),
            Paragraph("VALOR MENSUAL", s_t_th),
        ]
    ]
    for label, base, val in [
        ("Cesantías", "8.33% sobre salario + aux.", res["cesantias"]),
        (
            "Intereses sobre Cesantías",
            "12% anual sobre cesantías",
            res["intereses_cesantias"],
        ),
        ("Prima de Servicios", "8.33% sobre salario + aux.", res["prima_servicios"]),
        ("Vacaciones", "4.17% sobre salario", res["vacaciones"]),
        ("Salud (Empleador)", "8.5% sobre salario", res["salud_empleador"]),
        ("Pensión (Empleador)", "12% sobre salario", res["pension_empleador"]),
        ("ARL (Clase I, referencia)", "0.522% sobre salario", res["arl"]),
    ]:
        p_rows.append(
            [
                Paragraph(label, s_t_tc),
                Paragraph(base, s_t_tc),
                Paragraph(_fmt(val), s_t_tc),
            ]
        )
    p_rows.append(
        [
            Paragraph("TOTAL PRESTACIONES + APORTES EMPLEADOR", s_tot_l),
            Paragraph("", s_tot_l),
            Paragraph(
                f"+ {_fmt(res['total_prestaciones'] + res['aportes_empleador'])}",
                s_tot_r,
            ),
        ]
    )
    p_tbl = Table(p_rows, colWidths=[W * 0.32, W * 0.43, W * 0.25], repeatRows=1)
    p_tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), C_VERDE_OSC),
                ("BACKGROUND", (0, -1), (-1, -1), C_VERDE_OSC),
                ("GRID", (0, 1), (-1, -2), 0.3, C_GRIS_BORDE),
                ("BOX", (0, 0), (-1, -1), 0.5, C_GRIS_BORDE),
                ("ROWBACKGROUNDS", (0, 1), (-1, -2), [C_BLANCO, C_VERDE_CLARO]),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(p_tbl)
    story.append(Spacer(1, 3 * mm))

    ct = Table(
        [
            [
                Paragraph("COSTO TOTAL MENSUAL DEL TRABAJADOR", s_nl),
                Paragraph(f"{_fmt(res['costo_total_mes'])} COP", s_nv),
            ]
        ],
        colWidths=[W * 0.55, W * 0.45],
    )
    ct.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_VERDE_MED),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (0, -1), 14),
                ("RIGHTPADDING", (1, 0), (1, -1), 14),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]
        )
    )
    story.append(ct)
    story.append(Spacer(1, 5 * mm))

    # ── PAZ Y SALVO BLINDADA ────────────────────────────────
    story.append(sec_tit("CLÁUSULA DE PAZ Y SALVO BLINDADA · ART. 65 C.S.T."))
    story.append(Spacer(1, 2 * mm))
    texto_paz = (
        f"Yo, <b>{res['empleado']}</b>, identificado(a) con cédula de ciudadanía "
        f"No. <b>{res['cedula']}</b>, declaro que recibo este pago a entera satisfacción, "
        f"que los cálculos se ajustan a la <b>Ley 2026</b> (Decreto 2910/2024 SMLMV, "
        f"Decreto 2911/2024 Auxilio de Transporte, Ley 2101/2021 jornada de 42 horas, "
        f"y CST Art. 65, 168, 173, 177 y 179) y que me encuentro a "
        f"<b>PAZ Y SALVO</b> con mi empleador <b>{res['empresa']}</b> por el período "
        f"liquidado <b>{periodo_str}</b>, por concepto de salarios, recargos, horas extras, "
        f"comisiones, auxilio de transporte, auxilio de incapacidad y demás emolumentos "
        f"derivados de la relación laboral durante dicho período, renunciando expresamente "
        f"a cualquier reclamación posterior por estos conceptos."
    )
    pb = Table([[Paragraph(texto_paz, s_paz)]], colWidths=[W])
    pb.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), C_VERDE_CLARO),
                ("TOPPADDING", (0, 0), (-1, -1), 12),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
                ("LEFTPADDING", (0, 0), (-1, -1), 14),
                ("RIGHTPADDING", (0, 0), (-1, -1), 14),
                ("BOX", (0, 0), (-1, -1), 1.2, C_VERDE_OSC),
            ]
        )
    )
    story.append(pb)
    story.append(Spacer(1, 9 * mm))

    # ── FIRMAS Y HUELLA ─────────────────────────────────────
    story.append(sec_tit("FIRMAS Y ACEPTACIÓN"))
    story.append(Spacer(1, 11 * mm))
    fw = W * 0.40
    hw = W * 0.10
    sp = W * 0.10

    t_emp = Table(
        [
            [Paragraph("_" * 44, s_fn)],
            [Paragraph(res["empleado"], s_fn)],
            [Paragraph(f"C.C. {res['cedula']}", s_fs)],
            [Paragraph("TRABAJADOR(A)", s_fs)],
        ],
        colWidths=[fw],
    )

    t_hue = Table(
        [
            [Paragraph(" ", s_fn)],
            [Paragraph(" ", s_fn)],
            [Paragraph("HUELLA<br/>DACTILAR", s_fs)],
        ],
        colWidths=[hw],
    )
    t_hue.setStyle(
        TableStyle(
            [
                ("BOX", (0, 0), (-1, -1), 1, C_VERDE_OSC),
                ("BACKGROUND", (0, 0), (-1, -1), C_VERDE_INPUT),
                ("TOPPADDING", (0, 0), (-1, -1), 14),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 14),
            ]
        )
    )

    t_emp2 = Table(
        [
            [Paragraph("_" * 44, s_fn)],
            [Paragraph(res["empresa"][:35], s_fn)],
            [Paragraph("Representante Legal", s_fs)],
            [Paragraph("EMPLEADOR", s_fs)],
        ],
        colWidths=[fw],
    )

    firmas = Table(
        [[t_emp, t_hue, Table([[""]], colWidths=[sp]), t_emp2]],
        colWidths=[fw, hw, sp, fw],
    )
    firmas.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "BOTTOM")]))
    story.append(firmas)
    story.append(Spacer(1, 8 * mm))

    # ── PIE ─────────────────────────────────────────────────
    story.append(
        HRFlowable(width="100%", thickness=0.5, color=C_VERDE_SUAVE, spaceAfter=3)
    )
    story.append(
        Paragraph(
            "Asistente de Nómina Blindada · Colombia 2026 · Verde Profesional · "
            "Ley 2101/2021 · Decreto 2910/2024 (SMLMV $1.512.000) · "
            "Decreto 2911/2024 (Aux. Transporte $182.000) · CST Art. 65, 168, 173, 177, 179. "
            "Esta herramienta no reemplaza la asesoría de un contador o abogado laboral certificado.",
            s_foot,
        )
    )

    doc.build(story)
    buf.seek(0)
    return buf.read()
