import streamlit as st
import pandas as pd

# 1. Configuración inicial de la interfaz
st.set_page_config(page_title="Liquidador de Nómina 2026", layout="wide")
st.title("Liquidador de Nómina 2026 y Prestaciones - Colombia 2026")
st.markdown("---")

# 2. Datos Generales de la Empresa y Empleado
col1, col2 = st.columns(2)
with col1:
    # Ahora la empresa es un campo de texto en blanco que tú puedes llenar
    empresa = st.text_input("Nombre de la empresa:", placeholder="Ingrese el nombre aquí...")
    empleado = st.text_input("Nombre del empleado:")
with col2:
    # Esto soluciona tu problema de liquidar cualquier cantidad de días
    dias_trabajados = st.number_input("Días a liquidar (Ej: 15 para quincena, 30 para mes):", min_value=1, max_value=360, value=15)
    tiene_auxilio = st.checkbox("¿Tiene derecho a auxilio de transporte?", value=True)

st.markdown("---")

# 3. Parámetros Legales Oficiales 2026
st.subheader("Parámetros de Ley 2026")
col3, col4 = st.columns(2)
with col3:
    salario_base = st.number_input("Salario Base Mensual (COP):", value=1750905, step=10000)
with col4:
    auxilio_base = st.number_input("Auxilio de Transporte Mensual (COP):", value=249095, step=10000) if tiene_auxilio else 0

# 4. Cálculos Matemáticos
salario_proporcional = (salario_base / 30) * dias_trabajados
auxilio_proporcional = (auxilio_base / 30) * dias_trabajados if tiene_auxilio else 0
total_devengado = salario_proporcional + auxilio_proporcional

salud = salario_proporcional * 0.04
pension = salario_proporcional * 0.04
total_deducciones = salud + pension

neto_pagar = total_devengado - total_deducciones

# 5. Visualización de Resultados
st.markdown("---")
st.subheader("Resumen de Liquidación")

resumen_df = pd.DataFrame({
    "Concepto": ["Salario Base Proporcional", "Auxilio de Transporte", "Deducción Salud (4%)", "Deducción Pensión (4%)", "TOTAL NETO A PAGAR"],
    "Valor (COP)": [
        f"${salario_proporcional:,.2f}", 
        f"${auxilio_proporcional:,.2f}", 
        f"-${salud:,.2f}", 
        f"-${pension:,.2f}", 
        f"${neto_pagar:,.2f}"
    ]
})

st.table(resumen_df)

if st.button("Generar Recibo"):
    if empresa and empleado:
        st.success(f"Recibo calculado exitosamente para {empleado} de la empresa {empresa}. Valor a pagar: ${neto_pagar:,.2f}")
    else:
        st.warning("Por favor, ingrese el nombre de la empresa y del empleado.")
        