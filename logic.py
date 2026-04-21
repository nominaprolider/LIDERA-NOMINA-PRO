# logic.py

# --- CONSTANTES LEGALES 2026 ---
SMLMV_2026 = 1512000
AUX_TRANSPORTE = 182000
HORAS_MES = 240
VALOR_HORA_MINIMA = SMLMV_2026 / HORAS_MES

def calcular_nomina(salario_base, he_diurnas, recargos_noc, dias_incapacidad, faltas_injustificadas, prestamos):
    # 1. Valores base
    valor_dia = salario_base / 30
    valor_hora = salario_base / HORAS_MES
    
    # 2. Cálculos de Tiempo Extra
    pago_he_diurnas = he_diurnas * valor_hora * 1.25
    pago_recargos_noc = recargos_noc * valor_hora * 0.35
    total_extras = pago_he_diurnas + pago_recargos_noc
    
    # 3. Módulo de Incapacidades (Blindaje 2026 - Mínimo Vital)
    pago_incapacidad = 0
    if dias_incapacidad > 0:
        # La ley ordena el 66.67% (Art. 227 CST), pero NUNCA por debajo del mínimo diario.
        # Esto aplica igual para los días a cargo del empleador (1-2) y de la EPS (3+).
        valor_dia_incapacidad = valor_dia * 0.6667
        valor_dia_minimo_legal = SMLMV_2026 / 30
        
        if valor_dia_incapacidad < valor_dia_minimo_legal:
            valor_dia_incapacidad = valor_dia_minimo_legal
            
        pago_incapacidad = dias_incapacidad * valor_dia_incapacidad
            
    # 4. Descuentos por faltas (Pérdida de Dominical - Art. 173 CST)
    descuento_faltas = 0
    if faltas_injustificadas > 0:
        # Faltar 1 día injustificadamente = Pierde el pago de ese día + el pago del Domingo
        descuento_faltas = faltas_injustificadas * 2 * valor_dia
        
    # 5. Auxilio de Transporte (Solo se paga sobre los días efectivamente trabajados)
    dias_trabajados = 30 - dias_incapacidad - faltas_injustificadas
    aux_transporte_pagar = 0
    if salario_base <= (SMLMV_2026 * 2):
        aux_transporte_pagar = (AUX_TRANSPORTE / 30) * dias_trabajados
        
    # 6. Seguridad Social (Salud y Pensión a cargo del trabajador)
    ibc = (salario_base / 30 * dias_trabajados) + total_extras + pago_incapacidad
    salud = ibc * 0.04
    pension = ibc * 0.04
    
    # 7. Liquidación Final
    total_devengado = (salario_base / 30 * dias_trabajados) + total_extras + pago_incapacidad + aux_transporte_pagar
    total_deducciones = salud + pension + descuento_faltas + prestamos
    
    neto = total_devengado - total_deducciones
    
    # Retornamos el diccionario completo para que el App y el PDF lo lean
    return {
        "salario_base": salario_base,
        "dias_trabajados": dias_trabajados,
        "total_extras": total_extras,
        "pago_incapacidad": pago_incapacidad,
        "aux_transporte": aux_transporte_pagar,
        "salud": salud,
        "pension": pension,
        "descuento_faltas": descuento_faltas,
        "prestamos": prestamos,
        "total_devengado": total_devengado,
        "total_deducciones": total_deducciones,
        "neto": neto
    }
