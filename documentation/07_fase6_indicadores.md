# AQMI — Fase 6: Indicadores (KPI)

**Documento:** `documentation/07_fase6_indicadores.md`
**Estado:** Aprobada el 17/11/2026
**Fecha:** 17/11/2026

> AEROQ MRO es una empresa ficticia y todos sus datos son sintéticos. **Ningún objetivo de este documento es un umbral regulatorio.** Todos los objetivos y niveles de alerta son **objetivos internos ficticios de AEROQ MRO**, elegidos para que los indicadores sean informativos en el portfolio. Ninguna norma, tampoco EASA Part-145, fija estos valores.

---

## Índice

1. Qué se ha construido
2. Reglas comunes a todos los indicadores
3. Resumen de resultados
4. Fichas de los 18 indicadores
5. Los controles de los indicadores (reglas K)
6. Lo que cuentan los indicadores
7. Decisiones de definición tomadas en esta fase
8. Archivos de esta fase
9. Cómo comprobar que funciona
10. Limitaciones generales

---

## 1. Qué se ha construido

| Pieza | Qué hace | Dónde está |
|---|---|---|
| **18 consultas de referencia** | Una por indicador. Calculan el valor de cada mes y el valor del periodo completo | `sql/kpi/` |
| **Vista del calendario** | Los 24 meses del periodo y una fila TOTAL | `sql/views/11_vw_kpi_periods.sql` |
| **Calculadora de indicadores** | Ejecuta las 18 consultas, aplica los controles K, calcula el semáforo y escribe los informes | `scripts/run_kpis.py` |
| **Informe de indicadores** | Resumen legible con semáforos, comparación entre años y últimos 12 meses | `reports/kpi_report.md` |
| **Dos CSV** | `kpi_summary.csv` (una fila por indicador) y `kpi_values.csv` (una fila por indicador y mes) | `reports/` |
| **29 pruebas nuevas** | Recalculan indicadores en Python y comprueban que los controles detectan errores | `tests/test_kpis.py` |

El proceso completo tiene ahora tres pasos y se ejecuta con un solo comando (`run_pipeline.py`):

```text
1. Generar los datos  →  2. Validar (82 reglas)  →  3. Calcular y controlar los indicadores
                         si falla, se detiene      si falla, se detiene
```

La **consulta SQL de referencia** de cada indicador es la definición oficial. En la Fase 7, cada medida DAX de Power BI se construirá a partir de ella. En la Fase 9 se comprobará que los dos dan el mismo valor (regla K03).

---

## 2. Reglas comunes a todos los indicadores

### 2.1 Dos tipos de indicador

| Tipo | Qué mide | Ejemplo | Valor del periodo completo (fila TOTAL) |
|---|---|---|---|
| **FLOW** (flujo) | Cosas que **ocurren** en un periodo | No conformidades detectadas en marzo | Suma de los 24 meses |
| **SNAPSHOT** (foto) | Un **estado** en una fecha | No conformidades abiertas el 31 de marzo | Estado en la fecha de corte (31/10/2026) |

Un indicador de foto no se puede sumar: tener 13 incidencias abiertas en marzo y 13 en abril no son 26.

### 2.2 Cálculo mensual

Cada consulta devuelve **25 filas**: una por cada mes (de 2024-11 a 2026-10) y una fila `TOTAL`. Las cuatro columnas son siempre las mismas:

| Columna | Contenido |
|---|---|
| `period` | `AAAA-MM` o `TOTAL` |
| `numerator` | Lo que se cuenta (o la suma de días, en los promedios) |
| `denominator` | Sobre qué se cuenta. Vacío en los indicadores que son un recuento |
| `value` | El resultado. Vacío si no hay datos |

Guardar el numerador y el denominador, y no solo el porcentaje, permite **agregar correctamente**. El porcentaje de un año no es la media de los porcentajes mensuales: hay que dividir la suma de numeradores entre la suma de denominadores.

### 2.3 La foto en una fecha pasada se reconstruye desde la auditoría

Algunas fechas cambian con el tiempo. La fecha límite de una acción se amplía y la fecha de revisión de un documento se prorroga tras una revisión periódica. Para saber si una acción estaba vencida el 30/04/2025, no sirve su fecha límite de hoy: hay que saber cuál estaba en vigor ese día.

Las consultas QUA-06, DOC-01 y DOC-03 **reconstruyen esa fecha a partir del registro de auditoría** (`Audit_Log`). Toman el último cambio anterior a la fecha, o el valor original si el primer cambio fue posterior. Es el módulo F (trazabilidad) puesto al servicio del análisis. La regla K05 (sección 5) comprueba que esta reconstrucción, aplicada a la fecha de corte, da exactamente el estado actual de los datos.

### 2.4 Otras reglas

| Regla | Motivo |
|---|---|
| Fecha de corte fija: **31/10/2026** | Los indicadores no cambian según el día en que se ejecuten |
| Las no conformidades y órdenes **canceladas** se excluyen | Una cancelación indica un registro hecho por error |
| Un denominador cero da **"sin datos"**, nunca 0 % | 0 % significaría que todo fue mal, cuando en realidad no hubo nada que medir |
| Días naturales | Es la referencia más simple y la que usan las fechas de la base de datos |
| Valores redondeados a 1 decimal | Se redondea solo el resultado; numerador y denominador son exactos |

### 2.5 Objetivos internos ficticios y semáforo

Algunos indicadores tienen un **objetivo** y un **nivel de alerta**, ambos **ficticios** y definidos por AEROQ MRO para sí misma:

| Color | Significado |
|---|---|
| 🟢 Verde | Se cumple el objetivo |
| 🟡 Ámbar | No se cumple el objetivo, pero no se supera el nivel de alerta |
| 🔴 Rojo | Se supera el nivel de alerta |
| — | Indicador de seguimiento, sin objetivo |

Los objetivos se fijaron **antes** de calcular los valores y no se han ajustado después para mejorar el resultado. Por eso hay varios indicadores en rojo. Un sistema de calidad que muestra todo en verde no resulta creíble.

Los indicadores de volumen (por ejemplo, el total de no conformidades) no tienen objetivo, a propósito. Detectar más no conformidades puede significar que se trabaja peor, pero también que se controla mejor. Fijar un máximo invitaría a no registrarlas.

---

## 3. Resumen de resultados

Valores con los datos actuales (semilla 145). Año 1 = nov 2024–oct 2025. Año 2 = nov 2025–oct 2026.

| KPI | Indicador | Tipo | Valor | Objetivo ficticio | Estado | Año 1 | Año 2 |
|---|---|---|---|---|---|---|---|
| QUA-01 | Total Quality Incidents | Flujo | 141 | — | — | 86 | 55 |
| QUA-02 | Open Non-Conformities | Foto | 13 | — | — | 11 | 13 |
| QUA-03 | Non-Conformity Rate | Flujo | 29,8 por 100 órdenes | — | — | 36,8 | 23,0 |
| QUA-04 | Corrective Action Closure Rate | Flujo | 69,1 % | ≥ 85 % | 🔴 | 73,1 % | 63,9 % |
| QUA-05 | Average Resolution Time | Flujo | 82,0 días | ≤ 75 días | 🟡 | 75,3 | 91,4 |
| QUA-06 | Overdue Corrective Actions | Foto | 2 | 0 | 🟡 | 1 | 2 |
| DOC-01 | Document Compliance Rate | Foto | 94,4 % | ≥ 95 % | 🟡 | 96,7 % | 94,4 % |
| DOC-02 | Documentation Error Rate | Flujo | 8,3 % | ≤ 5 % | 🔴 | 8,7 % | 8,0 % |
| DOC-03 | Expired Documents | Foto | 12 | 0 | 🔴 | 7 | 12 |
| DOC-04 | Traceability Compliance | Flujo | 99,2 % | 100 % | 🟡 | 99,1 % | 99,3 % |
| INV-01 | Inventory Accuracy | Flujo | 89,9 % | ≥ 95 % | 🔴 | 85,6 % | 94,2 % |
| INV-02 | Stock Availability | Foto | 93,0 % | ≥ 95 % | 🟡 | 93,0 % | 93,0 % |
| INV-03 | Material Shortage Rate | Flujo | 6,6 % | ≤ 5 % | 🟡 | 6,2 % | 7,0 % |
| INV-04 | Pending Purchase Orders | Foto | 9 | — | — | 3 | 9 |
| MNT-01 | Maintenance Order Completion Rate | Flujo | 60,8 % | ≥ 85 % | 🔴 | 65,5 % | 56,2 % |
| MNT-02 | Average Maintenance Delay | Flujo | 2,3 días | ≤ 2 días | 🟡 | 2,2 | 2,3 |
| MNT-03 | Work Orders Blocked by Material | Foto | 4 | — | — | 1 | 4 |
| MNT-04 | Work Orders Blocked by Documentation | Foto | 0 | — | — | 0 | 0 |

En los indicadores de foto, "Año 1" y "Año 2" son el estado al final de cada año (31/10/2025 y 31/10/2026).

---

## 4. Fichas de los 18 indicadores

Cada ficha responde a las seis preguntas del encargo: qué mide, fórmula exacta, tablas, frecuencia, interpretación y limitaciones. Además indica el objetivo interno ficticio, si lo hay. La fórmula exacta es la consulta SQL del archivo indicado. Aquí se describe en lenguaje natural.

**Frecuencia de cálculo (todos los indicadores):** mensual, al cierre de cada mes. Además, valor del periodo completo (flujo) o en la fecha de corte (foto). Power BI permitirá agruparlos por trimestre o año.

---

### QUALITY

#### QUA-01 — Total Quality Incidents (Total de no conformidades)

| | |
|---|---|
| **Qué mide** | Cuántas no conformidades se detectaron en el periodo |
| **Fórmula** | Nº de no conformidades con `detected_date` dentro del periodo y estado distinto de `CANCELLED` |
| **Tablas** | `Quality_Incidents` |
| **Archivo** | `sql/kpi/QUA01_total_quality_incidents.sql` |
| **Interpretación** | Volumen de problemas detectados. Su desglose por categoría, gravedad, departamento y origen (Fase 7) muestra dónde se concentran |
| **Objetivo** | Ninguno, a propósito (sección 2.5) |
| **Limitaciones** | Depende de la detección: un descenso puede significar menos problemas o menos control. Debe leerse junto con QUA-03 |

#### QUA-02 — Open Non-Conformities (No conformidades abiertas)

| | |
|---|---|
| **Qué mide** | Cuántas no conformidades estaban abiertas al final del periodo |
| **Fórmula** | Nº de no conformidades no canceladas con `detected_date` ≤ fecha y (`closed_date` vacía o posterior a la fecha) |
| **Tablas** | `Quality_Incidents` |
| **Archivo** | `sql/kpi/QUA02_open_non_conformities.sql` |
| **Interpretación** | Carga de trabajo pendiente de la oficina de calidad. Si crece de forma sostenida, se abren más no conformidades de las que se cierran |
| **Objetivo** | Ninguno: es un indicador de carga, que depende del volumen de entrada |
| **Limitaciones** | No distingue gravedad ni antigüedad: una abierta ayer cuenta igual que una abierta hace un año. Debe leerse junto con QUA-05 y con la regla Q12 (abiertas fuera de plazo) |

#### QUA-03 — Non-Conformity Rate (Tasa de no conformidades)

| | |
|---|---|
| **Qué mide** | Cuántas no conformidades se detectan por cada 100 órdenes de trabajo completadas |
| **Fórmula** | No conformidades detectadas en el periodo ÷ órdenes completadas en el periodo (`actual_end_date` en el periodo, no canceladas) × 100 |
| **Tablas** | `Quality_Incidents`, `Maintenance_Orders` |
| **Archivo** | `sql/kpi/QUA03_non_conformity_rate.sql` |
| **Interpretación** | Normaliza QUA-01 por la actividad: si se trabaja más, es normal detectar más. Bajó de 36,8 a 23,0 entre el año 1 y el año 2 |
| **Objetivo** | Ninguno, por el mismo motivo que QUA-01 |
| **Limitaciones** | No es un porcentaje (puede superar 100). El numerador incluye no conformidades que no proceden de órdenes (auditorías, proveedores), así que mide la actividad general de calidad por unidad de trabajo, no la calidad de cada orden |

#### QUA-04 — Corrective Action Closure Rate (Cierre de acciones correctivas en plazo)

| | |
|---|---|
| **Qué mide** | De las acciones correctivas cuya fecha límite caía en el periodo, qué porcentaje se implantó a tiempo |
| **Fórmula** | Acciones `CORRECTIVE` no canceladas con `due_date` en el periodo y `completed_date` ≤ `due_date` ÷ acciones `CORRECTIVE` no canceladas con `due_date` en el periodo × 100 |
| **Tablas** | `CAPA_Actions` |
| **Archivo** | `sql/kpi/QUA04_corrective_action_closure_rate.sql` |
| **Interpretación** | Capacidad de la organización para cumplir los compromisos de corrección |
| **Objetivo ficticio** | ≥ 85 % (alerta por debajo de 75 %) |
| **Limitaciones** | Usa la fecha límite vigente, con sus ampliaciones: una acción replanificada cuenta como "a tiempo" si cumple la nueva fecha. Por eso conviene leerlo junto con el número de acciones replanificadas (`was_rescheduled` en `vw_capa_status`). Mide la implantación, no el cierre formal tras la verificación de eficacia (sección 7). En noviembre y diciembre de 2024 no vencía ninguna acción: el valor es "sin datos" |

#### QUA-05 — Average Resolution Time (Tiempo medio de resolución)

| | |
|---|---|
| **Qué mide** | Cuántos días se tarda, de media, en cerrar una no conformidad |
| **Fórmula** | Suma de (`closed_date` − `detected_date`) de las no conformidades cerradas en el periodo ÷ nº de no conformidades cerradas en el periodo |
| **Tablas** | `Quality_Incidents` |
| **Archivo** | `sql/kpi/QUA05_average_resolution_time.sql` |
| **Interpretación** | Agilidad del ciclo completo: análisis, acciones, verificación de eficacia y cierre |
| **Objetivo ficticio** | ≤ 75 días (alerta por encima de 90). Coherente con los plazos internos ficticios de cierre por gravedad (45/75/90/30 días, documento 05) |
| **Limitaciones** | Se asigna al mes de cierre, así que un mes con el cierre de casos antiguos sube aunque el trabajo vaya bien. **Efecto de arranque:** en los primeros meses solo podían cerrarse casos rápidos (la empresa simulada empieza sin casos antiguos), así que el año 1 sale favorecido. Las no conformidades abiertas no entran: su antigüedad la mide la regla Q12 |

#### QUA-06 — Overdue Corrective Actions (Acciones correctivas vencidas)

| | |
|---|---|
| **Qué mide** | Cuántas acciones correctivas habían superado su fecha límite sin estar implantadas, al final del periodo |
| **Fórmula** | Nº de acciones `CORRECTIVE` no canceladas, creadas ≤ fecha, no implantadas en esa fecha (`completed_date` vacía o posterior) y con la fecha límite **vigente en esa fecha** anterior a ella. La fecha vigente se reconstruye desde `Audit_Log` (sección 2.3) |
| **Tablas** | `CAPA_Actions`, `Audit_Log` |
| **Archivo** | `sql/kpi/QUA06_overdue_corrective_actions.sql` |
| **Interpretación** | Compromisos incumplidos en este momento. Es el indicador que más rápidamente pide intervención de la dirección |
| **Objetivo ficticio** | 0 (alerta por encima de 2) |
| **Limitaciones** | No mide cuánto tiempo llevan vencidas (lo da la consulta `07_open_actions_by_owner.sql`). Una ampliación de plazo aprobada saca una acción de la lista: el indicador depende de que las ampliaciones estén justificadas |

---

### DOCUMENT CONTROL

#### DOC-01 — Document Compliance Rate (Cumplimiento documental)

| | |
|---|---|
| **Qué mide** | Qué porcentaje de los documentos controlados tenía, en la fecha, una revisión en vigor dentro de su fecha de revisión periódica |
| **Fórmula** | Documentos controlados (`is_controlled` = 1) con revisión en vigor en la fecha (`effective_date` ≤ fecha y no sustituida) y fecha de revisión vigente ≥ fecha ÷ documentos controlados con revisión en vigor × 100. La fecha de revisión vigente se reconstruye desde `Audit_Log` |
| **Tablas** | `Documents`, `Document_Revisions`, `Audit_Log` |
| **Archivo** | `sql/kpi/DOC01_document_compliance_rate.sql` |
| **Interpretación** | Grado en que el sistema documental está al día |
| **Objetivo ficticio** | ≥ 95 % (alerta por debajo de 90 %) |
| **Limitaciones** | Mide la vigencia formal, no si el contenido es correcto (eso lo mide DOC-02). Los 36 documentos no controlados (libros de registro de las aeronaves, que no tienen revisión periódica) quedan fuera |

#### DOC-02 — Documentation Error Rate (Tasa de errores documentales)

| | |
|---|---|
| **Qué mide** | De las comprobaciones rutinarias de documentos y registros, qué porcentaje encontró una discrepancia |
| **Fórmula** | Verificaciones del periodo con resultado distinto de `CONFORM` ÷ verificaciones del periodo × 100. Se excluyen las de tipo `INTERNAL_AUDIT` (sección 7) |
| **Tablas** | `Document_Verifications` |
| **Archivo** | `sql/kpi/DOC02_documentation_error_rate.sql` |
| **Interpretación** | Calidad de la información: comprobación de registros frente al original, revisiones periódicas y comprobaciones previas al uso. Es el indicador más cercano al trabajo diario de una oficina de calidad técnica |
| **Objetivo ficticio** | ≤ 5 % (alerta por encima de 8 %) |
| **Limitaciones** | Cuenta igual una discrepancia menor (`MINOR_DISCREPANCY`) que una no conformidad. Mezcla tipos de verificación con tasas distintas: el desglose por tipo (Fase 7) es imprescindible. El rediseño del formulario de cierre (mayo de 2025) cae dentro del año 1, así que la comparación entre años lo diluye. Antes del rediseño, el 12,8 % de las verificaciones encontraba discrepancias; después, el 7,1 % |

#### DOC-03 — Expired Documents (Documentos caducados)

| | |
|---|---|
| **Qué mide** | Cuántos documentos controlados habían superado su fecha de revisión periódica, al final del periodo |
| **Fórmula** | Nº de documentos controlados con revisión en vigor en la fecha y fecha de revisión vigente anterior a la fecha (reconstruida desde `Audit_Log`) |
| **Tablas** | `Documents`, `Document_Revisions`, `Audit_Log` |
| **Archivo** | `sql/kpi/DOC03_expired_documents.sql` |
| **Interpretación** | Lista de trabajo del control documental. A la fecha de corte coincide con la regla D12 (12 documentos) |
| **Objetivo ficticio** | 0 (alerta por encima de 5) |
| **Limitaciones** | No distingue un documento vencido ayer de uno vencido hace un año (lo da la consulta `06_expired_documents_in_use.sql`). Tampoco indica si el documento caducado se está usando, que es lo realmente grave |

#### DOC-04 — Traceability Compliance (Cumplimiento de trazabilidad)

| | |
|---|---|
| **Qué mide** | De las salidas de material a órdenes de trabajo, qué porcentaje tiene todos los datos de trazabilidad |
| **Fórmula** | Salidas (`ISSUE`) del periodo con orden de trabajo, lote, número de serie (solo piezas serializadas) y certificado de conformidad (solo materiales que lo exigen) ÷ salidas del periodo × 100 |
| **Tablas** | `Inventory_Movements`, `Materials` |
| **Archivo** | `sql/kpi/DOC04_traceability_compliance.sql` |
| **Interpretación** | Si se puede reconstruir, para cada pieza montada, de dónde vino y con qué documentación |
| **Objetivo ficticio** | 100 % (alerta por debajo de 99 %) |
| **Limitaciones** | Comprueba que los datos existen, no que sean correctos. Las 11 salidas incompletas proceden de las **2 recepciones sembradas sin certificado** (Fase 4): un único error en la recepción se propagó a 11 piezas entregadas a órdenes |

---

### INVENTORY

#### INV-01 — Inventory Accuracy (Exactitud de inventario)

| | |
|---|---|
| **Qué mide** | De los recuentos cíclicos realizados, qué porcentaje coincidió con el stock del sistema |
| **Fórmula** | Recuentos `CYCLE` del periodo con `counted_qty` = `system_qty` ÷ recuentos `CYCLE` del periodo × 100. Los recuentos de apertura se excluyen |
| **Tablas** | `Stock_Counts` |
| **Archivo** | `sql/kpi/INV01_inventory_accuracy.sql` |
| **Interpretación** | Fiabilidad de los registros de almacén. Si el sistema no coincide con la estantería, las decisiones de compra y de planificación fallan |
| **Objetivo ficticio** | ≥ 95 % (alerta por debajo de 90 %) |
| **Limitaciones** | Tolerancia cero: cualquier diferencia cuenta como error, aunque sea de 0,25 m de alambre. Una tolerancia interna por tipo de material sería una mejora posible. Con unos 17 recuentos al mes, el valor mensual es muy sensible: un solo recuento con diferencia supone ~6 puntos |

#### INV-02 — Stock Availability (Disponibilidad de stock)

| | |
|---|---|
| **Qué mide** | Qué porcentaje de los materiales activos tenía stock disponible igual o superior a su mínimo, al final del periodo |
| **Fórmula** | Materiales activos con stock `AVAILABLE` ≥ `min_stock_qty` en la fecha ÷ materiales activos × 100. El stock en una fecha es la suma de movimientos hacia `AVAILABLE` menos los movimientos desde `AVAILABLE` hasta esa fecha |
| **Tablas** | `Materials`, `Inventory_Movements` |
| **Archivo** | `sql/kpi/INV02_stock_availability.sql` |
| **Interpretación** | Capacidad del almacén para atender la demanda sin esperar a un pedido |
| **Objetivo ficticio** | ≥ 95 % (alerta por debajo de 90 %) |
| **Limitaciones** | No cuenta el material en inspección de recepción, que llegará pronto (la regla I16 sí lo cuenta). Todas las referencias pesan igual: una arandela y un componente caro cuentan lo mismo. Usa el estado actual de "activo" para todo el periodo |

#### INV-03 — Material Shortage Rate (Tasa de faltas de material)

| | |
|---|---|
| **Qué mide** | De las líneas de material necesarias en el periodo, qué porcentaje no estaba disponible en la fecha requerida |
| **Fórmula** | Líneas de material de órdenes no canceladas con `required_by_date` en el periodo que faltaron ÷ esas líneas × 100. Una línea faltó si se reservó después de la fecha requerida, o si sigue sin reservar con la fecha ya pasada (definición de `vw_mo_material_status`) |
| **Tablas** | `Maintenance_Order_Materials`, `Inventory_Movements` |
| **Archivo** | `sql/kpi/INV03_material_shortage_rate.sql` |
| **Interpretación** | Impacto del almacén y las compras en el taller. Es la causa principal de retraso de las órdenes (sección 6) |
| **Objetivo ficticio** | ≤ 5 % (alerta por encima de 8 %) |
| **Limitaciones** | Una falta de un día cuenta igual que una de un mes (la duración la mide `material_hold_days` en `vw_mo_status`). Se asigna al mes de la fecha requerida |

#### INV-04 — Pending Purchase Orders (Pedidos pendientes)

| | |
|---|---|
| **Qué mide** | Cuántos pedidos a proveedores estaban enviados y no recibidos del todo, al final del periodo |
| **Fórmula** | Nº de pedidos con `order_date` ≤ fecha, no cancelados en esa fecha y con al menos una línea cuya cantidad recibida hasta esa fecha (movimientos `RECEIPT`) es menor que la pedida |
| **Tablas** | `Purchase_Orders`, `Purchase_Order_Lines`, `Inventory_Movements` |
| **Archivo** | `sql/kpi/INV04_pending_purchase_orders.sql` |
| **Interpretación** | Carga de seguimiento de compras. Su lectura útil es el detalle: qué pedidos van con retraso (`vw_po_line_status`) |
| **Objetivo** | Ninguno: más pedidos pendientes no es peor en sí mismo |
| **Limitaciones** | No distingue un pedido en plazo de uno retrasado, ni su valor económico |

---

### MAINTENANCE

#### MNT-01 — Maintenance Order Completion Rate (Órdenes completadas en plazo)

| | |
|---|---|
| **Qué mide** | De las órdenes que debían terminar en el periodo, qué porcentaje se completó en la fecha prevista o antes |
| **Fórmula** | Órdenes no canceladas con `planned_end_date` en el periodo y `actual_end_date` ≤ `planned_end_date` ÷ órdenes no canceladas con `planned_end_date` en el periodo × 100. Una orden sin terminar cuenta como no completada en plazo |
| **Tablas** | `Maintenance_Orders` |
| **Archivo** | `sql/kpi/MNT01_maintenance_order_completion_rate.sql` |
| **Interpretación** | Fiabilidad de la planificación ante el cliente: cuántas veces se cumple la fecha comprometida |
| **Objetivo ficticio** | ≥ 85 % (alerta por debajo de 75 %) |
| **Limitaciones** | Un día de retraso cuenta igual que un mes: debe leerse junto con MNT-02. Las 4 órdenes con fin previsto en el periodo que siguen abiertas cuentan como fuera de plazo |

#### MNT-02 — Average Maintenance Delay (Retraso medio de las órdenes)

| | |
|---|---|
| **Qué mide** | Cuántos días de retraso tienen, de media, las órdenes completadas (las que terminan a tiempo cuentan como 0) |
| **Fórmula** | Suma de máx(0, `actual_end_date` − `planned_end_date`) de las órdenes completadas en el periodo ÷ nº de órdenes completadas en el periodo |
| **Tablas** | `Maintenance_Orders` |
| **Archivo** | `sql/kpi/MNT02_average_maintenance_delay.sql` |
| **Interpretación** | Magnitud del retraso. Con MNT-01 se distingue entre "muchas órdenes con poco retraso" y "pocas con mucho" |
| **Objetivo ficticio** | ≤ 2 días (alerta por encima de 4) |
| **Limitaciones** | Las órdenes que terminan antes de tiempo cuentan como 0, no compensan. Las órdenes abiertas y ya retrasadas no entran hasta que se completan |

#### MNT-03 — Work Orders Blocked by Material (Órdenes bloqueadas por material)

| | |
|---|---|
| **Qué mide** | Cuántas órdenes estaban paradas por falta de material al final del periodo |
| **Fórmula** | Nº de órdenes distintas con un bloqueo `MATERIAL` activo en la fecha (`start_date` ≤ fecha y `end_date` vacía o posterior) |
| **Tablas** | `Maintenance_Order_Holds` |
| **Archivo** | `sql/kpi/MNT03_work_orders_blocked_by_material.sql` |
| **Interpretación** | Trabajo detenido por el suministro. El detalle (qué falta y cuándo llega) lo da la consulta `03_blocked_orders.sql` |
| **Objetivo** | Ninguno: es un indicador de seguimiento diario |
| **Limitaciones** | Es una foto: un bloqueo que empieza y acaba dentro del mes no aparece. La historia completa está en `vw_mo_status` (`material_hold_days`) |

#### MNT-04 — Work Orders Blocked by Documentation (Órdenes bloqueadas por documentación)

| | |
|---|---|
| **Qué mide** | Cuántas órdenes estaban paradas por un problema documental (documento caducado o datos técnicos no disponibles) al final del periodo |
| **Fórmula** | Igual que MNT-03, con bloqueos `DOCUMENTATION` |
| **Tablas** | `Maintenance_Order_Holds` |
| **Archivo** | `sql/kpi/MNT04_work_orders_blocked_by_documentation.sql` |
| **Interpretación** | Impacto del control documental en el taller |
| **Objetivo** | Ninguno |
| **Limitaciones** | Los bloqueos documentales son cortos (17 en total, de 2,8 días de media, porque se resuelven con una revisión urgente) y casi nunca coinciden con un fin de mes: el valor es 0 en todos los meses salvo marzo de 2025. En la Fase 7 se complementará con los días de bloqueo por documentación |

---

### CONTINUOUS IMPROVEMENT *(añadido en la Fase 9)*

#### LRN-01 — Lesson Incorporation Rate (Lecciones aprendidas incorporadas)

| | |
|---|---|
| **Qué mide** | De las lecciones aprendidas aprobadas hasta la fecha, qué porcentaje está ya incorporado a un documento controlado |
| **Fórmula** | Lecciones con `incorporated_date` ≤ fecha ÷ lecciones con `approved_date` ≤ fecha × 100. Tipo *foto a fecha* (SNAPSHOT); el TOTAL es la situación en la fecha de corte |
| **Tablas** | `Lessons_Learned` (y `Document_Revisions` para la revisión incorporada) |
| **Archivo** | `sql/kpi/LRN01_lesson_incorporation_rate.sql` |
| **Frecuencia** | Mensual |
| **Interpretación** | Si lo aprendido llega de verdad a los procedimientos, instrucciones y formularios, o se queda en el registro. Un valor bajo indica lecciones aprobadas que nadie ha llevado a un documento |
| **Objetivo ficticio** | ≥ 80 % (alerta por debajo de 60 %). **Objetivo interno ficticio de AEROQ MRO**, no un requisito normativo |
| **Limitaciones** | Las lecciones rechazadas o aún sin decidir no cuentan. Una lección aprobada al final del periodo baja el valor aunque todavía esté en plazo razonable: por eso la regla L07 solo avisa a partir de 90 días. No mide la calidad del cambio introducido en el documento |

Definición completa y diseño del registro: `09b_fase9_lecciones_aprendidas.md`. La regla K05 compara la situación reconstruida en la fecha de corte con el estado actual de `Lessons_Learned`.

---

### Indicador complementario: Data Quality Score

Definido en la Fase 5 (documento 06): **reglas de validación superadas ÷ reglas ejecutadas × 100**. Valor en la Fase 6: **90,2 %** (82 reglas). Tras la Fase 9: **89,9 %** (89 reglas). No mide a AEROQ MRO, sino la calidad de los datos del propio sistema. Se mostrará en la página *Audit & Traceability* de Power BI.

---

## 5. Los controles de los indicadores (reglas K)

Un indicador mal calculado es peor que no tener indicador. Por eso `run_kpis.py` comprueba los resultados antes de darlos por buenos. Si algún control falla, el proceso se detiene.

| Regla | Control | Cómo se comprueba | Resultado |
|---|---|---|---|
| **K01** | Todo porcentaje está entre 0 y 100; ningún valor es negativo | Se revisan los 450 valores (18 × 25) | ✅ |
| **K02** | Un denominador cero da "sin datos", nunca 0 % | Para cada fila: denominador 0 ⇒ valor vacío; denominador > 0 ⇒ valor presente | ✅ |
| **K03** | Power BI muestra el mismo valor que la consulta SQL | Prueba documentada en la **Fase 9** | Pendiente |
| **K04** | Las partes suman el total | La suma de los 24 meses = TOTAL (numerador y denominador) en todos los indicadores de flujo. Además, las no conformidades por categoría, por gravedad y por departamento suman el total | ✅ |
| **K05** *(nueva)* | La foto reconstruida desde la historia coincide con el estado actual | Para los 8 indicadores de foto, el valor en la fecha de corte calculado desde la historia (y la auditoría) debe ser idéntico al que dan las vistas del estado actual | ✅ |

**Por qué se añade K05.** Los indicadores de foto calculan el pasado con una lógica distinta de la de las vistas (reconstruyen fechas desde la auditoría). Si esa lógica tuviera un error, los valores históricos serían falsos sin que nadie lo notara. Comparar los dos caminos en la fecha de corte, donde deben coincidir, demuestra que la reconstrucción es correcta. La prueba negativa correspondiente altera a propósito un registro de auditoría en una copia de la base de datos, y K05 lo detecta.

---

## 6. Lo que cuentan los indicadores

Estos son los hallazgos principales. Los cuadros de mando de la Fase 7 deberán ponerlos en evidencia. Recuerda que los datos son sintéticos: los hallazgos muestran que el sistema permite detectar este tipo de situaciones, no describen una empresa real.

1. **Las faltas de material explican gran parte de los retrasos.** Ninguna de las 69 órdenes completadas que sufrieron un bloqueo por material terminó a tiempo. Las órdenes sin bloqueo terminan a tiempo en el 71,8 % de los casos. Mejorar INV-03 y INV-02 es la vía más directa para mejorar MNT-01.
2. **Las mejoras funcionan y se ven en los datos.**
   - Tras revisar el procedimiento de recuento (agosto de 2025), la exactitud de inventario pasa del 85,6 % al 94,2 %.
   - Tras rediseñar el formulario de cierre (mayo de 2025), las discrepancias en verificaciones pasan del 12,8 % al 7,1 %.
   - Las no conformidades por cada 100 órdenes bajan de 36,8 a 23,0.
3. **El control documental se está deteriorando.** Los documentos caducados pasan de 2 a 12 a lo largo del periodo y el cumplimiento documental cae por debajo del objetivo ficticio. Es una tendencia que pide acción antes de que llegue a las órdenes (en la Fase 5 ya se detectaron dos documentos caducados usados en 8 órdenes cada uno).
4. **El ciclo de acciones correctivas se ha ralentizado en el año 2.**
   - El cierre en plazo baja del 73,1 % al 63,9 %.
   - El tiempo medio de resolución sube de 75 a 91 días. Parte de esa subida se debe al efecto de arranque descrito en QUA-05.
5. **Un error pequeño se propaga.** Dos recepciones sin certificado acabaron en 11 piezas entregadas a órdenes sin trazabilidad completa (DOC-04). Es exactamente el tipo de situación que justifica comprobar la información frente a su documentación original en el momento de la recepción.

---

## 7. Decisiones de definición tomadas en esta fase

La Fase 1 fijó una **definición de trabajo** para cada indicador. Al escribir la fórmula exacta ha habido que concretar algunos puntos. Ninguno cambia la arquitectura.

| Indicador | Definición de trabajo (Fase 1) | Definición final | Motivo |
|---|---|---|---|
| **DOC-02** | Todas las verificaciones | Se excluyen las auditorías internas | Las auditorías se dirigen a donde hay más riesgo y encuentran algo en el 38–45 % de los casos. Mezclarlas con las comprobaciones rutinarias distorsiona el indicador. Sus hallazgos ya se miden como no conformidades de origen "auditoría interna". Con auditorías: 10,0 %; sin ellas: 8,3 % |
| **QUA-04** | "Cerradas" / que vencían en el periodo | Implantadas (`completed_date`) en plazo / que vencían en el periodo | El cierre formal llega semanas después, tras la verificación de eficacia. Medir el cierre formal contra la fecha límite de implantación castigaría el buen trabajo de verificar la eficacia |
| **QUA-06** | Sin cerrar con fecha límite anterior a la fecha | Sin **implantar**, con la fecha límite **vigente en esa fecha** | Coherencia con QUA-04, y medición correcta del pasado (sección 2.3) |
| **DOC-04** | Salidas con lote, certificado y orden | Certificado solo si el material lo exige; número de serie si es serializado | Una arandela estándar no lleva certificado individual. Exigirlo a todo daría falsos incumplimientos |
| **INV-01** | Sin diferencia o dentro de la tolerancia | Tolerancia cero | Más simple y más exigente. Una tolerancia por tipo de material queda como mejora posible |
| **MNT-01** | Completadas a tiempo / con fin previsto en el periodo | Igual; las no terminadas cuentan como fuera de plazo | Concreta el caso de las órdenes abiertas |
| **Todos** | — | Se excluyen las no conformidades y órdenes canceladas | Una cancelación indica un registro hecho por error |
| **Reglas K** | K01–K04 | Se añade **K05** | Ver sección 5. El documento `03` está actualizado (87 reglas) |

---

## 8. Archivos de esta fase

Todos están en la carpeta del proyecto.

| Archivo | Novedad |
|---|---|
| `sql/kpi/*.sql` | Nuevos: 18 archivos, uno por indicador |
| `sql/views/11_vw_kpi_periods.sql` | Nuevo: calendario de los indicadores (vista número 14) |
| `scripts/run_kpis.py` | Nuevo: cálculo, controles K, semáforo e informes |
| `scripts/run_pipeline.py` | Actualizado: paso 3, indicadores |
| `config/settings.py` | Actualizado: ruta `SQL_KPI_DIR` |
| `tests/test_kpis.py` | Nuevo: 29 pruebas |
| `tests/test_validations.py` | Ajustado: ahora hay 14 vistas |
| `reports/kpi_report.md` | Generado: informe de indicadores |
| `reports/kpi_summary.csv`, `reports/kpi_values.csv` | Generados: se abren en Excel |
| `reports/validation_*` | Regenerados (sin cambios en los resultados) |
| `documentation/07_fase6_indicadores.md` | Este documento |
| `documentation/03_reglas_de_negocio.md`, `06_fase5_consultas_y_validaciones.md`, `README.md` | Actualizados |

---

## 9. Cómo comprobar que funciona

En **PowerShell**, desde la carpeta del proyecto, con el entorno virtual activado (`(.venv)` al principio de la línea).

### Paso 1 — Proceso completo

```powershell
python scripts/run_pipeline.py
```

Al final debe aparecer el paso 3, con los 18 indicadores y su estado:

```text
INFO    | STEP 3/3 — Indicators (KPI checks)
INFO    | DOC-01 Document Compliance Rate                       94.4 %  AMBER
INFO    | DOC-02 Documentation Error Rate                        8.3 %  RED
...
INFO    | QUA-06 Overdue Corrective Actions                          2  AMBER
INFO    | KPI checks: K01 ok, K02 ok, K04 ok, K05 ok
INFO    | Reports written to reports
INFO    | KPI CHECKS PASSED
INFO    | PIPELINE OK
```

`RED` o `AMBER` no son errores del programa: son el estado del indicador frente a su objetivo ficticio. Lo importante son las tres últimas líneas.

Para recalcular solo los indicadores, con la base de datos ya generada:

```powershell
python scripts/run_kpis.py
```

### Paso 2 — Leer el informe

Abre `reports/kpi_report.md` en VS Code y pulsa `Ctrl + Mayús + V`. Verás los semáforos por área, la comparación entre años, los controles K y los últimos 12 meses. Para trabajar con los números, abre `reports/kpi_values.csv` en Excel y crea una tabla dinámica con `kpi_id` en filas y `period` en columnas.

### Paso 3 — Pruebas

```powershell
pytest -v
```

Resultado esperado: **`106 passed`** (25 + 28 + 24 de las fases anteriores y 29 de esta fase). Tarda unos 20 segundos.

### Paso 4 — Un indicador en DB Browser

1. Abre `database/aqmi.db` en DB Browser for SQLite.
2. Pestaña **Ejecutar SQL** → **Abrir archivo SQL** → `sql/kpi/QUA06_overdue_corrective_actions.sql`.
3. **Ejecutar todo**.

Verás 25 filas: las acciones vencidas al final de cada mes y la fila TOTAL con el valor **2**. Es el mismo número que da la regla C10 de la Fase 5, calculado por otro camino.

---

## 10. Limitaciones generales

| Limitación | Consecuencia |
|---|---|
| **Efecto de arranque** | La empresa simulada empieza el 01/11/2024 sin no conformidades ni acciones antiguas. Los primeros meses de QUA-02, QUA-04, QUA-05 y QUA-06 no son comparables con el resto |
| **Valores mensuales con poca base** | Hay pocos casos al mes (unas 6 no conformidades, 17 recuentos, 6 acciones con vencimiento). Un solo caso mueve mucho el porcentaje: las tendencias deben leerse por trimestre o año, no mes a mes |
| **El periodo completo mezcla el antes y el después** | El valor TOTAL de 24 meses incluye la etapa anterior a las mejoras. Por eso el informe muestra también el año 1 y el año 2 |
| **Objetivos ficticios** | Son decisiones de una empresa inventada, no referencias del sector ni requisitos normativos |
| **Datos sintéticos** | Los hallazgos de la sección 6 demuestran la capacidad de análisis del sistema, no describen una organización real |
| **SQL específico de SQLite** | Usa `julianday()`, `date()` y CTE recursivas; habría que adaptarlo si se migra a PostgreSQL |
