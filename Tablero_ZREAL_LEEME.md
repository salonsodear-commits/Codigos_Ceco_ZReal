# Tablero_ZREAL — Proyecto Power BI (PBIP)

Proyecto Power BI en **formato abierto PBIP** (texto/TMDL). No es un `.pbix` binario porque
un `.pbix` sólo puede escribirlo Power BI Desktop; este formato lo abrís y lo **guardás como
`.pbix`** en un clic.

## Cómo abrirlo y convertirlo a .pbix

1. Power BI Desktop → `Archivo → Opciones → Características de versión preliminar` →
   tildá **"Guardar proyectos de Power BI (.pbip)"** (en versiones recientes ya viene activado).
2. `Archivo → Abrir → Examinar` → elegí **`Tablero_ZREAL.pbip`**.
3. **Apuntá el parámetro de ruta al Excel:** `Transformar datos → Administrar parámetros →
   `RutaArchivo`` → pegá la ruta completa a tu `Real_y_pa_2026v2.xlsx` (ej.
   `C:\Users\TuUsuario\...\Real_y_pa_2026v2.xlsx`) → `Cerrar y aplicar`.
4. Power BI refresca y carga la `Base Real` ya decodificada.
5. `Archivo → Guardar como → Archivo de Power BI (*.pbix)`. **Listo, ahí tenés tu `.pbix`.**

## Qué ya viene armado (modelo)

**Tabla `Base Real`** con columnas decodificadas en Power Query:
`CECO`, `Letra`, `NegArea`, `ProdSector`, `ZonaCECO`, `Tipologia` (Directo/Indirecto/Locación
inferida del código) y `ZonaHuerfana` (marca las 228 filas de zonas fuera del V106: 901C/902B/902C/915E/916E).

**Medidas DAX listas:**
- `OPEX Total`
- `OPEX Directo` · `OPEX Indirecto`
- `% Directo` · `% Indirecto`
- `OPEX Indirecto Transversal` (excluye sectores dedicados a OC)
- `OPEX Indirecto Dedicado OC` (N03/N10/N12/N16/C13)

## Medidas de prorrateo — agregar cuando exista la tabla de ventas

**No se incluyeron en el modelo** porque dependen de una tabla `Ventas` que todavía no existe
(la venta por UN×período es PENDIENTE DE VALIDAR con Comercial/DW) y no se inventó ningún dato.
Cuando cargues la tabla real `Ventas` (`UN`, `mes año`, `Venta`), creá estas medidas
(`Modelado → Nueva medida`):

```dax
Venta Segmento = SUM ( Ventas[Venta] )

% Incidencia UN =
DIVIDE ( [Venta Segmento], CALCULATE ( [Venta Segmento], ALL ( Ventas[UN] ) ) )

Gasto Indirecto Asignado = [OPEX Indirecto Transversal] * [% Incidencia UN]

Chequeo Cuadre Prorrateo =
SUMX ( VALUES ( Ventas[UN] ), [Gasto Indirecto Asignado] )   // debe = OPEX Indirecto Transversal
```

## Visualizaciones incluidas
El reporte ya trae **2 páginas** con visuales ligados al modelo:

**Página 1 — `Resumen OPEX`**
- Tarjetas: `OPEX Total`, `% Directo`, `% Indirecto`
- Slicer `VERTICAL`
- Columnas: OPEX por Vertical · Barras: OPEX por rubro (`Denominación de la cuenta`)
- Línea: OPEX por `mes año` · Tabla de zonas con marca `ZonaHuerfana`

**Página 2 — `Directo / Indirecto`**
- Tarjetas: `OPEX Indirecto Transversal`, `OPEX Indirecto Dedicado OC`
- Slicer `TIPO CECO`
- Matriz: Rubro (`Denominación de la cuenta`) × `VERTICAL`
- Columnas: Directo/Indirecto por Vertical (serie `TIPO CECO`)
- Tabla: `NEGOCIO/AREA` + OPEX

> Si algún visual no renderizara, el modelo está intacto: borralo y rearmalo arrastrando el
> campo, o seguí `guia_powerbi_excel.md`.

## Estructura de archivos
```
Tablero_ZREAL.pbip                     <- abrir este
Tablero_ZREAL.SemanticModel/           <- modelo (tablas, M, medidas) en TMDL
Tablero_ZREAL.Report/                  <- reporte (página en blanco)
```
