import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración y Diseño Visual
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
    <p>Liquidación Integral · Colombia 2026</p>
</div>
<div class="badge-container">
    <span class="badge">⚖️ Jornada 44h (Divisor 220)</span>
    <span class="badge">🔄 Ley 2466/2025</span>
    <span class="badge">📑 Decreto 2616/2013 (Por días)</span>
</div>
""", unsafe_allow_html=True)

# 2. Constantes Legales 2026
SMLMV_2026 = 1750905
AUXILIO_2026 = 249095
LIMITE_AUXILIO = SMLMV_2026 * 2
DIVISOR_HORAS = 220

# 3. Datos del Empleador y Empleado
st.markdown("### 📋 1. Datos Generales")
col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Nombre de la Empresa / Empleador")
    nit = st.text_input("NIT o Cédula del Empleador")
with col2:
    empleado = st.text_input("Nombre completo del trabajador")
    cedula = st.text_input("Cédula del trabajador")

st.divider()

# 4. CONFIGURACIÓN SALARIAL Y MODALIDAD (LA SOLUCIÓN A TUS DUDAS)
st.markdown("### ⚙️ 2. Modalidad y Base Salarial")

modalidad = st.radio(
    "Seleccione el tipo de vinculación del trabajador:",
    ["Ordinaria (Tiempo Completo / Quincena / Mes)", "Por Días (Ej: Servicio Doméstico, Meseros)"],
    horizontal=True
)

st.info("💡 **AQUÍ ESTÁ LA CASILLA EDITABLE:** Modifica el valor si el trabajador gana más del salario mínimo. El sistema quitará automáticamente el auxilio de transporte si supera los 2 SMLMV ($3.501.810).")

salario_base = st.number_input("Salario Base Mensual Pactado (COP)", min_value=1750905, value=1750905, step=50000)
VALOR_HORA_ORDINARIA = salario_base / DIVISOR_HORAS

# Verificación automática del auxilio de transporte
aplica_auxilio_ley = True if salario_base <= LIMITE_AUXILIO else False

if modalidad == "Ordinaria (Tiempo Completo / Quincena / Mes)":
    col3, col4 = st.columns(2)
    with col3:
        dias_periodo = st.number_input("Días del período a liquidar (Ej: 15 o 30)", min_value=1, max_value=30, value=15)
    with col4:
        tiene_auxilio = st.checkbox("Incluir Auxilio de Transporte", value=aplica_auxilio_ley)
        if not aplica_auxilio_ley:
            st.caption("Desactivado por ley: Supera los 2 SMLMV.")
    
    # Cálculos Ordinarios
    salario_proporcional = (salario_base / 30) * dias_periodo
    auxilio_proporcional = (AUXILIO_2026 / 30) * dias_periodo if tiene_auxilio else 0

else: # Modalidad por Días
    st.warning("⚖️ **Decreto 2616 de 2013:** La seguridad social de este trabajador debe aportarse a través de PILA por cotización de semanas, dependiendo de los días laborados al mes.")
    col3, col4 = st.columns(2)
    with col3:
        dias_periodo = st.number_input("Días efectivamente laborados en el mes", min_value=1, max_value=21, value=4)
    with col4:
        tiene_auxilio = st.checkbox("Incluir Auxilio de Transporte (Proporcional a días idos)", value=True)
    
    # Cálculos por Días (El auxilio se paga dividiendo el mensual en 30 y multiplicando por días laborados)
    salario_proporcional = (salario_base / 30) * dias_periodo
    auxilio_proporcional = (AUXILIO_2026 / 30) * dias_periodo if tiene_auxilio else 0

# 5. Novedades y Descuentos
with st.expander("➕ Novedades: Trabajo Extra y Recargos"):
    col_he1, col_he2, col_he3 = st.columns(3)
    with col_he1:
        he_diurnas = st.number_input("H. Extras Diurnas (25%)", min_value=0.0, value=0.0)
        he_nocturnas = st.number_input("H. Extras Nocturnas (75%)", min_value=0.0, value=0.0)
    with col_he2:
        recargo_nocturno = st.number_input("Recargos Nocturnos (35%)", min_value=0.0, value=0.0)
        dom_fest_ordinario = st.number_input("Dominical/Festivo Ordinario (80%)", min_value=0.0, value=0.0)
    with col_he3:
        he_dom_diurna = st.number_input("H.E. Dom Diurna (105%)", min_value=0.0, value=0.0)
        he_dom_nocturna = st.number_input("H.E. Dom Nocturna (155%)", min_value=0.0, value=0.0)

with st.expander("➖ Deducciones"):
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        faltas = st.number_input("Días de falta injustificada", min_value=0, max_value=30, value=0)
    with col_d2:
        prestamos = st.number_input("Préstamos u otras deducciones (COP)", min_value=0, value=0, step=10000)

# Lógica de descuentos
salario_proporcional = max(0, salario_proporcional - ((salario_base/30) * faltas) - ((salario_base/30) * faltas)) # Descuenta día faltado + dominical
if tiene_auxilio:
    auxilio_proporcional = max(0, auxilio_proporcional - ((AUXILIO_2026/30) * faltas))

total_extras = (he_diurnas * VALOR_HORA_ORDINARIA * 1.25) + (he_nocturnas * VALOR_HORA_ORDINARIA * 1.75) + (recargo_nocturno * VALOR_HORA_ORDINARIA * 0.35) + (dom_fest_ordinario * VALOR_HORA_ORDINARIA * 1.80) + (he_dom_diurna * VALOR_HORA_ORDINARIA * 2.05) + (he_dom_nocturna * VALOR_HORA_ORDINARIA * 2.55)

total_devengado = salario_proporcional + total_extras + auxilio_proporcional
base_seguridad_social = salario_proporcional + total_extras

salud = base_seguridad_social * 0.04
pension = base_seguridad_social * 0.04
total_deducciones = salud + pension + prestamos

neto_pagar = total_devengado - total_deducciones

# 6. Visualización
st.markdown("---")
st.markdown("### 📊 Liquidación y Comprobante")
df_resultados = pd.DataFrame({
    "Concepto": ["Salario Base Proporcional", "Horas Extras y Recargos", "Aux. Transporte", "Salud (4%)", "Pensión (4%)", "Préstamos/Otros", "TOTAL NETO"],
    "Valor (COP)": [f"+ ${salario_proporcional:,.0f}", f"+ ${total_extras:,.0f}", f"+ ${auxilio_proporcional:,.0f}", f"- ${salud:,.0f}", f"- ${pension:,.0f}", f"- ${prestamos:,.0f}", f"${neto_pagar:,.0f}"]
})
st.table(df_resultados)