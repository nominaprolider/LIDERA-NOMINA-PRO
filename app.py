import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================================
# NÓMINA BLINDADA LIDERA - MVP COLOMBIA 2026
# Liquidación de nómina periódica:
# - Ordinaria: quincenal / mensual
# - Por días: doméstica, aseo, jardinería y afines
#
# En modalidad por días aplica lógica estricta de cotización
# parcial por semanas cuando:
# 1) Hay contrato laboral.
# 2) Trabaja menos de 30 días en el mes.
# 3) Devenga menos de 1 SMMLV en el mes.
# 4) Está cubierto en salud por régimen subsidiado o como beneficiario.
#
# En ese caso:
# - No se descuenta salud.
# - Se descuenta pensión trabajador 4% sobre IBC parcial semanal.
# - ARL y caja se muestran como informativos a cargo del empleador.
# ============================================================


# ============================================================
# 1. CONFIGURACIÓN VISUAL
# ============================================================

st.set_page_config(
    page_title="Nómina Blindada Lidera",
    layout="wide",
    page_icon="🌿"
)

st.markdown("""
<style>
.main-header {
    background-color: #2E8B57;
    padding: 25px;
    border-radius: 12px;
    color: white;
    text-align: center;
    margin-bottom: 20px;
}
.main-header h1 {
    color: white;
    font-family: 'Segoe UI', sans-serif;
    margin-bottom: 5px;
}
.badge-container {
    display: flex;
    gap: 15px;
    flex-wrap: wrap;
    margin-bottom: 30px;
    justify-content: center;
}
.badge {
    border: 1px solid #4CAF50;
    background-color: #F1F8E9;
    border-radius: 20px;
    padding: 8px 18px;
    color: #2E7D32;
    font-weight: 600;
    font-size: 0.9rem;
}
.recibo-box {
    border: 2px solid #2E8B57;
    padding: 30px;
    border-radius: 10px;
    background-color: white;
    margin-top: 20px;
    color: black;
}
.alerta-legal {
    background-color: #FFF8E1;
    border-left: 6px solid #F9A825;
    padding: 16px;
    border-radius: 8px;
    margin-top: 15px;
    color: #4E342E;
}
.success-box {
    background-color: #E8F5E9;
    border-left: 6px solid #2E8B57;
    padding: 16px;
    border-radius: 8px;
    margin-top: 15px;
    color: #1B5E20;
}
</style>

<div class="main-header">
    <h1>🌿 Asistente de Nómina Blindada</h1>
    <p>MVP de Liquidación de Nómina Periódica · Colombia 2026</p>
</div>

<div class="badge-container">
    <span class="badge">⚖️ Nómina periódica</span>
    <span class="badge">🏠 Trabajo doméstico por días</span>
    <span class="badge">📊 Cotización parcial por semanas</span>
    <span class="badge">🇨🇴 Colombia 2026</span>
</div>
""", unsafe_allow_html=True)


# ============================================================
# 2. CONSTANTES 2026
# ============================================================

SMLMV_2026 = 1_750_905
AUXILIO_2026 = 249_095
LIMITE_AUXILIO = SMLMV_2026 * 2

DIVISOR_HORAS = 220

TASA_SALUD_TRABAJADOR = 0.04
TASA_PENSION_TRABAJADOR = 0.04

TASA_PENSION_EMPLEADOR = 0.12
TASA_CAJA_EMPLEADOR = 0.04

ARL_RIESGOS = {
    "Riesgo I - 0.522%": 0.00522,
    "Riesgo II - 1.044%": 0.01044,
    "Riesgo III - 2.436%": 0.02436,
    "Riesgo IV - 4.350%": 0.04350,
    "Riesgo V - 6.960%": 0.06960,
}


# ============================================================
# 3. FUNCIONES AUXILIARES
# ============================================================

def formato_pesos(valor: float) -> str:
    return f"$ {valor:,.0f}".replace(",", ".")


def semanas_cotizadas_por_dias(dias_laborados_mes: int) -> int:
    """
    Tabla de cotización parcial por semanas:
    1 a 7 días     = 1 cotización mínima semanal
    8 a 14 días    = 2 cotizaciones mínimas semanales
    15 a 21 días   = 3 cotizaciones mínimas semanales
    22 a 29 días   = 4 cotizaciones mínimas semanales

    Nota:
    Si labora 30 días o más, no aplica cotización parcial.
    """
    if dias_laborados_mes <= 0:
        return 0
    if 1 <= dias_laborados_mes <= 7:
        return 1
    if 8 <= dias_laborados_mes <= 14:
        return 2
    if 15 <= dias_laborados_mes <= 21:
        return 3
    if 22 <= dias_laborados_mes <= 29:
        return 4
    return 4


def calcular_factor_periodo(periodicidad: str) -> float:
    """
    Sirve para distribuir deducciones mensuales de seguridad social
    cuando el pago es quincenal.
    """
    if periodicidad == "Quincenal":
        return 0.5
    return 1.0


# ============================================================
# 4. DATOS GENERALES
# ============================================================

st.markdown("### 📋 1. Datos Generales")

col1, col2 = st.columns(2)

with col1:
    empresa = st.text_input("Nombre de la Empresa / Empleador", value="")
    nit = st.text_input("NIT o Cédula del Empleador", value="")

with col2:
    empleado = st.text_input("Nombre completo del trabajador", value="")
    cedula = st.text_input("Cédula del trabajador", value="")

st.divider()


# ============================================================
# 5. MODALIDAD Y BASE SALARIAL
# ============================================================

st.markdown("### ⚙️ 2. Modalidad y Base Salarial")

modalidad = st.radio(
    "Tipo de vinculación:",
    [
        "Ordinaria (Quincena/Mes)",
        "Por Días (Doméstica/Aseo/Jardinería y afines)"
    ],
    horizontal=True
)

periodicidad = st.radio(
    "Periodicidad del pago:",
    ["Quincenal", "Mensual"],
    horizontal=True
)

salario_base = st.number_input(
    "Salario Base Mensual Pactado de Referencia (COP)",
    min_value=SMLMV_2026,
    value=SMLMV_2026,
    step=50_000
)

valor_dia = salario_base / 30
valor_auxilio_dia = AUXILIO_2026 / 30
valor_hora_ordinaria = salario_base / DIVISOR_HORAS

aplica_auxilio_ley = salario_base <= LIMITE_AUXILIO


# ============================================================
# 6. CONFIGURACIÓN SEGÚN MODALIDAD
# ============================================================

st.markdown("### 🧾 3. Datos del Período a Liquidar")

if modalidad == "Ordinaria (Quincena/Mes)":
    col3, col4, col5 = st.columns(3)

    with col3:
        dias_periodo = st.number_input(
            "Días del período a liquidar",
            min_value=1,
            max_value=30,
            value=15 if periodicidad == "Quincenal" else 30
        )

    with col4:
        dias_laborados_mes_pila = dias_periodo

    with col5:
        tiene_auxilio = st.checkbox(
            "Incluir Auxilio de Transporte",
            value=aplica_auxilio_ley
        )

    trabajador_cubierto_salud = True
    aplica_cotizacion_parcial = False

else:
    col3, col4, col5 = st.columns(3)

    with col3:
        dias_periodo = st.number_input(
            "Días efectivamente trabajados en este pago",
            min_value=1,
            max_value=29,
            value=4 if periodicidad == "Quincenal" else 8,
            help="Ejemplo: si paga quincenal y trabaja martes/viernes, normalmente serían 4 días en la quincena."
        )

    with col4:
        dias_laborados_mes_pila = st.number_input(
            "Días trabajados/proyectados en el mes para PILA",
            min_value=1,
            max_value=29,
            value=8,
            help="Este dato define el rango de cotización parcial por semanas. Ejemplo: martes y viernes durante 4 semanas = 8 días."
        )

    with col5:
        tiene_auxilio = st.checkbox(
            "Incluir Auxilio de Transporte Proporcional",
            value=True
        )

    st.markdown("#### 🩺 Validación de cobertura en salud")

    trabajador_cubierto_salud = st.checkbox(
        "El trabajador ya está cubierto en salud como afiliado al régimen subsidiado o beneficiario del régimen contributivo",
        value=True,
        help="Condición necesaria para aplicar cotización parcial por semanas sin cotización al subsistema de salud."
    )


st.divider()


# ============================================================
# 7. NOVEDADES
# ============================================================

st.markdown("### 📊 4. Novedades del Período")

with st.expander("➕ Horas Extras y Recargos"):
    col_h1, col_h2 = st.columns(2)

    with col_h1:
        he_d = st.number_input(
            "Horas Extras Diurnas (25%)",
            min_value=0.0,
            value=0.0,
            step=0.5
        )
        he_n = st.number_input(
            "Horas Extras Nocturnas (75%)",
            min_value=0.0,
            value=0.0,
            step=0.5
        )
        rec_n = st.number_input(
            "Recargos Nocturnos (35%)",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

    with col_h2:
        dom = st.number_input(
            "Dominical/Festivo Ordinario (80%)",
            min_value=0.0,
            value=0.0,
            step=0.5
        )
        he_dom_d = st.number_input(
            "Hora Extra Dominical/Festiva Diurna (105%)",
            min_value=0.0,
            value=0.0,
            step=0.5
        )
        he_dom_n = st.number_input(
            "Hora Extra Dominical/Festiva Nocturna (155%)",
            min_value=0.0,
            value=0.0,
            step=0.5
        )

with st.expander("⚠️ Ausencias e Incapacidades"):
    col_a1, col_a2 = st.columns(2)

    with col_a1:
        faltas_injustificadas = st.number_input(
            "Faltas injustificadas en el período",
            min_value=0,
            value=0,
            help="En nómina ordinaria puede afectar salario, auxilio y descanso. En modalidad por días se recomienda registrar únicamente días efectivamente trabajados."
        )

    with col_a2:
        inasistencias_justificadas = st.number_input(
            "Inasistencias justificadas / incapacidad en el período",
            min_value=0,
            value=0,
            help="Para este MVP no se liquidan incapacidades complejas. Solo se ajusta auxilio si no hubo desplazamiento."
        )

with st.expander("➖ Otras Deducciones Autorizadas"):
    prestamos = st.number_input(
        "Préstamos / embargos / otras deducciones autorizadas (COP)",
        min_value=0,
        value=0,
        step=10_000,
        help="Debe existir autorización legal o escrita cuando aplique."
    )

st.divider()


# ============================================================
# 8. CÁLCULO DE DEVENGOS
# ============================================================

if modalidad == "Ordinaria (Quincena/Mes)":
    dias_salario = max(0, dias_periodo - faltas_injustificadas)
    salario_final = valor_dia * dias_salario

    # En nómina ordinaria el descanso dominical ya está incluido en el salario mensual/quincenal.
    dominical_proporcional = 0

    dias_auxilio = max(0, dias_periodo - faltas_injustificadas - inasistencias_justificadas)
    auxilio_final = valor_auxilio_dia * dias_auxilio if tiene_auxilio else 0

else:
    # En modalidad por días se liquida sobre días efectivamente trabajados en el período.
    dias_salario = dias_periodo

    salario_final = valor_dia * dias_salario

    # Descanso dominical proporcional: 1 día de descanso por cada 6 días trabajados.
    dominical_proporcional = (salario_final / 6)

    dias_auxilio = max(0, dias_periodo - inasistencias_justificadas)
    auxilio_final = valor_auxilio_dia * dias_auxilio if tiene_auxilio else 0


total_extras = (
    (he_d * valor_hora_ordinaria * 1.25) +
    (he_n * valor_hora_ordinaria * 1.75) +
    (rec_n * valor_hora_ordinaria * 0.35) +
    (dom * valor_hora_ordinaria * 1.80) +
    (he_dom_d * valor_hora_ordinaria * 2.05) +
    (he_dom_n * valor_hora_ordinaria * 2.55)
)

devengado = salario_final + dominical_proporcional + total_extras + auxilio_final

# Base salarial real: excluye auxilio de transporte.
base_salarial_real = salario_final + dominical_proporcional + total_extras


# ============================================================
# 9. SEGURIDAD SOCIAL Y DEDUCCIONES
# ============================================================

factor_periodo = calcular_factor_periodo(periodicidad)

semanas_cotizadas = 0
ibc_pension = base_salarial_real
ibc_salud = base_salarial_real
ibc_arl = base_salarial_real
ibc_caja = base_salarial_real

salud_trabajador = 0
pension_trabajador = 0

pension_empleador = 0
arl_empleador = 0
caja_empleador = 0

tipo_cotizacion = "Cotización ordinaria"
mensaje_cotizacion = ""

riesgo_arl = st.selectbox(
    "Nivel de Riesgo ARL para referencia del empleador",
    list(ARL_RIESGOS.keys()),
    index=0
)

tasa_arl = ARL_RIESGOS[riesgo_arl]

if modalidad == "Por Días (Doméstica/Aseo/Jardinería y afines)":
    semanas_cotizadas = semanas_cotizadas_por_dias(dias_laborados_mes_pila)

    cumple_menos_30_dias = dias_laborados_mes_pila < 30
    cumple_menos_1_smmlv = base_salarial_real < SMLMV_2026

    aplica_cotizacion_parcial = (
        cumple_menos_30_dias and
        cumple_menos_1_smmlv and
        trabajador_cubierto_salud
    )

    if aplica_cotizacion_parcial:
        tipo_cotizacion = "Cotización parcial por semanas"

        # IBC mensual parcial según rango de días trabajados en el mes.
        ibc_pension_mensual = (SMLMV_2026 / 4) * semanas_cotizadas
        ibc_caja_mensual = ibc_pension_mensual

        # ARL se calcula sobre 1 SMMLV mensual completo.
        ibc_arl_mensual = SMLMV_2026

        # Para desprendible quincenal, se distribuye la deducción mensual.
        ibc_pension = ibc_pension_mensual * factor_periodo
        ibc_caja = ibc_caja_mensual * factor_periodo
        ibc_arl = ibc_arl_mensual * factor_periodo

        # En cotización parcial por semanas:
        # Salud: no aplica descuento porque debe existir cobertura previa.
        ibc_salud = 0
        salud_trabajador = 0

        # Pensión trabajador: 4%.
        pension_trabajador = ibc_pension * TASA_PENSION_TRABAJADOR

        # Informativos a cargo del empleador.
        pension_empleador = ibc_pension * TASA_PENSION_EMPLEADOR
        caja_empleador = ibc_caja * TASA_CAJA_EMPLEADOR
        arl_empleador = ibc_arl * tasa_arl

        mensaje_cotizacion = (
            "Aplica cotización parcial por semanas: no se liquida salud en este esquema "
            "porque el trabajador debe estar cubierto en salud como afiliado al régimen "
            "subsidiado o beneficiario del régimen contributivo. Se descuenta únicamente "
            "pensión del trabajador."
        )

    else:
        tipo_cotizacion = "Cotización ordinaria mínima"

        # Si no cumple requisitos de cotización parcial, se usa mínimo mensual.
        ibc_ordinario_mensual = max(base_salarial_real, SMLMV_2026)

        ibc_pension = ibc_ordinario_mensual * factor_periodo
        ibc_salud = ibc_ordinario_mensual * factor_periodo
        ibc_arl = ibc_ordinario_mensual * factor_periodo
        ibc_caja = ibc_ordinario_mensual * factor_periodo

        salud_trabajador = ibc_salud * TASA_SALUD_TRABAJADOR
        pension_trabajador = ibc_pension * TASA_PENSION_TRABAJADOR

        pension_empleador = ibc_pension * TASA_PENSION_EMPLEADOR
        caja_empleador = ibc_caja * TASA_CAJA_EMPLEADOR
        arl_empleador = ibc_arl * tasa_arl

        mensaje_cotizacion = (
            "No se cumplen todos los requisitos de cotización parcial por semanas. "
            "Por prudencia, el sistema liquida seguridad social con lógica ordinaria mínima."
        )

else:
    tipo_cotizacion = "Cotización ordinaria"

    ibc_pension = base_salarial_real
    ibc_salud = base_salarial_real
    ibc_arl = base_salarial_real
    ibc_caja = base_salarial_real

    salud_trabajador = ibc_salud * TASA_SALUD_TRABAJADOR
    pension_trabajador = ibc_pension * TASA_PENSION_TRABAJADOR

    pension_empleador = ibc_pension * TASA_PENSION_EMPLEADOR
    caja_empleador = ibc_caja * TASA_CAJA_EMPLEADOR
    arl_empleador = ibc_arl * tasa_arl

    mensaje_cotizacion = (
        "Liquidación ordinaria sobre base salarial del período. "
        "El auxilio de transporte no integra la base de seguridad social."
    )


total_deducciones = salud_trabajador + pension_trabajador + prestamos
neto = devengado - total_deducciones

costo_referencial_empleador = devengado + pension_empleador + arl_empleador + caja_empleador


# ============================================================
# 10. RESULTADOS
# ============================================================

st.markdown("### 💰 5. Resultado de Liquidación")

col_r1, col_r2, col_r3 = st.columns(3)

with col_r1:
    st.metric("Total Devengado", formato_pesos(devengado))

with col_r2:
    st.metric("Total Deducciones", formato_pesos(total_deducciones))

with col_r3:
    st.metric("Neto a Pagar", formato_pesos(neto))


st.markdown(f"""
<div class="success-box">
<strong>Modalidad aplicada:</strong> {tipo_cotizacion}<br>
<strong>Nota:</strong> {mensaje_cotizacion}
</div>
""", unsafe_allow_html=True)


# ============================================================
# 11. TABLA PRINCIPAL DEL DESPRENDIBLE
# ============================================================

resumen = pd.DataFrame({
    "Concepto": [
        "Salario proporcional",
        "Descanso dominical proporcional",
        "Horas extras y recargos",
        "Auxilio de transporte",
        "TOTAL DEVENGADO",
        "IBC salud",
        "IBC pensión",
        "Salud trabajador",
        "Pensión trabajador",
        "Otras deducciones autorizadas",
        "TOTAL DEDUCCIONES",
        "NETO FINAL A PAGAR"
    ],
    "Valor": [
        formato_pesos(salario_final),
        formato_pesos(dominical_proporcional),
        formato_pesos(total_extras),
        formato_pesos(auxilio_final),
        formato_pesos(devengado),
        formato_pesos(ibc_salud),
        formato_pesos(ibc_pension),
        f"- {formato_pesos(salud_trabajador)}",
        f"- {formato_pesos(pension_trabajador)}",
        f"- {formato_pesos(prestamos)}",
        f"- {formato_pesos(total_deducciones)}",
        formato_pesos(neto)
    ]
})

st.table(resumen)


# ============================================================
# 12. INFORMACIÓN PARA EMPLEADOR
# ============================================================

with st.expander("📌 Ver aportes referenciales a cargo del empleador"):
    aportes_empleador = pd.DataFrame({
        "Concepto": [
            "Pensión empleador",
            "ARL empleador",
            "Caja de compensación",
            "Costo referencial total empleador"
        ],
        "Valor": [
            formato_pesos(pension_empleador),
            formato_pesos(arl_empleador),
            formato_pesos(caja_empleador),
            formato_pesos(costo_referencial_empleador)
        ]
    })

    st.table(aportes_empleador)

    st.markdown("""
    <div class="alerta-legal">
    <strong>Nota:</strong> estos valores corresponden a una estimación referencial para orientación del empleador.
    El pago definitivo de seguridad social debe realizarse mediante PILA conforme al operador autorizado y la información real del trabajador.
    </div>
    """, unsafe_allow_html=True)


# ============================================================
# 13. ALERTAS JURÍDICAS
# ============================================================

st.markdown("### ⚠️ Alertas legales del MVP")

st.markdown("""
<div class="alerta-legal">
<strong>Advertencia 1:</strong> Este MVP liquida nómina periódica. No liquida prestaciones sociales definitivas, cesantías, intereses de cesantías, prima, vacaciones acumuladas ni indemnizaciones.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="alerta-legal">
<strong>Advertencia 2:</strong> En trabajadores por días, el descanso dominical proporcional se incluye como concepto salarial separado.
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="alerta-legal">
<strong>Advertencia 3:</strong> En cotización parcial por semanas, el trabajador debe estar cubierto en salud por régimen subsidiado o como beneficiario del régimen contributivo. Si no lo está, debe revisarse la afiliación y liquidación ordinaria correspondiente.
</div>
""", unsafe_allow_html=True)


# ============================================================
# 14. COMPROBANTE PARA FIRMA
# ============================================================

if st.button("📄 Generar Comprobante para Firma", type="primary"):
    fecha_actual = datetime.now().strftime("%d/%m/%Y")

    st.markdown(f"""
    <div class="recibo-box">
        <h3 style="text-align: center;">DESPRENDIBLE / RECIBO DE PAGO DE NÓMINA</h3>

        <p><strong>Fecha de generación:</strong> {fecha_actual}</p>
        <p><strong>Empleador:</strong> {empresa if empresa else "No informado"} |
        <strong>NIT/Cédula:</strong> {nit if nit else "No informado"}</p>

        <p><strong>Trabajador:</strong> {empleado if empleado else "No informado"} |
        <strong>Cédula:</strong> {cedula if cedula else "No informada"}</p>

        <p><strong>Modalidad:</strong> {modalidad}</p>
        <p><strong>Periodicidad:</strong> {periodicidad}</p>
        <p><strong>Tipo de cotización aplicada:</strong> {tipo_cotizacion}</p>

        <hr>

        <h4>Devengos</h4>
        <p>Salario proporcional: <strong>{formato_pesos(salario_final)}</strong></p>
        <p>Descanso dominical proporcional: <strong>{formato_pesos(dominical_proporcional)}</strong></p>
        <p>Horas extras y recargos: <strong>{formato_pesos(total_extras)}</strong></p>
        <p>Auxilio de transporte: <strong>{formato_pesos(auxilio_final)}</strong></p>
        <p><strong>Total devengado: {formato_pesos(devengado)}</strong></p>

        <h4>Deducciones</h4>
        <p>Salud trabajador: <strong>{formato_pesos(salud_trabajador)}</strong></p>
        <p>Pensión trabajador: <strong>{formato_pesos(pension_trabajador)}</strong></p>
        <p>Otras deducciones autorizadas: <strong>{formato_pesos(prestamos)}</strong></p>
        <p><strong>Total deducciones: {formato_pesos(total_deducciones)}</strong></p>

        <h3 style="text-align: center;">NETO FINAL PAGADO: {formato_pesos(neto)}</h3>

        <p style="font-size: 0.82rem; margin-top: 25px;">
        El trabajador declara haber recibido a conformidad el pago correspondiente al período liquidado,
        incluyendo salario proporcional, descanso dominical proporcional cuando aplica, auxilio de transporte,
        novedades reportadas y descuentos legales calculados según la modalidad seleccionada.
        </p>

        <p style="font-size: 0.82rem;">
        Este comprobante corresponde a nómina periódica y no constituye liquidación definitiva de prestaciones sociales,
        cesantías, intereses de cesantías, prima, vacaciones acumuladas ni indemnizaciones.
        </p>

        <div style="display: flex; justify-content: space-around; margin-top: 45px;">
            <div style="border-top: 1px solid black; width: 40%; text-align: center;">Firma Empleador</div>
            <div style="border-top: 1px solid black; width: 40%; text-align: center;">Firma Trabajador</div>
        </div>
    </div>
    """, unsafe_allow_html=True)