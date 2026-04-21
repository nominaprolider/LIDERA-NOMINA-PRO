import streamlit as st
from logic import calcular_nomina, SMLMV_2026, AUX_TRANSPORTE
from pdf_generator import generar_pdf

st.set_page_config(page_title="Lidera Nómina Legal", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button { background-color: #0D47A1; color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; padding: 10px; }
    .stButton>button:hover { background-color: #1565C0; color: white; }
    div[data-baseweb="input"] { background-color: #FFFFFF !important; border-radius: 5px; border: 1px solid #BBDEFB; }
    div[data-testid="stExpander"] { border-color: #0D47A1 !important; border-width: 1px; border-radius: 8px; background-color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("""
    <div style='background-color: #0D47A1; padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h1 style='margin: 0; color: white;'>⚖️ Lidera Nómina Pro - Colombia</h1>
        <p style='margin: 5px 0 0 0; font-size: 18px;'>Liquidador de Nómina • Blindado Legalmente • Normativa 2026</p>
    </div>
    """, unsafe_allow_html=True)

with st.expander("👤 1. DATOS DEL EMPLEADOR, EMPLEADO Y PERÍODO", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        restaurante = st.text_input("Nombre de la Empresa / Empleador")
        empleado = st.text_input("Nombre del Trabajador")
        fecha_inicio = st.date_input("Fecha Inicio Período")
    with col2:
        nit = st.text_input("NIT / Cédula Empleador")
        cedula = st.text_input("Cédula Trabajador")
        fecha_fin = st.date_input("Fecha Fin Período")

with st.expander("💰 2. SALARIO Y TIEMPO ADICIONAL (Horas Extras y Dominicales)"):
    salario_base = st.number_input("Salario Mensual Base", value=SMLMV_2026)
    st.markdown("**Recargos y Horas Adicionales**")
    col3, col4 = st.columns(2)
    with col3:
        he_diurnas = st.number_input("Horas Extra Diurnas", value=0)
        recargos_noc = st.number_input("Horas Recargo Nocturno", value=0)
    with col4:
        recargos_dom = st.number_input("Horas Trabajadas Dom/Fest (Ordinarias)", value=0)
        he_dom = st.number_input("Horas Extra en Dom/Festivo", value=0)

with st.expander("🏥 3. FALTAS E INCAPACIDADES (Descuentos de Ley)"):
    col5, col6 = st.columns(2)
    with col5:
        dias_incapacidad = st.number_input("Días de Incapacidad Médica", value=0)
    with col6:
        faltas_injustificadas = st.number_input("Faltas sin permiso (Activa Art. 173)", value=0)

with st.expander("📉 4. OTROS DESCUENTOS"):
    prestamos = st.number_input("Vales, préstamos o adelantos de sueldo", value=0)

st.write("<br>", unsafe_allow_html=True)

if st.button("🚀 CALCULAR NÓMINA Y GENERAR SOPORTE"):
    resultados = calcular_nomina(salario_base, he_diurnas, recargos_noc, recargos_dom, he_dom, dias_incapacidad, faltas_injustificadas, prestamos)
    st.success("✅ Liquidación calculada con precisión legal.")
    
    st.markdown(f"<h2 style='text-align: center; color: #0D47A1; background-color: #E3F2FD; padding: 15px; border-radius: 10px;'>💵 NETO A PAGAR: ${resultados['neto']:,.0f}</h2>", unsafe_allow_html=True)
    
    try:
        # Ahora enviamos las fechas y documentos al generador de PDF
        pdf_file = generar_pdf(restaurante, nit, empleado, cedula, str(fecha_inicio), str(fecha_fin), resultados)
        st.download_button("📩 Descargar Comprobante Legal (PDF)", data=pdf_file, file_name=f"Nomina_{empleado}.pdf")
    except Exception as e:
        st.error(f"Error al crear PDF: {e}")
