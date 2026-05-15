import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuración y Diseño Visual
st.set_page_config(page_title="Nómina Blindada Lidera", layout="wide", page_icon="🌿")

st.markdown("""
<style>
.main-header { background-color: #2E8B57; padding: 25px; border-radius: 12px; color: white; text-align: center; margin-bottom: 20px; }
.main-header h1 { color: white; font-family: 'Segoe UI', sans-serif; margin-bottom: 5px; }
.main-header p { font-size: 1.1rem; color: #E8F5E9; }
.badge-container { display: flex; gap: 15px; flex-wrap: wrap; margin-bottom: 30px; justify-content: center; }
.badge { border: 1px solid #4CAF50; background-color: #F1F8E9; border-radius: 20px; padding: 8px 18px; color: #2E7D32; font-weight: 600; font-size: 0.9rem; }
.recibo-box { border: 2px solid #2E8B57; padding: 30px; border-radius: 10px; background-color: white; margin-top: 20px; color: black; }
.firma-line { border-top: 1px solid black; margin-top: 60px; padding-top: 10px; text-align: center; }
</style>

<div class="main-header">
    <h1>🌿 Asistente de Nómina Blindada</h1>
    <p>Liquidación integral conforme al Código Sustantivo del Trabajo · Colombia 2026</p>
</div>
<div class="badge-container">
    <span class="badge">✓ SMLMV 2026: $1.750.905</span>
    <span class="badge">✓ Aux. Transporte: $249.095</span>
    <span class="badge">⚖️ Jornada 42h (Divisor 210)</span>
</div>
""", unsafe_allow_html=True)

# 2. Constantes Legales 2026
SMLMV_2026 = 1750905
AUXILIO_2026 = 249095
DIVISOR_HORAS = 210
VALOR_HORA_ORDINARIA = SMLMV_2026 / DIVISOR_HORAS

st.markdown("### 📋 1. Datos del Período")
col1, col2 = st.columns(2)
with col1:
    empresa = st.text_input("Nombre de la Empresa / Empleador")
    nit = st.text_input("NIT o Cédula del Empleador")
with col2:
    empleado = st.text_input("Nombre completo del trabajador")
    cedula = st.text_input("Cédula del trabajador")
    
col3, col4 = st.columns(2)
with col3:
    dias_periodo = st.number_input("Días del período a liquidar (Ej: 15 para quincena)", min_value=1, max_value=30, value=15)
with col4:
    tiene_auxilio = st.checkbox("¿Tiene derecho a Auxilio de Transporte? (Gana menos de 2 SMLMV)", value=True)

# 3. Novedades (Ingresos Adicionales)
with st.expander("➕ Novedades: Trabajo Extra y Recargos (Desplegar si aplica)"):
    st.info("Ingresa la cantidad de horas extras o recargos laborados en el período.")
    col_he1, col_he2, col_he3 = st.columns(3)
    with col_he1:
        he_diurnas = st.number_input("Horas Extras Diurnas (25%)", min_value=0.0, value=0.0, step=1.0)
        he_nocturnas = st.number_input("Horas Extras Nocturnas (75%)", min_value=0.0, value=0.0, step=1.0)
    with col_he2:
        recargo_nocturno = st.number_input("Recargos Nocturnos (35%)", min_value=0.0, value=0.0, step=1.0)
        dom_fest_ordinario = st.number_input("Dominical/Festivo Ordinario (75%)", min_value=0.0, value=0.0, step=1.0)
    with col_he3:
        he_dom_diurna = st.number_input("H. Extra Dom/Fest Diurna (100%)", min_value=0.0, value=0.0, step=1.0)
        he_dom_nocturna = st.number_input("H. Extra Dom/Fest Nocturna (150%)", min_value=0.0, value=0.0, step=1.0)

# 4. Descuentos y Ausentismos (CON TOOLTIPS LEGALES)
with st.expander("➖ Deducciones y Ausentismos (Desplegar si aplica)"):
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        # Tooltip para faltas
        faltas_injustificadas = st.number_input(
            "Días de falta injustificada", 
            min_value=0, max_value=30, value=0,
            help="Art. 173 CST: La ausencia injustificada genera el descuento del día no laborado, la pérdida del descanso dominical remunerado y el no pago del auxilio de transporte por esos días."
        )
        # Tooltip para incapacidad
        dias_incapacidad = st.number_input(
            "Días de incapacidad médica", 
            min_value=0, max_value=30, value=0,
            help="Durante la incapacidad (EPS o ARL) no hay desplazamiento al lugar de trabajo, por lo tanto, la ley exime al empleador de pagar el Auxilio de Transporte por estos días."
        )
    with col_d2:
        # Tooltip para préstamos
        prestamos = st.number_input(
            "Descuento por préstamos (COP)", 
            min_value=0, value=0, step=10000,
            help="Art. 59 CST: Todo descuento por préstamos o anticipos debe estar expresa y previamente autorizado por escrito por el trabajador. Nunca se puede afectar el salario mínimo vital inembargable."
        )
        # Tooltip para otras deducciones
        otras_deducciones = st.number_input(
            "Otras deducciones (Embargos/Sindicato)", 
            min_value=0, value=0, step=10000,
            help="Art. 150 CST: Aplica para embargos judiciales (hasta 1/5 parte del excedente del SMLMV, o hasta 50% por cuotas alimentarias), cuotas sindicales o fondos de empleados."
        )

# 5. LÓGICA MATEMÁTICA Y BLINDAJE LEGAL
dias_salario = dias_periodo - faltas_injustificadas - dias_incapacidad
dias_salario = max(0, dias_salario - faltas_injustificadas) # Descuento dominical

dias_transporte = dias_periodo - faltas_injustificadas - dias_incapacidad

salario_proporcional = (SMLMV_2026 / 30) * dias_salario
auxilio_proporcional = (AUXILIO_2026 / 30) * dias_transporte if tiene_auxilio else 0

total_extras = (
    (he_diurnas * VALOR_HORA_ORDINARIA * 1.25) +
    (he_nocturnas * VALOR_HORA_ORDINARIA * 1.75) +
    (recargo_nocturno * VALOR_HORA_ORDINARIA * 0.35) +
    (dom_fest_ordinario * VALOR_HORA_ORDINARIA * 1.75) +
    (he_dom_diurna * VALOR_HORA_ORDINARIA * 2.00) +
    (he_dom_nocturna * VALOR_HORA_ORDINARIA * 2.50)
)

total_devengado = salario_proporcional + total_extras + auxilio_proporcional
base_seguridad_social = salario_proporcional + total_extras

salud = base_seguridad_social * 0.04
pension = base_seguridad_social * 0.04
total_deducciones = salud + pension + prestamos + otras_deducciones

neto_pagar = total_devengado - total_deducciones

# 6. Visualización Rápida
st.markdown("---")
st.markdown("### 📊 Liquidación Rápida")
df_resultados = pd.DataFrame({
    "Concepto": ["Salario Base", "Horas Extras", "Aux. Transporte", "Salud (4%)", "Pensión (4%)", "Préstamos/Otros", "TOTAL NETO"],
    "Valor (COP)": [f"+ ${salario_proporcional:,.0f}", f"+ ${total_extras:,.0f}", f"+ ${auxilio_proporcional:,.0f}", f"- ${salud:,.0f}", f"- ${pension:,.0f}", f"- ${(prestamos+otras_deducciones):,.0f}", f"${neto_pagar:,.0f}"]
})
st.table(df_resultados)

# 7. GENERACIÓN DE COMPROBANTE LEGAL (Recibo a Paz y Salvo)
st.markdown("---")
if st.button("📄 Generar Comprobante de Pago para Firma", type="primary"):
    if not empresa or not empleado or not cedula or not nit:
        st.error("⚠️ Para generar el comprobante legal, debes llenar el Nombre/NIT de la Empresa y el Nombre/Cédula del Trabajador en la sección 1.")
    else:
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        st.markdown(f"""
        <div class="recibo-box">
            <h2 style="text-align: center; color: #2E8B57;">COMPROBANTE DE PAGO DE NÓMINA</h2>
            <p style="text-align: right;"><strong>Fecha de expedición:</strong> {fecha_actual}</p>
            <hr>
            <p><strong>EMPLEADOR:</strong> {empresa} (NIT: {nit})</p>
            <p><strong>TRABAJADOR:</strong> {empleado} (C.C: {cedula})</p>
            <p><strong>PERÍODO LIQUIDADO:</strong> {dias_periodo} días.</p>
            <hr>
            <h4>RESUMEN FINANCIERO:</h4>
            <ul>
                <li><strong>Total Devengado (Ingresos):</strong> ${total_devengado:,.0f}</li>
                <li><strong>Total Deducido (Descuentos):</strong> ${total_deducciones:,.0f}</li>
                <li style="font-size: 1.2rem; color: #2E8B57;"><strong>TOTAL NETO PAGADO: ${neto_pagar:,.0f}</strong></li>
            </ul>
            <hr>
            <p style="font-size: 0.85rem; text-align: justify; color: #555;">
                <strong>DECLARACIÓN DE RECIBIDO A CONFORMIDAD Y PAZ Y SALVO:</strong><br>
                El trabajador abajo firmante declara haber recibido a su entera satisfacción, por parte del empleador, el valor líquido estipulado en este comprobante, el cual corresponde al pago completo y oportuno de su salario, trabajo suplementario, auxilio de transporte y demás conceptos derivados de su relación laboral durante el período especificado. Asimismo, autoriza los descuentos legales y convenidos aquí reflejados. Con la firma de este documento, ambas partes declaran encontrarse a paz y salvo por los conceptos salariales aquí liquidados.
            </p>
            <br>
            <div style="display: flex; justify-content: space-around; margin-top: 30px;">
                <div style="width: 40%;">
                    <div class="firma-line"><strong>FIRMA DEL EMPLEADOR</strong></div>
                </div>
                <div style="width: 40%;">
                    <div class="firma-line"><strong>FIRMA DEL TRABAJADOR</strong><br>C.C: {cedula}</div>
                </div>
            </div>
        </div>
        <p style="text-align: center; color: gray; margin-top: 10px;"><i>Para imprimir este comprobante, presiona Ctrl+P (o Cmd+P en Mac)</i></p>
        """, unsafe_allow_html=True)