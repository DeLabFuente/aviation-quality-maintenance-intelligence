# AQMI — Fase 7: Cuadros de mando de Power BI

**Documento:** `documentation/08_fase7_power_bi.md`
**Estado:** Aprobada el 19/11/2026 (primera apertura en Power BI Desktop sin errores)
**Fecha:** 18/11/2026

> AEROQ MRO es una empresa ficticia y todos sus datos son sintéticos. Los objetivos que aparecen en los cuadros de mando son **objetivos internos ficticios de AEROQ MRO**, no umbrales regulatorios. El sistema no está certificado.

---

## Índice

1. Qué se ha construido
2. Cómo llegan los datos a Power BI
3. El modelo de datos (estrella)
4. Las medidas DAX
5. Las 8 páginas
6. Identidad visual
7. Cómo se ha comprobado sin abrir Power BI
8. **Cómo abrirlo por primera vez (paso a paso)**
9. Archivos de esta fase
10. Limitaciones
11. Anexos: tablas, relaciones y catálogo de medidas

---

## 1. Qué se ha construido

| Pieza | Qué hace | Dónde está |
|---|---|---|
| **Exportación con control de calidad** | Comprueba de nuevo las 82 reglas y los controles de los indicadores. Si algo falla, no exporta nada. Si todo está bien, escribe el modelo en estrella en CSV | `scripts/export_powerbi.py`, `sql/analytics/` |
| **Datos para Power BI** | 27 tablas en CSV y una descripción de sus columnas (`_schema.json`) | `data/processed/` |
| **Proyecto de Power BI (.pbip)** | El informe completo en formato de texto: modelo, 41 relaciones, 81 medidas DAX, tema visual y 8 páginas con 144 elementos | `powerbi/` |
| **Generador del proyecto** | Crea la primera versión del proyecto a partir del modelo. No sobrescribe nunca un proyecto existente salvo que se le pida | `scripts/build_powerbi_project.py` |
| **Validador del proyecto** | Revisa el proyecto antes de abrirlo en Power BI (sección 7) | `scripts/validate_powerbi.py` |
| **Esquemas oficiales de Microsoft** | Copia de los esquemas JSON del formato de informe, para validar sin conexión | `tests/schemas/` |
| **27 pruebas nuevas** | Comprueban la exportación, el modelo y el validador | `tests/test_powerbi.py` |

El proceso completo tiene ahora 5 pasos y se ejecuta con un solo comando:

```text
1. Generar datos → 2. Validar (82 reglas) → 3. Indicadores (controles K) → 4. Exportar a Power BI → 5. Revisar el proyecto .pbip
                   si falla, se detiene     si falla, se detiene                                  si falla, se detiene
```

### Por qué un proyecto .pbip y no un archivo .pbix

Un `.pbix` es un archivo binario: GitHub no puede mostrar qué ha cambiado entre dos versiones. Un `.pbip` guarda lo mismo en archivos de texto:

- el modelo en **TMDL**: una tabla por archivo, con sus columnas y medidas DAX legibles;
- el informe en **PBIR**: un archivo JSON por página y por gráfico.

Power BI Desktop lo abre y lo guarda igual que un `.pbix`. Además:

- cada cambio queda registrado y se puede revisar en GitHub;
- se puede validar automáticamente;
- quien vea el repositorio puede leer cada medida sin instalar nada.

Esta posibilidad ya se recogía en la Fase 1 (sección 7) y la elegiste al empezar esta fase.

---

## 2. Cómo llegan los datos a Power BI

```text
 aqmi.db (SQLite)
     │  sql/analytics/*.sql   ← una consulta por tabla del modelo
     ▼
 scripts/export_powerbi.py    ← solo exporta si el control de calidad y los controles K se superan
     │
     ▼
 data/processed/*.csv         ← 27 tablas + _schema.json
     │  parámetro DataFolder (ruta de esa carpeta)
     ▼
 Power BI (modelo importado) → medidas DAX → 8 páginas
```

- **Por qué CSV y no conexión directa a SQLite.** Power BI no trae un conector para SQLite: habría que instalar un controlador ODBC en cada ordenador. Con CSV basta con abrir el proyecto. Es la decisión D5 de la Fase 1.
- **Los CSV están en el repositorio.** Así, quien descargue el proyecto puede abrir el informe sin ejecutar Python.
- **Una sola ruta que cambiar.** Power BI lee los CSV de la carpeta indicada en el parámetro `DataFolder`. Si el proyecto se mueve de carpeta, solo hay que cambiar ese parámetro (sección 8).

---

## 3. El modelo de datos (estrella)

El modelo sigue un **esquema en estrella**:

- **Tablas de hechos** (`Fact_`): los sucesos que se miden.
- **Dimensiones** (`Dim_`): los ejes por los que se filtran.

Cada hecho se relaciona directamente con sus dimensiones. Ninguna dimensión depende de otra.

```text
                      Dim_Date ─────────────┐
                          │                 │
 Dim_IncidentCategory ─ Fact_Incidents ─ Dim_Department ─ Fact_CAPA ─ Dim_Employee
                          │                 │
           Dim_Aircraft ─ Fact_MaintenanceOrders / Fact_Holds / Fact_MO_Materials ─ Dim_Material
                                                                                     │
               Dim_Supplier ─ Fact_PurchaseOrderLines ─────────────── Fact_InventoryMovements
                                                                                     │
               Dim_Document ─ Fact_DocumentVerifications / Fact_DocumentSnapshot    Fact_StockSnapshot
                                                                                     Fact_StockCounts
               Dim_KPI ─ Fact_KPI_Monthly        Fact_ValidationResults ─ Fact_ValidationFindings
```

Las decisiones de diseño:

| Decisión | Motivo |
|---|---|
| **Todas las relaciones filtran en un solo sentido** (de la dimensión al hecho) | Evita caminos ambiguos y resultados inesperados. El validador comprueba que ningún filtro llega a una tabla por dos caminos distintos |
| **El departamento del empleado se guarda como texto** en `Dim_Employee`, sin relación con `Dim_Department` | Si `Dim_Employee` se relacionara con `Dim_Department`, una acción correctiva podría filtrarse por departamento por dos caminos: el suyo y el de su responsable |
| **`Dim_Date` es una tabla de fechas marcada** | Cubre exactamente los 730 días del periodo. La fecha de corte y la tabla coinciden |
| **Relaciones inactivas** con fechas secundarias (cierre, vencimiento, fin real, fin previsto) | Una tabla solo puede tener una relación activa con `Dim_Date`. Las medidas activan la que necesitan con `USERELATIONSHIP` |
| **Tablas de foto mensual** (`*_Snapshot`) | Algunos estados del pasado, como la fecha límite vigente entonces o el stock de cada mes, se calculan una vez en SQL con la misma lógica que los indicadores de la Fase 6. Así las medidas DAX son sencillas y el resultado coincide con la consulta de referencia |
| **Las columnas se muestran con nombres legibles** (`Detected Date`) y conservan el nombre original del CSV (`detected_date`) como origen | Los gráficos y las tablas muestran nombres claros, y la trazabilidad con el CSV no se pierde |
| **Los identificadores y columnas de orden están ocultos** | Se usan para relacionar y ordenar, pero no aportan nada al usuario del informe |
| **Medidas explícitas** (opción `discourageImplicitMeasures`) | Todo número del informe sale de una medida definida y documentada. Power BI no suma columnas por su cuenta |

El detalle de las 27 tablas y las 41 relaciones está en los anexos A y B.

---

## 4. Las medidas DAX

Las 81 medidas están en la tabla `_Measures`, organizadas en carpetas:

| Carpeta | Contenido |
|---|---|
| `0. KPI Framework` | Valor de cualquier indicador, comparación con la consulta SQL (K03) y semáforo |
| `1. Quality` · `2. CAPA` · `3. Documents` · `4. Inventory` · `5. Maintenance` | Los 18 indicadores y las medidas de apoyo de cada página |
| `6. Aircraft` · `7. Audit & Data Quality` | Medidas de flota y de calidad de los datos |
| `9. Helpers` | Fecha de corte, fecha seleccionada y fecha de la foto mensual |
| `8. Lessons Learned` *(Fase 9)* | Lecciones propuestas, aprobadas, incorporadas y pendientes, y el indicador LRN-01. Con ellas el modelo tiene **87 medidas** |

### Tres patrones que conviene entender

**1. Indicadores de flujo** (lo que ocurre en un periodo). Se cuentan las filas que caen en las fechas seleccionadas. Si la fecha que importa no es la de la relación activa, se activa otra relación:

```dax
Completed Orders =
COALESCE (
    CALCULATE (
        COUNTROWS ( Fact_MaintenanceOrders ),
        USERELATIONSHIP ( Fact_MaintenanceOrders[Actual End Date], Dim_Date[Date] ),
        Fact_MaintenanceOrders[Is Cancelled] = 0,
        NOT ISBLANK ( Fact_MaintenanceOrders[Actual End Date] )
    ),
    0
)
```

**2. Indicadores de foto** (un estado en una fecha). Se calcula la última fecha seleccionada (`Selected Date`, nunca posterior a la fecha de corte) y se mide el estado en ese momento. Se quita el filtro de fechas para que cuenten también las incidencias detectadas antes del periodo elegido:

```dax
Open Non-Conformities =
VAR _d = [Selected Date]
RETURN
    COALESCE (
        CALCULATE (
            COUNTROWS ( Fact_Incidents ),
            REMOVEFILTERS ( Dim_Date ),
            Fact_Incidents[Is Cancelled] = 0,
            Fact_Incidents[Detected Date] <= _d,
            ISBLANK ( Fact_Incidents[Closed Date] ) || Fact_Incidents[Closed Date] > _d
        ),
        0
    )
```

**3. Porcentajes con `DIVIDE`.** Si el denominador es cero, `DIVIDE` devuelve un valor vacío: el informe muestra "sin datos", nunca 0 %. Es la regla K02 de la Fase 6. Los porcentajes se guardan como proporción (0,944) con formato `0.0%`.

### El control K03 está dentro del informe

La página **Audit & Traceability** incluye una tabla que compara, para cada indicador:

- el valor calculado por la consulta SQL de referencia (Fase 6);
- el valor calculado por las medidas DAX.

Ambos deben coincidir en los 18 indicadores (`✔ Match`). Es la regla K03, que quedó pendiente en la Fase 6. Es la prueba de que los cuadros de mando muestran exactamente lo que define la documentación. La revisaremos juntos en tu primera apertura (sección 8) y quedará registrada en la Fase 9.

---

## 5. Las 8 páginas

Todas las páginas comparten la misma estructura, para que la navegación sea predecible:

```text
┌──────────┬─────────────────────────────────────────────────────────────┐
│  AQMI    │  Título de la página                       [Filtro] [Filtro] │
│          │  Subtítulo · fecha de los datos                              │
│ ▸ Página │ ┌─────────────────────────────────────────────────────────┐ │
│   Página │ │  5 tarjetas KPI                                          │ │
│   Página │ └─────────────────────────────────────────────────────────┘ │
│   ...    │ ┌───────────────────────────────┐ ┌───────────────────────┐ │
│          │ │  Gráfico principal (tendencia) │ │  Desglose             │ │
│          │ └───────────────────────────────┘ └───────────────────────┘ │
│          │ ┌─────────────────────────────────────────────────────────┐ │
│ Datos    │ │  Tabla de detalle o segundo análisis                     │ │
│ sintét.  │ └─────────────────────────────────────────────────────────┘ │
└──────────┴─────────────────────────────────────────────────────────────┘
```

| Página | Tarjetas KPI | Gráficos y tablas | Qué pregunta responde |
|---|---|---|---|
| **Executive Overview** | NC abiertas · acciones vencidas · cumplimiento documental · disponibilidad de stock · órdenes en plazo | No conformidades por mes y tasa por 100 órdenes · **tabla de los 18 indicadores con semáforo** · no conformidades abiertas | ¿Cómo está la empresa y dónde hay que actuar? |
| **Quality Performance** | Total NC · abiertas · tasa · tiempo de resolución · cobertura del análisis de causa raíz | NC por mes y gravedad · Pareto por categoría · tiempo de resolución por departamento · causas raíz (Ishikawa 6M) | ¿Qué falla, con qué gravedad y por qué? |
| **Corrective Actions** | Pendientes de implantar · correctivas vencidas · cierre en plazo · eficacia · replanificadas | Acciones por estado y tipo · evolución de la cartera pendiente · tabla de acciones abiertas | ¿Se cumplen los compromisos de corrección? |
| **Document Control** | Cumplimiento · caducados · tasa de errores · trazabilidad · verificaciones | Cumplimiento y caducados por mes · discrepancias por tipo de verificación · documentos caducados | ¿Está la documentación al día y es correcta? |
| **Materials & Inventory** | Disponibilidad · bajo mínimo · exactitud · faltas · pedidos pendientes | Exactitud y faltas por mes · puntualidad por proveedor · materiales bajo mínimo | ¿Hay material cuando se necesita? |
| **Maintenance Production** | Órdenes abiertas · en plazo · retraso medio · bloqueadas por material y por documentación | Órdenes completadas y % en plazo · **impacto de las faltas de material** · órdenes bloqueadas | ¿Se cumplen las fechas y qué lo impide? |
| **Aircraft Overview** | Flota · en mantenimiento · órdenes · % no programado · no conformidades | Órdenes por aeronave y tipo · evolución mensual (filtrable por aeronave) · comparativa de la flota | ¿Qué aeronave da más trabajo y por qué? |
| **Audit & Traceability** | Data Quality Score · reglas ejecutadas · fallos críticos · sembradas detectadas · eventos de auditoría | **Historial de cualquier registro** · **K03: Power BI = SQL** · hallazgos de validación | ¿Son fiables los datos y quién hizo qué? |

**Filtros.** Casi todas las páginas tienen un filtro de periodo (año 1 / año 2) y un filtro propio de la página (departamento, tipo de documento, clase de material, tipo de mantenimiento o aeronave). Con el filtro de periodo:

- los indicadores de flujo cuentan lo ocurrido en ese año;
- los de foto muestran el estado al final de ese año.

**Las tablas de detalle "a la fecha de corte"** (abiertas, caducadas, bloqueadas) muestran siempre la situación del 31/10/2026, porque son listas de trabajo, no análisis históricos. Su subtítulo lo indica.

**Historial de un registro.** En Audit & Traceability, elige un registro en el filtro *Record* (por ejemplo `NC-2025-0021` o `WO-2025-0125`). La tabla mostrará todo su historial: creación, cada cambio de estado, quién lo hizo y cuándo. Es el módulo F funcionando sobre el registro de auditoría.

---

## 6. Identidad visual

| Uso | Color | Código |
|---|---|---|
| Barra lateral, valores de las tarjetas, cabeceras de tabla | Azul marino | `#0B1F3A` |
| Página activa, barras, acentos | Azul aeronáutico | `#1F6FB2` |
| Series secundarias | Azul claro | `#7FA7D6` |
| Texto | Gris antracita | `#1E2A3B` |
| Texto secundario | Gris | `#5B6577` |
| Fondo del lienzo | Gris muy claro | `#F3F5F8` |
| Estado correcto | Verde | `#2E7D32` |
| Advertencia | Ámbar | `#D99A00` |
| Crítico | Rojo | `#C62828` |

Los criterios aplicados:

- **Tipografía:** Segoe UI, la de Windows y Power BI. Es legible y no necesita instalar nada.
- **El color tiene significado.** Verde, ámbar y rojo se reservan para el semáforo de los indicadores, y nunca se usan como decoración.
- **Cada página tiene como máximo 5 tarjetas y 4 gráficos o tablas**, con el mismo esquema en todas. Una pantalla sobrecargada esconde lo importante.
- **El tema está en un archivo** (`AQMI_Theme.json`). Cambiar un color en el tema lo cambia en todo el informe.
- **La advertencia de datos sintéticos** aparece en la barra lateral de todas las páginas.

---

## 7. Cómo se ha comprobado sin abrir Power BI

No puedo ejecutar Power BI Desktop en mi entorno de trabajo. Por eso he comprobado todo lo que se puede comprobar sin él:

| Comprobación | Qué detecta | Resultado |
|---|---|---|
| **Esquemas oficiales de Microsoft** | Cualquier propiedad mal escrita o en un sitio incorrecto en los archivos del informe | 156 archivos válidos |
| **Sintaxis TMDL** | Tablas, columnas, tipos, columnas de orden, particiones y sangría | Sin errores |
| **Columnas = cabecera del CSV** | Que cada tabla lee exactamente las columnas de su archivo | 27 de 27 |
| **Referencias DAX** | Que cada `Tabla[Columna]` y cada `[Medida]` usada existe, y que paréntesis y comillas están equilibrados | 81 medidas sin errores |
| **Relaciones** | Columnas existentes, una sola relación activa entre dos tablas, sin caminos de filtro ambiguos | 41 relaciones correctas |
| **Campos de los gráficos** | Que cada campo de cada gráfico existe en el modelo, con el tipo correcto (columna o medida) | 144 elementos correctos |
| **Navegación y posiciones** | Que los botones apuntan a páginas que existen y nada se sale de la página ni se solapa | Correcto |
| **Reproducción de los 18 KPI desde los CSV** | Que el modelo en estrella contiene todo lo necesario y que los filtros de las medidas dan el valor de la consulta SQL | 18 de 18 iguales |

**Pruebas negativas.** El validador se ha probado estropeando el proyecto a propósito de 8 formas distintas. Las 8 se detectan:

- una columna mal escrita en una medida;
- una medida que no existe;
- una medida inexistente en un gráfico;
- una propiedad no permitida;
- dos relaciones activas entre las mismas tablas;
- un botón hacia una página que no existe;
- una columna que no coincide con el CSV;
- un JSON roto.

**Lo que solo puede comprobarse en Power BI:**

- que cada medida DAX calcula lo esperado (el control K03 lo muestra en la propia página de auditoría);
- que el aspecto final es el previsto (algún formato puede necesitar un retoque manual).

---

## 8. Cómo abrirlo por primera vez (paso a paso)

### Paso 0 — Requisitos

- **Power BI Desktop** reciente (2025 o 2026). Para ver la versión: *Ayuda → Acerca de*.
- Los archivos de esta fase en tu carpeta del proyecto. Ya están copiados, incluidos los CSV de `data\processed\`.

### Paso 1 — Comprobar las opciones de vista previa (solo si aparecen)

En Power BI Desktop: **Archivo → Opciones y configuración → Opciones → Características en versión preliminar**.

Si en la lista aparece alguna de estas opciones, márcala y reinicia Power BI Desktop:

- *Opción de guardar proyectos de Power BI (.pbip)*
- *Almacenar informes con el formato de metadatos mejorado (PBIR)*
- *Almacenar el modelo semántico con el formato TMDL*

En las versiones recientes estas funciones ya son estándar y no aparecen en la lista. En ese caso no hay que hacer nada.

### Paso 2 — Abrir el proyecto

En el Explorador de archivos, entra en `<carpeta del proyecto>\powerbi\` y haz doble clic en **`AQMI.pbip`**. También se puede abrir desde Power BI Desktop: *Archivo → Abrir → Examinar* y elegir `AQMI.pbip`.

### Paso 3 — Cargar los datos

La primera vez el informe aparece sin datos, porque el proyecto guarda la estructura pero no los datos. Pulsa **Inicio → Actualizar**. Tarda unos segundos: son 27 tablas pequeñas.

Si aparece un error de que no se encuentra un archivo, revisa la ruta de los datos:

1. Ve a *Inicio → Transformar datos → Editar parámetros*.
2. Comprueba que `DataFolder` es `<carpeta del proyecto>\data\processed\`. Debe terminar en `\`.
3. Pulsa *Aceptar → Aplicar cambios*.

### Paso 4 — Comprobar el control K03

1. Ve a la página **Audit & Traceability**, con los botones de la izquierda.
2. En la tabla *K03 · Power BI vs SQL reference*, las 18 filas deben mostrar **✔ Match**.
3. Recorre después las 8 páginas.

### Paso 5 — Guardar

Pulsa **Archivo → Guardar**. Power BI guarda en el mismo formato `.pbip` y crea unas carpetas `.pbi` con datos locales, que el `.gitignore` excluye de GitHub.

### Qué contarme después de abrirlo

Este primer arranque es la parte de la fase que solo puedes hacer tú. Cuéntame:

1. Si el proyecto se abrió o dio algún mensaje de error (copia el texto o haz una captura).
2. Si la actualización de datos terminó bien.
3. Cuántas filas de la tabla K03 muestran `✔ Match`.
4. Qué gráficos muestran un error o no se ven como esperabas (una captura de la página es lo más útil).

Con eso corregimos juntos lo que haga falta antes de cerrar la fase.

### Resultado de la primera apertura (19/11/2026)

El proyecto se abrió y se actualizó en Power BI Desktop sin errores, y se aprobó la fase. Al guardarlo, Power BI Desktop reescribió los archivos en su propio formato:

- añadió un identificador `lineageTag` a cada tabla, columna y medida;
- creó `definition/cultures/en-US.tmdl` (sinónimos para preguntas en lenguaje natural) y `diagramLayout.json` (posición de las tablas en la vista de modelo);
- subió el nivel de compatibilidad del modelo de 1601 a 1606.

Desde ese momento, **la versión de referencia es la guardada por Power BI Desktop**, no la generada por el script. El validador se ajustó para aceptar las propiedades que añade Power BI, y una prueba nueva comprueba en cada ejecución que el proyecto guardado en el repositorio sigue pasando todos los controles.

---

## 9. Archivos de esta fase

Todos están en la carpeta del proyecto.

| Archivo o carpeta | Novedad |
|---|---|
| `sql/analytics/*.sql` | Nuevos: 22 consultas, una por tabla del modelo en estrella |
| `scripts/export_powerbi.py` | Nuevo: exportación protegida por el control de calidad |
| `scripts/build_powerbi_project.py` | Nuevo: generador del proyecto `.pbip` (modelo, medidas, páginas y tema) |
| `scripts/validate_powerbi.py` | Nuevo: validador del proyecto |
| `scripts/run_pipeline.py` | Actualizado: pasos 4 y 5 |
| `config/settings.py` | Actualizado: rutas de Power BI |
| `data/processed/` | Nuevo: 27 CSV y `_schema.json` |
| `powerbi/AQMI.pbip` | Nuevo: **el archivo que se abre en Power BI** |
| `powerbi/AQMI.SemanticModel/` | Nuevo: el modelo (TMDL): 28 tablas, 41 relaciones, 81 medidas |
| `powerbi/AQMI.Report/` | Nuevo: el informe (PBIR): tema y 8 páginas |
| `tests/test_powerbi.py` | Nuevo: 27 pruebas |
| `tests/schemas/` | Nuevo: esquemas oficiales de Microsoft (licencia MIT) |
| `documentation/08_fase7_power_bi.md` | Este documento |
| `README.md` | Actualizado |

### Cómo comprobarlo desde PowerShell

En PowerShell, desde la carpeta del proyecto y con el entorno virtual activado:

```powershell
python scripts/run_pipeline.py
```

Al final deben aparecer:

```text
INFO    | STEP 4/5 — Export the star schema for Power BI
...
INFO    | EXPORT OK
INFO    | STEP 5/5 — Check the Power BI project
INFO    | Model: 28 tables, 334 columns, 81 measures
INFO    | Report: 8 pages, 144 visuals; JSON files checked against official schemas: 154
INFO    | POWER BI PROJECT OK
INFO    | PIPELINE OK
```

```powershell
pytest -v
```

Resultado esperado: **`133 passed`** (151 desde la Fase 8, que añade sus propias pruebas).

Para revisar solo el proyecto de Power BI, por ejemplo después de editarlo en Power BI Desktop:

```powershell
python scripts/validate_powerbi.py
```

> **Importante.** Si modificas el informe en Power BI Desktop, no vuelvas a ejecutar `build_powerbi_project.py --force`: regeneraría el proyecto y perderías tus cambios. Sin `--force`, el script se niega a sobrescribirlo.

---

## 10. Limitaciones

| Limitación | Consecuencia |
|---|---|
| El proyecto se ha generado sin abrir Power BI | El formato, los nombres de campos y la sintaxis están validados, pero el cálculo real de cada medida DAX se confirma en Power BI (control K03, sección 8) |
| Algunas opciones de formato no están cubiertas por el esquema oficial (por ejemplo, el texto de los botones) | Si alguna no se aplica, el elemento se verá con el formato del tema y habrá que retocarlo a mano |
| La ruta de los datos es absoluta | Si el proyecto se mueve de carpeta o lo abre otra persona, hay que cambiar el parámetro `DataFolder` (sección 8, paso 3) |
| Los filtros de periodo distinguen año 1 y año 2 | Para análisis mensuales, los gráficos de tendencia ya muestran los 24 meses. Se pueden añadir filtros más finos en Power BI Desktop |
| Las tablas de detalle muestran la situación a la fecha de corte | Son listas de trabajo. Los gráficos de tendencia dan la evolución |
| La comparación K03 se hace sobre el periodo completo | El valor SQL de referencia es el del periodo completo. Con un filtro de periodo activo, los valores no son comparables |
| Datos sintéticos | Los cuadros de mando demuestran la capacidad de análisis del sistema, no describen una empresa real |

---

## 11. Anexos

### Anexo A — Tablas del modelo

| Tabla | Filas | Contenido |
|---|---|---|
| `Dim_Date` | 730 | Calendar of the simulated period (01/11/2024 - 31/10/2026). Marked as date table. |
| `Dim_Department` | 6 | The six departments of AEROQ MRO. |
| `Dim_Employee` | 46 | Employees (department kept as text to avoid ambiguous relationship paths). |
| `Dim_Aircraft` | 12 | The fleet: aircraft, customer and operational status at the cut-off date. |
| `Dim_Material` | 100 | Material catalogue. |
| `Dim_Supplier` | 40 | Suppliers and their approval status at the cut-off date. |
| `Dim_Document` | 250 | Controlled documents and records, with their current revision and validity. |
| `Dim_IncidentCategory` | 8 | Categories of non-conformity. |
| `Fact_Incidents` | 143 | One row per non-conformity. |
| `Fact_CAPA` | 165 | One row per corrective or preventive action. |
| `Fact_CAPA_Snapshot` | 212 | Actions not yet implemented at each month end (periodic snapshot). |
| `Fact_MaintenanceOrders` | 491 | One row per work order. |
| `Fact_Holds` | 93 | One row per work-order hold (material or documentation). |
| `Fact_MO_Materials` | 1.188 | One row per material line required by a work order. |
| `Fact_InventoryMovements` | 3.695 | One row per stock movement. |
| `Fact_StockSnapshot` | 2.400 | Stock of each active material at each month end, by state (periodic snapshot). |
| `Fact_StockCounts` | 516 | One row per stock count. |
| `Fact_PurchaseOrderLines` | 341 | One row per purchase order line. |
| `Fact_PO_Snapshot` | 119 | Purchase orders pending at each month end (periodic snapshot). |
| `Fact_DocumentVerifications` | 808 | One row per verification of a document or record. |
| `Fact_DocumentSnapshot` | 5.136 | Controlled documents in force at each month end (periodic snapshot). |
| `Fact_AuditEvents` | 17.383 | The audit trail: one row per recorded change. |
| `Dim_KPI` | 18 | The 18 indicators: definition, fictitious internal target and SQL reference value. |
| `Fact_KPI_Monthly` | 432 | Monthly KPI values as calculated by the SQL reference queries. |
| `Fact_ValidationResults` | 82 | Result of each of the 82 validation rules. |
| `Fact_ValidationFindings` | 26 | Records flagged by the validation rules. |
| `Model_Info` | 1 | One row: cut-off date, quality gate status and disclaimer. |

### Anexo B — Relaciones

Todas son de varios a uno y filtran en un solo sentido (de la dimensión al hecho).

| Desde (lado varios) | Hacia (lado uno) | Activa |
|---|---|---|
| Fact_Incidents[Detected Date] | Dim_Date[Date] | Sí |
| Fact_Incidents[Closed Date] | Dim_Date[Date] | No (USERELATIONSHIP) |
| Fact_Incidents[Category ID] | Dim_IncidentCategory[Category ID] | Sí |
| Fact_Incidents[Responsible Department ID] | Dim_Department[Department ID] | Sí |
| Fact_Incidents[Aircraft ID] | Dim_Aircraft[Aircraft ID] | Sí |
| Fact_Incidents[Owner ID] | Dim_Employee[Employee ID] | Sí |
| Fact_CAPA[Created Date] | Dim_Date[Date] | Sí |
| Fact_CAPA[Due Date] | Dim_Date[Date] | No (USERELATIONSHIP) |
| Fact_CAPA[Department ID] | Dim_Department[Department ID] | Sí |
| Fact_CAPA[Responsible ID] | Dim_Employee[Employee ID] | Sí |
| Fact_CAPA_Snapshot[Department ID] | Dim_Department[Department ID] | Sí |
| Fact_CAPA_Snapshot[Responsible ID] | Dim_Employee[Employee ID] | Sí |
| Fact_MaintenanceOrders[Opened Date] | Dim_Date[Date] | Sí |
| Fact_MaintenanceOrders[Planned End Date] | Dim_Date[Date] | No (USERELATIONSHIP) |
| Fact_MaintenanceOrders[Actual End Date] | Dim_Date[Date] | No (USERELATIONSHIP) |
| Fact_MaintenanceOrders[Aircraft ID] | Dim_Aircraft[Aircraft ID] | Sí |
| Fact_MaintenanceOrders[Responsible Department ID] | Dim_Department[Department ID] | Sí |
| Fact_Holds[Start Date] | Dim_Date[Date] | Sí |
| Fact_Holds[Aircraft ID] | Dim_Aircraft[Aircraft ID] | Sí |
| Fact_Holds[Material ID] | Dim_Material[Material ID] | Sí |
| Fact_MO_Materials[Required By Date] | Dim_Date[Date] | Sí |
| Fact_MO_Materials[Material ID] | Dim_Material[Material ID] | Sí |
| Fact_MO_Materials[Aircraft ID] | Dim_Aircraft[Aircraft ID] | Sí |
| Fact_InventoryMovements[Movement Date] | Dim_Date[Date] | Sí |
| Fact_InventoryMovements[Material ID] | Dim_Material[Material ID] | Sí |
| Fact_StockSnapshot[Material ID] | Dim_Material[Material ID] | Sí |
| Fact_StockCounts[Count Date] | Dim_Date[Date] | Sí |
| Fact_StockCounts[Material ID] | Dim_Material[Material ID] | Sí |
| Fact_PurchaseOrderLines[Order Date] | Dim_Date[Date] | Sí |
| Fact_PurchaseOrderLines[Supplier ID] | Dim_Supplier[Supplier ID] | Sí |
| Fact_PurchaseOrderLines[Material ID] | Dim_Material[Material ID] | Sí |
| Fact_PO_Snapshot[Supplier ID] | Dim_Supplier[Supplier ID] | Sí |
| Fact_DocumentVerifications[Verification Date] | Dim_Date[Date] | Sí |
| Fact_DocumentVerifications[Document ID] | Dim_Document[Document ID] | Sí |
| Fact_DocumentVerifications[Verified By] | Dim_Employee[Employee ID] | Sí |
| Fact_DocumentSnapshot[Document ID] | Dim_Document[Document ID] | Sí |
| Fact_DocumentSnapshot[Owner Department ID] | Dim_Department[Department ID] | Sí |
| Fact_AuditEvents[Event Date] | Dim_Date[Date] | Sí |
| Fact_AuditEvents[Changed By] | Dim_Employee[Employee ID] | Sí |
| Fact_KPI_Monthly[KPI ID] | Dim_KPI[KPI ID] | Sí |
| Fact_ValidationFindings[Rule ID] | Fact_ValidationResults[Rule ID] | Sí |

### Anexo C — Catálogo de medidas

La fórmula DAX completa de cada medida está en `powerbi/AQMI.SemanticModel/definition/tables/_Measures.tmdl`, con esta misma descripción encima.

| Carpeta | Medida | Formato | Qué calcula |
|---|---|---|---|
| 0. KPI Framework | KPI Value (Power BI) | `0.0` | Value of the KPI selected in Dim_KPI, calculated by the DAX measures (percentages as 0-100). |
| 0. KPI Framework | KPI Value (SQL) | `0.0` | Value of the KPI for the whole period, from its SQL reference query (Phase 6). |
| 0. KPI Framework | KPI Reconciliation | `texto` | Rule K03: the Power BI value must equal the SQL reference value (whole period, no filters). |
| 0. KPI Framework | KPI Status | `texto` | Traffic light against the fictitious internal target of AEROQ MRO. |
| 0. KPI Framework | KPI Status Color | `texto` | Colour of the traffic light (used by conditional formatting). |
| 0. KPI Framework | KPI Status Label | `texto` | Traffic light as text. |
| 0. KPI Framework | KPI Display Value | `texto` | KPI value formatted with its unit. |
| 1. Quality | Total Quality Incidents | `#,0` | QUA-01. Non-conformities detected in the period (cancelled excluded). |
| 1. Quality | Open Non-Conformities | `#,0` | QUA-02. Non-conformities open at the end of the selected period. |
| 1. Quality | Non-Conformity Rate | `0.0` | QUA-03. Non-conformities per 100 work orders completed. |
| 1. Quality | Non-Conformities Closed | `#,0` | Non-conformities closed in the period (by closing date). |
| 1. Quality | Resolution Days (Sum) | `#,0` | Sum of the days to close the non-conformities closed in the period. |
| 1. Quality | Average Resolution Time | `0.0` | QUA-05. Average days from detection to closure. |
| 1. Quality | RCA Coverage (Critical & Major) | `0.0%` | Share of critical and major non-conformities with a root-cause analysis. |
| 1. Quality | Analysed Non-Conformities | `#,0` | Non-conformities with an Ishikawa (6M) root cause. |
| 1. Quality | Open NC Age (days) | `#,0` | Age in days of each non-conformity open at the cut-off date. |
| 2. CAPA | Corrective Actions Due | `#,0` | Corrective actions whose due date falls in the period. |
| 2. CAPA | Corrective Actions Due On Time | `#,0` | Of the actions due in the period, those implemented by their due date. |
| 2. CAPA | Corrective Action Closure Rate | `0.0%` | QUA-04. Corrective actions implemented by their due date. |
| 2. CAPA | Overdue Corrective Actions | `#,0` | QUA-06. Corrective actions past their due date (as it was then) and not implemented, at the snapshot date. |
| 2. CAPA | Actions Pending Implementation | `#,0` | Corrective and preventive actions not yet implemented at the snapshot date. |
| 2. CAPA | Actions Created | `#,0` | Actions created in the period (cancelled excluded). |
| 2. CAPA | Effectiveness Rate | `0.0%` | Of the actions whose effectiveness was verified, share found effective. |
| 2. CAPA | Rescheduled Actions | `#,0` | Actions whose due date was extended at least once. |
| 2. CAPA | Open Action Days Overdue | `#,0` | Days overdue of each open action at the cut-off date (0 = within its due date). |
| 2. CAPA | Open Action Progress | `0%` | Latest progress reported for each open action. |
| 3. Documents | Controlled Documents In Force | `#,0` | Controlled documents with a revision in force at the snapshot date. |
| 3. Documents | Compliant Documents | `#,0` | Controlled documents within their review date at the snapshot date. |
| 3. Documents | Document Compliance Rate | `0.0%` | DOC-01. Controlled documents within their review date. |
| 3. Documents | Expired Documents | `#,0` | DOC-03. Controlled documents past their review date at the snapshot date. |
| 3. Documents | Routine Verifications | `#,0` | Document and record checks, internal audits excluded. |
| 3. Documents | Routine Verification Discrepancies | `#,0` | Routine checks that found a discrepancy. |
| 3. Documents | Documentation Error Rate | `0.0%` | DOC-02. Routine checks that found a discrepancy. |
| 3. Documents | Discrepancy Rate (All Verifications) | `0.0%` | Verifications with a discrepancy, all types (for the breakdown by type). |
| 3. Documents | Material Issues | `#,0` | Material issued to work orders. |
| 3. Documents | Traceable Issues | `#,0` | Issues with work order, lot, serial number and certificate where required. |
| 3. Documents | Traceability Compliance | `0.0%` | DOC-04. Issues with complete traceability data. |
| 3. Documents | Expired Document Days Overdue | `#,0` | Days past the review date of each expired document (cut-off date). |
| 4. Inventory | Cycle Counts | `#,0` | Cycle counts made in the period (opening counts excluded). |
| 4. Inventory | Accurate Counts | `#,0` | Cycle counts that matched the stock recorded in the system. |
| 4. Inventory | Inventory Accuracy | `0.0%` | INV-01. Cycle counts that matched the system. |
| 4. Inventory | Active Materials | `#,0` | Active materials at the snapshot date. |
| 4. Inventory | Materials Below Minimum | `#,0` | Active materials with available stock below their minimum. |
| 4. Inventory | Stock Availability | `0.0%` | INV-02. Active materials with available stock at or above their minimum. |
| 4. Inventory | Material Lines Required | `#,0` | Material lines of work orders required in the period. |
| 4. Inventory | Material Lines Short | `#,0` | Material lines not available on the required date. |
| 4. Inventory | Material Shortage Rate | `0.0%` | INV-03. Material lines not available on the required date. |
| 4. Inventory | Pending Purchase Orders | `#,0` | INV-04. Purchase orders sent and not fully received at the snapshot date. |
| 4. Inventory | Available Qty (Below Minimum) | `#,0.##` | Available stock of the materials below their minimum. |
| 4. Inventory | Minimum Stock (Below Minimum) | `#,0.##` | Minimum stock of the materials below their minimum. |
| 4. Inventory | In Receiving Inspection (Below Minimum) | `#,0.##` | Stock in receiving inspection of the materials below their minimum. |
| 4. Inventory | PO Lines Received | `#,0` | Purchase order lines fully received (by order date). |
| 4. Inventory | PO Lines On Time | `#,0` | Lines fully received on or before the promised date. |
| 4. Inventory | On-Time Delivery Rate | `0.0%` | Supplier lines received on time (complement to the KPIs). |
| 5. Maintenance | Orders Opened | `#,0` | Work orders opened in the period (cancelled excluded). |
| 5. Maintenance | Completed Orders | `#,0` | Work orders completed in the period (by actual end date). |
| 5. Maintenance | Orders Due | `#,0` | Work orders planned to finish in the period. |
| 5. Maintenance | Orders Due On Time | `#,0` | Of the orders due in the period, those completed by the planned date. |
| 5. Maintenance | Maintenance Order Completion Rate | `0.0%` | MNT-01. Work orders completed by the planned date. |
| 5. Maintenance | Delay Days (Sum) | `#,0` | Sum of the days of delay of the orders completed in the period. |
| 5. Maintenance | Average Maintenance Delay | `0.0` | MNT-02. Average days of delay of completed orders (on time = 0). |
| 5. Maintenance | Open Work Orders | `#,0` | Work orders open at the end of the selected period. |
| 5. Maintenance | Work Orders Blocked by Material | `#,0` | MNT-03. Work orders stopped by a material hold at the end of the selected period. |
| 5. Maintenance | Work Orders Blocked by Documentation | `#,0` | MNT-04. Work orders stopped by a documentation hold at the end of the selected period. |
| 5. Maintenance | On-Time Rate (Completed Orders) | `0.0%` | Completed orders that finished by the planned date. |
| 5. Maintenance | Active Hold Days | `#,0` | Days each active hold has lasted at the cut-off date. |
| 5. Maintenance | Material Hold Days (Total) | `#,0` | Days work orders opened in the period spent stopped by material. |
| 5. Maintenance | Unscheduled Share | `0.0%` | Share of work orders that were unscheduled. |
| 6. Aircraft | Fleet Size | `#,0` | Aircraft in the selection. |
| 6. Aircraft | Aircraft In Maintenance | `#,0` | Aircraft with an open work order at the cut-off date. |
| 7. Audit & Data Quality | Audit Events | `#,0` | Changes recorded in the audit trail. |
| 7. Audit & Data Quality | Audit Events (Label) | text | Audit Events as text (17,383): the new card visual abbreviates numbers (17K) whatever the format string. Added in Phase 8. |
| 7. Audit & Data Quality | Data Quality Score (Rules Passed) | `0.0%` | Validation rules passed / rules executed (Phase 5). |
| 7. Audit & Data Quality | Validation Rules Executed | `#,0` | Validation rules executed. |
| 7. Audit & Data Quality | Critical Rule Failures | `#,0` | CRITICAL validation rules with findings (must be 0). |
| 7. Audit & Data Quality | Planted Discrepancies Detected | `texto` | Discrepancies planted on purpose by the generator and detected by the rules. |
| 7. Audit & Data Quality | Validation Findings | `#,0` | Records flagged by the WARNING rules. |
| 9. Helpers | Cut-off Date | `dd mmm yyyy` | Cut-off date of the data (31/10/2026). |
| 9. Helpers | Selected Date | `dd mmm yyyy` | Last date of the period selected in the report, never later than the cut-off date. |
| 9. Helpers | Snapshot Month End | `dd mmm yyyy` | Last month end on or before the selected date: the date at which 'state' KPIs are measured. |
| 9. Helpers | Data As Of Label | `texto` | Subtitle shown on every page. |
