#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Agrega la página 'Apertura por Proveedor' (con drill total) al report.json."""
import json, uuid

REPORT = "Tablero_ZREAL.Report/report.json"
ENTITY = {"b": "Base Real"}

def gid():
    return uuid.uuid4().hex

def sel_measure(alias, prop):
    ref = f"{ENTITY[alias]}.{prop}"
    return {"Measure": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop}, "Name": ref}, ref

def sel_column(alias, prop):
    ref = f"{ENTITY[alias]}.{prop}"
    return {"Column": {"Expression": {"SourceRef": {"Source": alias}}, "Property": prop}, "Name": ref}, ref

def visual(x, y, w, h, z, vtype, froms, selects, projections):
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

# --- slicers ---
s_vert, r_vert = sel_column("b", "VERTICAL")
vis.append(visual(16, 16, 210, 150, 0, "slicer", ["b"], [s_vert], {"Values": [r_vert]}))
s_tipo, r_tipo = sel_column("b", "TIPO CECO")
vis.append(visual(16, 176, 210, 150, 1, "slicer", ["b"], [s_tipo], {"Values": [r_tipo]}))

# --- tarjeta OPEX Total ---
m_opex, r_opex = sel_measure("b", "OPEX Total")
vis.append(visual(16, 336, 210, 100, 2, "card", ["b"], [m_opex], {"Values": [r_opex]}))

# --- barras: OPEX por Proveedor (contrapartida) ---
c_prov, r_prov = sel_column("b", "Denominacion cuenta contrapartida")
mb_opex, _ = sel_measure("b", "OPEX Total")
vis.append(visual(240, 16, 470, 688, 3, "barChart", ["b"], [c_prov, mb_opex],
                  {"Category": [r_prov], "Y": [r_opex]}))

# --- matriz: APERTURA TOTAL (jerarquía expandible) ---
hier = [
    sel_column("b", "VERTICAL"),
    sel_column("b", "Denominación de la cuenta"),
    sel_column("b", "NEGOCIO/AREA"),
    sel_column("b", "Denominacion cuenta contrapartida"),
    sel_column("b", "Centro de coste"),
]
mm_opex, _ = sel_measure("b", "OPEX Total")
selects = [s for s, _ in hier] + [mm_opex]
rows = [r for _, r in hier]
vis.append(visual(724, 16, 540, 688, 4, "pivotTable", ["b"],
                  selects, {"Rows": rows, "Values": [r_opex]}))

section = {
    "name": "ReportSection" + gid(),
    "displayName": "Apertura por Proveedor",
    "filters": "[]",
    "ordinal": 3,
    "visualContainers": vis,
    "config": "{}",
    "displayOption": 1,
    "height": 720.0,
    "width": 1280.0,
}

with open(REPORT, "r", encoding="utf-8") as f:
    d = json.load(f)
d["sections"] = [s for s in d["sections"] if s.get("displayName") != "Apertura por Proveedor"]
d["sections"].append(section)
for i, s in enumerate(d["sections"]):
    s["ordinal"] = i
with open(REPORT, "w", encoding="utf-8") as f:
    json.dump(d, f, ensure_ascii=False, indent=2)
print("Página 'Apertura por Proveedor' agregada. Páginas:", [s["displayName"] for s in d["sections"]])
