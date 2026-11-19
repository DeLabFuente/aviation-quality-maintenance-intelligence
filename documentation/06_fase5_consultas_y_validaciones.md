# AQMI — Fase 5: Consultas SQL y validaciones

**Documento:** `documentation/06_fase5_consultas_y_validaciones.md`
**Estado:** Aprobada el 17/11/2026
**Fecha:** 17/11/2026

> AEROQ MRO es una empresa ficticia y todos sus datos son sintéticos. Las reglas de este documento son **reglas de negocio internas del proyecto**, no requisitos normativos. El sistema no está certificado ni demuestra el cumplimiento de ninguna norma.

---

## Índice

1. Qué se ha construido
2. Las vistas: los cálculos, en un solo sitio
3. Las 82 reglas de validación
4. El control de calidad de los datos (quality gate)
5. Las discrepancias sembradas: la prueba de que el control funciona
6. Resultado de la validación
7. Las 8 consultas de negocio
8. Las pruebas automáticas
9. Archivos de esta fase
10. Cómo comprobar que funciona
11. Cambios y correcciones durante esta fase
12. Limitaciones

---

## 1. Qué se ha construido

En la Fase 4 la base de datos se llenó con 24 meses de actividad simulada. En esta fase se construye **el control de esos datos**, igual que lo haría una oficina de calidad:

| Pieza | Qué hace | Dónde está |
|---|---|---|
| **13 vistas SQL** | Calculan los valores derivados (stock por estado, retrasos, vigencia de documentos, plazos vencidos…) sin guardarlos en las tablas | `sql/views/` |
| **82 reglas de validación** | Una consulta por regla de negocio. Cada una devuelve los registros que la incumplen | `sql/validation/` |
| **Validador** | Ejecuta las 82 reglas, escribe el informe y decide si los datos pueden pasar a Power BI | `scripts/run_validations.py` |
| **Pipeline** | Ejecuta todo el proceso con un solo comando | `scripts/run_pipeline.py` |
| **Informe de validación** | Resultado legible y dos CSV para Excel | `reports/` |
| **8 consultas de negocio** | Responden a preguntas típicas de la oficina | `sql/queries/` |
| **24 pruebas nuevas** | Comprueban que el control detecta los errores, también los provocados a propósito | `tests/test_validations.py` |

La idea central de esta fase: **el proyecto se controla a sí mismo**. Antes de que un dato llegue a un cuadro de mando, tiene que superar las mismas comprobaciones que se harían en una oficina de calidad real: comprobar la información frente a su origen, detectar incoherencias y documentar lo que se encuentra.

---

## 2. Las vistas: los cálculos, en un solo sitio

Una **vista** es una consulta guardada con nombre, que se usa como si fuera una tabla. No ocupa espacio: se calcula cada vez que se consulta, así que nunca está desactualizada.

En el diseño (Fase 2) se decidió **no guardar valores derivados** en las tablas. Por ejemplo, el stock disponible no se guarda: se calcula sumando los movimientos. Las vistas son el lugar donde se hacen esos cálculos, una sola vez, para que las consultas, los indicadores (Fase 6) y Power BI (Fase 7) usen **la misma definición**.

| Archivo | Vista | Qué calcula |
|---|---|---|
| `00_vw_parameters.sql` | `vw_parameters` | Fecha de corte y fecha de inicio del periodo, leídas de `System_Parameters` |
| `01_vw_po_line_status.sql` | `vw_po_line_status` | Estado de cada línea de pedido, cantidad pendiente, días de retraso, si se entregó a tiempo |
| `02_vw_po_status.sql` | `vw_po_status` | Estado de cada pedido y si sigue pendiente |
| `03_vw_stock_by_bucket.sql` | `vw_stock_by_bucket` | Stock de cada referencia por estado (disponible, reservado, cuarentena, bloqueado, no conforme), cantidad pedida y si está bajo mínimo |
| `04_vw_mo_material_status.sql` | `vw_mo_material_status` | Para cada material de una orden: si faltó a tiempo |
| `05_vw_mo_status.sql` | `vw_mo_status` | Retraso de cada orden, días bloqueada y por qué |
| `06_vw_document_status.sql` | `vw_revision_status`, `vw_document_status` | Vigencia de cada documento: `VALID`, `REVIEW_OVERDUE`, `NOT_CONTROLLED`, `OBSOLETE` o `DRAFT` |
| `07_vw_incident_status.sql` | `vw_incident_status` | Antigüedad, tiempo de resolución, si está fuera de plazo, si se cerró a tiempo |
| `08_vw_capa_status.sql` | `vw_capa_status` | Días de retraso, último avance, si se replanificó |
| `09_vw_stock_count_result.sql` | `vw_stock_count_result` | Diferencia de cada recuento frente al sistema |
| `10_vw_master_status.sql` | `vw_employee_status`, `vw_aircraft_status` | Si un empleado está activo y si una aeronave está en mantenimiento |

`build_database.py` crea las vistas automáticamente, en el orden del nombre del archivo, después de las tablas.

---

## 3. Las 82 reglas de validación

El documento `03_reglas_de_negocio.md` define 86 reglas. Las **82** de los grupos G, D, M, I, Q, C y A tienen ahora su propia consulta. Las 4 del grupo K (indicadores) se implementarán en la Fase 6, cuando existan los indicadores.

### 3.1 Un archivo por regla

Cada regla está en su propio archivo, por ejemplo `sql/validation/M09_obsolete_revision_used.sql`. Así se puede abrir, leer y ejecutar por separado en DB Browser.

Cada archivo empieza con una **cabecera** que el validador lee:

```sql
-- rule: M09
-- title: An order only uses revisions in force on the date they were linked
-- severity: WARNING
-- type: N
-- enforced_by: VALIDATION
-- returns: one row per record that breaks the rule (record_ref, detail)
```

Y todas las consultas siguen el mismo contrato: **devuelven una fila por cada registro que incumple la regla**, con dos columnas:

| Columna | Contenido | Ejemplo |
|---|---|---|
| `record_ref` | El código de negocio del registro, el que usaría una persona | `WO-2025-0125` |
| `detail` | Una frase que explica el problema | `WIN-MNT-018 R00 linked on 2025-07-24 (superseded on 2023-10-02)` |

Si la consulta no devuelve nada, la regla se cumple.

### 3.2 Por qué también se comprueban las reglas que impone la base de datos

Muchas reglas ya las impone la base de datos (claves externas, `CHECK`, triggers). Aun así, todas tienen su consulta. El motivo es el mismo que en una oficina de calidad: **no basta con que exista un control; hay que comprobar que funciona**. Si alguien abriera la base de datos sin activar las claves externas, o borrara un trigger, la validación lo detectaría (reglas G01, G08 y G09).

### 3.3 Gravedad

| Gravedad | Significado | Efecto |
|---|---|---|
| **CRITICAL** | El dato es incoherente: rompe la integridad o la lógica del sistema | Un solo registro cierra el control y los datos no pasan a Power BI |
| **WARNING** | El dato es coherente, pero refleja una situación que la oficina debe revisar | Aparece en el informe; no detiene el proceso |

Ejemplos: una salida de almacén mayor que el stock disponible es CRITICAL (regla I03), porque es imposible. Un documento con la fecha de revisión vencida es WARNING (regla D12), porque es una situación real que hay que gestionar, no un error del sistema.

---

## 4. El control de calidad de los datos (quality gate)

El script `run_validations.py` actúa como un **punto de control**: los datos solo continúan si lo superan. El control se supera cuando se cumplen **las tres** condiciones:

1. Ninguna regla CRITICAL encuentra registros.
2. Todas las reglas se pueden ejecutar (una regla que falla al ejecutarse es un fallo del propio control).
3. Las discrepancias sembradas se detectan **exactamente** (sección 5).

Si alguna falla, el script termina con un **código de salida 1**. Es la forma estándar de que un programa le diga a otro "algo ha ido mal". `run_pipeline.py` lo comprueba y se detiene: en la Fase 7, la exportación a Power BI irá después de este punto, así que **nunca se exportarán datos que no hayan superado el control**.

### Data Quality Score

El informe muestra un indicador sencillo:

> **Data Quality Score = reglas superadas ÷ reglas ejecutadas × 100**

Es un indicador interno del proyecto, sin ningún valor normativo. Su limitación es evidente: todas las reglas pesan lo mismo, y una regla con 1 registro cuenta igual que una con 12. Por eso el informe siempre lo acompaña del detalle por regla.

---

## 5. Las discrepancias sembradas: la prueba de que el control funciona

Un control que nunca encuentra nada no demuestra nada: puede que los datos estén bien o que el control no funcione. Para distinguirlo, el generador de la Fase 4 introdujo **9 discrepancias** a propósito y las anotó en `data/synthetic/planted_discrepancies.csv`.

El validador cruza ese archivo con lo que encuentran las reglas:

| Tipo sembrado | Regla | Sembradas | Detectadas | No detectadas | Inesperadas |
|---|---|---|---|---|---|
| Orden asociada a una revisión ya sustituida | M09 | 3 | 3 | — | — |
| Recepción sin certificado | I09 | 2 | 2 | — | — |
| Bloqueo por material cuando sí había stock | M08 | 2 | 2 | — | — |
| No conformidad sin ningún registro asociado | Q08 | 2 | 2 | — | — |

La comparación es **exacta en los dos sentidos**:

- Si una discrepancia sembrada no se detecta, la regla es demasiado débil.
- Si la regla encuentra registros que no se sembraron, la regla es demasiado amplia (falsos positivos) o el generador tiene un error.

En ambos casos el control se cierra. Durante esta fase este cruce encontró dos problemas reales del generador, que se corrigieron (sección 11).

---

## 6. Resultado de la validación

Con los datos actuales (semilla 145, fecha de corte 31/10/2026):

| Resultado | Valor |
|---|---|
| Reglas ejecutadas | 82 |
| Fallos CRITICAL | **0** |
| Reglas que no se pudieron ejecutar | 0 |
| Discrepancias sembradas detectadas | **9 de 9, sin inesperadas** |
| Reglas con avisos (WARNING) | 8 |
| Registros señalados | 26 |
| Data Quality Score | 90,2 % (74 de 82) |
| **Quality gate** | **SUPERADO** |
| Tiempo de ejecución | menos de 1 segundo |

### Los avisos, uno a uno

| Regla | Registros | Origen | Qué significa |
|---|---|---|---|
| M09 | 3 | Sembrado | Órdenes que usaron una revisión ya sustituida |
| I09 | 2 | Sembrado | Recepciones sin referencia de certificado |
| M08 | 2 | Sembrado | Bloqueos registrados con stock disponible |
| Q08 | 2 | Sembrado | No conformidades sin registro asociado |
| D12 | 12 | Natural | Documentos con la revisión periódica vencida: alguien olvidó revisarlos |
| C10 | 2 | Natural | Acciones correctivas abiertas fuera de plazo |
| Q12 | 2 | Natural | No conformidades abiertas fuera de su plazo interno (ficticio) |
| I16 | 1 | Natural | Una referencia bajo mínimo sin pedido en curso (AQ-3342-06) |

Los avisos **naturales** no son errores del proyecto: son la consecuencia de simular una empresa en la que a veces se olvidan cosas. Son precisamente lo que medirán los indicadores de la Fase 6.

---

## 7. Las 8 consultas de negocio

Están en `sql/queries/`. Cada una responde a una pregunta que se haría en una oficina de calidad y producción, y tiene un comentario al principio que explica qué hace.

| Archivo | Pregunta | Filas con los datos actuales |
|---|---|---|
| `01_nonconformity_full_history.sql` | ¿Qué pasó con esta no conformidad, quién hizo cada cosa y cuándo? | 23 eventos de NC-2025-0021 |
| `02_lot_traceability.sql` | ¿De dónde viene este lote, con qué certificado, y en qué aeronave y orden se usó? | 15 movimientos |
| `03_blocked_orders.sql` | ¿Qué órdenes están paradas hoy, desde cuándo y qué esperan? | 4 órdenes |
| `04_stock_below_minimum.sql` | ¿Qué se está agotando y ya está pedido? | 7 referencias |
| `05_supplier_delivery_performance.sql` | ¿Qué proveedores entregan a tiempo y cuáles dan problemas? | 19 proveedores |
| `06_expired_documents_in_use.sql` | ¿Qué documentos están caducados y se han usado después de caducar? | 12 documentos |
| `07_open_actions_by_owner.sql` | ¿Quién tiene acciones pendientes y cuáles van con retraso? | 9 acciones |
| `08_recurring_problems_pareto.sql` | ¿Qué categorías concentran las no conformidades y qué causa domina? | 8 categorías |

Las consultas 01 y 02 tienen un **parámetro**: el número de no conformidad o de lote que se quiere consultar. Está en las primeras líneas, marcado con `<-`. Si se deja como está, la consulta elige un ejemplo representativo.

Algunas observaciones que ya muestran los datos, y que los cuadros de mando deberán poner en evidencia:

- **SUP-006** es el proveedor con peor puntualidad del periodo completo (46 % de entregas a tiempo), aunque mejoró tras su plan de octubre de 2025.
- Las categorías de **mantenimiento, inventario y registro** concentran el 56 % de las no conformidades. El método de trabajo (METHOD) es la causa raíz dominante en inventario y registro.
- Dos documentos técnicos caducados se han seguido usando en **8 órdenes** cada uno después de su fecha de revisión. Es una situación que una oficina de control documental debe detectar.

---

## 8. Las pruebas automáticas

El archivo `tests/test_validations.py` añade 24 pruebas. Lo más importante son las **pruebas negativas**: se hace una copia de la base de datos, se introduce un error a propósito y se comprueba que la regla lo detecta y que el control se cierra.

| Error introducido | Regla que debe detectarlo |
|---|---|
| Una salida de almacén de 999 unidades de un lote que no existe | I03 (stock negativo) e I07 (lote nunca recibido) |
| Una orden en estado ON_HOLD sin ningún bloqueo registrado | M05 |
| Una acción abierta en una no conformidad ya cerrada | Q05 |
| Un empleado de un departamento que no existe (con las claves externas desactivadas) | G01 |
| Una discrepancia sembrada que no está en los datos | El cruce de la sección 5 |

El resto de pruebas comprueba:

- Que hay 82 reglas, con cabeceras válidas, sin identificadores repetidos y con la gravedad que indica el documento `03`.
- Que todas se ejecutan, que ninguna CRITICAL falla y que el cruce con las sembradas es exacto.
- Que las vistas y las reglas dan **las mismas cifras** (por ejemplo, documentos caducados en la vista = registros de la regla D12).
- Que el stock calculado por la vista coincide con la suma de los movimientos.
- Que las 13 vistas y las 8 consultas devuelven resultados.

En total, el proyecto tiene ahora **77 pruebas**: 25 de la Fase 3, 28 de la Fase 4 y 24 de esta fase.

---

## 9. Archivos de esta fase

Todos están dentro de la carpeta del proyecto.

| Archivo | Novedad |
|---|---|
| `sql/views/00_…sql` a `10_…sql` | Nuevos: 11 archivos con las 13 vistas |
| `sql/validation/*.sql` | Nuevos: 82 archivos, uno por regla |
| `sql/queries/01_…sql` a `08_…sql` | Nuevos: 8 consultas de negocio |
| `scripts/run_validations.py` | Nuevo: validador y quality gate |
| `scripts/run_pipeline.py` | Nuevo: proceso completo con un comando |
| `scripts/build_database.py` | Actualizado: crea también las vistas |
| `scripts/generator/inventory.py`, `world.py` | Corregidos (sección 11) |
| `config/settings.py` | Actualizado: rutas de las nuevas carpetas |
| `tests/test_validations.py` | Nuevo: 24 pruebas |
| `tests/test_database_schema.py` | Ajustado: la prueba de tablas STRICT ya no confunde las vistas con tablas |
| `reports/validation_report.md` | Generado: el informe de validación |
| `reports/validation_results.csv` | Generado: una fila por regla (se abre en Excel) |
| `reports/validation_findings.csv` | Generado: una fila por registro señalado (se abre en Excel) |
| `data/synthetic/*.csv`, `database/aqmi.db` | Regenerados |
| `documentation/06_fase5_consultas_y_validaciones.md` | Este documento |
| `documentation/03_reglas_de_negocio.md`, `05_fase4_datos_sinteticos.md`, `README.md` | Actualizados |

---

## 10. Cómo comprobar que funciona

Todos los comandos se escriben en **PowerShell**, desde la carpeta principal del proyecto y con el entorno virtual activado (como en la Fase 3, apartado de activación: `.venv\Scripts\activate`; al principio de la línea debe aparecer `(.venv)`).

### Paso 1 — Ejecutar el proceso completo

```powershell
python scripts/run_pipeline.py
```

Tarda unos segundos. Las últimas líneas deben ser:

```text
INFO    | STEP 2/2 — Validations (quality gate)
WARNING | C10 WARNING  Open action past its due date (overdue action)          2 record(s)
WARNING | D12 WARNING  Current revision with its review date passed (expired d 12 record(s)
WARNING | I09 WARNING  Receipts of materials that require a certificate carry  2 record(s)
WARNING | I16 WARNING  Stock below minimum (available + in quarantine) with no 1 record(s)
WARNING | M08 WARNING  A material hold corresponds to a real shortage when it  2 record(s)
WARNING | M09 WARNING  An order only uses revisions in force on the date they  3 record(s)
WARNING | Q08 WARNING  A non-conformity is linked to at least one record (airc 2 record(s)
WARNING | Q12 WARNING  Open non-conformity past its target closure date        2 record(s)
INFO    | Rules: 82 | passed: 74 | warnings: 8 | critical failures: 0 | errors: 0 | 0.10 s
INFO    | Planted discrepancies detected: 9 of 9 (exact match)
INFO    | Data Quality Score: 90.2 %
INFO    | Reports written to reports
INFO    | QUALITY GATE PASSED
INFO    | PIPELINE OK
```

Las líneas `WARNING` no son errores del programa: son los avisos del informe (sección 6). Lo importante son las tres últimas líneas.

Si ya tienes la base de datos generada y solo quieres repetir la validación:

```powershell
python scripts/run_validations.py
```

### Paso 2 — Leer el informe

Abre `reports/validation_report.md` en VS Code y pulsa `Ctrl + Mayús + V` para verlo con formato. En GitHub se verá con formato automáticamente. Los dos CSV de la misma carpeta se abren directamente en Excel.

### Paso 3 — Ejecutar las pruebas

```powershell
pytest -v
```

Resultado esperado: **`77 passed`**. Tarda unos 15 segundos.

### Paso 4 — Probar una consulta en DB Browser

1. Abre `database/aqmi.db` en DB Browser for SQLite.
2. Ve a la pestaña **Ejecutar SQL**.
3. Pulsa el botón **Abrir archivo SQL** (icono de carpeta) y elige `sql/queries/03_blocked_orders.sql`.
4. Pulsa **Ejecutar todo** (el triángulo, o `Ctrl + Intro`).

Deben aparecer 4 órdenes bloqueadas por material, con la fecha de inicio del bloqueo y la próxima entrega prometida.

Puedes hacer lo mismo con cualquier archivo de `sql/validation/`: por ejemplo, `M09_obsolete_revision_used.sql` devuelve las 3 órdenes sembradas.

### Paso 5 (opcional) — Ver cómo el control se cierra

Para ver el control en acción, puedes provocar un error en una **copia** de la base de datos. No es necesario: las pruebas negativas de la sección 8 lo hacen automáticamente cada vez que ejecutas `pytest`.

---

## 11. Cambios y correcciones durante esta fase

El cruce con las discrepancias sembradas cumplió su función: encontró dos problemas en el generador antes de que llegaran a los cuadros de mando.

| Problema encontrado | Causa | Corrección |
|---|---|---|
| La regla M08 señalaba bloqueos por material que no se habían sembrado | Al reservar material, el generador a veces pedía una unidad de más (margen de seguridad) y registraba un bloqueo aunque el stock cubría lo necesario | Si el stock cubre la cantidad necesaria, no se pide la unidad de más (`inventory.py`) |
| El cruce no podía comparar las referencias sembradas | El archivo de sembradas guardaba identificadores internos (`mo_id`) y las reglas devuelven códigos de negocio (`WO-2025-0049`) | El archivo de sembradas usa ahora códigos de negocio (`world.py`) |
| La regla I16 señalaba como "sin pedido" una referencia cuyo material ya estaba recibido, en inspección | La regla solo contaba el stock disponible | La regla cuenta también el stock en inspección de recepción, que ya está en el almacén. Documentado en `03` |

Con las dos correcciones del generador, los datos se regeneraron y cambiaron ligeramente (por ejemplo, 491 órdenes en lugar de 492). El documento `05` y el `README` están actualizados con las cifras nuevas.

---

## 12. Limitaciones

| Limitación | Consecuencia |
|---|---|
| Las reglas K (indicadores) no se ejecutan en esta fase | Implementadas en la Fase 6 (`scripts/run_kpis.py`, documento 07) |
| Las reglas comprueban la coherencia interna, no la verdad del dato | Si un dato es coherente pero falso (por ejemplo, una cantidad bien registrada pero mal contada), ninguna regla lo detecta. Es la misma limitación que tiene cualquier sistema de gestión, y la razón de que existan los recuentos físicos y las verificaciones frente al documento original |
| El cruce exacto depende de que las sembradas estén bien anotadas | Por eso las pruebas comprueban también el caso contrario: una sembrada que no existe debe cerrar el control |
| El Data Quality Score pesa igual todas las reglas | Se acompaña siempre del detalle por regla |
| Las consultas están pensadas para SQLite | Usan funciones como `julianday()` y `group_concat()`. Si en el futuro se migra a PostgreSQL, habrá que adaptarlas (decisión D1 de la Fase 1) |
