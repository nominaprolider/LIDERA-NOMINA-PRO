import streamlit as st
from logic import calcular_nomina, SMLMV_2026, AUX_TRANSPORTE, VALOR_HORA_MINIMA
from pdf_generator import generar_pdf

# Configuración de página
st.set_page_config(page_title="Lidera Nómina Pro", layout="wide")

# Estilo personalizado: VERDE OSCURO y fondo claro
st.markdown("""
    <style>
    .main { background-color: #F5F7F5; }
    .stButton>button { background-color: #1B5E20; color: white; border-radius: 10px; }
    div[data-baseweb="input"] { background-color: #E8F5E9 !important; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ Lidera Nómina - Blindaje Gastronómico")
st.write("Liquidador profesional ajustado a Normativa 2026")

# --- SECCIÓN 1: DATOS BÁSICOS ---
with st.expander("👤 1. Datos del Empleador y Empleado", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        restaurante = st.text_input("Nombre del Restaurante")
        empleado = st.text_input("Nombre del Trabajador")
    with col2:
        nit = st.text_input("NIT / Cédula Empleador")
        cedula = st.text_input("Cédula Trabajador")

# --- SECCIÓN 2: SALARIO Y TIEMPO ---
with st.expander("💰 2. Salario y Tiempo Adicional"):
    salario_base = st.number_input("Salario Mensual Base (SMLMV 2026: $1.512.000)", value=SMLMV_2026)
    st.info("¿Trabajó tiempo adicional?")
    he_diurnas = st.number_input("Horas Extra Diurnas", value=0)
    recargos_noc = st.number_input("Horas con Recargo Nocturno", value=0)

# --- SECCIÓN 3: NOVEDADES (AUSENCIAS E INCAPACIDADES) ---
with st.expander("🏥 3. ¿Hubo faltas o incapacidades?"):
    st.write("Registra aquí si el empleado no asistió.")
    dias_incapacidad = st.number_input("Días de Incapacidad (Ley: Primeros 2 al 100%)", value=0)
    faltas_injustificadas = st.number_input("Días de faltas sin permiso (Afecta Domingo Art. 173)", value=0)

# --- SECCIÓN 4: DESCUENTOS Y VALES ---
with st.expander("📉 4. Préstamos y Descuentos"):
    prestamos = st.number_input("Vales, préstamos o adelantos de sueldo", value=0)

if st.button("🚀 Calcular Nómina y Blindar"):
    # Aquí llamamos a tu lógica de Logic.py
    resultados = calcular_nomina(salario_base, he_diurnas, recargos_noc, dias_incapacidad, faltas_injustificadas, prestamos)
    
    st.success("Cálculo Realizado con Éxito")
    
    # Mostrar resultados amigables
    st.subheader("Resumen de Pago")
    st.write(f"**Total a Recibir:** ${resultados['neto']:,.0f}")
    
    # Botón PDF
    pdf_file = generar_pdf(restaurante, empleado, resultados)
    st.download_button("📩 Descargar Comprobante Legal (PDF)", data=pdf_file, file_name=f"Nomina_{empleado}.pdf")
