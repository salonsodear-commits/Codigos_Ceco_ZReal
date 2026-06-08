#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generar_manual.py
Genera el Manual de Procedimiento del Tablero ZREAL en PDF (reportlab).
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                PageBreak, ListFlowable, ListItem, HRFlowable, KeepTogether)

AZUL = colors.HexColor("#12239E")
AZULC = colors.HexColor("#118DFF")
GRIS = colors.HexColor("#605E5C")
GRISCLARO = colors.HexColor("#F3F2F1")
NARANJA = colors.HexColor("#E66C37")
VERDE = colors.HexColor("#1AAB40")

styles = getSampleStyleSheet()
def S(name, **kw):
    base = kw.pop("parent", styles["Normal"])
    return ParagraphStyle(name, parent=base, **kw)

st_title   = S("t", fontName="Helvetica-Bold", fontSize=26, textColor=AZUL, leading=30, spaceAfter=6)
st_subtitle= S("s", fontName="Helvetica", fontSize=13, textColor=GRIS, leading=17, spaceAfter=4)
st_h1      = S("h1", fontName="Helvetica-Bold", fontSize=16, textColor=AZUL, leading=20, spaceBefore=16, spaceAfter=6)
st_h2      = S("h2", fontName="Helvetica-Bold", fontSize=12.5, textColor=AZULC, leading=16, spaceBefore=10, spaceAfter=4)
st_body    = S("b", fontName="Helvetica", fontSize=10.3, leading=15, alignment=TA_JUSTIFY, spaceAfter=6)
st_bullet  = S("bu", fontName="Helvetica", fontSize=10.3, leading=14.5, alignment=TA_LEFT)
st_small   = S("sm", fontName="Helvetica", fontSize=8.5, textColor=GRIS, leading=11)
st_callq   = S("cq", fontName="Helvetica-Bold", fontSize=10.8, textColor=colors.white, leading=14)
st_calltxt = S("ct", fontName="Helvetica", fontSize=10, textColor=colors.black, leading=14, alignment=TA_JUSTIFY)
st_cell    = S("ce", fontName="Helvetica", fontSize=9, leading=12)
st_cellb   = S("ceb", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white)
st_step    = S("stp", fontName="Helvetica", fontSize=10.3, leading=15, leftIndent=4)

def bullets(items, st=st_bullet):
    return ListFlowable(
        [ListItem(Paragraph(t, st), leftIndent=12, value="•") for t in items],
        bulletType="bullet", start="•", leftIndent=14, spaceAfter=6)

def callout(titulo, cuerpo, color=AZULC):
    """Caja de definición/concepto."""
    inner = [Paragraph(titulo, st_callq)]
    head = Table([[inner[0]]], colWidths=[16.0*cm])
    head.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),color),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),5),("BOTTOMPADDING",(0,0),(-1,-1),5)]))
    body = Table([[Paragraph(cuerpo, st_calltxt)]], colWidths=[16.0*cm])
    body.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),GRISCLARO),
        ("LEFTPADDING",(0,0),(-1,-1),8),("RIGHTPADDING",(0,0),(-1,-1),8),
        ("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
        ("LINEBELOW",(0,0),(-1,-1),0.5,color),
        ("LINEAFTER",(0,0),(-1,-1),0.5,color),
        ("LINEBEFORE",(0,0),(-1,-1),0.5,color)]))
    return KeepTogether([head, body, Spacer(1,8)])

def tabla(data, anchos, header=True):
    t = Table(data, colWidths=anchos, repeatRows=1 if header else 0)
    ts = [("FONTNAME",(0,0),(-1,-1),"Helvetica"),("FONTSIZE",(0,0),(-1,-1),9),
          ("VALIGN",(0,0),(-1,-1),"MIDDLE"),
          ("LEFTPADDING",(0,0),(-1,-1),5),("RIGHTPADDING",(0,0),(-1,-1),5),
          ("TOPPADDING",(0,0),(-1,-1),4),("BOTTOMPADDING",(0,0),(-1,-1),4),
          ("GRID",(0,0),(-1,-1),0.4,colors.HexColor("#C8C6C4")),
          ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white, GRISCLARO])]
    if header:
        ts += [("BACKGROUND",(0,0),(-1,0),AZUL),("TEXTCOLOR",(0,0),(-1,0),colors.white),
               ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold")]
    t.setStyle(TableStyle(ts))
    return t

def P(t): return Paragraph(t, st_body)
def H1(t): return Paragraph(t, st_h1)
def H2(t): return Paragraph(t, st_h2)

# pie de página con numeración
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(GRIS)
    canvas.drawString(2*cm, 1.1*cm, "Manual de Procedimiento · Tablero ZREAL — OPEX Operaciones Complejas")
    canvas.drawRightString(19*cm, 1.1*cm, "Página %d" % doc.page)
    canvas.setStrokeColor(colors.HexColor("#C8C6C4"))
    canvas.line(2*cm, 1.4*cm, 19*cm, 1.4*cm)
    canvas.restoreState()

E = []  # story

# ====================== PORTADA ======================
E += [Spacer(1, 3.2*cm)]
bar = Table([[ "" ]], colWidths=[16.0*cm], rowHeights=[0.18*cm])
bar.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,-1),AZULC)]))
E += [bar, Spacer(1,0.5*cm)]
E += [Paragraph("Manual de Procedimiento", st_title)]
E += [Paragraph("Tablero ZREAL — OPEX de Operaciones Complejas (Petróleo · Minería · Otras)", st_subtitle)]
E += [Spacer(1,0.3*cm)]
E += [Paragraph("Cómo funciona, de dónde toma los datos, cómo se actualiza y qué significa cada concepto. "
                "Escrito para que lo entienda cualquier persona del área, sin tecnicismos.", st_subtitle)]
E += [Spacer(1,1.2*cm)]
meta = Table([
    ["Herramienta", "Power BI Desktop (proyecto .pbip / archivo .pbix)"],
    ["Fuente de datos", "Real_y_pa_2026v2.xlsx — hoja «Base Real» (el ZREAL)"],
    ["Diccionario maestro", "CECOS_-_Resumen_y_explicacion_V106.xlsx"],
    ["Cobertura", "ene-2023 a abr-2026 · 65.818 registros"],
    ["Versión del manual", "1.0 — junio 2026"],
], colWidths=[4.2*cm, 11.8*cm])
meta.setStyle(TableStyle([
    ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),10),
    ("TEXTCOLOR",(0,0),(0,-1),AZUL),
    ("LEFTPADDING",(0,0),(-1,-1),8),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6),
    ("ROWBACKGROUNDS",(0,0),(-1,-1),[GRISCLARO, colors.white]),
    ("LINEBELOW",(0,0),(-1,-1),0.4,colors.HexColor("#C8C6C4"))]))
E += [meta]
E += [Spacer(1,0.6*cm)]
E += [Paragraph("Nota: los importes que se muestran como ejemplo en este manual son ilustrativos. Los números "
                "reales son los que aparezcan en el tablero al actualizar contra el archivo de origen.", st_small)]
E += [PageBreak()]

# ====================== 1. QUÉ ES ======================
E += [H1("1. ¿Qué es este tablero y para qué sirve?")]
E += [P("Este tablero es una <b>herramienta de visualización de gastos (OPEX)</b> de las Operaciones "
        "Complejas de la empresa. Toma todos los gastos registrados en el sistema contable (SAP) y los "
        "ordena para responder preguntas del día a día de Control de Gestión, por ejemplo:")]
E += [bullets([
    "¿Cuánto gastamos en total y cómo se reparte entre <b>Petróleo</b>, <b>Minería</b> y <b>Otras operaciones</b>?",
    "¿Qué porción del gasto es <b>directo</b> (atribuible a un negocio puntual) y qué porción es <b>indirecto</b> (compartido / de estructura)?",
    "¿En qué <b>rubros</b> se va la plata (alquileres, personal, honorarios, movilidad, etc.)?",
    "¿Cómo evoluciona el gasto <b>mes a mes</b>?",
    "¿Hay registros con datos mal cargados que haya que corregir (por ejemplo, zonas «huérfanas»)?",
])]
E += [callout("En una frase",
    "El tablero transforma una planilla de miles de asientos contables en gráficos que muestran "
    "<b>en qué, dónde y para qué negocio</b> se gasta, separando lo directo de lo indirecto.")]

# ====================== 2. DE DÓNDE SALEN LOS DATOS ======================
E += [H1("2. ¿De dónde salen los datos?")]
E += [P("Toda la información proviene de <b>un único archivo de Excel</b>: "
        "<b>Real_y_pa_2026v2.xlsx</b>, específicamente de la hoja llamada <b>«Base Real»</b>. "
        "Esa hoja es el <b>ZREAL</b>: la descarga de gastos reales del sistema SAP, con un registro por "
        "cada movimiento contable (unos 65.818 en total, de enero 2023 a abril 2026).")]
E += [P("El tablero <b>no modifica</b> ese archivo: solo lo lee. Cada vez que se actualiza, vuelve a leer "
        "la hoja «Base Real» y recalcula todos los gráficos.")]
E += [H2("¿Qué columnas usa de esa hoja?")]
E += [P("La hoja original tiene 57 columnas. El tablero toma las que necesita y, además, "
        "<b>descompone el código de centro de costo (CECO)</b> para entender cada gasto. Las principales:")]
E += [tabla([
    ["Columna del Excel", "Para qué se usa en el tablero"],
    ["Centro de coste", "El CECO de 10 caracteres. Es la «llave» que dice negocio, producto y zona."],
    ["Valor/mon.inf.", "El importe del gasto (lo que se suma en todos los visuales)."],
    ["TIPO CECO", "Si el gasto es Directo o Indirecto."],
    ["VERTICAL", "Petróleo / Minería / Otras operaciones dedicadas."],
    ["Denominación de la cuenta", "El rubro de OPEX (Alquileres, Honorarios, Movilidad, etc.)."],
    ["RUBRO EBITDA", "Costo de Servicio / Gasto de Comercialización / Estructura."],
    ["mes año", "La fecha, para ver la evolución temporal."],
    ["ZONA", "La provincia / región del gasto."],
], [5.2*cm, 10.8*cm])]
E += [callout("Dato importante sobre la ruta del archivo",
    "El tablero busca el Excel en una <b>ruta de tu computadora o de la red</b>. Si el archivo se mueve "
    "de carpeta, hay que avisarle la nueva ruta (se explica en el punto 4). Hoy está apuntando a: "
    "<i>O:\\Nuevos Negocios\\...\\Datos\\Real y pa 2026v2.xlsx</i>.", color=NARANJA)]

E += [PageBreak()]

# ====================== 3. CÓMO ESTÁ ARMADO (EL CECO) ======================
E += [H1("3. La clave de todo: el código CECO")]
E += [P("Cada gasto en SAP está «etiquetado» con un <b>Centro de Costo (CECO)</b>: un código de "
        "<b>10 caracteres</b> que, leído por partes, dice todo lo que necesitamos. Es como un código "
        "postal: cada tramo significa algo.")]
E += [tabla([
    ["Posición", "1", "2 y 3", "4 a 6", "7 a 10"],
    ["Qué indica", "Letra de\nsociedad", "Negocio o Área", "Producto o Sector", "Zona"],
    ["Ejemplo  C 04 001 901A", "C", "04", "001", "901A"],
], [4.6*cm, 2.2*cm, 3.4*cm, 3.4*cm, 2.4*cm])]
E += [P("El tablero <b>parte ese código automáticamente</b> y crea columnas nuevas: "
        "Letra, NegArea, ProdSector, ZonaCECO y, lo más importante, la <b>Tipología</b> "
        "(Directo / Indirecto / Locación). Así no hace falta interpretar el código a mano.")]

E += [callout("¿Cómo sabe si es Directo o Indirecto?",
    "Mira las posiciones 2 y 3 del código:<br/>"
    "• Si son <b>dos números</b> (ej. «04») → es <b>DIRECTO</b>.<br/>"
    "• Si son <b>dos letras</b> (ej. «AF», «ON») → es <b>INDIRECTO</b>.<br/>"
    "• Si son las letras «LE» → es una <b>Locación</b> (un edificio/oficina).")]

# ====================== 4. CÓMO SE ACTUALIZA ======================
E += [H1("4. Cómo se actualiza el tablero (paso a paso)")]
E += [P("Cuando hay datos nuevos (un mes nuevo, correcciones, etc.), el proceso es:")]
E += [Paragraph("<b>Paso 1.</b> Reemplazá el archivo <b>Real_y_pa_2026v2.xlsx</b> en su carpeta por la "
                "versión actualizada (mismo nombre y misma hoja «Base Real»).", st_step), Spacer(1,3)]
E += [Paragraph("<b>Paso 2.</b> Abrí el tablero en Power BI Desktop.", st_step), Spacer(1,3)]
E += [Paragraph("<b>Paso 3.</b> En la pestaña <b>Inicio</b>, hacé clic en <b>Actualizar</b>. Power BI vuelve "
                "a leer el Excel y recalcula todos los gráficos.", st_step), Spacer(1,3)]
E += [Paragraph("<b>Paso 4.</b> Guardá (Archivo → Guardar).", st_step), Spacer(1,8)]
E += [H2("Si el archivo cambió de carpeta o de nombre")]
E += [P("Hay que actualizar la <b>ruta</b>. Es un «parámetro» configurable:")]
E += [Paragraph("Inicio → <b>Transformar datos</b> → <b>Administrar parámetros</b> → "
                "campo <b>RutaArchivo</b> → pegá la nueva ruta completa → <b>Cerrar y aplicar</b>.", st_step)]
E += [Spacer(1,6)]
E += [callout("¿Por qué un «parámetro» de ruta?",
    "Para que el tablero no dependa de una carpeta fija. Cada usuario puede apuntarlo a donde tenga el "
    "Excel (su PC, una unidad de red como O:\\, OneDrive) sin tocar nada más.")]

E += [PageBreak()]

# ====================== 5. CONCEPTOS CLAVE ======================
E += [H1("5. Conceptos clave (explicados simple)")]

E += [H2("5.1 Gasto Directo vs. Gasto Indirecto")]
E += [P("Es la distinción más importante del tablero.")]
E += [callout("Gasto DIRECTO",
    "Gasto que se puede atribuir <b>sin dudas a un negocio puntual</b>: su CECO dice exactamente "
    "el negocio, el producto y la zona. Ejemplo: el agua para los operarios de una base de Petróleo en "
    "Neuquén. En la base son <b>4.857 registros</b> (~4,1% del total).", color=VERDE)]
E += [callout("Gasto INDIRECTO",
    "Gasto <b>compartido o de estructura</b> que no pertenece a un solo negocio: administración, "
    "finanzas, sistemas, capital humano, dirección. Su CECO usa un Área (dos letras) y un Sector. "
    "En la base son <b>60.961 registros</b> (~95,9% del total). Para repartirlo entre negocios hace "
    "falta una regla de <b>prorrateo</b> (ver punto 7).", color=NARANJA)]
E += [P("<b>¿Por qué importa?</b> Porque el costo directo se carga tal cual al negocio, mientras que el "
        "indirecto hay que <b>distribuirlo</b> con un criterio para saber cuánto le toca a Petróleo, "
        "cuánto a Minería y cuánto a Otras.")]

E += [H2("5.2 Vertical")]
E += [P("Es el segmento de negocio de Operaciones Complejas. El tablero lo trae ya resuelto en la columna "
        "<b>VERTICAL</b>, con tres valores: <b>PETRÓLEO</b> (clientes como YPF y Vista, zona Vaca Muerta), "
        "<b>MINERÍA</b> y <b>OTRAS OPERACIONES DEDICADAS</b>.")]

E += [H2("5.3 OPEX y rubros")]
E += [P("<b>OPEX</b> significa «gastos operativos»: lo que cuesta operar (no incluye inversiones de capital). "
        "El tablero agrupa el OPEX en <b>rubros consolidados</b> tomados de la columna "
        "<b>Denominación de la cuenta</b>: Alquileres, Beneficios al Personal, Movilidad y Representación, "
        "Honorarios y Servicios Contratados, Mantenimiento, Limpieza y Vigilancia, Seguros, Servicios "
        "Públicos, Insumos de Oficina, Promoción y Publicidad, Comisiones, Deudores Incobrables, Gastos de "
        "Rodados y Equipos.")]

E += [H2("5.4 Costo de Servicio vs. Gasto de Comercialización")]
E += [P("Es la naturaleza del gasto según el área que lo genera (columna <b>RUBRO EBITDA</b>):")]
E += [bullets([
    "<b>Costo de Servicio</b>: gasto de la operación que presta el servicio (áreas OPERATIVAS).",
    "<b>Gasto de Comercialización</b>: gasto de vender (áreas COMERCIALES).",
    "<b>Gasto de Estructura y Soporte</b>: gasto de soporte general (residual).",
])]

E += [H2("5.5 Zona y «zona huérfana» (lo que preguntaste)")]
E += [P("La <b>Zona</b> son las últimas 4 posiciones del CECO (ej. 901A = CABA, 915A = Neuquén). "
        "Existe un <b>catálogo oficial de zonas</b> en el diccionario maestro V106. El tablero compara "
        "la zona de cada gasto contra ese catálogo.")]
E += [callout("¿Qué es una «zona HUÉRFANA»?",
    "Es una zona que <b>aparece en los datos pero NO está dada de alta en el catálogo oficial</b>. "
    "El código tiene la forma correcta (parece una zona válida), pero nadie la registró en el "
    "diccionario maestro. Es como un código postal que alguien escribió bien pero que la oficina de "
    "correos nunca cargó en su lista oficial: existe en la práctica, pero «no figura».", color=NARANJA)]
E += [P("<b>¿Por qué se marcan?</b> Porque son registros válidos en monto pero que quedan «colgados»: "
        "conviene que Control de Gestión / el dueño de los datos las <b>dé de alta en el diccionario "
        "V106</b> para que queden bien clasificadas. El tablero las señala con la etiqueta "
        "«HUÉRFANA (alta V106 pendiente)» en la columna <b>ZonaHuerfana</b> de la tabla de la página 1.")]
E += [P("En total son <b>228 registros</b> (~0,35% del total) por unos <b>$25,3 millones</b>, "
        "concentrados en 5 códigos:")]
E += [tabla([
    ["Zona huérfana", "Registros", "Probable", "Comentario"],
    ["902B", "33", "Buenos Aires", "Es la de mayor monto (~$21,7 M)."],
    ["901C", "116", "CABA", "La de más registros."],
    ["915E", "68", "Neuquén", "Montos chicos."],
    ["916E", "9", "Río Negro", "Montos chicos."],
    ["902C", "2", "Buenos Aires", "Marginal."],
], [3.0*cm, 2.4*cm, 3.4*cm, 7.2*cm])]
E += [Paragraph("«Probable» es una interpretación por el prefijo numérico; debe confirmarlo el dueño del dato.", st_small)]

E += [PageBreak()]

# ====================== 6. CÓMO LEER CADA PÁGINA ======================
E += [H1("6. Cómo leer el tablero, página por página")]
E += [P("El tablero tiene <b>dos páginas</b> (pestañas abajo a la izquierda). En todas, al hacer clic "
        "en un elemento de un gráfico, el resto se <b>resalta/filtra</b> automáticamente.")]

E += [H2("Página 1 — «Resumen OPEX»")]
E += [tabla([
    ["Visual", "Qué muestra / cómo leerlo"],
    ["Tarjeta «OPEX Total»", "El gasto total acumulado del período (o del filtro aplicado)."],
    ["Tarjetas «% Directo» y «% Indirecto»", "Qué porción del gasto es directa vs. indirecta (≈4,1% / 95,9%)."],
    ["Filtro «VERTICAL» (slicer)", "Tildá Petróleo / Minería / Otras para enfocar todo el tablero en ese segmento."],
    ["Columnas «OPEX por Vertical»", "Compara el gasto entre los tres segmentos."],
    ["Barras «OPEX por rubro»", "En qué rubros se va la plata. La barra más larga = el rubro más caro."],
    ["Línea «OPEX por mes año»", "La evolución mensual; sirve para ver picos y tendencias."],
    ["Tabla de Zonas", "Lista zonas con su OPEX y marca las «HUÉRFANAS»."],
], [4.8*cm, 11.2*cm])]

E += [H2("Página 2 — «Directo / Indirecto»")]
E += [tabla([
    ["Visual", "Qué muestra / cómo leerlo"],
    ["Tarjeta «OPEX Indirecto Transversal»", "El indirecto compartido que habría que prorratear (excluye sectores ya dedicados a OC)."],
    ["Tarjeta «OPEX Indirecto Dedicado OC»", "El indirecto que ya está asignado a Op. Complejas (sectores N03, N10, N12, N16, C13)."],
    ["Filtro «TIPO CECO» (slicer)", "Permite ver solo Directo o solo Indirecto."],
    ["Matriz «Rubro x Vertical»", "Cruce: cuánto gasta cada Vertical en cada rubro. La vista más analítica."],
    ["Columnas Directo/Indirecto por Vertical", "Dentro de cada Vertical, qué parte es directa y qué parte indirecta."],
    ["Tabla «Negocio/Área»", "Detalle del gasto por negocio o área."],
], [4.8*cm, 11.2*cm])]

E += [callout("Cómo interactuar (vale para todo el tablero)",
    "1) Usá los <b>filtros (slicers)</b> para enfocar un Vertical o un Tipo. "
    "2) <b>Hacé clic</b> en una barra/porción y el resto de los gráficos reacciona. "
    "3) Para sacar el filtro, volvé a clickear el mismo elemento. "
    "4) Pasá el mouse por encima para ver el <b>detalle (tooltip)</b>.")]

# ====================== 7. PENDIENTE / LIMITACIONES ======================
E += [H1("7. Qué está pendiente y limitaciones")]
E += [P("Para ser transparentes, el tablero hoy <b>todavía no reparte automáticamente</b> el gasto "
        "indirecto compartido entre los negocios. Eso se llama <b>prorrateo</b> y necesita un dato que "
        "<b>aún no está disponible</b> en el archivo: la <b>venta por unidad de negocio y por período</b>.")]
E += [bullets([
    "<b>Prorrateo por incidencia de venta:</b> la idea es repartir el indirecto según cuánto vende cada "
    "Vertical. La fórmula está definida y documentada, pero <b>falta la tabla de ventas</b> para activarla.",
    "<b>Período de referencia:</b> hay que confirmar si el % de venta se toma del mismo mes, del mes "
    "anterior o del acumulado.",
    "<b>Zonas huérfanas:</b> pendiente darlas de alta en el diccionario V106 (228 registros).",
    "<b>Sectores dedicados a OC</b> (N03 Petróleo, N10 Minería, C13 Op. Complejas): definir si se tratan "
    "como directos aunque su CECO sea indirecto.",
])]
E += [callout("Responsables sugeridos",
    "Fuente de ventas y período → <b>Comercial / Dueño del Data Warehouse</b>. "
    "Alta de zonas y reglas de negocio → <b>Control de Gestión</b>.")]

# ====================== 8. GLOSARIO ======================
E += [H1("8. Glosario rápido")]
E += [tabla([
    ["Término", "Significado en una línea"],
    ["ZREAL", "La descarga de gastos reales de SAP (hoja «Base Real»)."],
    ["CECO", "Centro de Costo: código de 10 caracteres que clasifica cada gasto."],
    ["OPEX", "Gastos operativos (lo que cuesta operar)."],
    ["Directo", "Gasto atribuible a un negocio puntual."],
    ["Indirecto", "Gasto compartido / de estructura."],
    ["Vertical", "Segmento: Petróleo, Minería u Otras operaciones dedicadas."],
    ["Rubro", "Tipo de gasto (Alquileres, Honorarios, Movilidad, etc.)."],
    ["Zona", "Provincia/región (posiciones 7-10 del CECO)."],
    ["Zona huérfana", "Zona que está en los datos pero no en el catálogo oficial V106."],
    ["Prorrateo", "Repartir el gasto indirecto entre los negocios con un criterio."],
    ["V106", "El diccionario maestro de códigos (CECOS_-_Resumen_y_explicacion_V106)."],
    ["Parámetro RutaArchivo", "La configuración que le dice al tablero dónde está el Excel."],
], [4.2*cm, 11.8*cm])]

# ====================== 9. PROBLEMAS COMUNES ======================
E += [H1("9. Solución de problemas comunes")]
E += [tabla([
    ["Síntoma", "Qué hacer"],
    ["Al actualizar dice que no encuentra el archivo", "Actualizá la ruta en Transformar datos → Administrar parámetros → RutaArchivo."],
    ["Los números no cambian con datos nuevos", "Asegurate de pegar el Excel nuevo con el MISMO nombre y hoja, y tocá «Actualizar»."],
    ["Un visual aparece vacío", "Verificá que el filtro (slicer) no esté excluyendo todo; limpialo."],
    ["Aparece una zona nueva sin clasificar", "Probablemente sea «huérfana»: avisá a Control de Gestión para darla de alta en V106."],
    ["Los totales parecen altos/bajos", "Revisá qué filtros están activos (Vertical, mes, Tipo) antes de leer el total."],
], [5.4*cm, 10.6*cm])]
E += [Spacer(1,10)]
E += [HRFlowable(width="100%", thickness=0.6, color=AZULC)]
E += [Spacer(1,4)]
E += [Paragraph("Documento de referencia interna. Acompaña a los archivos: validar_ceco.py, "
                "lineamientos_ceco_zreal.md, reglas_segmentacion.csv y el proyecto Tablero_ZREAL (PBIP).", st_small)]

doc = SimpleDocTemplate("Manual_Tablero_ZREAL.pdf", pagesize=A4,
                        leftMargin=2*cm, rightMargin=2*cm, topMargin=1.8*cm, bottomMargin=1.8*cm,
                        title="Manual de Procedimiento - Tablero ZREAL", author="Control de Gestión")
doc.build(E, onFirstPage=lambda c,d: None, onLaterPages=footer)
print("PDF generado: Manual_Tablero_ZREAL.pdf")
