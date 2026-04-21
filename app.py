import streamlit as st
from logic import calcular_nomina, SMLMV_2026, AUX_TRANSPORTE
from pdf_generator import generar_pdf

# Configuración de página
st.set_page_config(page_title="Lidera Nómina Legal", layout="wide")

# ESTILO PREMIUM: AZUL CORPORATIVO Y BANNER
st.markdown("""
    <style>
    .main { background-color: #F8FAFC; }
    .stButton>button { background-color: #0D47A1; color: white; border-radius: 8px; font-weight: bold; border: none; width: 100%; padding: 10px; }
    .stButton>button:hover { background-color: #1565C0; color: white; }
    div[data-baseweb="input"] { background-color: #FFFFFF !important; border-radius: 5px; border: 1px solid #BBDEFB; }
    div[data-testid="stExpander"] { border-color: #0D47A1 !important; border-width: 1px; border-radius: 8px; background-color: #FFFFFF; }
    </style>
    """, unsafe_allow_html=True)

# BANNER PRINCIPAL
st.markdown("""
    <div style='background-color: #0D47A1; padding: 25px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h1 style='margin: 0; color: white;'>⚖️ Lidera Nómina Pro - Colombia</h1>
        <p style='margin: 5px 0 0 0; font-size: 18px;'>Liquidador de Nómina • Blindado Legalmente • Normativa 2026</p>
    </div>
    """, unsafe_allow_html=True)

# BOTONES INFORMATIVOS (BADGES)
c1, c2, c3, c4 = st.columns(4)
c1.markdown("<div style='background-color: #E3F2FD; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #0D47A1; font-weight: bold; color: #0D47A1;'>✅ SMLMV: $1.512.000</div>", unsafe_allow_html=True)
c2.markdown("<div style='background-color: #E3F2FD; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #0D47A1; font-weight: bold; color: #0D47A1;'>✅ Aux. Transp: $182.000</div>", unsafe_allow_html=True)
c3.markdown("<div style='background-color: #FFF8E1; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #FF8F00; font-weight: bold; color: #FF8F00;'>⚖️ Jornada: Ley 2101</div>", unsafe_allow_html=True)
c4.markdown("<div style='background-color: #FFF8E1; padding: 8px; border-radius: 5px; text-align: center; border: 1px solid #FF8F00; font-weight: bold; color: #FF8F00;'>🌙 Recargo Nocturno</div>", unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# FORMULARIO CON EXPANDERS
with st.expander("👤 1. DATOS DEL EMPLEADOR Y EMPLEADO", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        restaurante = st.text_input("Nombre de la Empresa / Empleador", placeholder="Ej: Restaurante El Fogón S.A.S.")
        empleado = st.text_input("Nombre del Trabajador", placeholder="Ej: Juan Pérez")
    with col2:
        nit = st.text_input("NIT / Cédula Empleador")
        cedula = st.text_input("Cédula Trabajador")

with st.expander("💰 2. SALARIO Y TIEMPO ADICIONAL"):
    salario_base = st.number_input("Salario Mensual Base (SMLMV 2026: $1.512.000)", value=SMLMV_2026)
    col3, col4 = st.columns(2)
    with col3:
        he_diurnas = st.number_input("Horas Extra Diurnas", value=0)
    with col4:
        recargos_noc = st.number_input("Horas con Recargo Nocturno", value=0)

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
    resultados = calcular_nomina(salario_base, he_diurnas, recargos_noc, dias_incapacidad, faltas_injustificadas, prestamos)
    
    st.success("✅ Liquidación calculada con precisión legal.")
    
    # --- DESGLOSE EN PANTALLA ---
    st.markdown("### 📊 Desglose Detallado de la Liquidación")
    
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("<div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; border-left: 5px solid #2E7D32;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #2E7D32; margin-top: 0;'>🟢 DEVENGOS (Ingresos)</h4>", unsafe_allow_html=True)
        st.write(f"**Salario Base (Proporcional a {resultados['dias_trabajados']} días):** ${resultados['salario_base']/30*resultados['dias_trabajados']:,.0f}")
        st.write(f"**Horas Extras y Recargos:** ${resultados['total_extras']:,.0f}")
        st.write(f"**Pago por Incapacidad:** ${resultados['pago_incapacidad']:,.0f}")
        st.write(f"**Auxilio de Transporte:** ${resultados['aux_transporte']:,.0f}")
        st.markdown(f"#### Total Devengado: ${resultados['total_devengado']:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col_der:
        st.markdown("<div style='background-color: #FFEBEE; padding: 15px; border-radius: 8px; border-left: 5px solid #C62828;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #C62828; margin-top: 0;'>🔴 DEDUCCIONES (Descuentos)</h4>", unsafe_allow_html=True)
        st.write(f"**Salud (4%):** ${resultados['salud']:,.0f}")
        st.write(f"**Pensión (4%):** ${resultados['pension']:,.0f}")
        st.write(f"**Castigo por Faltas (Art. 173):** ${resultados['descuento_faltas']:,.0f}")
        st.write(f"**Préstamos/Adelantos:** ${resultados['prestamos']:,.0f}")
        st.markdown(f"#### Total Deducciones: ${resultados['total_deducciones']:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.markdown("---")
    st.markdown(f"<h2 style='text-align: center; color: #0D47A1; background-color: #E3F2FD; padding: 15px; border-radius: 10px;'>💵 NETO A PAGAR: ${resultados['neto']:,.0f}</h2>", unsafe_allow_html=True)
    
    # Generador de PDF
    try:
        pdf_file = generar_pdf(restaurante, empleado, resultados)
        st.download_button("📩 Descargar Comprobante Legal (PDF)", data=pdf_file, file_name=f"Nomina_{empleado}.pdf")
    except Exception as e:
        st.error(f"Error al crear PDF: {e}")
