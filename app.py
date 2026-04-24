import streamlit as st
from datetime import datetime, date, time
import pandas as pd
from logic import calcular_nomina, SMLMV_2026, AUX_TRANSPORTE, VALOR_HORA_MIN
from pdf_generator import generar_pdf
import historial as hist
import base64
import urllib.parse

# ── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Asistente de Nómina Blindada · Colombia 2026",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CUSTOM CSS — PALETA VERDE OSCURO PROFESIONAL ──────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --verde-oscuro: #1B5E20;
    --verde-medio:  #2E7D32;
    --verde-suave:  #43A047;
    --verde-claro:  #E8F5E9;
    --verde-input:  #F1F8F4;
    --gris-seda:    #F5F7F4;
    --rojo:         #C62828;
    --rojo-soft:    #FFEBEE;
    --ambar:        #F9A825;
    --ambar-soft:   #FFF8E1;
    --bg:           #FAFCFA;
    --texto:        #1B3A1F;
    --texto-soft:   #4F6B53;
    --borde:        #C5D8C8;
    --blanco:       #FFFFFF;
}

html, body, [class*="css"], .stApp {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--texto) !important;
}

h1, h2, h3, h4, .syne { font-family: 'Syne', sans-serif !important; color: var(--verde-oscuro) !important; }

.header-band {
    background: linear-gradient(135deg, #1B5E20 0%, #2E7D32 60%, #43A047 100%);
    border-radius: 18px;
    padding: 30px 34px;
    margin-bottom: 26px;
    display: flex; align-items: center; gap: 20px;
    box-shadow: 0 6px 20px rgba(27,94,32,0.18);
}
.header-band h1 { color: #fff !important; font-size: 2.1rem; margin: 0; line-height: 1.1; }
.header-band p  { color: rgba(255,255,255,0.9); margin: 6px 0 0; font-size: 1rem; }

.badge-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 22px; }
.badge {
    background: var(--verde-claro); border: 1px solid var(--verde-suave);
    border-radius: 999px; padding: 7px 14px; font-size: 0.78rem;
    color: var(--verde-oscuro); font-weight: 600;
    display: inline-flex; align-items: center; gap: 6px;
}

.card {
    background: var(--blanco); border: 1px solid var(--borde);
    border-radius: 14px; padding: 20px;
    margin-bottom: 14px;
    box-shadow: 0 2px 8px rgba(27,94,32,0.05);
}
.card-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.92rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 1.2px;
    color: var(--verde-oscuro); margin-bottom: 14px;
    display: flex; align-items: center; gap: 8px;
    border-bottom: 2px solid var(--verde-claro);
    padding-bottom: 10px;
}

.result-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 4px; border-bottom: 1px solid var(--verde-claro);
    font-size: 0.92rem;
}
.result-row:last-child { border-bottom: none; }
.result-label { color: var(--texto-soft); }
.result-value { font-weight: 700; color: var(--texto); }
.result-value.positive { color: var(--verde-medio); }
.result-value.negative { color: var(--rojo); }

.total-box {
    background: linear-gradient(135deg, var(--verde-oscuro) 0%, var(--verde-medio) 100%);
    border-radius: 16px; padding: 26px;
    text-align: center; margin-top: 14px;
    box-shadow: 0 6px 20px rgba(27,94,32,0.25);
}
.total-box .label  { color: rgba(255,255,255,0.85); font-size: 0.88rem; margin-bottom: 6px; letter-spacing: 1.5px; }
.total-box .amount { color: #fff; font-size: 2.4rem; font-weight: 800; font-family: 'Syne', sans-serif; }

.alert-error {
    background: var(--rojo-soft); border-left: 4px solid var(--rojo);
    border-radius: 8px; padding: 12px 14px; color: var(--rojo); font-size: 0.88rem;
}
.alert-warning {
    background: var(--ambar-soft); border-left: 4px solid var(--ambar);
    border-radius: 8px; padding: 12px 14px; color: #7A5300; font-size: 0.88rem;
}
.alert-info {
    background: var(--verde-claro); border-left: 4px solid var(--verde-suave);
    border-radius: 8px; padding: 12px 14px; color: var(--verde-oscuro); font-size: 0.88rem;
}

/* ── INPUTS — verde muy claro / gris seda ─────────────── */
.stTextInput input,
.stNumberInput input,
.stDateInput input,
.stTimeInput input {
    background-color: var(--verde-input) !important;
    border: 1px solid var(--borde) !important;
    color: var(--texto) !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stSelectbox > div > div,
[data-baseweb="select"] > div {
    background-color: var(--verde-input) !important;
    border: 1px solid var(--borde) !important;
    color: var(--texto) !important;
    border-radius: 8px !important;
}
[data-baseweb="select"] span { color: var(--texto) !important; }
.stNumberInput button { background-color: var(--verde-claro) !important; color: var(--verde-oscuro) !important; }
.stNumberInput button p { color: var(--verde-oscuro) !important; }
input::placeholder { color: var(--texto-soft) !important; opacity: 0.7 !important; }

/* ── EXPANDERS — limpieza visual ──────────────────────── */
.streamlit-expanderHeader, [data-testid="stExpander"] summary {
    background: linear-gradient(90deg, var(--verde-claro), var(--gris-seda)) !important;
    border-radius: 10px !important;
    border: 1px solid var(--borde) !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    color: var(--verde-oscuro) !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
}
[data-testid="stExpander"] {
    border: none !important;
    margin-bottom: 10px !important;
}
[data-testid="stExpander"] details {
    background: transparent !important;
    border: none !important;
}
[data-testid="stExpander"] details[open] > summary {
    border-bottom-left-radius: 0 !important;
    border-bottom-right-radius: 0 !important;
    background: var(--verde-oscuro) !important;
    color: white !important;
}
[data-testid="stExpander"] details[open] > summary svg { color: white !important; fill: white !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background: white !important;
    border: 1px solid var(--borde) !important;
    border-top: none !important;
    border-bottom-left-radius: 10px !important;
    border-bottom-right-radius: 10px !important;
    padding: 18px !important;
}

/* ── BUTTONS ──────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    transition: all 0.2s !important;
    padding: 10px 18px !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--verde-oscuro), var(--verde-medio)) !important;
    border: none !important;
    color: white !important;
    box-shadow: 0 3px 10px rgba(27,94,32,0.25) !important;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px);
    box-shadow: 0 5px 14px rgba(27,94,32,0.35) !important;
}
.stButton > button[kind="secondary"] {
    background: white !important;
    border: 1.5px solid var(--verde-medio) !important;
    color: var(--verde-oscuro) !important;
}

label, .stMarkdown p { color: var(--texto) !important; }
.stMarkdown small, .stCaption { color: var(--texto-soft) !important; }

hr { border-color: var(--borde) !important; }

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 1280px; }
</style>
""", unsafe_allow_html=True)

# ── HEADER ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-band">
  <div style="font-size:2.8rem">🌿</div>
  <div>
    <h1>Asistente de Nómina Blindada</h1>
    <p>Tu nómina quincenal correcta, clara y legalmente protegida · Colombia 2026</p>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown(f"""
<div class="badge-row">
  <div class="badge">✔ Salario Mínimo Legal 2026: ${SMLMV_2026:,.0f}</div>
  <div class="badge">✔ Auxilio de Transporte: $182.000</div>
  <div class="badge">⚖️ Jornada 42h/semana (Ley 2101/2021)</div>
  <div class="badge">🌙 Recargo nocturno desde las 7:00 p.m.</div>
  <div class="badge">📅 Domingo / Festivo: +100%</div>
  <div class="badge">🛡️ Blindaje legal CST</div>
</div>
""", unsafe_allow_html=True)

# ── SESSION STATE ────────────────────────────────────────────────────────────
if "turnos" not in st.session_state:
    st.session_state.turnos = []
if "resultado" not in st.session_state:
    st.session_state.resultado = None
if "guardado_id" not in st.session_state:
    st.session_state.guardado_id = None

# Prefill defaults (used by widget keys)
_defaults = {
    "f_empresa": "", "f_nit": "", "f_empleado": "", "f_cedula": "",
    "f_periodo_inicio": date.today().replace(day=1),
    "f_periodo_fin":    date.today(),
    "f_tipo_salario":   "Sueldo Fijo Mensual",
    "f_salario_base":   int(SMLMV_2026),
    "f_valor_hora":     7200,
    "f_dias_laborados": 15,
}
for _k, _v in _defaults.items():
    st.session_state.setdefault(_k, _v)


def _cargar_empleado(cedula: str):
    """Pre-rellena los campos del formulario con datos del empleado guardado."""
    emp = hist.obtener_empleado(cedula)
    if not emp:
        return
    st.session_state.f_empresa  = emp.get("empresa") or ""
    st.session_state.f_nit      = emp.get("nit") or ""
    st.session_state.f_empleado = emp.get("nombre") or ""
    st.session_state.f_cedula   = emp.get("cedula") or ""
    ts = emp.get("tipo_salario") or "Fijo Mensual"
    st.session_state.f_tipo_salario = (
        "Sueldo Fijo Mensual" if "Fijo" in ts else "Por Horas o Turnos"
    )
    if emp.get("salario_base"):
        st.session_state.f_salario_base = int(emp["salario_base"])
    if emp.get("valor_hora"):
        st.session_state.f_valor_hora = int(emp["valor_hora"])

# ── LAYOUT: 2 COLUMNAS ───────────────────────────────────────────────────────
col_izq, col_der = st.columns([1.05, 1], gap="large")

# ═══════════════════════════════════════════════════════════════
# COLUMNA IZQUIERDA — FORMULARIO POR EXPANDERS
# ═══════════════════════════════════════════════════════════════
with col_izq:
    st.markdown("### 📋 Llena los datos de la nómina")
    st.caption("Despliega cada sección solo si necesitas registrar información allí.")

    # ── CARGAR EMPLEADO GUARDADO ───────────────────────────
    _empleados_guardados = hist.listar_empleados()
    if _empleados_guardados:
        with st.expander(f"⚡ Cargar empleado guardado ({len(_empleados_guardados)} disponibles)", expanded=False):
            st.caption("Selecciona un trabajador para autocompletar sus datos básicos.")
            opciones = ["— Selecciona —"] + [
                f"{e['nombre']} · CC {e['cedula']}" for e in _empleados_guardados
            ]
            sel = st.selectbox("Empleado guardado", opciones, key="sel_empleado_hist")
            cs1, cs2 = st.columns([1, 1])
            with cs1:
                if st.button("📥 Cargar datos", use_container_width=True, type="primary",
                             disabled=(sel == "— Selecciona —")):
                    idx = opciones.index(sel) - 1
                    _cargar_empleado(_empleados_guardados[idx]["cedula"])
                    st.success(f"✅ Datos cargados: {_empleados_guardados[idx]['nombre']}")
                    st.rerun()
            with cs2:
                if st.button("🗑 Eliminar empleado", use_container_width=True, type="secondary",
                             disabled=(sel == "— Selecciona —")):
                    idx = opciones.index(sel) - 1
                    hist.borrar_empleado(_empleados_guardados[idx]["cedula"])
                    st.warning("Empleado y sus nóminas eliminados.")
                    st.rerun()

    # ── SECCIÓN 1 · DATOS BÁSICOS ──────────────────────────
    with st.expander("①  Datos básicos del empleado y el período", expanded=True):
        empresa = st.text_input("Nombre del Restaurante / Empresa",
                                placeholder="Ej: Restaurante El Fogón S.A.S.", key="f_empresa")
        nit = st.text_input("NIT o Cédula del Empleador",
                            placeholder="900.123.456-7", key="f_nit")

        c1, c2 = st.columns(2)
        with c1:
            empleado = st.text_input("Nombre completo del trabajador",
                                     placeholder="Juan Pérez García", key="f_empleado")
        with c2:
            cedula = st.text_input("Cédula del trabajador",
                                   placeholder="1.000.123.456", key="f_cedula")

        c3, c4 = st.columns(2)
        with c3:
            periodo_inicio = st.date_input("¿Desde qué día empieza la quincena?", key="f_periodo_inicio")
        with c4:
            periodo_fin = st.date_input("¿Hasta qué día va?", key="f_periodo_fin")

        st.markdown("---")
        st.markdown("**💰 Cuánto gana el trabajador**")

        tipo_salario = st.selectbox(
            "¿Cómo le pagas?",
            ["Sueldo Fijo Mensual", "Por Horas o Turnos"],
            key="f_tipo_salario",
        )

        if tipo_salario == "Sueldo Fijo Mensual":
            salario_base = st.number_input(
                "Salario base mensual (COP)",
                min_value=0, step=10000, format="%d",
                help=f"El Salario Mínimo Legal para 2026 es ${SMLMV_2026:,.0f}",
                key="f_salario_base",
            )
            if salario_base > 0 and salario_base < SMLMV_2026:
                st.markdown(f'<div class="alert-error">⚠️ El salario no puede ser menor al Salario Mínimo Legal (${SMLMV_2026:,.0f})</div>', unsafe_allow_html=True)
            valor_hora = 0
            tipo_salario_internal = "Fijo Mensual"
        else:
            valor_hora = st.number_input(
                "Valor de la hora ordinaria (COP)",
                min_value=0, step=100, format="%d",
                help=f"Mínimo legal: ${VALOR_HORA_MIN:,.0f}/hora",
                key="f_valor_hora",
            )
            if valor_hora > 0 and valor_hora < VALOR_HORA_MIN:
                st.markdown(f'<div class="alert-error">⚠️ El valor por hora mínimo es ${VALOR_HORA_MIN:,.0f}</div>', unsafe_allow_html=True)
            salario_base = 0
            tipo_salario_internal = "Por Horas / Turnos"

        dias_laborados = st.number_input(
            "¿Cuántos días tiene la quincena/período?",
            min_value=1, max_value=30,
            help="Normalmente 15 (quincena) o 30 (mes completo)",
            key="f_dias_laborados",
        )

    # ── SECCIÓN 2 · TIEMPO ADICIONAL ───────────────────────
    with st.expander("②  ¿Trabajó tiempo adicional? (Horas extras y turnos especiales)"):
        st.caption("Solo despliega si el trabajador hizo turnos nocturnos, dominicales o de horas extras.")

        tc1, tc2 = st.columns(2)
        with tc1:
            turno_fecha = st.date_input("Fecha del turno", key="t_fecha")
            tipo_dia = st.selectbox("Tipo de día", ["Ordinario (Lun-Sáb)", "Domingo", "Festivo"], key="t_tipo")
        with tc2:
            hora_entrada = st.time_input("Hora de entrada", value=time(8, 0), key="t_entrada")
            hora_salida = st.time_input("Hora de salida", value=time(16, 0), key="t_salida")

        if st.button("➕ Agregar este turno", use_container_width=True, type="primary", key="add_turno"):
            if hora_salida <= hora_entrada:
                st.error("La hora de salida debe ser posterior a la de entrada.")
            else:
                tipo_normalizado = "Ordinario" if tipo_dia.startswith("Ordinario") else tipo_dia
                st.session_state.turnos.append({
                    "fecha": turno_fecha.strftime("%d/%m/%Y"),
                    "tipo_dia": tipo_normalizado,
                    "entrada": hora_entrada.strftime("%H:%M"),
                    "salida": hora_salida.strftime("%H:%M"),
                })
                st.success("✅ Turno agregado")

        if st.session_state.turnos:
            st.markdown("**Turnos registrados:**")
            for i, t in enumerate(st.session_state.turnos):
                cols = st.columns([3, 2, 2, 2, 0.7])
                cols[0].caption(t["fecha"])
                cols[1].caption(t["tipo_dia"])
                cols[2].caption(t["entrada"])
                cols[3].caption(f"→ {t['salida']}")
                if cols[4].button("🗑", key=f"del_{i}"):
                    st.session_state.turnos.pop(i)
                    st.rerun()
            if st.button("Limpiar todos los turnos", type="secondary", use_container_width=True):
                st.session_state.turnos = []
                st.rerun()

    # ── SECCIÓN 3 · NOVEDADES DE SALUD Y AUSENCIAS ─────────
    with st.expander("③  Novedades de salud y ausencias (días enfermo o que faltó)"):
        st.caption("Registra aquí incapacidades médicas o días que el trabajador no asistió.")

        nc1, nc2 = st.columns(2)
        with nc1:
            incapacidades = st.number_input(
                "Días que estuvo enfermo (con incapacidad médica)",
                min_value=0, max_value=30, value=0,
                help="Los primeros 2 días los paga el empleador al 100%. Del día 3 en adelante los paga la EPS al 66.67%. Si gana el mínimo, siempre se paga 100%."
            )
        with nc2:
            dias_no_laborados = st.number_input(
                "Días que faltó sin justificación",
                min_value=0, max_value=30, value=0,
                help="Por cada falta sin justa causa también se descuenta el día de descanso dominical (Art. 173 CST)"
            )

        if dias_no_laborados > 0:
            st.markdown(
                '<div class="alert-warning">⚖️ <b>Ajuste legal por falta:</b> por cada día no trabajado se descuenta '
                'también el día de descanso dominical correspondiente.</div>',
                unsafe_allow_html=True
            )
        if incapacidades > 0:
            st.markdown(
                '<div class="alert-info">🏥 <b>Pago de incapacidad:</b> los primeros 2 días los paga el empleador al 100%; '
                'del día 3 en adelante los cubre la EPS al 66.67%. <b>Si el trabajador gana el salario mínimo, '
                'todos los días se pagan al 100%</b> para proteger el mínimo vital.</div>',
                unsafe_allow_html=True
            )

    # ── SECCIÓN 4 · PAGOS EXTRA Y DESCUENTOS ───────────────
    with st.expander("④  Pagos extra y descuentos (comisiones, bonos, préstamos, vales)"):
        st.markdown("**➕ Pagos adicionales**")
        ic1, ic2 = st.columns(2)
        with ic1:
            comisiones = st.number_input(
                "Comisiones por ventas (suman al salario)",
                min_value=0, value=0, step=1000, format="%d",
                help="Estas comisiones sí cotizan a salud y pensión"
            )
        with ic2:
            bonif_no_salariales = st.number_input(
                "Bonificaciones / bonos no salariales",
                min_value=0, value=0, step=1000, format="%d",
                help="Estos bonos NO cotizan a salud y pensión"
            )

        st.markdown("---")
        st.markdown("**➖ Descuentos del trabajador**")
        dc1, dc2 = st.columns(2)
        with dc1:
            prestamos = st.number_input(
                "Préstamos o adelantos (cuota)",
                min_value=0, value=0, step=1000, format="%d"
            )
        with dc2:
            sanciones = st.number_input(
                "Multas o sanciones disciplinarias",
                min_value=0, value=0, step=1000, format="%d"
            )

        saldo_prestamo = st.number_input(
            "Saldo total del préstamo (antes de esta cuota)",
            min_value=0, value=0, step=1000, format="%d",
            help="Para mostrar cuánto le queda por pagar al trabajador"
        )

    # ── BOTÓN CALCULAR ─────────────────────────────────────
    st.markdown("---")
    if st.button("🧮  CALCULAR LA NÓMINA", use_container_width=True, type="primary"):
        errores = []
        if not empresa.strip(): errores.append("• Falta el nombre del restaurante")
        if not empleado.strip(): errores.append("• Falta el nombre del trabajador")
        if not cedula.strip(): errores.append("• Falta la cédula del trabajador")
        if tipo_salario == "Sueldo Fijo Mensual" and salario_base < SMLMV_2026:
            errores.append(f"• El salario es menor al Salario Mínimo Legal (${SMLMV_2026:,.0f})")
        if tipo_salario == "Por Horas o Turnos":
            if valor_hora < VALOR_HORA_MIN:
                errores.append(f"• Valor de la hora menor al mínimo (${VALOR_HORA_MIN:,.0f})")
            if not st.session_state.turnos:
                errores.append("• Agrega al menos un turno trabajado")
        if dias_no_laborados + incapacidades > dias_laborados:
            errores.append("• Las faltas + días enfermo no pueden superar los días del período")

        if errores:
            st.markdown(f'<div class="alert-error">{"<br>".join(errores)}</div>', unsafe_allow_html=True)
        else:
            params = {
                "empresa": empresa, "nit": nit,
                "empleado": empleado, "cedula": cedula,
                "periodo_inicio": periodo_inicio, "periodo_fin": periodo_fin,
                "tipo_salario": tipo_salario_internal,
                "salario_base": salario_base if tipo_salario == "Sueldo Fijo Mensual" else 0,
                "valor_hora": valor_hora if tipo_salario == "Por Horas o Turnos" else 0,
                "dias_laborados": dias_laborados,
                "dias_no_laborados": dias_no_laborados,
                "incapacidades": incapacidades,
                "comisiones": comisiones,
                "bonif_no_salariales": bonif_no_salariales,
                "prestamos": prestamos, "sanciones": sanciones,
                "saldo_prestamo": saldo_prestamo,
                "turnos": st.session_state.turnos,
            }
            st.session_state.resultado = calcular_nomina(params)
            st.session_state.guardado_id = None
            st.rerun()

# ═══════════════════════════════════════════════════════════════
# COLUMNA DERECHA — RESULTADOS
# ═══════════════════════════════════════════════════════════════
with col_der:
    st.markdown("### 📊 Resumen de la liquidación")
    res = st.session_state.resultado

    if res is None:
        st.markdown("""
        <div class="card" style="text-align:center; padding: 56px 24px; border:2px dashed #C5D8C8;">
          <div style="font-size:4rem; margin-bottom:16px">🌱</div>
          <div style="font-family:'Syne',sans-serif; font-size:1.15rem; color:#1B5E20; font-weight:700;">
            Llena los datos a la izquierda<br>y pulsa <span style="color:#2E7D32">Calcular la Nómina</span>
          </div>
          <div style="margin-top:12px; font-size:0.85rem; color:#4F6B53;">
            Aquí verás todo el detalle de pagos y descuentos
          </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        # ── Encabezado del trabajador ──
        st.markdown(f"""
        <div class="card" style="border-left:5px solid #1B5E20;">
          <div style="font-family:'Syne',sans-serif;font-weight:700;font-size:1.1rem;color:#1B5E20;">
            👤 {res['empleado']}
          </div>
          <div style="font-size:0.88rem;color:#4F6B53;margin-top:6px;">
            {res['empresa']} · CC {res['cedula']}<br>
            Período: {res['periodo_inicio'].strftime('%d/%m/%Y')} — {res['periodo_fin'].strftime('%d/%m/%Y')}<br>
            Días del período: <b>{res['dias_laborados']}</b> · Días efectivos: <b>{res['dias_efectivos']}</b>
            {f"· Faltó: <b>{res['dias_no_laborados']}d</b>" if res['dias_no_laborados'] else ""}
            {f"· Enfermo: <b>{res['incapacidades']}d</b>" if res['incapacidades'] else ""}
          </div>
        </div>
        """, unsafe_allow_html=True)

        # ── LO QUE EL TRABAJADOR RECIBE ──
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💚 Lo que el trabajador recibe</div>', unsafe_allow_html=True)

        items = [
            ("Salario base del período", res["salario_base_calc"]),
            (f"Auxilio de Transporte (proporcional a {res['dias_efectivos']}d)", res["aux_transporte"]),
        ]
        if res["comisiones"] > 0:
            items.append(("Comisiones (suman al salario)", res["comisiones"]))
        if res["bonif_no_salariales"] > 0:
            items.append(("Bonificaciones (no salariales)", res["bonif_no_salariales"]))
        if res["auxilio_incapacidad"] > 0:
            tag = " · 100% (mínimo protegido)" if res.get("devenga_smlmv") and res["dias_incap_eps"] > 0 else ""
            items.append((
                f"Pago por días enfermo ({res['dias_incap_empleador']}d empleador + {res['dias_incap_eps']}d EPS){tag}",
                res["auxilio_incapacidad"]
            ))
        if res["recargo_nocturno"] > 0:
            items.append((f"Recargo Nocturno (35%) · {res['horas_nocturnas']:.1f}h", res["recargo_nocturno"]))
        if res["recargo_dominical"] > 0:
            items.append((f"Recargo Domingo/Festivo (100%) · {res['horas_dominical']:.1f}h", res["recargo_dominical"]))
        if res["he_diurnas_valor"] > 0:
            items.append((f"Horas Extra Diurnas (25%) · {res['he_diurnas_horas']:.1f}h", res["he_diurnas_valor"]))
        if res["he_nocturnas_valor"] > 0:
            items.append((f"Horas Extra Nocturnas (75%) · {res['he_nocturnas_horas']:.1f}h", res["he_nocturnas_valor"]))

        for label, val in items:
            if val == 0 and "Salario base" not in label and "Auxilio" not in label:
                continue
            st.markdown(f"""
            <div class="result-row">
              <span class="result-label">{label}</span>
              <span class="result-value positive">+ ${val:,.0f}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-row" style="font-weight:800;font-size:1rem;background:#E8F5E9;padding:12px 8px;border-radius:8px;margin-top:6px;">
          <span style="color:#1B5E20">TOTAL QUE RECIBE</span>
          <span class="result-value positive">+ ${res['total_devengado']:,.0f}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── DESCUENTOS REALIZADOS ──
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">💸 Descuentos realizados</div>', unsafe_allow_html=True)

        descs = [
            (f"Salud (4% sobre ${res['base_ss']:,.0f})", res["salud"]),
            (f"Pensión (4% sobre ${res['base_ss']:,.0f})", res["pension"]),
        ]
        if res["desc_falta_dominical"] > 0:
            descs.append(("Descuento por el domingo perdido (Art. 173)", res["desc_falta_dominical"]))
        if res["prestamos"] > 0:
            descs.append(("Préstamo / Adelanto", res["prestamos"]))
        if res["sanciones"] > 0:
            descs.append(("Multa o sanción disciplinaria", res["sanciones"]))

        for label, val in descs:
            st.markdown(f"""
            <div class="result-row">
              <span class="result-label">{label}</span>
              <span class="result-value negative">− ${val:,.0f}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-row" style="font-weight:800;font-size:1rem;background:#FFEBEE;padding:12px 8px;border-radius:8px;margin-top:6px;">
          <span style="color:#C62828">TOTAL DESCONTADO</span>
          <span class="result-value negative">− ${res['total_deducciones']:,.0f}</span>
        </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        # ── NETO A PAGAR ──
        st.markdown(f"""
        <div class="total-box">
          <div class="label">💰 NETO A PAGAR AL TRABAJADOR</div>
          <div class="amount">${res['neto_a_pagar']:,.0f} COP</div>
          <div style="color:rgba(255,255,255,0.85);font-size:0.82rem;margin-top:8px;">
            {res['empleado']} · Período {res['periodo_fin'].strftime('%B de %Y')}
          </div>
        </div>
        """, unsafe_allow_html=True)

        if res["saldo_prestamo_pendiente"] > 0:
            st.markdown(
                f'<div class="alert-warning" style="margin-top:12px;">💼 Saldo de préstamo pendiente: '
                f'<b>${res["saldo_prestamo_pendiente"]:,.0f} COP</b></div>',
                unsafe_allow_html=True
            )

        # ── PRESTACIONES SOCIALES (COSTO MENSUAL EMPLEADOR) ──
        with st.expander("🏛️ Prestaciones Sociales y costo total mensual del trabajador (a cargo del empleador)"):
            st.caption(
                "Estimación mensual de prestaciones, parafiscales y aportes adicionales que el empleador "
                "asume por encima del salario neto. No se descuentan del trabajador."
            )

            st.markdown('<div class="card-title">📦 Prestaciones Sociales (Mensual)</div>', unsafe_allow_html=True)
            for label, val in [
                ("Cesantías (8.33%)",                    res["cesantias"]),
                ("Intereses sobre cesantías (12% anual)", res["intereses_cesantias"]),
                ("Prima de servicios (8.33%)",           res["prima_servicios"]),
                ("Vacaciones (4.17%)",                   res["vacaciones"]),
            ]:
                st.markdown(f"""
                <div class="result-row">
                  <span class="result-label">{label}</span>
                  <span class="result-value positive">+ ${val:,.0f}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="result-row" style="font-weight:800;background:#E8F5E9;padding:10px 8px;border-radius:8px;">
              <span style="color:#1B5E20">Subtotal Prestaciones</span>
              <span class="result-value positive">+ ${res['total_prestaciones']:,.0f}</span>
            </div>""", unsafe_allow_html=True)

            st.markdown("")
            st.markdown('<div class="card-title">🏥 Aportes del Empleador a Seguridad Social (Mensual)</div>', unsafe_allow_html=True)
            for label, val in [
                ("Salud · Empleador (8.5%)",   res["salud_empleador"]),
                ("Pensión · Empleador (12%)",  res["pension_empleador"]),
                ("ARL Clase I (0.522%)",       res["arl"]),
            ]:
                st.markdown(f"""
                <div class="result-row">
                  <span class="result-label">{label}</span>
                  <span class="result-value positive">+ ${val:,.0f}</span>
                </div>""", unsafe_allow_html=True)
            st.markdown(f"""
            <div class="result-row" style="font-weight:800;background:#E8F5E9;padding:10px 8px;border-radius:8px;">
              <span style="color:#1B5E20">Subtotal Aportes</span>
              <span class="result-value positive">+ ${res['aportes_empleador']:,.0f}</span>
            </div>""", unsafe_allow_html=True)

            st.markdown("")
            st.markdown(f"""
            <div class="total-box" style="background:linear-gradient(135deg,#2E7D32,#43A047);">
              <div class="label">💼 COSTO TOTAL MENSUAL DEL TRABAJADOR</div>
              <div class="amount">${res['costo_total_mes']:,.0f} COP</div>
              <div style="color:rgba(255,255,255,0.85);font-size:0.78rem;margin-top:6px;">
                Salario proyectado + Auxilio + Prestaciones + Aportes empleador
              </div>
            </div>
            """, unsafe_allow_html=True)

        if res.get("detalle_turnos"):
            with st.expander("📋 Ver desglose detallado de turnos"):
                df = pd.DataFrame(res["detalle_turnos"])
                df.columns = ["Fecha","Tipo","Entrada","Salida","Hrs Ord.","Hrs Noc.","Dom/Fest.","HE Diur.","HE Noct.","Valor"]
                df["Valor"] = df["Valor"].apply(lambda x: f"${x:,.0f}")
                st.dataframe(df, use_container_width=True, hide_index=True)

        st.markdown("---")
        b1, b2 = st.columns(2)
        with b1:
            if st.button("📄  Generar Comprobante PDF", use_container_width=True, type="primary"):
                try:
                    pdf_bytes = generar_pdf(res)
                    b64 = base64.b64encode(pdf_bytes).decode()
                    nombre = f"Comprobante_{res['empleado'].replace(' ','_')}_{res['periodo_fin'].strftime('%Y%m')}.pdf"
                    href = (f'<a href="data:application/pdf;base64,{b64}" download="{nombre}" '
                            f'style="display:block;text-align:center;background:linear-gradient(135deg,#1B5E20,#2E7D32);'
                            f'color:white;padding:14px;border-radius:10px;font-family:Syne,sans-serif;font-weight:700;'
                            f'text-decoration:none;margin-top:8px;">⬇️ Descargar Comprobante PDF</a>')
                    st.markdown(href, unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Error generando PDF: {e}")
        with b2:
            if st.button("💬  Enviar resumen por WhatsApp", use_container_width=True, type="secondary"):
                texto = (
                    f"🌿 *COMPROBANTE DE NÓMINA*\n"
                    f"Restaurante: {res['empresa']}\n"
                    f"Trabajador: {res['empleado']} (CC {res['cedula']})\n"
                    f"Período: {res['periodo_inicio'].strftime('%d/%m/%Y')} - {res['periodo_fin'].strftime('%d/%m/%Y')}\n\n"
                    f"💚 Lo que recibe: ${res['total_devengado']:,.0f}\n"
                    f"💸 Descuentos: -${res['total_deducciones']:,.0f}\n\n"
                    f"✅ *NETO A PAGAR: ${res['neto_a_pagar']:,.0f} COP*\n\n"
                    f"_Generado con Asistente de Nómina Blindada · Colombia 2026_"
                )
                url_wa = f"https://wa.me/?text={urllib.parse.quote(texto)}"
                st.markdown(
                    f'<a href="{url_wa}" target="_blank" '
                    f'style="display:block;text-align:center;background:#25D366;color:white;padding:14px;'
                    f'border-radius:10px;font-family:Syne,sans-serif;font-weight:700;text-decoration:none;'
                    f'margin-top:8px;">💬 Abrir WhatsApp</a>',
                    unsafe_allow_html=True
                )

        # ── GUARDAR EN HISTORIAL ──────────────────────────────────
        st.markdown("---")
        if st.session_state.guardado_id:
            st.markdown(
                f'<div class="alert-info">📚 <b>Nómina #{st.session_state.guardado_id}</b> guardada en el historial. '
                f'Puedes consultarla más abajo en la sección de historial.</div>',
                unsafe_allow_html=True
            )
        else:
            if st.button("💾  Guardar esta nómina al historial", use_container_width=True, type="primary"):
                try:
                    nuevo_id = hist.guardar_nomina(res)
                    st.session_state.guardado_id = nuevo_id
                    st.rerun()
                except Exception as e:
                    st.error(f"No se pudo guardar: {e}")

# ═══════════════════════════════════════════════════════════════
# HISTORIAL DE NÓMINAS (sección inferior, ancho completo)
# ═══════════════════════════════════════════════════════════════
st.markdown("---")
_todas_nominas = hist.listar_nominas()
with st.expander(f"📚  Historial de nóminas guardadas ({len(_todas_nominas)} registros)",
                 expanded=False):
    if not _todas_nominas:
        st.caption("Aún no has guardado ninguna nómina. Calcula una y pulsa "
                   "**Guardar esta nómina al historial**.")
    else:
        st.caption("Filtra, consulta o elimina nóminas anteriores. "
                   "Al consultar una, se carga en el panel de resultados.")

        empleados_uniq = sorted({n["empleado"] for n in _todas_nominas})
        filtro = st.selectbox(
            "Filtrar por empleado",
            ["Todos"] + empleados_uniq,
            key="filtro_hist",
        )
        nominas_vistas = (
            _todas_nominas if filtro == "Todos"
            else [n for n in _todas_nominas if n["empleado"] == filtro]
        )

        df_h = pd.DataFrame([{
            "ID":          n["id"],
            "Trabajador":  n["empleado"],
            "Cédula":      n["cedula"],
            "Período":     f"{n['periodo_inicio'][:10]} → {n['periodo_fin'][:10]}",
            "Devengado":   f"${n['total_devengado']:,.0f}",
            "Deducciones": f"${n['total_deducciones']:,.0f}",
            "Neto":        f"${n['neto_a_pagar']:,.0f}",
            "Costo total mes": f"${n['costo_total_mes']:,.0f}",
            "Calculado":   n["fecha_calculo"][:16].replace("T", " "),
        } for n in nominas_vistas])
        st.dataframe(df_h, use_container_width=True, hide_index=True)

        st.markdown("**Acciones sobre una nómina:**")
        ac1, ac2, ac3 = st.columns([1.3, 1, 1])
        with ac1:
            ids_disp = [n["id"] for n in nominas_vistas]
            etiquetas = [
                f"#{n['id']} · {n['empleado']} · {n['periodo_fin'][:10]}"
                for n in nominas_vistas
            ]
            sel_idx = st.selectbox(
                "Selecciona una nómina",
                range(len(ids_disp)) if ids_disp else [0],
                format_func=lambda i: etiquetas[i] if etiquetas else "—",
                key="sel_nom_hist",
            )
            sel_id = ids_disp[sel_idx] if ids_disp else None
        with ac2:
            if st.button("👁  Ver / Reabrir", use_container_width=True, type="primary",
                         disabled=(sel_id is None)):
                data = hist.obtener_nomina(sel_id)
                if data:
                    st.session_state.resultado = data
                    st.session_state.guardado_id = sel_id
                    st.rerun()
        with ac3:
            if st.button("🗑  Borrar nómina", use_container_width=True, type="secondary",
                         disabled=(sel_id is None)):
                hist.borrar_nomina(sel_id)
                if st.session_state.guardado_id == sel_id:
                    st.session_state.guardado_id = None
                st.warning(f"Nómina #{sel_id} eliminada.")
                st.rerun()

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#4F6B53;font-size:0.78rem;padding:8px 0;">
  Asistente de Nómina Blindada · Colombia 2026 · Verde Profesional<br>
  Basado en: Ley 2101/2021 · Decreto 2910/2024 · Decreto 2911/2024 · CST Art. 65, 168, 173, 177, 179<br>
  <em>Esta herramienta no reemplaza la asesoría de un contador o abogado laboral certificado.</em>
</div>
""", unsafe_allow_html=True)
