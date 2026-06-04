# Lineamientos e interconexiones CECO / ZREAL — Segmentación Operaciones Complejas (IHSA)

**Fuentes:** `CECOS_-_Resumen_y_explicacion_V106.xlsx` (diccionario maestro V106) ·
`Real_y_pa_2026v2.xlsx` → hoja `Base Real` (ZREAL).
**Alcance ejecutado:** 65.818 filas (total), ene-2023 → abr-2026.
**Fecha:** 2026-06-04. **Script reproducible:** `validar_ceco.py`.

> Todos los conteos de este documento salen de la ejecución de `validar_ceco.py` sobre el
> **total** de filas. Los números de ejemplo en el modelo de prorrateo están **rotulados como
> ilustrativos**. Lo derivado del código se distingue siempre de lo que requiere validación humana.

---

## 0. Cifras de control (verificadas sobre el total)

| Métrica | Valor |
|---|---|
| Filas `Base Real` | **65.818** |
| Monto total (`Valor/mon.inf.`) | **6.913.254.737,47** |
| `TIPO CECO` Directo / Indirecto | **4.857 / 60.961** |
| `VERTICAL` PETROLEO / MINERIA / OTRAS OP. DEDICADAS | **39.336 / 22.780 / 3.702** |
| `Sociedad` 10 / 99 | 65.113 / 705 |
| `EMPRESA` 0010 / 0099 / "SRL" | 65.036 / 705 / 77 |
| Letra CECO (pos.1) C / V | 65.113 / 705 |

Catálogos V106 cargados: NEGOCIOS=11 · PRODUCTOS=35 · ÁREAS=15 · SECTORES=189 ·
pares (Área,Sector)=190 · ZONAS=36 (unión limpia) · órdenes de LOCACIÓN=78.

---

## 1. Reglas de decodificación por tipología

El CECO tiene **10 caracteres**. La posición 1 es la letra de sociedad; las posiciones 2-10
dependen de la tipología, que se **infiere del propio código** (alta confianza):

```
Posición:        1          2-3            4-6           7-10
DIRECTO:       Letra    Negocio (NN)    Producto (NNN)   Zona      ej. C04001901A
INDIRECTO:     Letra    Área (LL)       Sector (LNN)     Zona      ej. CAFF01901A
LOCACIÓN:      Letra    "LE" fijo       L+Nº orden (LNN) Zona      ej. CLEL03901A
```

**Inferencia de tipología (regla derivada, no requiere `TIPO CECO`):**
- pos. 2-3 = `LE` → **Locación**.
- pos. 2-3 = dos dígitos `NN` → **Directo**.
- pos. 2-3 = dos letras `LL` (≠ `LE`) → **Indirecto**.

Validado contra `TIPO CECO` de origen: **0 divergencias** (C3). La base no tiene tipología
"Locación" propia; las locaciones se imputan dentro de Indirectos en `TIPO CECO`.

**Letra de sociedad (pos.1)** — hoja `Tabla Inicial CECO`:
`C`=IHSA(0010)·`E`=EMME(0060)·`M`=MARCODINA(0040)·`R`=EUROMEDIC(0020)·`V`=REPORTING(0099);
y compartiendo la letra **`C`**: ASISMIN(0070), UTE(0080), UTE ACE IOMA(0090), UMA ARG(0050).
> La letra `C` es ambigua a nivel sociedad: **la sociedad real se confirma con el campo
> `Sociedad`/`EMPRESA` del ZREAL**, no con la letra. En la base sólo aparecen letras `C` y `V`,
> ambas válidas y coherentes con `Sociedad` 10/99 (C2 = 0 incoherencias).

---

## 2. Matriz de interconexiones

`CECO → {Sociedad, Tipología, Negocio/Área, Producto/Sector, Zona} → Vertical → Unidad de Negocio`

| Eslabón | Origen | Hoja/columna fuente | Confianza |
|---|---|---|---|
| Letra → Sociedad | pos.1 + campo `Sociedad`/`EMPRESA` | `Tabla Inicial CECO`; ZREAL | **Alta** (letra C requiere campo Sociedad) |
| CECO → Tipología | pos. 2-3 (LE / NN / LL) | derivado del código | **Alta** (derivada) |
| pos. 2-3 → Negocio (directo) | catálogo | `Direct NEGOCIOS` | **Alta** (catálogo) |
| pos. 2-3 → Área (indirecto) | catálogo | `INDIRECTOS` (15 áreas) | **Alta** (catálogo) |
| pos. 4-6 → Producto (directo) | catálogo | `Direct PRODUCTOS` | **Alta** (catálogo) |
| pos. 4-6 → Sector (indirecto) | catálogo + par (Área,Sector) | `INDIRECTOS` (190 pares) | **Alta** (catálogo) |
| pos. 4-6 → Orden de locación | catálogo | `LOCACIONES` | **Alta** (catálogo) |
| pos. 7-10 → Zona | catálogo (unión 3 hojas) | `ZONAS`+`INDIRECTOS`+`LOCACIONES` | **Alta** salvo 228 filas huérfanas (ver C6) |
| CECO → Vertical | **ya resuelto en origen** | ZREAL `VERTICAL` | **Alta** (resuelto en origen) |
| Vertical → Unidad de Negocio | regla externa de negocio | PENDIENTE DE VALIDAR | **Requiere regla** |
| Sector dedicado → Vertical (N03/N10/N12/N16/C13) | regla externa | PENDIENTE DE VALIDAR | **Requiere regla** |

**Verificación de consistencia con origen (C7):** la descomposición por posiciones reproduce
`CODIGO NEGOCIO/AREA` (pos. 2-3), `CODIGO PRODUCTO/SECTOR` (pos. 4-6) y `ZONA` (pos. 7-10)
ya presentes en la base: **0 divergencias**. La decodificación de origen es consistente con V106.

**Áreas indirectas relevantes para Op. Complejas:** `NO` Nuevos Negocios Operativos
(N03 Petróleo, N10 Minería, N12 Base Cipolletti, N16 Expansión LATAM Op Complejas) y
`CM` Comercial Gral (**C13 Operaciones Complejas**). Áreas transversales (aplican a todas las UN):
`AF` Adm y Finanzas, `DH` Capital Humano, `ST` Sistemas y Tecnología, `DG` Dirección General.

---

## 3. Clasificación OPEX y naturaleza de gasto

### 3.1 Rubro OPEX consolidado — mapeo verificado **1:1**
El ZREAL ya trae el rubro OPEX consolidado en la columna **`Denominación de la cuenta`**,
derivado de `Clase de coste`. Se verificó: **cada `Clase de coste` mapea a exactamente un rubro
consolidado, 0 nulos** (mapa completo en `mapa_clase_coste_opex.csv`). Rubros y volumen:

| Rubro OPEX consolidado | Filas |
|---|---|
| BENEFICIOS AL PERSONAL | 16.323 |
| MANTENIMIENTO | 12.331 |
| MOVILIDAD Y REPRESENTACION | 10.679 |
| HONORARIOS, SERVICIOS CONTRATADOS | 6.486 |
| ALQUILERES | 5.396 |
| LIMPIEZA Y VIGILANCIA | 3.564 |
| INSUMOS DE OFICINA | 3.215 |
| SEGUROS | 3.037 |
| GASTOS DE RODADOS Y EQUIPOS | 2.453 |
| PROMOCION Y PUBLICIDAD | 1.219 |
| SERVICIOS PUBLICOS | 1.032 |
| COMISIONES | 57 |
| DEUDORES INCOBRABLES | 20 |
| **TASAS Y CONTRIBUCIONES** | 6 |

> **No mapea limpio:** `TASAS Y CONTRIBUCIONES` (6 filas) **no figura** en la lista de rubros OPEX
> consolidados del reporte; revisar si es OPEX o se excluye (coincide con `TIPO DE CUENTA = Impuestos`).

### 3.2 Costo de Servicio vs. Comercialización vs. Estructura
`RUBRO EBITDA` **no se deriva de `Clase de coste`** (15 clases caen tanto en Costo Servicio como en
Gasto Comercialización). Se deriva del **`GRUPO AREA`**:

| GRUPO AREA | RUBRO EBITDA | Filas |
|---|---|---|
| OPERATIVA | Costo Servicio | 64.744 |
| COMERCIAL | Gasto Comercialización | 1.072 |
| OPERATIVA | Gasto de Estructura y Soporte | 2 |

**Regla OPEX:** marcar OPEX cuando `TIPO DE CUENTA ∈ {GASTOS, Costo de Servicios}`; excluir
`Impuestos` y filas con `¿Son otros ingresos y egresos? = SI`. El `SUBRUBRO EBITDA` da la apertura
fina (`…Gastos operativos.` domina con 64.744 filas).

---

## 4. Directo vs. indirecto + prorrateo (núcleo)

### 4.1 Gasto directo (atribución 1:1)
CECO tipología **Directo** (4.857 filas) → atribuible unívocamente a
**Negocio + Producto + Zona + Vertical**. Pase a la UN directo, sin prorrateo (regla R17).

### 4.2 Gasto indirecto (60.961 filas)
CECO tipología **Indirecto** (Área/Sector) → **no atribuible unívocamente** a una UN. Dos sub-casos:
- **Indirecto dedicado a OC** — sectores `N03` Petróleo, `N10` Minería, `N12` Base Cipolletti,
  `N16` Expansión LATAM, `C13` Operaciones Complejas → **candidatos a tratarse como directos** a la
  Vertical pese a estar en CECO indirecto (R19, **PENDIENTE DE VALIDAR** con Control de Gestión).
- **Indirecto transversal/soporte** (`AF`, `DH`, `ST`, `DG` y demás) → requiere **prorrateo**.

### 4.3 Driver de prorrateo por incidencia de venta — **PARAMETRIZADO**
> **FUENTE DE VENTA NO DISPONIBLE en los archivos entregados.** `Real_y_pa_2026v2.xlsx` contiene
> únicamente costos/OPEX (Real vs PA); no hay tabla de ventas/ingresos por UN. El modelo queda
> parametrizado y marcado `PENDIENTE DE VALIDAR`.

Fórmula (parametrizada):

```
Para cada Unidad de Negocio (UN) i dentro del segmento S, en el período de referencia P:

    %_incidencia(i) = Venta(i, P) / Σ_j Venta(j, P)         [Σ %_incidencia = 100%]

    Gasto_indirecto_asignado(i) = %_incidencia(i) × Gasto_indirecto_transversal(S)

Validación de cuadre:  Σ_i Gasto_indirecto_asignado(i) = Gasto_indirecto_transversal(S)  (= 100%)
Redondeo: aplicar a la última UN el ajuste residual para forzar el cuadre exacto a 100%.
```

Parámetros a confirmar (placeholders):
- `Venta(i,P)` → **fuente de venta**: ⟨PENDIENTE — tabla/hoja de ventas por UN⟩.
- **Período de referencia P** → ⟨PENDIENTE — ¿mismo mes / mes anterior / acumulado?⟩.
- Segmento S → por `VERTICAL` (PETROLEO / MINERIA / OTRAS OP. DEDICADAS).

### 4.4 Ejemplo numérico — **ILUSTRATIVO (no es dato real)**
> Cifras inventadas sólo para mostrar el mecanismo de cuadre.

Gasto indirecto transversal del mes a repartir = **$100** (ilustrativo). Ventas del período
(ilustrativas): PETROLEO $600, MINERIA $300, OTRAS $100 → total $1.000.

| UN | Venta (ilustr.) | % incidencia | Gasto asignado (ilustr.) |
|---|---|---|---|
| PETROLEO | 600 | 60% | 60,00 |
| MINERIA | 300 | 30% | 30,00 |
| OTRAS | 100 | 10% | 10,00 |
| **Total** | **1.000** | **100%** | **100,00** ✔ cuadre |

### 4.5 Casos borde
- **Indirecto sin venta en el período:** definir fallback (acumulado / mes anterior / última venta) — R21.
- **UN nueva sin histórico:** driver alternativo (presupuesto, headcount) — R22.
- **Zona compartida:** un mismo gasto indirecto puede tocar varias zonas → prorratear también por zona si aplica.
- **Sectores transversales** (`AF`, `DH`, `ST`, `DG`): reparto a todas las UN por el driver.
- **Sectores dedicados a OC** (`N03`, `N10`, `C13`…): evaluar pase directo (R19).

---

## 5. Resultado de los 8 chequeos (C1-C8)

| Check | Descripción | Filas | % | Monto involucrado |
|---|---|---|---|---|
| **C1** | Longitud ≠ 10 | **0** | 0,000% | 0,00 |
| **C2** | Letra inválida o incoherente con Sociedad | **0** | 0,000% | 0,00 |
| **C3** | Tipología inferida ≠ `TIPO CECO` | **0** | 0,000% | 0,00 |
| **C4** | Negocio/Área (pos. 2-3) inexistente | **0** | 0,000% | 0,00 |
| **C5** | Producto/Sector (pos. 4-6) inexistente o sector no en Área | **0** | 0,000% | 0,00 |
| **C6** | Zona (pos. 7-10) fuera de catálogo | **228** | 0,346% | **25.330.903,23** |
| **C7** | Descomposición ≠ campos de origen | **0** | 0,000% | 0,00 |
| **C8** | Huérfanos de catálogo (informativo) | **257** | — | — |

**Detalle C6 (zonas huérfanas)** — todas con patrón válido `9NN+letra` pero **ausentes del
diccionario V106** (gap de catálogo, no error de dato):

| Zona (pos.7-10) | Filas | Monto |
|---|---|---|
| 901C | 116 | 3.724.376,25 |
| 915E | 68 | 16.511,08 |
| 902B | 33 | **21.681.370,90** |
| 916E | 9 | 6.631,00 |
| 902C | 2 | -97.986,00 |

**Detalle C8 (huérfanos a la inversa, informativo):** 257 códigos del diccionario sin uso en la base
— SECTOR 183, PRODUCTO 32, ZONA 19, ÁREA 13, NEGOCIO 10. Esperable: la base sólo contiene las
verticales de Op. Complejas, por lo que la mayoría de sectores/productos del catálogo total no aplican.

---

## 6. Validaciones pendientes (con responsable sugerido)

1. **Alta en V106 de zonas huérfanas** (`901C`, `902B`, `902C`, `915E`, `916E`) — 228 filas,
   $25,3M, con `902B` concentrando $21,7M. → **Dueño del DW / Control de Gestión.**
2. **Fuente de venta para el prorrateo** (tabla/hoja, granularidad UN×período) — bloqueante del
   núcleo de prorrateo. → **Comercial / Dueño del DW.**
3. **Período de referencia del % de incidencia** (mes / mes anterior / acumulado). → **Control de Gestión.**
4. **Regla Vertical → Unidad de Negocio** (mapeo de negocio definitivo). → **Control de Gestión.**
5. **Tratamiento de sectores dedicados a OC** (`N03`, `N10`, `N12`, `N16`, `C13`): ¿directo a la
   Vertical pese a CECO indirecto? → **Control de Gestión.**
6. **`TASAS Y CONTRIBUCIONES`** (6 filas): confirmar si es OPEX o se excluye. → **Control de Gestión.**
7. **`EMPRESA = "SRL"`** (77 filas): valor no normalizado; confirmar sociedad real. → **Dueño del DW.**

---

## 7. Archivos generados

- `validar_ceco.py` — script de validación reproducible (catálogos + C1-C8 + export).
- `validacion_ceco_excepciones.xlsx` — RESUMEN + una hoja por chequeo (C1-C8) con el detalle completo.
- `reglas_segmentacion.csv` — 23 reglas `Nombre,Condicion,Resultado,Fuente,Confianza` (aptas para M/DAX).
- `mapa_clase_coste_opex.csv` — mapeo `Clase de coste → rubro OPEX consolidado / RUBRO EBITDA` (1:1).
- `lineamientos_ceco_zreal.md` — este documento.
