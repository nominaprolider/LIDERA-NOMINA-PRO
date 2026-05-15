import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración y Diseño
st.set_page_config(page_title="Nómina Blindada Lidera", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main-header { background-color: #2E8B57; padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
.main-header h1 { color: white; font-family: 'Segoe UI', sans-serif; margin-bottom: 5px; }
.badge-container { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 30px; justify-content: center; }
.badge { border: 1px solid #4CAF50; background-color: #F1F8E9; border-radius: 20px; padding: 8px 18px; color: #2E7D32; font-weight: 600; font-size: 0.9rem; }
.recibo-box { border: 2px solid #2E8B57; padding: 30px; border-radius: 10px; background-color: white; margin-top: 20px; color: black; }
</style>

<div class="main-header">
    <h1>🌿 Asistente de Nómina Blindada</h1>
    <p>Gestión Integral Multisalario y Ausentismos · Colombia 2026</p>
</div>
<div class="badge-container">
    <span class="badge">⚖️ Jornada 44h (Divisor 220)</span>
    <span class="badge">🔄 Ley 2466/2025 (Recargo 80%)</span>
    <span class="badge">🛡️ Blindaje Jurisprudencial CSJ</span>
</div>
""", unsafe_allow_html=True)

# 2. Constantes Legales 2026
SMLMV_2026 = 1750905
AUXILIO_2026 = 249095
LIMITE_AUXILIO = SMLMV_2026 * 2
DIVISOR_HORAS = 220 

# 3. Datos Básicos
st.markdown("### 📋 1. Datos Generales")
col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Nombre de la Empresa / Empleador")
    nit = st.text_input("NIT o Cédula del Empleador")
with col2:
    empleado = st.text_input("Nombre completo del trabajador")
    cedula = st.text_input("Cédula del trabajador")

st.divider()

# 4. Configuración Salarial
st.markdown("### ⚙️ 2. Modalidad y Base Salarial")
modalidad = st.radio("Tipo de vinculación:", ["Ordinaria (Quincena/Mes)", "Por Días (Doméstica/Meseros)"], horizontal=True)

salario_base = st.number_input("Salario Base Mensual Pactado (COP)", min_value=1750905, value=1750905, step=50000)
VALOR_HORA_ORDINARIA = salario_base / DIVISOR_HORAS
aplica_auxilio_ley = True if salario_base <= LIMITE_AUXILIO else False

if modalidad == "Ordinaria (Quincena/Mes)":
    col3, col4 = st.columns(2)
    with col3:
        dias_periodo = st.number_input("Días del período a liquidar", min_value=1, max_value=30, value=15)
    with col4:
        tiene_auxilio = st.checkbox("Incluir Auxilio de Transporte", value=aplica_auxilio_ley)
else:
    col3, col4 = st.columns(2)
    with col3:
        dias_periodo = st.number_input("Días laborados en el mes", min_value=1, max_value=21, value=4)
    with col4:
        tiene_auxilio = st.checkbox("Incluir Auxilio Proporcional", value=True)

# 5. Novedades, Horas Extras y Ausentismos (TODO INTEGRADO)
st.markdown("### 📊 3. Novedades del Período")

with st.expander("➕ Horas Extras y Recargos"):
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        he_d = st.number_input("H. Extras Diurnas (25%)", value=0.0)
        he_n = st.number_input("H. Extras Nocturnas (75%)", value=0.0)
        rec_n = st.number_input("Recargos Nocturnos (35%)", value=0.0)
    with col_h2:
        dom = st.number_input("Dominical/Festivo Ordinario (80%)", value=0.0)
        he_dom_d = st.number_input("H.E. Dom Diurna (105%)", value=0.0)
        he_dom_n = st.number_input("H.E. Dom Nocturna (155%)", value=0.0)

with st.expander("⚠️ Registrar Ausencias e Incapacidades"):
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        faltas_injustificadas = st.number_input("Faltas INJUSTIFICADAS (Días)", min_value=0, help="CST Art. 173: Descuenta el día, el dominical y el auxilio de transporte.")
    with col_a2:
        inasistencias_justificadas = st.number_input("Inasistencias JUSTIFICADAS / Incapacidad", min_value=0, help="CSJ: Mantiene el dominical, pero descuenta el Auxilio de Transporte al no haber desplazamiento.")

with st.expander("➖ Otras Deducciones"):
    prestamos = st.number_input("Préstamos/Embargos (COP)", value=0, step=10000, help="Debe existir autorización escrita.")

# 6. Lógica Matemática Blindada
valor_dia = salario_base / 30

# Días a pagar (Descuentos inteligentes)
dias_salario = max(0, dias_periodo - (faltas_injustificadas * 2)) # Falta + Dominical
dias_auxilio = max(0, dias_periodo - faltas_injustificadas - inasistencias_justificadas) # Ambas quitan transporte

salario_final = (valor_dia * dias_salario)
auxilio_final = (AUXILIO_2026 / 30 * dias_auxilio) if tiene_auxilio else 0

total_extras = (he_d * VALOR_HORA_ORDINARIA * 1.25) + (he_n * VALOR_HORA_ORDINARIA * 1.75) + (rec_n * VALOR_HORA_ORDINARIA * 0.35) + (dom * VALOR_HORA_ORDINARIA * 1.80) + (he_dom_d * VALOR_HORA_ORDINARIA * 2.05) + (he_dom_n * VALOR_HORA_ORDINARIA * 2.55)

devengado = salario_final + total_extras + auxilio_final
base_ss = salario_final + total_extras

salud = base_ss * 0.04
pension = base_ss * 0.04
neto = devengado - salud - pension - prestamos

# 7. Visualización y Comprobante
st.markdown("---")
st.markdown(f"### 💰 TOTAL NETO A PAGAR: **${neto:,.0f}**")

resumen = pd.DataFrame({
    "Concepto": ["Salario Proporcional", "Total Horas Extras", "Auxilio de Transporte", "Salud (4%)", "Pensión (4%)", "Préstamos/Otros", "NETO FINAL"],
    "Valor": [f"+ $ {salario_final:,.0f}", f"+ $ {total_extras:,.0f}", f"+ $ {auxilio_final:,.0f}", f"- $ {salud:,.0f}", f"- $ {pension:,.0f}", f"- $ {prestamos:,.0f}", f"$ {neto:,.0f}"]
})
st.table(resumen)

if st.button("📄 Generar Comprobante para Firma", type="primary"):
    st.markdown(f"""
    <div class="recibo-box">
        <h3 style="text-align: center;">RECIBO DE PAGO Y PAZ Y SALVO</h3>
        <p><strong>Empresa:</strong> {empresa} | <strong>Trabajador:</strong> {empleado} ({cedula})</p>
        <p><strong>Neto Pagado:</strong> ${neto:,.0f}</p>
        <p style="font-size: 0.8rem;">El trabajador declara haber recibido a conformidad el pago exacto de su salario, auxilio de transporte, recargos y descuentos de ley, encontrándose a paz y salvo por este periodo.</p>
        <div style="display: flex; justify-content: space-around; margin-top: 40px;">
            <div style="border-top: 1px solid black; width: 40%; text-align: center;">Empleador</div>
            <div style="border-top: 1px solid black; width: 40%; text-align: center;">Trabajador</div>
        </div>
    </div>
    """, unsafe_allow_html=True)