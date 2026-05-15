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
    <p>Gestión Integral de Novedades y Ausentismos · Colombia 2026</p>
</div>
<div class="badge-container">
    <span class="badge">⚖️ Jornada 44h (Divisor 220)</span>
    <span class="badge">🔄 Ley 2466/2025 (Recargo 80%)</span>
    <span class="badge">🛡️ Blindaje Jurisprudencial CSJ</span>
</div>
""", unsafe_allow_html=True)

# 2. Constantes 2026
SMLMV_2026 = 1750905
AUXILIO_2026 = 249095
DIVISOR_HORAS = 220 
LIMITE_AUXILIO = SMLMV_2026 * 2

# 3. Datos Básicos
st.markdown("### 📋 1. Información General")
col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Empresa/Empleador")
    empleado = st.text_input("Trabajador")
with col2:
    salario_base = st.number_input("Salario Mensual Pactado (COP)", min_value=1750905, value=1750905, step=50000)
    modalidad = st.radio("Modalidad:", ["Mensual/Quincenal", "Por Días"], horizontal=True)

# 4. Gestión de Días y Auxilio
dias_periodo = st.number_input("Días del período a liquidar", min_value=1, max_value=30, value=15)
tiene_auxilio = st.checkbox("¿Aplica Auxilio de Transporte?", value=(salario_base <= LIMITE_AUXILIO))

st.divider()

# 5. NOVEDADES Y AUSENTISMOS (EL AJUSTE SOLICITADO)
st.markdown("### ⚙️ 2. Novedades del Período")
with st.expander("⚠️ Registrar Ausencias e Incapacidades (Click para desplegar)"):
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        faltas_injustificadas = st.number_input(
            "Faltas INJUSTIFICADAS (Días)", min_value=0, 
            help="CST Art. 173: Descuenta el salario del día, el auxilio de transporte y EL DOMINICAL."
        )
    with col_a2:
        inasistencias_justificadas = st.number_input(
            "Inasistencias JUSTIFICADAS / Incapacidad (Días)", min_value=0,
            help="Jurisprudencia CSJ: No descuenta el dominical, pero el Auxilio de Transporte NO se paga por estos días al no haber desplazamiento."
        )

# 6. LÓGICA MATEMÁTICA BLINDADA
valor_dia = salario_base / 30
valor_hora = salario_base / DIVISOR_HORAS

# Días para Salario: Se descuentan las injustificadas y se resta el dominical por cada falta
# Las justificadas no descuentan salario en este liquidador (se asume permiso pago o trámite EPS)
dias_a_pagar_salario = dias_periodo - (faltas_injustificadas * 2) 

# Días para Auxilio: Se descuentan AMBAS (Justificadas e Injustificadas)
dias_a_pagar_auxilio = max(0, dias_periodo - faltas_injustificadas - inasistencias_justificadas)

salario_final = (valor_dia * dias_a_pagar_salario)
auxilio_final = (AUXILIO_2026 / 30 * dias_a_pagar_auxilio) if tiene_auxilio else 0

# (Cálculo de seguridad social sobre el devengado de salario)
salud_pension = (salario_final * 0.08)
neto = salario_final + auxilio_final - salud_pension

# 7. Visualización
st.markdown("---")
st.markdown(f"### 📊 Resumen Liquidación: **${neto:,.0f}**")

# Tabla de Auditoría
resumen = pd.DataFrame({
    "Concepto": ["Días Salario Pagados", "Días Auxilio Pagados", "Salario Proporcional", "Auxilio Transporte", "Seguridad Social (8%)", "NETO FINAL"],
    "Detalle": [f"{dias_a_pagar_salario} días", f"{dias_a_pagar_auxilio} días", f"$ {salario_final:,.0f}", f"$ {auxilio_final:,.0f}", f"- $ {salud_pension:,.0f}", f"$ {neto:,.0f}"]
})
st.table(resumen)