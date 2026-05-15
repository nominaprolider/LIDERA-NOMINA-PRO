import streamlit as st
import pandas as pd

# 1. Configuración y Diseño Visual
st.set_page_config(page_title="Nómina Blindada Lidera", layout="wide", page_icon="🌿")

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
.main-header h1 { color: white; font-family: 'Segoe UI', sans-serif; margin-bottom: 5px; }
.main-header p { font-size: 1.1rem; color: #E8F5E9; }
.badge-container { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 30px; justify-content: center; }
.badge { border: 1px solid #4CAF50; background-color: #F1F8E9; border-radius: 20px; padding: 8px 18px; color: #2E7D32; font-weight: 600; font-size: 0.9rem; }
</style>

<div class="main-header">
    <h1>🌿 Asistente de Nómina Blindada</h1>
    <p>Liquidación integral conforme al Código Sustantivo del Trabajo · Colombia 2026</p>
</div>
<div class="badge-container">
    <span class="badge">✓ SMLMV 2026: $1.750.905</span>
    <span class="badge">✓ Aux. Transporte: $249.095</span>
    <span class="badge">⚖️ Jornada 42h (Divisor 210)</span>
</div>
""", unsafe_allow_html=True)

# 2. Constantes Legales 2026
SMLMV_2026 = 1750905
AUXILIO_2026 = 249095
DIVISOR_HORAS = 210
VALOR_HORA_ORDINARIA = SMLMV_2026 / DIVISOR_HORAS

st.markdown("### 📋 1. Datos del Período")
col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Nombre de la Empresa / Empleador")
    empleado = st.text_input("Nombre completo del trabajador")
with col2:
    dias_periodo = st.number_input("Días del período a liquidar (Ej: 15 para quincena)", min_value=1, max_value=30, value=15)
    tiene_auxilio = st.checkbox("¿Tiene derecho a Auxilio de Transporte?", value=True)

# 3. Novedades (Ingresos Adicionales)
with st.expander("➕ Novedades: Trabajo Extra y Recargos (Desplegar si aplica)"):
    st.info("Ingresa la cantidad de horas extras o recargos laborados en el período.")
    col_he1, col_he2, col_he3 = st.columns(3)
    with col_he1:
        he_diurnas = st.number_input("Horas Extras Diurnas (25%)", min_value=0.0, value=0.0, step=1.0)
        he_nocturnas = st.number_input("Horas Extras Nocturnas (75%)", min_value=0.0, value=0.0, step=1.0)
    with col_he2:
        recargo_nocturno = st.number_input("Recargos Nocturnos (35%)", min_value=0.0, value=0.0, step=1.0)
        dom_fest_ordinario = st.number_input("Dominical/Festivo Ordinario (75%)", min_value=0.0, value=0.0, step=1.0)
    with col_he3:
        he_dom_diurna = st.number_input("H. Extra Dom/Fest Diurna (100%)", min_value=0.0, value=0.0, step=1.0)
        he_dom_nocturna = st.number_input("H. Extra Dom/Fest Nocturna (150%)", min_value=0.0, value=0.0, step=1.0)

# 4. Descuentos y Ausentismos
with st.expander("➖ Deducciones y Ausentismos (Desplegar si aplica)"):
    st.warning("Los días de ausencia injustificada descuentan el día laborado, el auxilio de transporte de ese día, y causan la pérdida del dominical.")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        faltas_injustificadas = st.number_input("Días de falta injustificada", min_value=0, max_value=30, value=0)
        dias_incapacidad = st.number_input("Días de incapacidad médica (No suma aux. transp)", min_value=0, max_value=30, value=0)
    with col_d2:
        prestamos = st.number_input("Descuento por préstamos/anticipos (COP)", min_value=0, value=0, step=10000)
        otras_deducciones = st.number_input("Otras deducciones autorizadas (COP)", min_value=0, value=0, step=10000)

# 5. LÓGICA MATEMÁTICA Y BLINDAJE LEGAL
# Días a pagar (restando faltas)
dias_salario = dias_periodo - faltas_injustificadas - dias_incapacidad
# Descuento del dominical por faltas injustificadas (1 falta = 1 dominical perdido)
dias_salario = max(0, dias_salario - faltas_injustificadas) 

dias_transporte = dias_periodo - faltas_injustificadas - dias_incapacidad

salario_proporcional = (SMLMV_2026 / 30) * dias_salario
auxilio_proporcional = (AUXILIO_2026 / 30) * dias_transporte if tiene_auxilio else 0

# Cálculo de Extras
total_extras = (
    (he_diurnas * VALOR_HORA_ORDINARIA * 1.25) +
    (he_nocturnas * VALOR_HORA_ORDINARIA * 1.75) +
    (recargo_nocturno * VALOR_HORA_ORDINARIA * 0.35) +
    (dom_fest_ordinario * VALOR_HORA_ORDINARIA * 1.75) +
    (he_dom_diurna * VALOR_HORA_ORDINARIA * 2.00) +
    (he_dom_nocturna * VALOR_HORA_ORDINARIA * 2.50)
)

total_devengado = salario_proporcional + total_extras + auxilio_proporcional
base_seguridad_social = salario_proporcional + total_extras # El auxilio de transporte no hace base para salud/pensión

salud = base_seguridad_social * 0.04
pension = base_seguridad_social * 0.04
total_deducciones = salud + pension + prestamos + otras_deducciones

neto_pagar = total_devengado - total_deducciones

# 6. Visualización del Desprendible
st.markdown("---")
st.markdown("### 📊 Desprendible de Pago")

df_resultados = pd.DataFrame({
    "Concepto": [
        f"Salario Base ({dias_salario} días pagados)", 
        "Total Horas Extras y Recargos",
        f"Auxilio Transporte ({dias_transporte} días)", 
        "Deducción Salud (4%)", 
        "Deducción Pensión (4%)", 
        "Descuento Préstamos y Otros",
        "TOTAL NETO A PAGAR"
    ],
    "Valor (COP)": [
        f"+ ${salario_proporcional:,.0f}", 
        f"+ ${total_extras:,.0f}",
        f"+ ${auxilio_proporcional:,.0f}", 
        f"- ${salud:,.0f}", 
        f"- ${pension:,.0f}", 
        f"- ${(prestamos + otras_deducciones):,.0f}",
        f"💰 ${neto_pagar:,.0f}"
    ]
})

st.table(df_resultados)