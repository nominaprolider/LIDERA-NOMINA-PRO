import streamlit as st
from decimal import Decimal, ROUND_HALF_UP
from datetime import datetime

# --- CONFIGURACIÓN DE PÁGINA Y ESTILO ---
st.set_page_config(page_title="Lidera Nómina Pro - Comprobante", layout="centered")

st.markdown("""
    <style>
    .receipt-container {
        border: 1px solid #d1d1d1;
        padding: 30px;
        border-radius: 10px;
        background-color: #ffffff;
        color: #333333;
        font-family: Arial, sans-serif;
    }
    .header { border-bottom: 2px solid #4CAF50; padding-bottom: 10px; margin-bottom: 20px; }
    .badge { background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px; float: right; }
    .footer { margin-top: 30px; font-size: 0.8em; color: #777; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }
    .total-box { background-color: #f8f9fa; padding: 15px; border-top: 2px solid #333; font-weight: bold; font-size: 1.2em; }
    </style>
    """, unsafe_allow_html=True)

# --- CONSTANTES 2026 ---
SALARIO_MINIMO_2026 = Decimal('1750905')
AUX_TRANSPORTE_2026 = Decimal('249095')

# --- LÓGICA DE NEGOCIO ---
def calcular_nomina(tipo_empleado, base, dias, extras, deducciones_otras):
    # Cálculos base
    salario_diario = (SALARIO_MINIMO_2026 / 30)
    aux_transporte_diario = (AUX_TRANSPORTE_2026 / 30)
    dominical_diario = (salario_diario / 6)
    
    if tipo_empleado == "Tiempo Completo":
        # Base 30 días
        devengado_base = Decimal(base)
        aux_transporte = AUX_TRANSPORTE_2026
    else:
        # Por días: (valor_dia * dias) + proporcional dominical + aux transporte proporcional
        valor_dia = Decimal(base)
        devengado_base = valor_dia * Decimal(dias)
        # Dominical proporcional (1 día por cada 6 trabajados)
        dominical = (valor_dia / 6) * Decimal(dias)
        aux_transporte = aux_transporte_diario * Decimal(dias)
        devengado_base += dominical

    total_devengado = devengado_base + aux_transporte + Decimal(extras)
    
    # Deducciones (4% salud + 4% pensión)
    salud = (total_devengado * Decimal('0.04')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    pension = (total_devengado * Decimal('0.04')).quantize(Decimal('1'), rounding=ROUND_HALF_UP)
    total_deducciones = salud + pension + Decimal(deducciones_otras)
    
    neto_pagar = total_devengado - total_deducciones
    
    return {
        "devengado": total_devengado,
        "aux_transporte": aux_transporte,
        "salud": salud,
        "pension": pension,
        "otras": deducciones_otras,
        "total_deducciones": total_deducciones,
        "neto": neto_pagar
    }

# --- SIDEBAR: ENTRADA DE DATOS ---
with st.sidebar:
    st.header("Datos de Nómina")
    nombre = st.text_input("Nombre Empleado", "Ej. Juan Pérez")
    cedula = st.text_input("Cédula/ID", "123456789")
    tipo_empleado = st.radio("Modalidad", ["Tiempo Completo", "Por Días / Doméstico"])
    
    if tipo_empleado == "Tiempo Completo":
        base = st.number_input("Salario Base Mensual", min_value=1750905, value=1750905)
        dias = 30
    else:
        base = st.number_input("Valor día pactado", min_value=0, value=76394)
        dias = st.number_input("Días trabajados", min_value=1, max_value=30, value=8)
    
    extras = st.number_input("Horas Extras / Recargos", value=0)
    deducciones_extra = st.number_input("Otras deducciones", value=0)
    
    procesar = st.button("Generar Comprobante")

# --- RENDERIZADO DEL COMPROBANTE ---
if procesar:
    res = calcular_nomina(tipo_empleado, base, dias, extras, deducciones_extra)
    
    st.markdown('<div class="receipt-container">', unsafe_allow_html=True)
    
    # Header
    st.markdown(f'''
    <div class="header">
        <span class="badge">Nómina Procesada</span>
        <h2>Lidera Nómina Pro</h2>
        <p>Fecha: {datetime.now().strftime("%d/%m/%Y")}</p>
    </div>
    ''', unsafe_allow_html=True)
    
    # Info Empleado
    st.write(f"**Empleado:** {nombre} | **Cédula:** {cedula}")
    
    # Columnas Financieras
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("DEVENGOS")
        st.write(f"Salario/Días: ${res['devengado'] - res['aux_transporte'] - Decimal(extras):,.0f}")
        st.write(f"Aux. Transporte: ${res['aux_transporte']:,.0f}")
        st.write(f"Extras/Recargos: ${extras:,.0f}")
        st.write(f"**Total Devengado:** ${res['devengado']:,.0f}")
        
    with col2:
        st.subheader("DEDUCCIONES")
        st.write(f"Salud (4%): ${res['salud']:,.0f}")
        st.write(f"Pensión (4%): ${res['pension']:,.0f}")
        st.write(f"Otras: ${res['otras']:,.0f}")
        st.write(f"**Total Deducciones:** ${res['total_deducciones']:,.0f}")

    # Total Final
    st.markdown(f'''
    <div class="total-box">
        NETO A PAGAR: ${res['neto']:,.0f}
    </div>
    ''', unsafe_allow_html=True)
    
    # Footer
    st.markdown('<div class="footer">Este documento es un soporte de pago calculado conforme a la legislación laboral 2026.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.success("¡Comprobante generado con éxito!")
else:
    st.info("Ingresa los datos en el menú lateral para generar el comprobante.")