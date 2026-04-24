"""
logic.py — Lógica de liquidación de nómina quincenal · Colombia 2026
Parámetros inviolables según normativa vigente.
"""

from datetime import datetime, time, date
from typing import List, Dict, Any

# ════════════════════════════════════════════════════════════════════
# CONSTANTES LEGALES 2026
# ════════════════════════════════════════════════════════════════════
SMLMV_2026      = 1_512_000       # Decreto 2910 de 2024
AUX_TRANSPORTE  = 182_000         # Decreto 2911 de 2024
HORAS_SEMANA    = 42              # Ley 2101 de 2021
DIVISOR_HORA    = 210             # Para salario mensual → valor hora
VALOR_HORA_MIN  = round(SMLMV_2026 / DIVISOR_HORA)

# Factores de recargo (CST)
F_NOCTURNO      = 0.35
F_DOMINICAL     = 1.00
F_HE_DIURNA     = 0.25
F_HE_NOCTURNA   = 0.75

HORA_INICIO_NOCHE = 21
HORA_RECARGO_NOC  = 19

PCT_SALUD    = 0.04
PCT_PENSION  = 0.04

HORAS_ORDINARIAS_DIA = HORAS_SEMANA / 6

# Incapacidades (Ley 100 / Dec. 1406 / Ley 776 — ajuste técnico legal)
DIAS_INCAP_EMPLEADOR = 2          # Primeros 2 días: 100% a cargo del empleador
PCT_INCAP_EPS        = 2 / 3      # Día 3 en adelante: 66.67% por la EPS


def _hora_a_float(h: str) -> float:
    partes = h.split(":")
    return int(partes[0]) + int(partes[1]) / 60


def _calcular_turno(turno: Dict, valor_hora: float) -> Dict:
    entrada = _hora_a_float(turno["entrada"])
    salida  = _hora_a_float(turno["salida"])
    tipo    = turno["tipo_dia"]

    horas_totales = salida - entrada
    if horas_totales <= 0:
        horas_totales = 0

    es_dominical = tipo in ("Domingo", "Festivo")

    hrs_ordinarias = 0.0
    hrs_nocturnas  = 0.0
    hrs_dom_fest   = 0.0
    he_diurnas     = 0.0
    he_nocturnas   = 0.0

    max_ord = HORAS_ORDINARIAS_DIA

    hora_actual = entrada
    ordinarias_acum = 0.0
    for _ in range(int(horas_totales * 60)):
        minuto_frac = 1 / 60
        h_actual = hora_actual

        es_noche = h_actual >= HORA_RECARGO_NOC or h_actual < 6
        es_he = ordinarias_acum >= max_ord

        if es_he:
            if h_actual >= HORA_INICIO_NOCHE or h_actual < 6:
                he_nocturnas += minuto_frac
            else:
                he_diurnas += minuto_frac
        else:
            if es_dominical:
                hrs_dom_fest += minuto_frac
            elif es_noche:
                hrs_nocturnas += minuto_frac
            else:
                hrs_ordinarias += minuto_frac
            ordinarias_acum += minuto_frac

        hora_actual += minuto_frac
        if hora_actual >= 24:
            hora_actual -= 24

    valor_ordinario = valor_hora * hrs_ordinarias
    valor_nocturno  = valor_hora * hrs_nocturnas * (1 + F_NOCTURNO)
    valor_dom_fest  = valor_hora * hrs_dom_fest * (1 + F_DOMINICAL + (F_NOCTURNO if _hora_a_float(turno["entrada"]) >= HORA_RECARGO_NOC else 0))
    valor_he_diur   = valor_hora * he_diurnas * (1 + F_HE_DIURNA)
    valor_he_noct   = valor_hora * he_nocturnas * (1 + F_HE_NOCTURNA)

    recargo_nocturno_extra   = valor_hora * hrs_nocturnas * F_NOCTURNO
    recargo_dominical_extra  = valor_hora * hrs_dom_fest * F_DOMINICAL

    valor_turno_total = valor_ordinario + valor_nocturno + valor_dom_fest + valor_he_diur + valor_he_noct

    return {
        "fecha"           : turno["fecha"],
        "tipo"            : tipo,
        "entrada"         : turno["entrada"],
        "salida"          : turno["salida"],
        "hrs_ord"         : round(hrs_ordinarias, 2),
        "hrs_noc"         : round(hrs_nocturnas, 2),
        "hrs_dom"         : round(hrs_dom_fest, 2),
        "he_diur"         : round(he_diurnas, 2),
        "he_noct"         : round(he_nocturnas, 2),
        "valor"           : round(valor_turno_total),
        "rec_nocturno"    : round(recargo_nocturno_extra),
        "rec_dominical"   : round(recargo_dominical_extra),
        "valor_he_diur"   : round(valor_he_diur - valor_hora * he_diurnas),
        "valor_he_noct"   : round(valor_he_noct - valor_hora * he_nocturnas),
    }


def calcular_nomina(params: Dict[str, Any]) -> Dict[str, Any]:
    tipo_salario          = params["tipo_salario"]
    salario_base_in       = params["salario_base"]
    valor_hora_in         = params["valor_hora"]
    dias_laborados        = params["dias_laborados"]
    dias_no_laborados     = int(params.get("dias_no_laborados", 0) or 0)
    incapacidades         = int(params.get("incapacidades", 0) or 0)
    comisiones            = int(params.get("comisiones", 0) or 0)
    bonif_no_salariales   = int(params.get("bonif_no_salariales", 0) or 0)
    prestamos             = int(params.get("prestamos", 0) or 0)
    sanciones             = int(params.get("sanciones", 0) or 0)
    saldo_prestamo        = int(params.get("saldo_prestamo", 0) or 0)
    turnos                = params["turnos"]

    # ── 1. VALOR HORA EFECTIVO ─────────────────────────────────
    if tipo_salario == "Fijo Mensual":
        salario_base_in = max(salario_base_in, SMLMV_2026)
        valor_hora = salario_base_in / DIVISOR_HORA
    else:
        valor_hora = max(valor_hora_in, VALOR_HORA_MIN)
        salario_base_in = 0

    # Detectar si devenga el SMLMV (protección al mínimo)
    devenga_smlmv = (
        tipo_salario == "Fijo Mensual" and salario_base_in <= SMLMV_2026
    ) or (
        tipo_salario == "Por Horas / Turnos" and valor_hora <= VALOR_HORA_MIN
    )

    # ── 2. VALOR DÍA ───────────────────────────────────────────
    if tipo_salario == "Fijo Mensual":
        valor_dia = salario_base_in / 30
    else:
        valor_dia = valor_hora * HORAS_ORDINARIAS_DIA

    # Días efectivamente trabajados (sin faltas ni incapacidades)
    dias_efectivos = max(dias_laborados - dias_no_laborados - incapacidades, 0)

    # ── 3. SALARIO BASE PROPORCIONAL A DÍAS EFECTIVOS ─────────
    # El salario base se calcula ÚNICAMENTE sobre los días efectivamente
    # trabajados (sin faltas ni incapacidades). Los días no trabajados ya
    # quedan excluidos de raíz; no se requieren descuentos posteriores.
    if tipo_salario == "Fijo Mensual":
        salario_base_periodo = round(salario_base_in * dias_efectivos / 30)
    else:
        salario_base_periodo = 0  # se calcula desde turnos

    # ── 4. PROCESAR TURNOS ─────────────────────────────────────
    detalle_turnos = []
    total_hrs_noc, total_hrs_dom = 0.0, 0.0
    total_he_diur, total_he_noct = 0.0, 0.0
    total_rec_noct, total_rec_dom = 0, 0
    total_he_d_val, total_he_n_val = 0, 0
    salario_turnos = 0

    for t in turnos:
        d = _calcular_turno(t, valor_hora)
        detalle_turnos.append([
            d["fecha"], d["tipo"], d["entrada"], d["salida"],
            f"{d['hrs_ord']:.1f}", f"{d['hrs_noc']:.1f}", f"{d['hrs_dom']:.1f}",
            f"{d['he_diur']:.1f}", f"{d['he_noct']:.1f}",
            d["valor"]
        ])
        total_hrs_noc  += d["hrs_noc"]
        total_hrs_dom  += d["hrs_dom"]
        total_he_diur  += d["he_diur"]
        total_he_noct  += d["he_noct"]
        total_rec_noct += d["rec_nocturno"]
        total_rec_dom  += d["rec_dominical"]
        total_he_d_val += d["valor_he_diur"]
        total_he_n_val += d["valor_he_noct"]
        salario_turnos += d["valor"]

    if tipo_salario == "Por Horas / Turnos":
        salario_base_periodo = salario_turnos - total_rec_noct - total_rec_dom - total_he_d_val - total_he_n_val
        salario_base_periodo = round(max(salario_base_periodo, 0))

    # ── 5. AUXILIO DE TRANSPORTE PROPORCIONAL A DÍAS EFECTIVOS ──
    # Se liquida directamente sobre los días efectivamente trabajados.
    # No se muestra ningún descuento posterior en deducciones.
    salario_para_aux = salario_base_in if tipo_salario == "Fijo Mensual" else (
        salario_turnos * 30 / max(len(turnos)*8, 1) if turnos else 0
    )
    aux_aplica = salario_para_aux <= 2 * SMLMV_2026
    if aux_aplica:
        aux_transporte_periodo = round(AUX_TRANSPORTE * dias_efectivos / 30)
    else:
        aux_transporte_periodo = 0

    # ── 6. DESCUENTOS POR FALTA INJUSTIFICADA ─────────────────
    # Solo se descuenta el día de descanso dominical (Art. 173 CST).
    desc_falta_dominical = round(valor_dia * dias_no_laborados)

    # ── 7. INCAPACIDADES (BLINDAJE LEGAL · MÍNIMO VITAL) ──────
    # Los días de incapacidad NO se descuentan en deducciones; el salario
    # base ya los excluye de raíz. Se reconocen exclusivamente como
    # devengo (Auxilio por Incapacidad):
    #   • Días 1-2: 100% del salario, a cargo del EMPLEADOR
    #   • Día 3 en adelante: 66.67% del salario, a cargo de la EPS
    #   • PISO LEGAL: ningún día de incapacidad puede pagarse por debajo
    #     de un día de SMLMV ($50.400 en 2026). Aplica tanto al tramo
    #     empleador como al tramo EPS (protección al mínimo vital).
    PISO_DIA_SMLMV = SMLMV_2026 / 30  # $50.400 para 2026

    dias_incap_empleador = min(incapacidades, DIAS_INCAP_EMPLEADOR)
    dias_incap_eps       = max(incapacidades - DIAS_INCAP_EMPLEADOR, 0)

    pago_dia_empleador = max(valor_dia * 1.0,           PISO_DIA_SMLMV)
    pago_dia_eps       = max(valor_dia * PCT_INCAP_EPS, PISO_DIA_SMLMV)

    auxilio_incap_empleador = round(pago_dia_empleador * dias_incap_empleador)
    auxilio_incap_eps       = round(pago_dia_eps       * dias_incap_eps)
    auxilio_incapacidad     = auxilio_incap_empleador + auxilio_incap_eps

    # ── 8. TOTAL DEVENGADO ─────────────────────────────────────
    total_recargos = total_rec_noct + total_rec_dom + total_he_d_val + total_he_n_val
    total_devengado = (
        salario_base_periodo
        + total_recargos
        + comisiones
        + bonif_no_salariales
        + aux_transporte_periodo
        + auxilio_incapacidad
    )

    # ── 9. IBC SEGURIDAD SOCIAL (Ley 100 / Dec. 1406) ─────────
    # Base = Salario base efectivo + Recargos/HE + Comisiones salariales
    #        + Auxilio por Incapacidad  (las incapacidades SÍ son IBC)
    # El Auxilio de Transporte NUNCA hace parte del IBC.
    base_ss = (
        salario_base_periodo
        + total_recargos
        + comisiones
        + auxilio_incapacidad
    )
    # Piso IBC: no puede ser inferior al SMLMV proporcional a los
    # días remunerados (efectivos + incapacitados).
    dias_remunerados = dias_efectivos + incapacidades
    base_ss = max(base_ss, SMLMV_2026 * dias_remunerados / 30)

    # ── 10. DEDUCCIONES ────────────────────────────────────────
    salud   = round(base_ss * PCT_SALUD)
    pension = round(base_ss * PCT_PENSION)
    total_deducciones = (
        salud + pension
        + desc_falta_dominical
        + prestamos + sanciones
    )

    # ── 11. NETO A PAGAR ───────────────────────────────────────
    neto_a_pagar = round(total_devengado - total_deducciones)

    # Saldo de préstamo
    saldo_prestamo_pendiente = max(saldo_prestamo - prestamos, 0)

    # ── 12. PRESTACIONES SOCIALES (COSTO MENSUAL EMPLEADOR) ───
    # Calculadas sobre el salario base efectivo + recargos + comisiones
    # del período, proyectadas a 30 días para mostrar el costo mensual.
    sal_var_periodo = salario_base_periodo + total_recargos + comisiones
    if dias_efectivos > 0:
        sal_var_mes = sal_var_periodo * 30 / dias_efectivos
    else:
        sal_var_mes = 0
    aux_mes_full = AUX_TRANSPORTE if aux_aplica else 0
    base_prest = sal_var_mes + aux_mes_full       # cesantías y prima
    base_vac   = sal_var_mes                       # vacaciones (sin aux)

    cesantias        = round(base_prest / 12)              # 8.33%
    int_cesantias    = round(cesantias * 0.12)             # 12% anual sobre cesantías
    prima_servicios  = round(base_prest / 12)              # 8.33%
    vacaciones       = round(base_vac * 0.0417)            # 4.17% (15 días/año)
    total_prestaciones = cesantias + int_cesantias + prima_servicios + vacaciones

    # Aportes parafiscales y SS a cargo del empleador
    salud_emp     = round(sal_var_mes * 0.085)             # 8.5%
    pension_emp   = round(sal_var_mes * 0.12)              # 12%
    arl           = round(sal_var_mes * 0.00522)           # ARL Clase I (referencia)
    aportes_emp_total = salud_emp + pension_emp + arl
    costo_total_mes   = round(sal_var_mes + aux_mes_full + total_prestaciones + aportes_emp_total)

    return {
        # Identificación
        "empresa"       : params["empresa"],
        "nit"           : params.get("nit", ""),
        "empleado"      : params["empleado"],
        "cedula"        : params["cedula"],
        "periodo_inicio": params["periodo_inicio"],
        "periodo_fin"   : params["periodo_fin"],
        "tipo_salario"  : tipo_salario,
        "dias_laborados": dias_laborados,
        "dias_no_laborados": dias_no_laborados,
        "incapacidades" : incapacidades,
        "dias_efectivos": dias_efectivos,
        "devenga_smlmv" : devenga_smlmv,
        "dias_incap_empleador": dias_incap_empleador,
        "dias_incap_eps": dias_incap_eps,

        # Devengado
        "salario_base_calc": salario_base_periodo,
        "valor_hora"       : round(valor_hora),
        "valor_dia"        : round(valor_dia),
        "recargo_nocturno" : total_rec_noct,
        "recargo_dominical": total_rec_dom,
        "he_diurnas_valor" : total_he_d_val,
        "he_diurnas_horas" : total_he_diur,
        "he_nocturnas_valor": total_he_n_val,
        "he_nocturnas_horas": total_he_noct,
        "horas_nocturnas"  : total_hrs_noc,
        "horas_dominical"  : total_hrs_dom,
        "comisiones"       : comisiones,
        "bonif_no_salariales": bonif_no_salariales,
        "aux_transporte"   : aux_transporte_periodo,
        "auxilio_incapacidad": auxilio_incapacidad,
        "auxilio_incap_empleador": auxilio_incap_empleador,
        "auxilio_incap_eps": auxilio_incap_eps,
        "total_devengado"  : round(total_devengado),

        # Deducciones (separadas para transparencia)
        "base_ss"             : round(base_ss),
        "salud"               : salud,
        "pension"             : pension,
        "desc_falta_dominical": desc_falta_dominical,
        "prestamos"           : prestamos,
        "sanciones"           : sanciones,
        "total_deducciones"   : total_deducciones,

        # Neto + Saldo
        "neto_a_pagar"            : neto_a_pagar,
        "saldo_prestamo_pendiente": saldo_prestamo_pendiente,

        # Prestaciones sociales (proyección mensual a cargo empleador)
        "salario_proy_mes"  : round(sal_var_mes),
        "cesantias"         : cesantias,
        "intereses_cesantias": int_cesantias,
        "prima_servicios"   : prima_servicios,
        "vacaciones"        : vacaciones,
        "total_prestaciones": total_prestaciones,
        "salud_empleador"   : salud_emp,
        "pension_empleador" : pension_emp,
        "arl"               : arl,
        "aportes_empleador" : aportes_emp_total,
        "costo_total_mes"   : costo_total_mes,

        # Detalle
        "detalle_turnos"   : detalle_turnos,
    }
