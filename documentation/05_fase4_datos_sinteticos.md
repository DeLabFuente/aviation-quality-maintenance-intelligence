# AQMI — Fase 4: Generación de datos sintéticos coherentes

**Documento:** `documentation/05_fase4_datos_sinteticos.md`
**Estado:** Aprobada
**Fecha:** 17/11/2026

> AEROQ MRO es una empresa ficticia. Todos los datos de esta fase son sintéticos: personas, aeronaves, proveedores, números de pieza, documentos y textos son inventados. Las tasas, plazos y objetivos son **valores ficticios de la empresa**, no referencias del sector ni requisitos normativos.

---

## Índice

1. Qué se ha construido
2. Cómo funciona el simulador
3. Qué ocurre en la empresa simulada
4. Cuatro historias visibles en los datos
5. Discrepancias sembradas a propósito
6. Volúmenes obtenidos
7. Archivos de esta fase
8. Cómo ejecutarlo y qué debe aparecer
9. Cómo comprobar que funciona
10. Simplificaciones y limitaciones
11. Cambios en el diseño durante esta fase

---

## 1. Qué se ha construido

Un **generador de datos** que reproduce 24 meses de actividad de AEROQ MRO, del 01/11/2024 al 31/10/2026. No rellena las tablas con valores al azar: **simula la empresa día a día**. Cada registro nace de un hecho anterior.

Ejemplo real de una cadena del conjunto de datos:

> Se abre una orden → falta un material → se bloquea la orden → se lanza un pedido urgente → el proveedor entrega tarde → llega el material → inspección de recepción → se reserva y se entrega a la orden → termina el bloqueo → la orden se completa → producción revisa los registros frente al formulario original → detecta un error → se abre una no conformidad → análisis de 5 porqués → acción correctiva → avances → verificación de eficacia → cierre.

Cada paso queda en su tabla. El registro de auditoría lo escriben los triggers de la Fase 3, con la fecha y el autor de cada hecho.

---

## 2. Cómo funciona el simulador

### 2.1 Simulación por eventos

Cada hecho es un **evento** con fecha y hora: "abrir orden", "recibir pedido", "verificar eficacia"… Los eventos se guardan en una cola y se ejecutan **estrictamente en orden cronológico**. Un evento puede programar otros futuros; por ejemplo, al crear un pedido se programa su entrega.

Gracias a ese orden:

- el stock se calcula siempre en el momento correcto, así que nunca es negativo;
- las modificaciones de cada registro van en orden de fecha, como exigen los triggers;
- la auditoría resultante es idéntica a la que produciría un sistema real.

### 2.2 Reproducible

Todo el azar sale de una **semilla fija** (`RANDOM_SEED = 145` en `config/settings.py`). Con la misma semilla se obtienen **exactamente los mismos datos**, registro a registro; una prueba automática lo comprueba. Con otra semilla se obtiene otra empresa igual de coherente.

### 2.3 Parámetros

Las tasas y probabilidades están en `config/generator_parameters.py`, comentadas una a una: frecuencia de órdenes, retrasos de proveedores, probabilidad de error en registros, etc. Cambiar un parámetro cambia la historia que cuentan los datos sin tocar el código.

---

## 3. Qué ocurre en la empresa simulada

### 3.1 Puesta en marcha (01/11/2024, 08:00)

Se cargan los datos maestros, como en la migración de un sistema real:

| Elemento | Detalle |
|---|---|
| Personal | 44 empleados en 6 departamentos (2 incorporaciones y 1 baja durante el periodo) |
| Clientes y flota | 4 operadores ficticios y 12 helicópteros. EC-Q12 se incorpora en junio de 2025; el contrato de EC-Q04 termina en marzo de 2026 |
| Proveedores | 40, de los cuales 30 aprobados, 4 condicionados, 2 suspendidos y 4 inactivos (lista interna ficticia) |
| Materiales | 100 referencias. Stock mínimo y cantidad de pedido calculados a partir de la demanda esperada (política ficticia) |
| Documentos | 250, con su historial de revisiones anteriores |
| Stock inicial | Un recuento de apertura por material (tipo `OPENING`) y su ajuste de entrada, con lotes y certificados |

### 3.2 Actividad diaria

| Área | Qué se simula |
|---|---|
| **Órdenes** | Programadas cada 40–52 días por aeronave, no programadas aleatorias (con prioridad URGENT o AOG) y modificaciones ocasionales. Cada orden lleva entre 1 y 4 materiales y 4 documentos: instrucción de trabajo, datos técnicos, formulario de cierre y libro de la aeronave |
| **Materiales** | Reserva al empezar el trabajo, entrega por lotes (los más antiguos primero), devoluciones de sobrantes a cuarentena y reserva de nuevo cuando llega el material que faltaba |
| **Bloqueos** | Por falta de material, por documento caducado (se pide una revisión urgente) o por datos técnicos no disponibles. El trabajo se detiene y la orden se retrasa |
| **Compras** | Revisión semanal de stock (lunes). Se agrupan en un pedido las referencias de un mismo proveedor que están cerca del mínimo. Pedidos urgentes cuando una orden se bloquea. Entregas parciales, retrasos y alguna cancelación |
| **Recepción** | Toda entrada pasa por cuarentena e inspección. Si se rechaza, se abre una no conformidad, el material pasa a no conforme y después se da de baja |
| **Recuentos** | 4 referencias cada martes, en rotación. Las diferencias se ajustan con un movimiento trazado y, si son significativas, generan una no conformidad |
| **Documentos** | Revisión periódica según su vencimiento: confirmación, nueva revisión (borrador y después vigente) o hallazgo. Algunas revisiones se olvidan, y esos documentos acaban caducados |
| **Cierre de órdenes** | Producción revisa los registros de la orden frente al formulario original (`RECORD_VS_SOURCE`). Es la tarea de comprobación que caracteriza una oficina de calidad y producción |
| **Calidad** | No conformidades de 8 fuentes, análisis de causa raíz (obligatorio en CRITICAL y MAJOR), acciones correctivas con avances, ampliaciones de plazo, verificación de eficacia por una persona distinta del responsable y acciones de seguimiento cuando una acción no resulta eficaz |
| **Auditorías internas** | Cada trimestre se revisan entre 4 y 6 procedimientos, con 1 a 3 hallazgos |
| **Revisión por la dirección** | Cada trimestre se crean acciones preventivas a partir del análisis de tendencias |

### 3.3 Objetivos internos de cierre (ficticios)

| Gravedad | Días para cerrar una no conformidad |
|---|---|
| CRITICAL | 45 |
| MAJOR | 75 |
| MINOR | 90 |
| OBSERVATION | 30 |

Con estos objetivos, el 59 % de las no conformidades cerradas se cierra a tiempo. Es un valor intermedio, adecuado para que el indicador sea informativo.

---

## 4. Cuatro historias visibles en los datos

Son patrones introducidos a propósito para que el análisis de la Fase 7 tenga algo que descubrir. Están documentados para que nadie los confunda con una casualidad.

| Historia | Antes de la medida | Medida (CAPA) | Después |
|---|---|---|---|
| **Proveedor que entrega tarde** (SUP-006) | ~82 % de entregas tardías, frente a ~25 % del resto | Revisión de dirección de octubre de 2025: plan de mejora (PA) y proveedor CONDITIONAL | ~28 % de entregas tardías; el proveedor vuelve a APPROVED a finales de noviembre de 2025 |
| **Formulario de cierre mal diseñado** (FRM-PRD-004) | ~16 % de registros con discrepancias al revisarlos | Primera no conformidad de registro analizada desde abril de 2025: acción correctiva y rediseño del formulario (revisión R01, mayo de 2025) | ~6 % de registros con discrepancias |
| **Recuentos de piezas estándar** | ~30 % de recuentos con diferencias, frente a ~6 % del resto | Revisión de dirección de julio de 2025: revisión del procedimiento PRO-LOG-004 (R03, agosto de 2025) | ~5 % de recuentos con diferencias, igual que el resto |
| **Aeronave con más averías** (EC-Q07) | El 75 % de sus órdenes son no programadas, frente al 53 % del resto | — (dato para la comparativa de flota) | — |

Cada medida aparece en los datos como acción (CAPA), con sus avances, su cierre y, cuando corresponde, la nueva revisión del documento. **La causa y el efecto son trazables.**

---

## 5. Discrepancias sembradas a propósito

Una oficina de calidad real encuentra registros incompletos y errores. Para demostrar que los controles de la Fase 5 los detectan, el generador introduce **exactamente 9 discrepancias** controladas y las anota en `data/synthetic/planted_discrepancies.csv`:

| Tipo | Cantidad | Regla que debe detectarla |
|---|---|---|
| Orden asociada a una revisión ya sustituida de una instrucción de trabajo (2 se detectan en la revisión de registros y generan una no conformidad; 1 pasa sin detectar) | 3 | M09 |
| Recepción de material que exige certificado, registrada sin referencia de certificado | 2 | I09 |
| Bloqueo por material registrado cuando el material sí estaba disponible | 2 | M08 |
| Hallazgo de auditoría registrado sin referencia al procedimiento auditado | 2 | Q08 |

En la Fase 5 compararemos lo que encuentran las validaciones con este archivo. Si coinciden, queda demostrado que **el sistema detecta lo que debe detectar**.

Además aparecen discrepancias **naturales**, consecuencia de la propia simulación: documentos caducados porque se olvidó su revisión, no conformidades abiertas fuera de plazo y acciones vencidas. Son exactamente lo que miden los indicadores.

---

## 6. Volúmenes obtenidos

| Tabla | Referencia inicial | Obtenido | Comentario |
|---|---|---|---|
| Aircraft | 12 | 12 | |
| Maintenance_Orders | 500 | 491 | Volumen resultado de la simulación |
| Quality_Incidents | 150 | 143 | Volumen resultado de la simulación |
| Documents | 250 | 250 | 602 revisiones en total |
| Materials | 100 | 100 | |
| Inventory_Movements | 600 → ~3.000 (D3) | 3.695 | Reserva y entrega de ~1.190 líneas de material, más recepciones, inspecciones, ajustes y apertura |
| Purchase_Orders | 120 | 173 | 341 líneas, unas 2 por pedido. Ver el comentario |
| Suppliers | 40 | 40 | |
| CAPA_Actions | — | 165 | 144 correctivas y 21 preventivas |
| Document_Verifications | — | 808 | |
| Stock_Counts | — | 516 | 100 de apertura y 416 cíclicos |
| Maintenance_Order_Holds | — | 93 | 76 por material y 17 por documentación |
| Audit_Log | — | 17.383 | Escrito por los triggers |

**Sobre los 173 pedidos.** Para llegar a 120 habría que pedir cantidades mayores (más stock inmovilizado) o aceptar más faltas de material. Con la política actual, solo el 15,5 % de las órdenes se bloquea por material. Los 120 pedidos de la referencia inicial eran orientativos y la diferencia está justificada.

---

## 7. Archivos de esta fase

| Archivo | Qué es |
|---|---|
| `config/generator_parameters.py` | Todas las tasas y probabilidades (ficticias), comentadas |
| `scripts/generate_data.py` | **Comando principal**: crea la base de datos, simula, comprueba y exporta |
| `scripts/generator/engine.py` | Motor de simulación: reloj, cola de eventos y escritura en la base de datos |
| `scripts/generator/catalogs.py` | Catálogos inventados: nombres, 100 materiales, 250 documentos, plantillas de textos |
| `scripts/generator/staff.py` | Personal, clientes, flota y proveedores |
| `scripts/generator/documents.py` | Documentos, revisiones, revisiones periódicas y verificaciones |
| `scripts/generator/inventory.py` | Lotes, movimientos, compras, recepciones y recuentos |
| `scripts/generator/maintenance.py` | Órdenes, materiales, documentos usados, bloqueos y cierre |
| `scripts/generator/quality.py` | No conformidades, causa raíz, CAPA, auditorías y revisiones de dirección |
| `scripts/generator/world.py` | Conecta los módulos y pone en marcha la simulación |
| `tests/test_data_generation.py` | 28 pruebas de esta fase |
| `data/synthetic/*.csv` | Las 24 tablas exportadas (se abren en Excel) y la lista de discrepancias sembradas |
| `sql/schema/01_tables.sql` | Actualizado: tipo de recuento `OPENING` |

---

## 8. Cómo ejecutarlo y qué debe aparecer

Requisito: haber completado la guía de la Fase 3 (entorno virtual activo, `(.venv)` visible).

```
python scripts/generate_data.py
```

Tarda unos segundos. **Resultado esperado** (resumen):

```
INFO    | Database built: 24 tables, 62 indexes, 86 triggers, ...
INFO    | Simulation finished: 6xxx events in 1.x s
INFO    | CSV files written to data\synthetic
INFO    | Records per table:
INFO    |   Maintenance_Orders                 491
INFO    |   Quality_Incidents                  143
INFO    |   Inventory_Movements               3695
INFO    |   Audit_Log                        17383
...
INFO    | Planted discrepancies (to be detected in Phase 5): 9
INFO    | GENERATION OK -> ...\database\aqmi.db
```

Los números deben ser **exactamente estos**, porque la semilla es fija. Si salen otros, algo ha cambiado en el código o en los parámetros.

> Este comando reconstruye la base de datos desde cero cada vez. No hace falta ejecutar antes `build_database.py`.

---

## 9. Cómo comprobar que funciona

### 9.1 Pruebas automáticas

```
pytest -v
```

Resultado esperado al cerrar la Fase 4: **`53 passed`** (25 de la Fase 3 y 28 de esta fase). Desde la Fase 5 el total es mayor (ver el documento 06). Tarda unos 15 segundos, porque genera los datos varias veces.

| Grupo de pruebas | Qué comprueban |
|---|---|
| Volúmenes | Cada tabla principal tiene un número de registros dentro del rango esperado |
| Reproducibilidad | La misma semilla da datos idénticos; una semilla distinta da datos distintos |
| Coherencia | Integridad y claves externas; ningún evento posterior a la fecha de corte; stock nunca negativo; el stock "según sistema" de cada recuento coincide con los movimientos; las órdenes completadas recibieron todo su material; estado ON_HOLD ⇔ bloqueo activo; no conformidades cerradas ⇒ acciones cerradas; cadena de auditoría continua; revisiones sin solapes |
| Discrepancias sembradas | Hay exactamente las configuradas |
| Historias | El proveedor mejora tras su plan; el rediseño del formulario reduce errores; EC-Q07 es la aeronave con más órdenes no programadas |

### 9.2 Revisión visual en Excel

Abre `data\synthetic\Quality_Incidents.csv` con Excel. Ordena por `detected_date` y comprueba, por ejemplo, que cada incidencia cerrada tiene `closed_date`, `closed_by` y `closure_summary`.

### 9.3 Seguir una historia en DB Browser

Abre `database\aqmi.db`, ve a **Execute SQL** y ejecuta esta consulta. Reconstruye el historial completo de la no conformidad que dio origen al rediseño del formulario de cierre:

```sql
SELECT a.event_datetime, a.action, a.field_name, a.old_value, a.new_value,
       e.first_name || ' ' || e.last_name AS who
FROM Audit_Log a
LEFT JOIN Employees e ON e.employee_id = a.changed_by
WHERE a.table_name = 'Quality_Incidents'
  AND a.record_id = (SELECT incident_id FROM CAPA_Actions
                     WHERE title LIKE 'Redesign the work order closure record%')
ORDER BY a.event_datetime, a.audit_id;
```

Verás la creación, cada cambio de estado (abierta → en investigación → plan de acción → implantación → verificación de eficacia → cerrada), quién lo hizo y cuándo. **Es el módulo F (Audit & Traceability) funcionando con datos.**

---

## 10. Simplificaciones y limitaciones

| Simplificación | Motivo |
|---|---|
| El trabajo solo se registra de lunes a viernes | Simplifica el calendario sin afectar a los indicadores |
| La reserva de material es "todo o nada" por línea | Evita reservas parciales, que no aportan valor al análisis |
| Las caducidades de los lotes son largas | Ningún lote caduca en almacén durante el periodo (regla I15) |
| No hay unidades reparables que vuelvan del taller | Queda fuera del alcance administrativo del proyecto |
| Los textos se eligen de plantillas | Son genéricos y administrativos a propósito: AQMI no contiene información técnica |
| Las cifras dependen de la semilla | Con otra semilla los volúmenes varían ligeramente, dentro de los rangos de las pruebas |

---

## 11. Cambios en el diseño durante esta fase

> **Nota (Fase 5).** Las cifras de este documento corresponden a los datos regenerados al final de la Fase 5, después de dos pequeñas correcciones del generador descritas en el documento `06`.

| Cambio | Motivo |
|---|---|
| Nuevo tipo de recuento `OPENING` en `Stock_Counts` | El stock inicial necesita un origen trazable. Se registra como un recuento de apertura con su ajuste, en lugar de aparecer "de la nada". El indicador *Inventory Accuracy* excluirá estos recuentos |
| Precisión de la regla M09 | Es obsoleta la revisión sustituida **antes** del día en que se asoció a la orden. Para evitar ambigüedades, las revisiones nuevas entran en vigor a las 07:45, antes de que empiece el trabajo |
| Precisión de las reglas I07 e I11 | Los lotes del saldo inicial cuentan como recibidos, y el recuento de apertura queda excluido de la comparación con el sistema |
| Objetivos internos de cierre: 45 / 75 / 90 / 30 días | Los valores provisionales (15 / 30 / 60 / 90) no eran compatibles con un ciclo que incluye la verificación de eficacia |

El diccionario de datos (`02`) y las reglas de negocio (`03`) están actualizados con estos cambios.
