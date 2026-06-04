#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validar_ceco.py
===============
Validacion de la decodificacion del CECO (10 posiciones) del ZREAL contra el
diccionario maestro V106.

Corre los chequeos C1..C8 sobre el TOTAL de filas de la hoja `Base Real`,
reporta conteos exactos (filas, %, monto involucrado) y exporta el detalle
completo de excepciones a `validacion_ceco_excepciones.xlsx` (una hoja por
chequeo).

Fuentes:
  - CECOS_-_Resumen_y_explicacion_V106.xlsx  (diccionario maestro)
  - Real_y_pa_2026v2.xlsx  -> hoja `Base Real`  (ZREAL)

Trazabilidad: cada catalogo se carga de su hoja/columna concreta; el patron de
10 posiciones es  [1]Letra [2-3]Negocio/Area [4-6]Producto/Sector [7-10]Zona.
"""

import re
import sys
from collections import defaultdict

import pandas as pd

CAT = "CECOS_-_Resumen_y_explicacion_V106.xlsx"
REAL = "Real_y_pa_2026v2.xlsx"
HOJA_REAL = "Base Real"
OUT_XLSX = "validacion_ceco_excepciones.xlsx"

ZONE_RE = re.compile(r"^9\d{2}[A-Z]$")        # patron de zona valido: 9NN + letra
SECTOR_RE = re.compile(r"^[A-Z]\d{2}$")        # patron de sector indirecto: L+NN
PROD_RE = re.compile(r"^\d{3}$")               # patron de producto directo: NNN
LOC_RE = re.compile(r"^L\d{2,3}$")             # patron de orden de locacion: L+N


# ---------------------------------------------------------------------------
# 1) CARGA DE CATALOGOS (diccionario V106)
# ---------------------------------------------------------------------------
def cargar_catalogos():
    cat = {}

    # --- Tabla Inicial CECO: letra de sociedad <-> numero/nombre ---
    ti = pd.read_excel(CAT, sheet_name="Tabla Inicial CECO", header=2).dropna(how="all")
    ti = ti.rename(columns={"Letra CECO": "letra", "SOCIEDAD": "sociedad", "NÚMERO": "numero"})
    ti["letra"] = ti["letra"].astype(str).str.strip()
    ti["numero"] = ti["numero"].apply(lambda x: f"{int(x):04d}" if pd.notna(x) else None)
    cat["letras_validas"] = set(ti["letra"].dropna())
    # una letra puede mapear a varias sociedades (C es compartida)
    cat["letra_a_numeros"] = defaultdict(set)
    cat["numero_a_letra"] = {}
    for _, r in ti.iterrows():
        cat["letra_a_numeros"][r["letra"]].add(r["numero"])
        cat["numero_a_letra"][r["numero"]] = r["letra"]
    cat["tabla_inicial"] = ti

    # --- Direct NEGOCIOS: codigos pos 2-3 (directos) ---
    neg = pd.read_excel(CAT, sheet_name="Direct NEGOCIOS", header=2).dropna(how="all")
    neg = neg.rename(columns={"CÓDIGO": "codigo", "DESCRIPCIÓN": "desc"})
    neg["codigo"] = neg["codigo"].apply(lambda x: f"{int(x):02d}" if pd.notna(x) else None)
    cat["negocios"] = dict(zip(neg["codigo"], neg["desc"]))

    # --- Direct PRODUCTOS: codigos pos 4-6 (directos). Filtra filas espurias ---
    prod = pd.read_excel(CAT, sheet_name="Direct PRODUCTOS", header=2).dropna(how="all")
    prod = prod.rename(columns={"CÓDIGO": "codigo", "DESCRIPCIÓN": "desc"})
    prod["codigo"] = prod["codigo"].astype(str).str.strip()
    prod = prod[prod["codigo"].str.match(PROD_RE, na=False)]
    cat["productos"] = dict(zip(prod["codigo"], prod["desc"]))

    # --- INDIRECTOS: areas (pos 2-3), sectores (pos 4-6), pares Area->Sector ---
    ind = pd.read_excel(CAT, sheet_name="INDIRECTOS", header=2)
    ind = ind.rename(columns={
        "CÓDIGO.1": "area", "DESCRIPCIÓN": "area_desc", "RESPONSABLE": "area_resp",
        "CÓDIGO.2": "sector", "DESCRIPCIÓN.1": "sector_desc", "RESPONSABLE.1": "sector_resp",
        "CÓDIGO.3": "zona",
    })
    areas = ind[["area", "area_desc"]].dropna(subset=["area"])
    areas = areas[areas["area"].str.match(r"^[A-Z]{2}$", na=False)]
    cat["areas"] = dict(zip(areas["area"], areas["area_desc"]))
    secs = ind[["sector", "sector_desc"]].dropna(subset=["sector"])
    secs = secs[secs["sector"].str.match(SECTOR_RE, na=False)]
    cat["sectores"] = dict(zip(secs["sector"], secs["sector_desc"]))
    pares = ind[["area", "sector"]].dropna()
    pares = pares[pares["sector"].str.match(SECTOR_RE, na=False)
                  & pares["area"].str.match(r"^[A-Z]{2}$", na=False)]
    cat["pares_area_sector"] = set(zip(pares["area"], pares["sector"]))
    cat["sectores_por_area"] = defaultdict(set)
    for a, s in cat["pares_area_sector"]:
        cat["sectores_por_area"][a].add(s)
    # zonas presentes en INDIRECTOS (col CÓDIGO.3), filtrando ruido con el patron
    zind = {z for z in ind["zona"].dropna().astype(str) if ZONE_RE.match(z)}

    # --- ZONAS: catalogo de zonas pos 7-10 ---
    zon = pd.read_excel(CAT, sheet_name="ZONAS", header=2).dropna(how="all")
    zon = zon.rename(columns={"CÓDIGO": "codigo", "DESCRIPCIÓN": "desc"})
    zon["codigo"] = zon["codigo"].astype(str).str.strip()
    zmap = dict(zip(zon["codigo"], zon["desc"]))

    # --- LOCACIONES: ordenes L+N (pos 4-6) y zonas adicionales ---
    loc = pd.read_excel(CAT, sheet_name="LOCACIONES", header=2).dropna(how="all")
    loc = loc.rename(columns={"Nº ORDEN": "orden", "DESCRIPCIÓN": "desc", "ZONA": "zona", "CECO": "ceco"})
    loc["orden"] = loc["orden"].astype(str).str.strip()
    cat["locaciones_orden"] = {o for o in loc["orden"] if LOC_RE.match(o)}
    cat["locaciones_ceco"] = set(loc["ceco"].dropna().astype(str).str.strip())
    zloc = {z for z in loc["zona"].dropna().astype(str) if ZONE_RE.match(z)}

    # universo de zonas = union de las 3 fuentes (regex-limpias)
    zonas_validas = set(k for k in zmap if ZONE_RE.match(str(k))) | zind | zloc
    cat["zonas"] = zonas_validas
    cat["zonas_desc"] = zmap
    cat["zonas_origen"] = {"ZONAS": set(k for k in zmap if ZONE_RE.match(str(k))),
                           "INDIRECTOS": zind, "LOCACIONES": zloc}
    return cat


# ---------------------------------------------------------------------------
# 2) DESCOMPOSICION DEL CECO Y TIPOLOGIA INFERIDA
# ---------------------------------------------------------------------------
def inferir_tipologia(p23):
    if p23 == "LE":
        return "Locación"
    if re.match(r"^\d{2}$", p23):
        return "Directo"
    if re.match(r"^[A-Z]{2}$", p23):
        return "Indirecto"
    return "Desconocido"


def descomponer(df):
    cc = df["Centro de coste"].astype(str).str.strip()
    df = df.copy()
    df["_ceco"] = cc
    df["_len"] = cc.str.len()
    df["_p1"] = cc.str[0]
    df["_p23"] = cc.str[1:3]
    df["_p46"] = cc.str[3:6]
    df["_p710"] = cc.str[6:10]
    df["_tipo_inf"] = df["_p23"].apply(inferir_tipologia)
    return df


# ---------------------------------------------------------------------------
# 3) HELPERS DE REPORTE
# ---------------------------------------------------------------------------
COLS_DET = ["Centro de coste", "Sociedad", "EMPRESA", "TIPO CECO",
            "CODIGO NEGOCIO/AREA", "CODIGO PRODUCTO/SECTOR", "NEGOCIO/AREA",
            "PRODUCTO/SECTOR", "ZONA", "VERTICAL", "Clase de coste",
            "Denom.clase de coste", "Valor/mon.inf."]


def resumen(nombre, mask, df, total, monto_total):
    sub = df[mask]
    n = len(sub)
    monto = sub["Valor/mon.inf."].sum()
    ejemplos = sub["_ceco"].drop_duplicates().head(10).tolist()
    return {
        "check": nombre, "filas": n, "pct": round(100 * n / total, 4),
        "monto": monto, "pct_monto": round(100 * monto / monto_total, 4) if monto_total else 0,
        "ejemplos": ejemplos,
    }, sub


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------
def main():
    print(">> Cargando catalogos V106 ...")
    cat = cargar_catalogos()
    print(f"   negocios={len(cat['negocios'])}  productos={len(cat['productos'])} "
          f"areas={len(cat['areas'])}  sectores={len(cat['sectores'])} "
          f"pares A-S={len(cat['pares_area_sector'])}  zonas={len(cat['zonas'])} "
          f"locaciones={len(cat['locaciones_orden'])}")

    print(">> Cargando Base Real (total) ...")
    df = pd.read_excel(REAL, sheet_name=HOJA_REAL)
    df = descomponer(df)
    total = len(df)
    monto_total = df["Valor/mon.inf."].sum()
    print(f"   filas={total}  monto_total={monto_total:,.2f}")

    detalles = {}   # check -> dataframe de excepciones
    resumenes = []

    # --- C1 Longitud != 10 ---
    m = df["_len"] != 10
    r, sub = resumen("C1 Longitud != 10", m, df, total, monto_total); resumenes.append(r); detalles["C1"] = sub

    # --- C2 Letra de sociedad ---
    m_letra = ~df["_p1"].isin(cat["letras_validas"])
    # coherencia letra <-> numero de sociedad (Sociedad viene como 10/99 -> 0010/0099)
    soc4 = df["Sociedad"].apply(lambda x: f"{int(x):04d}" if pd.notna(x) and str(x).strip() not in ("", "nan") else None)
    df["_soc4"] = soc4
    def coherente(row):
        nums = cat["letra_a_numeros"].get(row["_p1"], set())
        return row["_soc4"] in nums if row["_soc4"] else False
    m_incoh = ~df.apply(coherente, axis=1)
    m = m_letra | m_incoh
    df["_C2_letra_invalida"] = m_letra
    df["_C2_incoherente"] = m_incoh
    r, sub = resumen("C2 Letra invalida o incoherente con Sociedad", m, df, total, monto_total); resumenes.append(r); detalles["C2"] = sub

    # --- C3 Tipologia inferida vs TIPO CECO ---
    tipo_base = df["TIPO CECO"].astype(str).str.strip().str.lower()
    tipo_inf = df["_tipo_inf"].str.lower().replace({"locación": "directo"})  # locacion no existe en TIPO CECO base
    # Comparamos: base marca Directo/Indirecto. Locacion inferida la tratamos aparte.
    m_loc = df["_tipo_inf"] == "Locación"
    m_mismatch = (~m_loc) & (tipo_inf != tipo_base)
    m = m_mismatch | (m_loc & (tipo_base != "directo") & (tipo_base != "indirecto") )  # locaciones: solo informo mismatch real
    # Para reporte util: mismatch = inferida (no-locacion) distinta a la base
    m = m_mismatch
    df["_C3_tipo_inferida"] = df["_tipo_inf"]
    r, sub = resumen("C3 Tipologia inferida != TIPO CECO", m, df, total, monto_total); resumenes.append(r); detalles["C3"] = sub

    # --- C4 Negocio/Area (pos 2-3) inexistente segun tipologia ---
    def c4_invalido(row):
        t = row["_tipo_inf"]
        if t == "Directo":
            return row["_p23"] not in cat["negocios"]
        if t == "Indirecto":
            return row["_p23"] not in cat["areas"]
        if t == "Locación":
            return row["_p23"] != "LE"
        return True
    m = df.apply(c4_invalido, axis=1)
    r, sub = resumen("C4 Negocio/Area (pos 2-3) inexistente", m, df, total, monto_total); resumenes.append(r); detalles["C4"] = sub

    # --- C5 Producto/Sector (pos 4-6) inexistente o sector no listado para esa Area ---
    def c5_invalido(row):
        t = row["_tipo_inf"]
        if t == "Directo":
            return row["_p46"] not in cat["productos"]
        if t == "Indirecto":
            if row["_p46"] not in cat["sectores"]:
                return True
            return (row["_p23"], row["_p46"]) not in cat["pares_area_sector"]
        if t == "Locación":
            return row["_p46"] not in cat["locaciones_orden"]
        return True
    m = df.apply(c5_invalido, axis=1)
    r, sub = resumen("C5 Producto/Sector (pos 4-6) inexistente o sector no en Area", m, df, total, monto_total); resumenes.append(r); detalles["C5"] = sub

    # --- C6 Zona (pos 7-10) fuera de catalogo ---
    m = ~df["_p710"].isin(cat["zonas"])
    r, sub = resumen("C6 Zona (pos 7-10) fuera de catalogo", m, df, total, monto_total); resumenes.append(r); detalles["C6"] = sub

    # --- C7 Consistencia con origen (reproducir CODIGO NEG/AREA, PROD/SECTOR, ZONA) ---
    cod_na = df["CODIGO NEGOCIO/AREA"].astype(str).str.strip()
    cod_ps = df["CODIGO PRODUCTO/SECTOR"].astype(str).str.strip()
    zona_o = df["ZONA"].astype(str).str.strip()
    # la base guarda ZONA sin distincion; comparamos contra pos 7-10
    m_na = cod_na != df["_p23"]
    m_ps = cod_ps != df["_p46"]
    m_z = zona_o != df["_p710"]
    df["_C7_dif_negarea"] = m_na
    df["_C7_dif_prodsec"] = m_ps
    df["_C7_dif_zona"] = m_z
    m = m_na | m_ps | m_z
    r, sub = resumen("C7 Descomposicion != campos de origen", m, df, total, monto_total); resumenes.append(r); detalles["C7"] = sub

    # --- C8 Huerfanos de catalogo a la inversa (codigos sin uso en la base) ---
    usados_neg = set(df.loc[df["_tipo_inf"] == "Directo", "_p23"])
    usados_prod = set(df.loc[df["_tipo_inf"] == "Directo", "_p46"])
    usados_area = set(df.loc[df["_tipo_inf"] == "Indirecto", "_p23"])
    usados_sec = set(df.loc[df["_tipo_inf"] == "Indirecto", "_p46"])
    usados_zona = set(df["_p710"])
    huerf = []
    for k, v in cat["negocios"].items():
        if k not in usados_neg: huerf.append(("NEGOCIO", k, v))
    for k, v in cat["productos"].items():
        if k not in usados_prod: huerf.append(("PRODUCTO", k, v))
    for k, v in cat["areas"].items():
        if k not in usados_area: huerf.append(("AREA", k, v))
    for k, v in cat["sectores"].items():
        if k not in usados_sec: huerf.append(("SECTOR", k, v))
    for k in sorted(cat["zonas"]):
        if k not in usados_zona: huerf.append(("ZONA", k, cat["zonas_desc"].get(k, "")))
    df_huerf = pd.DataFrame(huerf, columns=["tipo_catalogo", "codigo", "descripcion"])
    resumenes.append({"check": "C8 Huerfanos de catalogo (informativo)", "filas": len(df_huerf),
                      "pct": 0.0, "monto": 0.0, "pct_monto": 0.0,
                      "ejemplos": df_huerf["codigo"].head(10).tolist()})
    detalles["C8"] = df_huerf

    # ---------------- REPORTE EN CONSOLA ----------------
    print("\n" + "=" * 90)
    print(f"{'CHECK':<52}{'FILAS':>8}{'%':>8}{'MONTO':>20}")
    print("=" * 90)
    for r in resumenes:
        print(f"{r['check']:<52}{r['filas']:>8}{r['pct']:>8.3f}{r['monto']:>20,.2f}")
        if r["ejemplos"]:
            print(f"    ej: {', '.join(map(str, r['ejemplos'][:10]))}")
    print("=" * 90)

    # ---------------- EXPORT A DISCO ----------------
    print(f"\n>> Escribiendo {OUT_XLSX} ...")
    with pd.ExcelWriter(OUT_XLSX, engine="openpyxl") as xw:
        # hoja resumen
        res = pd.DataFrame([{k: v for k, v in r.items() if k != "ejemplos"} for r in resumenes])
        res["ejemplos"] = ["; ".join(map(str, r["ejemplos"])) for r in resumenes]
        res.to_excel(xw, sheet_name="RESUMEN", index=False)
        for ch in ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"]:
            sub = detalles[ch]
            if ch == "C8":
                sub.to_excel(xw, sheet_name=ch, index=False)
            else:
                cols = [c for c in COLS_DET if c in sub.columns]
                extra = [c for c in sub.columns if c.startswith("_C") ]
                out = sub[cols + extra].copy()
                # limitar tamaño de export por hoja (excel) si fuese gigante
                out.to_excel(xw, sheet_name=ch, index=False)
    print(">> Listo.")
    return resumenes


if __name__ == "__main__":
    main()
