import streamlit as st
import pandas as pd

# 1. Configuración de página
st.set_page_config(page_title="Nómina Blindada Lidera", layout="wide", page_icon="🌿")

# 2. Diseño Visual (CSS Integrado)
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
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin-bottom: 5px;
}
.main-header p {
    font-size: 1.1rem;
    color: #E8F5E9;
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
</style>

<div class="main-header">
    <h1>🌿 Asistente de Nómina Blindada</h1>
    <p>Tu nómina correcta, clara y legalmente protegida · Colombia 2026</p>
</div>

<div class="badge-container">
    <span class="badge">✓ Salario Mínimo Legal 2026: $1.750.905</span>
    <span class="badge">✓ Auxilio de Transporte: $249.095</span>
    <span class="badge">🛡️ Blindaje legal CST</span>
</div>
""", unsafe_allow_html=True)

# 3. Formulario de Ingreso
st.markdown("### 📋 Llena los datos de la nómina")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Nombre de la Empresa / Empleador")
    empleado = st.text_input("Nombre completo del trabajador")
with col2:
    dias = st.number_input("Días a liquidar (Ej: 15 para quincena, 30 para mes)", min_value=1, max_value=360, value=15)
    tiene_auxilio = st.checkbox("¿Tiene derecho a Auxilio de Transporte?", value=True)

# 4. Bases legales 2026 y Cálculos
SMLMV_2026 = 1750905
AUXILIO_2026 = 249095

salario_proporcional = (SMLMV_2026 / 30) * dias
auxilio_proporcional = (AUXILIO_2026 / 30) * dias if tiene_auxilio else 0
total_devengado = salario_proporcional + auxilio_proporcional

salud = salario_proporcional * 0.04
pension = salario_proporcional * 0.04
total_deducciones = salud + pension
neto = total_devengado - total_deducciones

# 5. Visualización de Resultados
st.markdown("---")
st.markdown("### 📊 Resumen de la liquidación")

df = pd.DataFrame({
    "Concepto": ["Salario Proporcional", "Auxilio Transporte", "Salud (4%)", "Pensión (4%)", "TOTAL NETO A PAGAR"],
    "Valor (COP)": [
        f"+ ${salario_proporcional:,.0f}", 
        f"+ ${auxilio_proporcional:,.0f}", 
        f"- ${salud:,.0f}", 
        f"- ${pension:,.0f}", 
        f"💰 ${neto:,.0f}"
    ]
})

st.table(df)