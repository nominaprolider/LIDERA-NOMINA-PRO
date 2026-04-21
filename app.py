import streamlit as st
from datetime import datetime, date, time
import pandas as pd
from logic import calcular_nomina, SMLMV_2026, AUX_TRANSPORTE, VALOR_HORA_MIN
from pdf_generator import generar_pdf
import base64
import urllib.parse
import json

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NóminaRest · Colombia 2026",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

:root {
    --verde: #00C896;
    --verde-dark: #009E76;
    --rojo: #FF4B4B;
    --amarillo: #FFD166;
    --bg: #0D1117;
    --bg2: #161B22;
    --bg3: #21262D;
    --borde: #30363D;
    --texto: #E6EDF3;
    --texto2: #8B949E;
    --blanco: #FFFFFF;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--texto) !important;
}

h1, h2, h3, .syne { font-family: 'Syne', sans-serif !important; }

/* HEADER */
.header-band {
    background: linear-gradient(135deg, #00C896 0%, #009E76 50%, #006B52 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 28px;
    display: flex; align-items: center; gap: 18px;
}
.header-band h1 { color: #fff !important; font-size: 2rem; margin: 0; }
.header-band p { color: rgba(255,255,255,0.82); margin: 0; font-size: 0.95rem; }

/* BADGES LEGALES */
.badge-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 24px; }
.badge {
    background: var(--bg3); border: 1px solid var(--borde);
    border-radius: 8px; padding: 8px 14px; font-size: 0.8rem;
    display: flex; align-items: center; gap: 6px;
}
.badge-green { border-color: var(--verde); color: var(--verde); }
.badge-yellow { border-color: var(--amarillo); color: var(--amarillo); }

/* CARDS */
.card {
    background: var(--bg2); border: 1px solid var(--borde);
    border-radius: 14px; padding: 22px;
    margin-bottom: 16px;
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--verde); margin-bottom: 16px;
    display: flex; align-items: center; gap: 8px;
}

/* RESULT ROWS */
.result-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 0; border-bottom: 1px solid var(--borde);
    font-size: 0.92rem;
}
.result-row:last-child { border-bottom: none; }
.result-label { color: var(--texto2); }
.result-value { font-weight: 600; color: var(--texto); }
.result-value.positive { color: var(--verde); }
.result-value.negative { color: var(--rojo); }

/* TOTAL BOX */
.total-box {
    background: linear-gradient(135deg, var(--verde) 0%, var(--verde-dark) 100%);
    border-radius: 14px; padding: 24px;
    text-align: center; margin-top: 12px;
}
.total-box .label { color: rgba(255,255,255,0.8); font-size: 0.85rem; margin-bottom: 4px; }
.total-box .amount { color: #fff; font-size: 2.2rem; font-weight: 800; font-family: 'Syne', sans-serif; }

/* ALERT */
.alert-error {
    background: rgba(255,75,75,0.12); border: 1px solid var(--rojo);
    border-radius: 10px; padding: 14px; color: var(--rojo); font-size: 0.88rem;
}
.alert-warning {
    background: rgba(255,209,102,0.1); border: 1px solid var(--amarillo);
    border-radius: 10px; padding: 14px; color: var(--amarillo); font-size: 0.88rem;
}

/* INPUTS */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > div,
.stDateInput > div > div > input {
    background-color: var(--bg3) !important;
    border: 1px solid var(--borde) !important;
    color: var(--texto) !important;
    border-radius: 8px !important;
}

.stButton > button {
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--verde), var(--verde-dark)) !important;
    border: none !important;
    color: white !important;
}
.stButton > button[kind="secondary"] {
    background: var(--bg3) !important;
    border: 1px solid var(--borde) !important;
    color: var(--texto) !important;
}

/* DIVIDER */
hr { border-color: var(--borde) !important; }

/* SHIFT TABLE */
.turno-row {
    background: var(--bg3); border-radius: 8px; padding: 10px 14px;
    margin-bottom: 8px; display: flex; justify-content: space-between;
    align-items: center; font-size: 0.88rem;
}

/* HIDE STREAMLIT DEFAULTS */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1100px; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-band">
  <div style="font-size:2.5rem">🍽️</div>
  <div>
    <h1>NóminaRest · Colombia</h1>
    <p>Liquidador de nómina y turnos · Blindado legalmente · Normativa 2026</p>
  </div>
</div>
""", unsafe_allow_html=True)

# Badges legales
st.markdown(f"""
<div class="badge-row">
  <div class="badge badge-green">✅ SMLMV 2026: ${SMLMV_2026:,.0f}</div>
  <div class="badge badge-green">✅ Aux. Transporte: $182.000</div>
  <div class="badge badge-yellow">⚖️ Jornada 42h/sem · Ley 2101/2021</div>
  <div class="badge badge-yellow">🌙 Recargo nocturno desde 19:00h</div>
  <div class="badge badge-yellow">📅 Dom/Festivo: +100%</div>
</div>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "turnos" not in st.session_state:
    st.session_state.turnos = []
if "resultado" not in st.session_state:
    st.session_state.resultado = None

# ── LAYOUT: 2 COLUMNAS ───────────────────────────────────────────────────────
col_izq, col_der = st.columns([1, 1], gap="large")

# ═══════════════════════════════════════════════════════════════
# COLUMNA IZQUIERDA — FORMULARIO
# ═══════════════════════════════════════════════════════════════
with col_izq:

    # — DATOS EMPRESA/EMPLEADO —
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">🏢 Datos del Empleador y Empleado</div>', unsafe_allow_html=True)

    empresa = st.text_input("Nombre del Restaurante / Empresa", placeholder="Ej: Restaurante El Fogón S.A.S.")
    nit = st.text_input("NIT / Cédula del Empleador", placeholder="900.123.456-7")

    c1, c2 = st.columns(2)
    with c1:
        empleado = st.text_input("Nombre Completo del Empleado", placeholder="Juan Pérez García")
    with c2:
        cedula = st.text_input("Cédula del Empleado", placeholder="1.000.123.456")

    periodo_inicio = st.date_input("Inicio del Período", value=date.today().replace(day=1))
    periodo_fin = st.date_input("Fin del Período", value=date.today())
    st.markdown('</div>', unsafe_allow_html=True)

    # — TIPO DE SALARIO —
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">💰 Salario y Comisiones</div>', unsafe_allow_html=True)

    tipo_salario = st.selectbox("Tipo de Salario", ["Fijo Mensual", "Por Horas / Turnos"])

    if tipo_salario == "Fijo Mensual":
        salario_base = st.number_input(
            "Salario Base Mensual (COP)",
            min_value=0, value=int(SMLMV_2026), step=10000,
            format="%d"
        )
        if salario_base > 0 and salario_base < SMLMV_2026:
            st.markdown(f'<div class="alert-error">⚠️ El salario no puede ser inferior al SMLMV (${SMLMV_2026:,.0f})</div>', unsafe_allow_html=True)
        dias_laborados = st.number_input("Días laborados en el período", min_value=1, max_value=30, value=30)
    else:
        valor_hora = st.number_input(
            "Valor por Hora Ordinaria (COP)",
            min_value=0, value=7200, step=100, format="%d"
        )
        if valor_hora > 0 and valor_hora < VALOR_HORA_MIN:
            st.markdown(f'<div class="alert-error">⚠️ El valor hora mínimo es ${VALOR_HORA_MIN:,.0f} COP</div>', unsafe_allow_html=True)
        salario_base = 0
        dias_laborados = 30

    comisiones = st.number_input("Comisiones / Bonificaciones (COP)", min_value=0, value=0, step=1000, format="%d")
    st.markdown('</div>', unsafe_allow_html=True)

    # — REGISTRO DE TURNOS —
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">⏰ Agregar Turno Trabajado</div>', unsafe_allow_html=True)

    tc1, tc2 = st.columns(2)
    with tc1:
        turno_fecha = st.date_input("Fecha del Turno", key="t_fecha")
        tipo_dia = st.selectbox("Tipo de Día", ["Ordinario (L-S)", "Domingo", "Festivo"], key="t_tipo")
    with tc2:
        hora_entrada = st.time_input("Hora Entrada", value=time(8, 0), key="t_entrada")
        hora_salida = st.time_input("Hora Salida", value=time(16, 0), key="t_salida")

    if st.button("➕ Agregar Turno", use_container_width=True, type="primary"):
        if hora_salida <= hora_entrada:
            st.error("La hora de salida debe ser posterior a la entrada.")
        else:
            st.session_state.turnos.append({
                "fecha": turno_fecha.strftime("%d/%m/%Y"),
                "tipo_dia": tipo_dia,
                "entrada": hora_entrada.strftime("%H:%M"),
                "salida": hora_salida.strftime("%H:%M"),
            })
            st.success("✅ Turno agregado")

    # Mostrar turnos
    if st.session_state.turnos:
        st.markdown("**Turnos registrados:**")
        for i, t in enumerate(st.session_state.turnos):
            cols = st.columns([3, 2, 2, 2, 0.7])
            cols[0].caption(t["fecha"])
            cols[1].caption(t["tipo_dia"])
            cols[2].caption(f"{t['entrada']}")
            cols[3].caption(f"→ {t['salida']}")
            if cols[4].button("🗑", key=f"del_{i}"):
                st.session_state.turnos.pop(i)
                st.rerun()

        if st.button("🗑 Limpiar todos los turnos", type="secondary", use_container_width=True):
            st.session_state.turnos = []
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # — CALCULAR —
    st.markdown("---")
    if st.button("🧮 CALCULAR NÓMINA", use_container_width=True, type="primary"):
        errores = []
        if not empresa.strip(): errores.append("• Ingresa el nombre del restaurante")
        if not empleado.strip(): errores.append("• Ingresa el nombre del empleado")
        if not cedula.strip(): errores.append("• Ingresa la cédula del empleado")
        if tipo_salario == "Fijo Mensual" and salario_base < SMLMV_2026:
            errores.append(f"• Salario inferior al SMLMV (${SMLMV_2026:,.0f})")
        if tipo_salario == "Por Horas / Turnos":
            if valor_hora < VALOR_HORA_MIN:
                errores.append(f"• Valor hora inferior al mínimo (${VALOR_HORA_MIN:,.0f})")
            if not st.session_state.turnos:
                errores.append("• Agrega al menos un turno")

        if errores:
            st.markdown(f'<div class="alert-error">{"<br>".join(errores)}</div>', unsafe_allow_html=True)
        else:
            params = {
                "empresa": empresa,
                "nit": nit,
                "empleado": empleado,
                "cedula": cedula,
                "periodo_inicio": periodo_inicio,
                "periodo_fin": periodo_fin,
                "tipo_salario": tipo_salario,
                "salario_base": salario_base if tipo_salario == "Fijo Mensual" else 0,
                "valor_hora": valor_hora if tipo_salario == "Por Horas / Turnos" else 0,
                "dias_laborados": dias_laborados,
                "comisiones": comisiones,
                "turnos": st.session_state.turnos,
            }
            st.session_state.resultado = calcular_nomina(params)
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# COLUMNA DERECHA — RESULTADOS
# ═══════════════════════════════════════════════════════════════
with col_der:
    res = st.session_state.resultado

    if res is None:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 48px 24px;">
          <div style="font-size:4rem; margin-bottom:16px">📊</div>
          <div style="font-family:'Syne',sans-serif; font-size:1.2rem; color:#8B949E;">
            Completa el formulario y pulsa<br><strong style="color:#00C896">Calcular Nómina</strong>
          </div>
          <div style="margin-top:16px; font-size:0.82rem; color:#8B949E;">
            Los resultados aparecerán aquí en tiempo real
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── ENCABEZADO RESULTADO ──
        st.markdown(f"""
        <div class="card" style="border-color:#00C896">
          <div class="card-title">👤 {res['empleado']}</div>
          <div style="font-size:0.85rem; color:var(--texto2);">
            {res['empresa']} · CC {res['cedula']}<br>
            Período: {res['periodo_inicio'].strftime('%d/%m/%Y')} — {res['periodo_fin'].strftime('%d/%m/%Y')}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── DEVENGADO ──
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📈 Devengado</div>', unsafe_allow_html=True)

        items_devengado = [
            ("Salario Base", res["salario_base_calc"]),
            ("Auxilio de Transporte", res["aux_transporte"]),
        ]
        if res["comisiones"] > 0:
            items_devengado.append(("Comisiones / Bonificaciones", res["comisiones"]))
        if res["recargo_nocturno"] > 0:
            items_devengado.append((f"Recargo Nocturno (35%) · {res['horas_nocturnas']:.1f}h", res["recargo_nocturno"]))
        if res["recargo_dominical"] > 0:
            items_devengado.append((f"Recargo Dom/Festivo (100%) · {res['horas_dominical']:.1f}h", res["recargo_dominical"]))
        if res["he_diurnas_valor"] > 0:
            items_devengado.append((f"HE Diurnas (25%) · {res['he_diurnas_horas']:.1f}h", res["he_diurnas_valor"]))
        if res["he_nocturnas_valor"] > 0:
            items_devengado.append((f"HE Nocturnas (75%) · {res['he_nocturnas_horas']:.1f}h", res["he_nocturnas_valor"]))

        for label, val in items_devengado:
            st.markdown(f"""
            <div class="result-row">
              <span class="result-label">{label}</span>
              <span class="result-value positive">${val:,.0f}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-row" style="font-weight:700; font-size:1rem;">
          <span style="color:var(--texto)">Total Devengado</span>
          <span class="result-value positive">${res['total_devengado']:,.0f}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── DEDUCCIONES ──
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">📉 Deducciones</div>', unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-row">
          <span class="result-label">Salud (4%) sobre ${res['base_ss']:,.0f}</span>
          <span class="result-value negative">- ${res['salud']:,.0f}</span>
        </div>
        <div class="result-row">
          <span class="result-label">Pensión (4%) sobre ${res['base_ss']:,.0f}</span>
          <span class="result-value negative">- ${res['pension']:,.0f}</span>
        </div>
        <div class="result-row" style="font-weight:700; font-size:1rem;">
          <span style="color:var(--texto)">Total Deducciones</span>
          <span class="result-value negative">- ${res['total_deducciones']:,.0f}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── NETO A PAGAR ──
        st.markdown(f"""
        <div class="total-box">
          <div class="label">💵 NETO A PAGAR</div>
          <div class="amount">${res['neto_a_pagar']:,.0f} COP</div>
          <div style="color:rgba(255,255,255,0.7); font-size:0.8rem; margin-top:6px;">
            {res['empleado']} · {res['periodo_fin'].strftime('%B %Y').upper()}
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("")

        # ── DESGLOSE TURNOS ──
        if res.get("detalle_turnos"):
            with st.expander("📋 Ver desglose detallado de turnos"):
                df = pd.DataFrame(res["detalle_turnos"])
                df.columns = ["Fecha", "Tipo", "Entrada", "Salida", "Hrs Ord.", "Hrs Noc.", "Dom/Fest.", "HE Diur.", "HE Noct.", "Valor"]
                df["Valor"] = df["Valor"].apply(lambda x: f"${x:,.0f}")
                st.dataframe(df, use_container_width=True, hide_index=True)

        # ── BOTONES ACCIÓN ──
        st.markdown("---")
        b1, b2 = st.columns(2)

        with b1:
            if st.button("📄 Generar PDF", use_container_width=True, type="primary"):
                try:
                    pdf_bytes = generar_pdf(res)
                    b64 = base64.b64encode(pdf_bytes).decode()
                    nombre_archivo = f"Comprobante_{res['empleado'].replace(' ','_')}_{res['periodo_fin'].strftime('%Y%m')}.pdf"
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{nombre_archivo}" style="display:block;text-align:center;background:linear-gradient(135deg,#00C896,#009E76);color:white;padding:12px;border-radius:10px;font-family:Syne,sans-serif;font-weight:700;text-decoration:none;margin-top:8px;">⬇️ Descargar Comprobante PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generando PDF: {e}")

        with b2:
            if st.button("💬 Enviar por WhatsApp", use_container_width=True, type="secondary"):
                texto = (
                    f"🍽️ *COMPROBANTE DE NÓMINA*\n"
                    f"Restaurante: {res['empresa']}\n"
                    f"Empleado: {res['empleado']} (CC {res['cedula']})\n"
                    f"Período: {res['periodo_inicio'].strftime('%d/%m/%Y')} - {res['periodo_fin'].strftime('%d/%m/%Y')}\n\n"
                    f"💰 *LIQUIDACIÓN:*\n"
                    f"• Salario Base: ${res['salario_base_calc']:,.0f}\n"
                    f"• Aux. Transporte: ${res['aux_transporte']:,.0f}\n"
                    f"• Recargos: ${res['recargo_nocturno'] + res['recargo_dominical']:,.0f}\n"
                    f"• Horas Extras: ${res['he_diurnas_valor'] + res['he_nocturnas_valor']:,.0f}\n"
                    f"• Comisiones: ${res['comisiones']:,.0f}\n"
                    f"• Total Devengado: ${res['total_devengado']:,.0f}\n"
                    f"• Deducciones S.S.: -${res['total_deducciones']:,.0f}\n\n"
                    f"✅ *NETO A PAGAR: ${res['neto_a_pagar']:,.0f} COP*\n\n"
                    f"_Generado con NóminaRest · Normativa Colombia 2026_"
                )
                url_wa = f"https://wa.me/?text={urllib.parse.quote(texto)}"
                st.markdown(f'<a href="{url_wa}" target="_blank" style="display:block;text-align:center;background:#25D366;color:white;padding:12px;border-radius:10px;font-family:Syne,sans-serif;font-weight:700;text-decoration:none;margin-top:8px;">💬 Abrir WhatsApp</a>', unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center; color:#8B949E; font-size:0.78rem; padding:8px 0;">
  NóminaRest · Liquidador de Nómina para Restaurantes · Colombia 2026<br>
  Basado en: Ley 2101/2021 · Decreto 2910/2024 (SMLMV) · CST Art. 168, 177, 179<br>
  <em>Este sistema no reemplaza la asesoría de un contador o abogado laboral certificado.</em>
</div>
""", unsafe_allow_html=True)
