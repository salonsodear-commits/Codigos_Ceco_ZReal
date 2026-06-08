#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrega la página 'Real vs PA' al report.json del Tablero_ZREAL."""
import json, uuid, os

REPORT = "Tablero_ZREAL.Report/report.json"

ENTITY = {"b": "Base Real", "p": "PA", "v": "Vertical", "c": "Calendario"}

def gid():
    return uuid.uuid4().hex

def sel_measure(alias, prop):
    table = ENTITY[alias]
    ref = f"{table}.{prop}"
    return {"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop}, "Name": ref}, ref

def sel_column(alias, prop):
    table = ENTITY[alias]
    ref = f"{table}.{prop}"
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop}, "Name": ref}, ref

def visual(x, y, w, h, z, vtype, froms, selects, projections):
    """froms: list de alias; selects: list de dicts Select; projections: {role:[refs]}"""
    cfg = {
        "name": gid(),
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": z, "width": w, "height": h, "tabOrder": z}}],
        "singleVisual": {
            "visualType": vtype,
            "projections": {role: [{"queryRef": r} for r in refs] for role, refs in projections.items()},
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": a, "Entity": ENTITY[a], "Type": 0} for a in froms],
                "Select": selects,
            },
            "drillFilterOtherVisuals": True,
        },
    }
    return {"x": float(x), "y": float(y), "z": float(z), "width": float(w), "height": float(h),
            "config": json.dumps(cfg, ensure_ascii=False), "filters": "[]"}

vis = []

# --- slicers (columna izquierda) ---
s_vert, r_vert = sel_column("v", "Vertical")
vis.append(visual(16, 16, 210, 150, 0, "slicer", ["v"], [s_vert], {"Values": [r_vert]}))

s_anio, r_anio = sel_column("c", "Año")
vis.append(visual(16, 176, 210, 150, 1, "slicer", ["c"], [s_anio], {"Values": [r_anio]}))

# --- tarjetas KPI ---
m_opex, r_opex = sel_measure("b", "OPEX Total")
vis.append(visual(240, 16, 250, 100, 2, "card", ["b"], [m_opex], {"Values": [r_opex]}))

m_ppto, r_ppto = sel_measure("p", "Presupuesto Total")
vis.append(visual(500, 16, 250, 100, 3, "card", ["p"], [m_ppto], {"Values": [r_ppto]}))

m_desv, r_desv = sel_measure("b", "Desvío OPEX vs PA")
vis.append(visual(760, 16, 250, 100, 4, "card", ["b"], [m_desv], {"Values": [r_desv]}))

m_ejec, r_ejec = sel_measure("b", "% Ejecución Ppto")
vis.append(visual(1020, 16, 244, 100, 5, "card", ["b"], [m_ejec], {"Values": [r_ejec]}))

# --- columnas: Real vs PA por Vertical ---
mv_opex, _ = sel_measure("b", "OPEX Total")
mv_ppto, _ = sel_measure("p", "Presupuesto Total")
cv_vert, rcv_vert = sel_column("v", "Vertical")
vis.append(visual(240, 128, 510, 200, 6, "clusteredColumnChart", ["v", "b", "p"],
                  [cv_vert, mv_opex, mv_ppto],
                  {"Category": [rcv_vert], "Y": [r_opex, r_ppto]}))

# --- línea: Real vs PA en el tiempo ---
ml_opex, _ = sel_measure("b", "OPEX Total")
ml_ppto, _ = sel_measure("p", "Presupuesto Total")
cl_mes, rcl_mes = sel_column("c", "Mes")
vis.append(visual(760, 128, 504, 200, 7, "lineChart", ["c", "b", "p"],
                  [cl_mes, ml_opex, ml_ppto],
                  {"Category": [rcl_mes], "Y": [r_opex, r_ppto]}))

# --- matriz: Vertical x (OPEX, Ppto, Desvío, %Ejec) ---
mm_opex, _ = sel_measure("b", "OPEX Total")
mm_ppto, _ = sel_measure("p", "Presupuesto Total")
mm_desv, _ = sel_measure("b", "Desvío OPEX vs PA")
mm_ejec, _ = sel_measure("b", "% Ejecución Ppto")
mr_vert, rmr_vert = sel_column("v", "Vertical")
vis.append(visual(16, 340, 1248, 360, 8, "pivotTable", ["v", "b", "p"],
                  [mr_vert, mm_opex, mm_ppto, mm_desv, mm_ejec],
                  {"Rows": [rmr_vert], "Values": [r_opex, r_ppto, r_desv, r_ejec]}))

section = {
    "name": "ReportSection" + gid(),
    "displayName": "Real vs PA",
    "filters": "[]",
    "ordinal": 2,
    "visualContainers": vis,
    "config": "{}",
    "displayOption": 1,
    "height": 720.0,
    "width": 1280.0,
}

with open(REPORT, "r", encoding="utf-8") as f:
    d = json.load(f)

# evita duplicar si se corre dos veces
d["sections"] = [s for s in d["sections"] if s.get("displayName") != "Real vs PA"]
d["sections"].append(section)

with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)

print("Página 'Real vs PA' agregada. Total páginas:", len(d["sections"]))
