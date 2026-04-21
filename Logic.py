"""
logic.py — Lógica de liquidación de nómina · Colombia 2026
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
VALOR_HORA_MIN  = round(SMLMV_2026 / DIVISOR_HORA)  # ~7.200

# Factores de recargo (CST)
F_NOCTURNO      = 0.35            # Art. 168 CST - desde las 19:00
F_DOMINICAL     = 1.00            # Art. 179 CST - 100% adicional
F_HE_DIURNA     = 0.25            # Art. 168 CST - HE diurnas
F_HE_NOCTURNA   = 0.75            # Art. 168 CST - HE nocturnas

HORA_INICIO_NOCHE = 21            # 21:00 según CST (para HE nocturnas)
HORA_RECARGO_NOC  = 19            # 19:00 inicio recargo nocturno ordinario

# SS deducciones empleado
PCT_SALUD    = 0.04
PCT_PENSION  = 0.04

# Horas ordinarias diarias equivalente (42h / 6 días = 7h)
HORAS_ORDINARIAS_DIA = HORAS_SEMANA / 6  # 7h


def _hora_a_float(h: str) -> float:
    """Convierte 'HH:MM' a horas decimales."""
    partes = h.split(":")
    return int(partes[0]) + int(partes[1]) / 60


def _calcular_turno(turno: Dict, valor_hora: float) -> Dict:
    """
    Desglosa un turno en horas ordinarias, nocturnas, dominicales y extras.
    Retorna un dict con todos los valores calculados.
    """
    entrada = _hora_a_float(turno["entrada"])
    salida  = _hora_a_float(turno["salida"])
    tipo    = turno["tipo_dia"]  # 'Ordinario (L-S)', 'Domingo', 'Festivo'

    horas_totales = salida - entrada
    if horas_totales <= 0:
        horas_totales = 0

    es_dominical = tipo in ("Domingo", "Festivo")

    # Distribución de horas
    hrs_ordinarias = 0.0
    hrs_nocturnas  = 0.0   # entre 19:00 y 21:00 + desde 21:00
    hrs_dom_fest   = 0.0
    he_diurnas     = 0.0
    he_nocturnas   = 0.0

    # Máximo de horas ordinarias diarias
    max_ord = HORAS_ORDINARIAS_DIA  # 7h

    hora_actual = entrada
    horas_restantes = horas_totales

    # Clasificar cada hora del turno
    ordinarias_acum = 0.0
    for _ in range(int(horas_totales * 60)):  # iterar por minutos
        minuto_frac = 1 / 60
        h_actual = hora_actual

        es_noche = h_actual >= HORA_RECARGO_NOC or h_actual < 6  # 19:00–06:00
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

    # Calcular valores monetarios
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
        "valor_he_diur"   : round(valor_he_diur - valor_hora * he_diurnas),  # solo el recargo
        "valor_he_noct"   : round(valor_he_noct - valor_hora * he_nocturnas),
    }


def calcular_nomina(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Función principal de liquidación.
    Recibe todos los parámetros del formulario y retorna el resultado completo.
    """
    tipo_salario    = params["tipo_salario"]
    salario_base_in = params["salario_base"]
    valor_hora_in   = params["valor_hora"]
    dias_laborados  = params["dias_laborados"]
    comisiones      = params["comisiones"]
    turnos          = params["turnos"]

    # ── 1. VALOR HORA EFECTIVO ─────────────────────────────────
    if tipo_salario == "Fijo Mensual":
        salario_base_in = max(salario_base_in, SMLMV_2026)
        valor_hora = salario_base_in / DIVISOR_HORA
    else:
        valor_hora = max(valor_hora_in, VALOR_HORA_MIN)
        salario_base_in = 0

    # ── 2. SALARIO BASE PROPORCIONAL ───────────────────────────
    if tipo_salario == "Fijo Mensual":
        salario_base_calc = round(salario_base_in * dias_laborados / 30)
    else:
        salario_base_calc = 0

    # ── 3. PROCESAR TURNOS ─────────────────────────────────────
    detalle_turnos = []
    total_hrs_ord     = 0.0
    total_hrs_noc     = 0.0
    total_hrs_dom     = 0.0
    total_he_diur     = 0.0
    total_he_noct     = 0.0
    total_rec_noct    = 0
    total_rec_dom     = 0
    total_he_d_val    = 0
    total_he_n_val    = 0
    salario_turnos    = 0

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

    # Si es salario fijo, los recargos se calculan sobre el salario base
    if tipo_salario == "Fijo Mensual" and turnos:
        pass  # ya se calculan en _calcular_turno con el valor_hora del salario fijo

    # Para salario fijo sin turnos con recargos explícitos, recargos = 0
    if tipo_salario == "Fijo Mensual" and not turnos:
        total_rec_noct = 0
        total_rec_dom  = 0
        total_he_d_val = 0
        total_he_n_val = 0

    # ── 4. SALARIO BASE TOTAL ──────────────────────────────────
    if tipo_salario == "Por Horas / Turnos":
        salario_base_calc = salario_turnos - total_rec_noct - total_rec_dom - total_he_d_val - total_he_n_val
        salario_base_calc = round(max(salario_base_calc, 0))

    # ── 5. AUXILIO DE TRANSPORTE ───────────────────────────────
    # Solo para salarios ≤ 2 SMLMV; proporcional a días laborados
    salario_para_aux = salario_base_in if tipo_salario == "Fijo Mensual" else (salario_turnos * 30 / max(len(turnos)*8, 1) if turnos else 0)
    if salario_para_aux <= 2 * SMLMV_2026:
        aux_transporte = round(AUX_TRANSPORTE * dias_laborados / 30)
    else:
        aux_transporte = 0

    # ── 6. TOTAL DEVENGADO ─────────────────────────────────────
    total_devengado = (
        salario_base_calc
        + total_rec_noct
        + total_rec_dom
        + total_he_d_val
        + total_he_n_val
        + comisiones
        + aux_transporte
    )

    # ── 7. BASE SEGURIDAD SOCIAL (sin aux transporte) ──────────
    base_ss = total_devengado - aux_transporte
    base_ss = max(base_ss, SMLMV_2026 * dias_laborados / 30)  # mínimo proporcional

    # ── 8. DEDUCCIONES ─────────────────────────────────────────
    salud   = round(base_ss * PCT_SALUD)
    pension = round(base_ss * PCT_PENSION)
    total_deducciones = salud + pension

    # ── 9. NETO A PAGAR ────────────────────────────────────────
    neto_a_pagar = round(total_devengado - total_deducciones)

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

        # Devengado
        "salario_base_calc": salario_base_calc,
        "valor_hora"       : round(valor_hora),
        "recargo_nocturno" : total_rec_noct,
        "recargo_dominical": total_rec_dom,
        "he_diurnas_valor" : total_he_d_val,
        "he_diurnas_horas" : total_he_diur,
        "he_nocturnas_valor": total_he_n_val,
        "he_nocturnas_horas": total_he_noct,
        "horas_nocturnas"  : total_hrs_noc,
        "horas_dominical"  : total_hrs_dom,
        "comisiones"       : comisiones,
        "aux_transporte"   : aux_transporte,
        "total_devengado"  : round(total_devengado),

        # SS
        "base_ss"         : round(base_ss),
        "salud"           : salud,
        "pension"         : pension,
        "total_deducciones": total_deducciones,

        # Neto
        "neto_a_pagar"    : neto_a_pagar,

        # Detalle
        "detalle_turnos"  : detalle_turnos,
    }
