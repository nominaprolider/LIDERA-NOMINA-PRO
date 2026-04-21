from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(13, 71, 161) # Azul corporativo
        self.cell(0, 10, "COMPROBANTE DE PAGO DE NOMINA", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

# IMPORTANTE: Aquí están los 3 argumentos (empresa, empleado, res) que arreglan el error
def generar_pdf(empresa, empleado, res):
    pdf = PDF()
    pdf.add_page()
    
    # Información Básica
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 8, f"Empleador: {empresa if empresa else 'No especificado'}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Trabajador: {empleado if empleado else 'No especificado'}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    def moneda(valor):
        return f"${valor:,.0f}"
        
    # SECCIÓN: DEVENGOS
    pdf.set_font("helvetica", "B", 12)
    pdf.set_fill_color(227, 242, 253) # Azul claro
    pdf.cell(0, 8, " DEVENGOS (INGRESOS)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    
    pdf.cell(140, 8, f"Salario Base (Dias trabajados: {res['dias_trabajados']})", border=1)
    pdf.cell(50, 8, moneda((res['salario_base']/30) * res['dias_trabajados']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, "Horas Extras y Recargos", border=1)
    pdf.cell(50, 8, moneda(res['total_extras']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, "Pago por Incapacidad", border=1)
    pdf.cell(50, 8, moneda(res['pago_incapacidad']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, "Auxilio de Transporte", border=1)
    pdf.cell(50, 8, moneda(res['aux_transporte']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(140, 8, "TOTAL DEVENGADO", border=1)
    pdf.cell(50, 8, moneda(res['total_devengado']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # SECCIÓN: DEDUCCIONES
    pdf.set_font("helvetica", "B", 12)
    pdf.set_fill_color(255, 235, 238) # Rojo claro
    pdf.cell(0, 8, " DEDUCCIONES (DESCUENTOS)", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("helvetica", "", 11)
    
    pdf.cell(140, 8, "Salud (4%)", border=1)
    pdf.cell(50, 8, moneda(res['salud']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, "Pension (4%)", border=1)
    pdf.cell(50, 8, moneda(res['pension']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, "Castigo por faltas (Art. 173)", border=1)
    pdf.cell(50, 8, moneda(res['descuento_faltas']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.cell(140, 8, "Prestamos / Adelantos", border=1)
    pdf.cell(50, 8, moneda(res['prestamos']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", "B", 11)
    pdf.cell(140, 8, "TOTAL DEDUCCIONES", border=1)
    pdf.cell(50, 8, moneda(res['total_deducciones']), border=1, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # SECCIÓN: NETO
    pdf.set_font("helvetica", "B", 14)
    pdf.set_fill_color(200, 230, 201) # Verde claro
    pdf.cell(140, 10, " NETO A PAGAR", border=1, fill=True)
    pdf.cell(50, 10, moneda(res['neto']), border=1, fill=True, align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(15)
    
    # CLAUSULA LEGAL
    pdf.set_font("helvetica", "I", 9)
    clausula = "Declaro que he recibido a satisfaccion el pago correspondiente a mi salario y demas conceptos laborales del periodo liquidado. Entiendo y acepto los descuentos realizados de acuerdo con la ley laboral colombiana y autorizaciones previas."
    pdf.multi_cell(0, 5, clausula)
    pdf.ln(20)
    
    # FIRMAS
    pdf.cell(80, 5, "___________________________________", new_x="RIGHT", new_y="TOP")
    pdf.cell(10, 5, "")
    pdf.cell(80, 5, "___________________________________", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(80, 5, "Firma del Empleador", align="C", new_x="RIGHT", new_y="TOP")
    pdf.cell(10, 5, "")
    pdf.cell(80, 5, "Firma del Trabajador (C.C.)", align="C", new_x="LMARGIN", new_y="NEXT")
    
    return bytes(pdf.output())
