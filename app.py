import streamlit as st
from logic import calcular_nomina, SMLMV_2026, AUX_TRANSPORTE, VALOR_HORA_MINIMA
from pdf_generator import generar_pdf

# Configuración de página
st.set_page_config(page_title="Lidera Nómina Legal", layout="wide")

# ESTILO: AZUL CORPORATIVO (Firma Legal)
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button { background-color: #0D47A1; color: white; border-radius: 8px; font-weight: bold; border: none; }
    .stButton>button:hover { background-color: #1565C0; color: white; }
    div[data-baseweb="input"] { background-color: #E3F2FD !important; border-radius: 5px; }
    div[data-testid="stExpander"] { border-color: #0D47A1 !important; border-width: 2px; }
    </style>
    """, unsafe_allow_html=True)

st.title("⚖️ Lidera Nómina - Despacho Legal")
st.write("Liquidador profesional ajustado a la Normativa Colombiana 2026")

with st.expander("👤 1. Datos del Empleador y Empleado", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        restaurante = st.text_input("Nombre de la Empresa / Empleador")
        empleado = st.text_input("Nombre del Trabajador")
    with col2:
        nit = st.text_input("NIT / Cédula Empleador")
        cedula = st.text_input("Cédula Trabajador")

with st.expander("💰 2. Salario y Tiempo Adicional"):
    salario_base = st.number_input("Salario Mensual Base (SMLMV 2026: $1.512.000)", value=SMLMV_2026)
    he_diurnas = st.number_input("Horas Extra Diurnas", value=0)
    recargos_noc = st.number_input("Horas con Recargo Nocturno", value=0)

with st.expander("🏥 3. ¿Hubo faltas o incapacidades?"):
    dias_incapacidad = st.number_input("Días de Incapacidad Médica", value=0)
    faltas_injustificadas = st.number_input("Días de faltas sin permiso (Activa Art. 173)", value=0)

with st.expander("📉 4. Préstamos y Descuentos"):
    prestamos = st.number_input("Vales, préstamos o adelantos de sueldo", value=0)

if st.button("🚀 Calcular Nómina y Generar Soporte"):
    resultados = calcular_nomina(salario_base, he_diurnas, recargos_noc, dias_incapacidad, faltas_injustificadas, prestamos)
    
    st.success("✅ Liquidación calculada con precisión legal.")
    
    # --- DESGLOSE EN PANTALLA ---
    st.subheader("📊 Desglose Detallado de la Liquidación")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🟢 DEVENGOS (Ingresos)")
        st.write(f"**Salario Base (Proporcional a {resultados['dias_trabajados']} días):** ${resultados['salario_base']/30*resultados['dias_trabajados']:,.0f}")
        st.write(f"**Horas Extras y Recargos:** ${resultados['total_extras']:,.0f}")
        st.write(f"**Pago por Incapacidad:** ${resultados['pago_incapacidad']:,.0f}")
        st.write(f"**Auxilio de Transporte:** ${resultados['aux_transporte']:,.0f}")
        st.markdown(f"#### Total Devengado: ${resultados['total_devengado']:,.0f}")
        
    with col2:
        st.markdown("### 🔴 DEDUCCIONES (Descuentos)")
        st.write(f"**Salud (4%):** ${resultados['salud']:,.0f}")
        st.write(f"**Pensión (4%):** ${resultados['pension']:,.0f}")
        st.write(f"**Castigo por Faltas (Art. 173):** ${resultados['descuento_faltas']:,.0f}")
        st.write(f"**Préstamos/Adelantos:** ${resultados['prestamos']:,.0f}")
        st.markdown(f"#### Total Deducciones: ${resultados['total_deducciones']:,.0f}")
        
    st.markdown("---")
    st.markdown(f"## 💵 NETO A PAGAR: ${resultados['neto']:,.0f}")
    
    # Generador de PDF Reparado
    try:
        pdf_file = generar_pdf(restaurante, empleado, resultados)
        st.download_button("📩 Descargar Comprobante Legal (PDF)", data=pdf_file, file_name=f"Nomina_{empleado}.pdf")
    except Exception as e:
        st.error(f"Error interno al crear PDF. Por favor avisa a soporte: {e}")
