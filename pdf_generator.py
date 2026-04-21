from fpdf import FPDF
from datetime import datetime

class PDF(FPDF):
    def header(self):
        # Membrete Profesional Corporativo
        self.set_fill_color(13, 71, 161) # Azul oscuro corporativo
        self.rect(0, 0, 210, 30, 'F')
        
        self.set_y(10)
        self.set_font("helvetica", "B", 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 10, "LIDERA NÓMINA PRO", align="L", new_x="RIGHT", new_y="TOP")
        
        self.set_font("helvetica", "I", 10)
        self.cell(0, 10, "Soporte Legal de Pago", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(15)

def generar_pdf(empresa, nit, empleado, cedula, fecha_inicio, fecha_fin, res):
    pdf = PDF()
    pdf.add_page()
    
    # 1. Bloque de Información del Período y Partes
    pdf.set_font("helvetica", "B", 10)
    pdf.set_text_color(0, 0, 0)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 8, " DATOS DE LA LIQUIDACIÓN", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "", 10)
    pdf.cell(95, 8, f" Empleador: {empresa if empresa else 'No especificado'}", border=1)
    pdf.cell(95, 8, f" NIT/CC: {nit if nit else 'No especificado'}", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(95, 8, f" Trabajador: {empleado if empleado else 'No especificado'}", border=1)
    pdf.cell(95, 8, f" Cédula: {cedula if cedula else 'No especificado'}", border=1, new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(190, 8, f" Período Liquidado: Del {fecha_inicio} al {fecha_fin}", border=1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    
    def moneda(valor):
        return f"${valor:,.0f}"
        
    # 2. SECCIÓN: DEVENGOS
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(227, 242, 253) # Azul claro
    pdf.cell(0, 8, " DEVENGOS (INGRESOS DEL TRABAJADOR)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    
    pdf.cell(140, 8, f" Salario Base Ordinario (Días trabajados: {res['dias_trabajados']})", border=1)
    salario_proporcional = (res['salario_base']/30) * res['dias_trabajados']
    pdf.cell(50, 8, moneda(salario_proporcional), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, " Total Horas Extras y Recargos (Inc. Dominicales)", border=1)
    pdf.cell(50, 8, moneda(res['total_extras']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, " Auxilio por Incapacidad Médica", border=1)
    pdf.cell(50, 8, moneda(res['pago_incapacidad']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, " Auxilio Legal de Transporte", border=1)
    pdf.cell(50, 8, moneda(res['aux_transporte']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(140, 8, " TOTAL DEVENGADO", border=1)
    pdf.cell(50, 8, moneda(res['total_devengado']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 3. SECCIÓN: DEDUCCIONES
    pdf.set_font("helvetica", "B", 11)
    pdf.set_fill_color(255, 235, 238) # Rojo claro
    pdf.cell(0, 8, " DEDUCCIONES Y RETENCIONES", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 10)
    
    pdf.cell(140, 8, " Aporte a Salud (4%)", border=1)
    pdf.cell(50, 8, moneda(res['salud']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, " Aporte a Pensión (4%)", border=1)
    pdf.cell(50, 8, moneda(res['pension']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    # Lenguaje corregido
    pdf.cell(140, 8, " Deducción inasistencia / Pérdida Dominical (Art. 173 CST)", border=1)
    pdf.cell(50, 8, moneda(res['descuento_faltas']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, " Abonos, préstamos o vales autorizados", border=1)
    pdf.cell(50, 8, moneda(res['prestamos']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(140, 8, " TOTAL DEDUCCIONES", border=1)
    pdf.cell(50, 8, moneda(res['total_deducciones']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # 4. SECCIÓN: NETO
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(200, 230, 201) # Verde claro
    pdf.cell(140, 10, " NETO PAGADO AL TRABAJADOR", border=1, fill=True)
    pdf.cell(50, 10, moneda(res['neto']), border=1, fill=True, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    
    # 5. CLAUSULA LEGAL
    pdf.set_font("helvetica", "I", 8)
    clausula = "De conformidad con la legislación laboral colombiana, el trabajador declara haber recibido a entera satisfacción el pago correspondiente a su salario y demás conceptos laborales del período liquidado. Así mismo, autoriza y acepta de manera expresa los descuentos realizados por concepto de aportes al sistema de seguridad social, inasistencias (Art. 173 CST) y obligaciones crediticias previamente autorizadas."
    pdf.multi_cell(0, 5, clausula)
    pdf.ln(20)
    
    # 6. FIRMAS
    pdf.cell(80, 5, "___________________________________", new_x="RIGHT", new_y="TOP")
    pdf.cell(30, 5, "")
    pdf.cell(80, 5, "___________________________________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(80, 5, f"Firma del Empleador (NIT: {nit})", align="C", new_x="RIGHT", new_y="TOP")
    pdf.cell(30, 5, "")
    pdf.cell(80, 5, f"Firma del Trabajador (C.C. {cedula})", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # Fecha de expedición del documento
    pdf.ln(10)
    pdf.set_font("helvetica", "I", 7)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 5, f"Documento generado por Lidera Nómina Pro el {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C")
    
    return bytes(pdf.output())
