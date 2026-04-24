import sqlite3
import json
import os
from datetime import datetime, date
from pathlib import Path

DB_PATH = Path(__file__).parent / "nomina_historial.db"


def _conn():
    c = sqlite3.connect(str(DB_PATH))
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS empleados (
            cedula         TEXT PRIMARY KEY,
            nombre         TEXT NOT NULL,
            empresa        TEXT,
            nit            TEXT,
            tipo_salario   TEXT,
            salario_base   INTEGER DEFAULT 0,
            valor_hora     INTEGER DEFAULT 0,
            actualizado    TEXT
        );
        CREATE TABLE IF NOT EXISTS nominas (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            cedula             TEXT NOT NULL,
            empleado           TEXT NOT NULL,
            empresa            TEXT,
            periodo_inicio     TEXT NOT NULL,
            periodo_fin        TEXT NOT NULL,
            total_devengado    INTEGER,
            total_deducciones  INTEGER,
            neto_a_pagar       INTEGER,
            costo_total_mes    INTEGER,
            fecha_calculo      TEXT NOT NULL,
            datos_json         TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_nom_ced  ON nominas(cedula);
        CREATE INDEX IF NOT EXISTS idx_nom_per  ON nominas(periodo_fin);
        """)


def _serialize(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    return str(obj)


def guardar_nomina(res: dict) -> int:
    """Guarda empleado (upsert) + nómina. Retorna id de la nómina."""
    init_db()
    cedula = (res.get("cedula") or "").strip()
    if not cedula:
        raise ValueError("La cédula es obligatoria para guardar.")

    datos_json = json.dumps(res, default=_serialize, ensure_ascii=False)

    with _conn() as c:
        c.execute("""
            INSERT INTO empleados (cedula, nombre, empresa, nit, tipo_salario, salario_base, valor_hora, actualizado)
            VALUES (?,?,?,?,?,?,?,?)
            ON CONFLICT(cedula) DO UPDATE SET
              nombre=excluded.nombre,
              empresa=excluded.empresa,
              nit=excluded.nit,
              tipo_salario=excluded.tipo_salario,
              salario_base=excluded.salario_base,
              valor_hora=excluded.valor_hora,
              actualizado=excluded.actualizado
        """, (
            cedula,
            res.get("empleado", ""),
            res.get("empresa", ""),
            res.get("nit", ""),
            res.get("tipo_salario", ""),
            int(res.get("salario_base") or 0),
            int(res.get("valor_hora") or 0),
            datetime.now().isoformat(timespec="seconds"),
        ))

        cur = c.execute("""
            INSERT INTO nominas (
              cedula, empleado, empresa, periodo_inicio, periodo_fin,
              total_devengado, total_deducciones, neto_a_pagar, costo_total_mes,
              fecha_calculo, datos_json
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
        """, (
            cedula,
            res.get("empleado", ""),
            res.get("empresa", ""),
            _serialize(res.get("periodo_inicio")),
            _serialize(res.get("periodo_fin")),
            int(res.get("total_devengado") or 0),
            int(res.get("total_deducciones") or 0),
            int(res.get("neto_a_pagar") or 0),
            int(res.get("costo_total_mes") or 0),
            datetime.now().isoformat(timespec="seconds"),
            datos_json,
        ))
        return cur.lastrowid


def listar_empleados() -> list[dict]:
    init_db()
    with _conn() as c:
        rows = c.execute("""
            SELECT e.*, COUNT(n.id) AS num_nominas, MAX(n.periodo_fin) AS ultima_nomina
            FROM empleados e
            LEFT JOIN nominas n ON n.cedula = e.cedula
            GROUP BY e.cedula
            ORDER BY e.nombre COLLATE NOCASE
        """).fetchall()
        return [dict(r) for r in rows]


def obtener_empleado(cedula: str) -> dict | None:
    init_db()
    with _conn() as c:
        r = c.execute("SELECT * FROM empleados WHERE cedula = ?", (cedula,)).fetchone()
        return dict(r) if r else None


def listar_nominas(cedula: str | None = None) -> list[dict]:
    init_db()
    with _conn() as c:
        if cedula:
            rows = c.execute("""
                SELECT id, cedula, empleado, empresa, periodo_inicio, periodo_fin,
                       total_devengado, total_deducciones, neto_a_pagar, costo_total_mes, fecha_calculo
                FROM nominas WHERE cedula = ?
                ORDER BY periodo_fin DESC, id DESC
            """, (cedula,)).fetchall()
        else:
            rows = c.execute("""
                SELECT id, cedula, empleado, empresa, periodo_inicio, periodo_fin,
                       total_devengado, total_deducciones, neto_a_pagar, costo_total_mes, fecha_calculo
                FROM nominas
                ORDER BY periodo_fin DESC, id DESC
            """).fetchall()
        return [dict(r) for r in rows]


def obtener_nomina(nomina_id: int) -> dict | None:
    init_db()
    with _conn() as c:
        r = c.execute("SELECT datos_json FROM nominas WHERE id = ?", (nomina_id,)).fetchone()
        if not r:
            return None
        data = json.loads(r["datos_json"])
        for k in ("periodo_inicio", "periodo_fin"):
            if isinstance(data.get(k), str):
                try:
                    data[k] = date.fromisoformat(data[k][:10])
                except Exception:
                    pass
        return data


def borrar_nomina(nomina_id: int):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM nominas WHERE id = ?", (nomina_id,))


def borrar_empleado(cedula: str):
    init_db()
    with _conn() as c:
        c.execute("DELETE FROM nominas WHERE cedula = ?", (cedula,))
        c.execute("DELETE FROM empleados WHERE cedula = ?", (cedula,))
