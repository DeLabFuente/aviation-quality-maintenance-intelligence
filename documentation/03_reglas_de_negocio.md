# AQMI — Fase 2: Reglas de negocio y de integridad

**Proyecto:** Aviation Quality & Maintenance Intelligence (AQMI)
**Documento:** `documentation/03_reglas_de_negocio.md`
**Documento relacionado:** `documentation/02_diccionario_de_datos.md`
**Estado:** Aprobado el 17/11/2026 (ampliado en la Fase 9: grupo L, lecciones aprendidas, sección 7 bis)
**Fecha:** 17/11/2026

> Las reglas marcadas como **política interna ficticia** son decisiones inventadas para AEROQ MRO con fines demostrativos. **No son requisitos normativos.**

---

## 1. Cómo se controla cada regla

| Mecanismo | Qué es | Cuándo actúa |
|---|---|---|
| **PK / FK / UQ** | Clave primaria, clave externa, valor único | La base de datos rechaza el registro al insertarlo |
| **CHECK** | Condición sobre los campos de un mismo registro | La base de datos rechaza el registro al insertarlo |
| **ÍNDICE PARCIAL** | Unicidad que solo se aplica a ciertos registros | La base de datos rechaza el registro al insertarlo |
| **TRIGGER** | Acción automática ante un cambio | Al insertar, modificar o borrar |
| **VALIDACIÓN** | Consulta SQL o comprobación en Python sobre varios registros o tablas | Al ejecutar `run_validations.py` (Fase 5) |

**Gravedad de un fallo de validación:**

| Gravedad | Significado | Efecto en el pipeline |
|---|---|---|
| **CRITICAL** | Los datos son incoherentes; un indicador calculado sobre ellos sería falso | **Detiene la exportación a Power BI** (puerta de calidad) |
| **WARNING** | Registro incompleto o discrepancia de negocio que la oficina de calidad debe revisar | Se informa en el informe de validación y se muestra en la página Audit & Traceability |

> **Propuesta para la Fase 4.** Las reglas WARNING representan lo que una oficina de calidad encuentra en la realidad: registros incompletos, una revisión obsoleta usada por error, un certificado que falta. Propongo que el generador **siembre deliberadamente un número pequeño y documentado** de estas discrepancias, para que el sistema demuestre que las detecta. Las reglas CRITICAL, en cambio, deben dar siempre 0 fallos.

**Tipo de regla:** **E** = integridad estructural · **N** = lógica de negocio · **P** = política interna ficticia de AEROQ MRO.

---

## 2. Reglas generales (G)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| G01 | Toda clave externa apunta a un registro existente | E | FK + `PRAGMA foreign_keys = ON` + validación | CRITICAL |
| G02 | Los códigos de negocio son únicos y siguen su formato | E | UQ + CHECK (`GLOB`) | CRITICAL |
| G03 | Las fechas y fechas-hora tienen formato ISO válido | E | CHECK (`date(x) IS x`) | CRITICAL |
| G04 | Ningún evento es posterior a la fecha de corte (`AS_OF_DATE`) | N | VALIDACIÓN | CRITICAL |
| G05 | Ningún evento operativo es anterior al inicio del periodo (`PERIOD_START`) | N | VALIDACIÓN | WARNING |
| G06 | Toda persona que actúa en un registro estaba de alta en esa fecha | N | VALIDACIÓN | CRITICAL |
| G07 | Los campos booleanos solo valen 0 o 1 | E | CHECK | CRITICAL |
| G08 | `Inventory_Movements` y `Audit_Log` no admiten modificaciones ni borrados | P | TRIGGER | CRITICAL |
| G09 | Ningún registro de negocio se borra físicamente | P | FK `ON DELETE RESTRICT` + TRIGGER | CRITICAL |
| G10 | Los registros de operación tienen `created_by` | E | NOT NULL | CRITICAL |
| G11 | No hay duplicados lógicos (mismo contenido con distinto código, p. ej. dos incidencias idénticas el mismo día) | N | VALIDACIÓN | WARNING |

## 3. Control documental (D)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| D01 | Un documento tiene como máximo una revisión vigente (CURRENT) | N | ÍNDICE PARCIAL | CRITICAL |
| D02 | Fechas de revisión ordenadas: emisión ≤ entrada en vigor ≤ revisión prevista; entrada en vigor ≤ sustitución | N | CHECK | CRITICAL |
| D03 | SUPERSEDED si y solo si tiene fecha de sustitución | N | CHECK | CRITICAL |
| D04 | Quien aprueba una revisión no es quien la preparó | P | CHECK | CRITICAL |
| D05 | Toda revisión que no sea borrador tiene aprobador | N | CHECK | CRITICAL |
| D06 | Las revisiones de un documento no se solapan: la nueva entra en vigor el día en que se sustituye la anterior | N | VALIDACIÓN | CRITICAL |
| D07 | Un registro de aeronave (AIRCRAFT_RECORD) está asociado a una aeronave | N | CHECK | CRITICAL |
| D08 | Un documento controlado tiene periodicidad de revisión, y su revisión vigente tiene fecha de revisión prevista | P | CHECK + VALIDACIÓN | CRITICAL |
| D09 | Una verificación con resultado distinto de CONFORM describe la discrepancia | N | CHECK | CRITICAL |
| D10 | Una verificación NON_CONFORM está vinculada a una no conformidad | P | VALIDACIÓN | CRITICAL |
| D11 | Una verificación es posterior a la emisión de la revisión verificada | N | VALIDACIÓN | CRITICAL |
| D12 | Revisión vigente con fecha de revisión vencida (documento caducado) | N | VALIDACIÓN | WARNING |

## 4. Órdenes de mantenimiento (M)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| M01 | Fin previsto ≥ apertura | N | CHECK | CRITICAL |
| M02 | COMPLETED o CLOSED si y solo si hay fecha real de fin | N | CHECK | CRITICAL |
| M03 | CLOSED si y solo si hay fecha y responsable de cierre; cierre ≥ fin real | N | CHECK | CRITICAL |
| M04 | CANCELLED si y solo si hay motivo de cancelación | N | CHECK | CRITICAL |
| M05 | ON_HOLD si y solo si la orden tiene al menos un bloqueo activo | N | VALIDACIÓN | CRITICAL |
| M06 | Como máximo un bloqueo activo por motivo en cada orden | N | ÍNDICE PARCIAL | CRITICAL |
| M07 | Un bloqueo por MATERIAL indica el material; uno por DOCUMENTATION indica el documento | N | CHECK | CRITICAL |
| M08 | Un bloqueo por material corresponde a una falta real de stock en su fecha de inicio (lo declarado coincide con los datos) | N | VALIDACIÓN | WARNING |
| M09 | Una orden solo usa revisiones vigentes en la fecha en que se asociaron (es obsoleta la revisión cuya fecha de sustitución es anterior a la fecha de asociación) | N | VALIDACIÓN | WARNING |
| M10 | La fecha en que se necesita un material está entre la apertura y el fin previsto de la orden | N | VALIDACIÓN | CRITICAL |
| M11 | Una orden COMPLETED o CLOSED ha recibido todo el material necesario, descontadas las devoluciones | N | VALIDACIÓN | CRITICAL |
| M12 | Las fechas de la orden están dentro del contrato de la aeronave | N | VALIDACIÓN | CRITICAL |
| M13 | No se cierra (CLOSED) una orden con una no conformidad CRITICAL abierta vinculada | P | VALIDACIÓN | CRITICAL |
| M14 | Los bloqueos de una orden están dentro de sus fechas | N | VALIDACIÓN | CRITICAL |

## 5. Materiales y almacén (I)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| I01 | Cada tipo de movimiento usa sus estados de origen y destino (matriz del diccionario, sección 6.6) | N | CHECK | CRITICAL |
| I02 | Cada tipo de movimiento lleva sus referencias obligatorias (orden, línea de pedido, incidencia, recuento, motivo) | N | CHECK | CRITICAL |
| I03 | Ningún estado de stock es negativo en ningún momento (saldo acumulado) | N | VALIDACIÓN | CRITICAL |
| I04 | Lo recibido acumulado de una línea no supera lo pedido | N | VALIDACIÓN | CRITICAL |
| I05 | No hay recepciones anteriores a la fecha del pedido, ni fechas comprometidas anteriores al pedido | N | VALIDACIÓN | CRITICAL |
| I06 | Solo se reserva o entrega material previsto en la orden y mientras la orden está abierta | N | VALIDACIÓN | CRITICAL |
| I07 | El lote entregado a una orden existe como lote recibido del mismo material (por recepción o como saldo inicial de la puesta en marcha) | N | VALIDACIÓN | CRITICAL |
| I08 | Los materiales serializados se mueven de unidad en unidad y con número de serie | N | VALIDACIÓN | CRITICAL |
| I09 | La recepción de un material que exige certificado lleva su referencia | P | VALIDACIÓN | WARNING |
| I10 | Los materiales medidos en unidades (EA) solo tienen cantidades enteras | N | VALIDACIÓN | CRITICAL |
| I11 | El stock "según sistema" de un recuento coincide con el stock calculado en ese momento (excepto el recuento de apertura) | N | VALIDACIÓN | CRITICAL |
| I12 | Todo recuento con diferencia tiene un ajuste por la misma cantidad y un comentario | N | VALIDACIÓN | CRITICAL |
| I13 | No hay pedidos a un proveedor suspendido después de su suspensión | P | VALIDACIÓN | CRITICAL |
| I14 | Un movimiento a NON_CONFORMING está vinculado a una incidencia de la categoría "Material no conforme" | N | VALIDACIÓN | CRITICAL |
| I15 | No se entrega a una orden material con la caducidad vencida en la fecha de entrega | N | VALIDACIÓN | CRITICAL |
| I16 | Material por debajo del mínimo sin pedido pendiente. Cuenta el stock disponible más el que está en inspección de recepción (cuarentena), que ya está en casa (precisado en la Fase 5) | N | VALIDACIÓN | WARNING |

## 6. No conformidades (Q)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| Q01 | CLOSED o CANCELLED si y solo si hay fecha de cierre; cierre ≥ detección | N | CHECK | CRITICAL |
| Q02 | Una incidencia CLOSED tiene responsable de cierre y resumen de medidas | N | CHECK | CRITICAL |
| Q03 | Las incidencias CRITICAL y MAJOR tienen acción de contención | P | CHECK | CRITICAL |
| Q04 | Las incidencias CRITICAL y MAJOR tienen análisis de causa raíz | P | VALIDACIÓN | CRITICAL |
| Q05 | Una incidencia CLOSED tiene todas sus acciones correctivas cerradas o canceladas | N | VALIDACIÓN | CRITICAL |
| Q06 | Una incidencia CLOSED (salvo OBSERVATION) tiene al menos una acción correctiva | P | VALIDACIÓN | WARNING |
| Q07 | Si la incidencia indica orden y aeronave, la aeronave es la de la orden | N | VALIDACIÓN | CRITICAL |
| Q08 | La incidencia está vinculada al menos a un objeto (aeronave, orden, revisión, material, proveedor o línea de pedido) | N | VALIDACIÓN | WARNING |
| Q09 | El análisis de causa raíz es posterior a la detección y anterior al cierre | N | VALIDACIÓN | CRITICAL |
| Q10 | Con 5 porqués, `why_1` es obligatorio y no hay huecos en la cadena | N | CHECK | CRITICAL |
| Q11 | Con Ishikawa, la categoría 6M es obligatoria | N | CHECK | CRITICAL |
| Q12 | Incidencia abierta con la fecha objetivo de cierre superada | N | VALIDACIÓN | WARNING |
| Q13 | Coherencia categoría–objeto: SUP implica proveedor o línea de pedido; INV implica material; DOC y TRC implican revisión u orden | N | VALIDACIÓN | WARNING |

## 7. Acciones correctivas y preventivas (C)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| C01 | Una acción correctiva tiene incidencia; origen INCIDENT si y solo si hay incidencia | N | CHECK | CRITICAL |
| C02 | El prefijo del número (CA/PA) coincide con el tipo | E | CHECK | CRITICAL |
| C03 | Fechas límite ≥ fecha de creación; la acción se crea en o después de la detección de la incidencia | N | CHECK + VALIDACIÓN | CRITICAL |
| C04 | Una acción CLOSED tiene resultado, fecha y responsable de la verificación de eficacia | N | CHECK | CRITICAL |
| C05 | Quien verifica la eficacia no es el responsable de la acción | P | CHECK | CRITICAL |
| C06 | Orden de fechas: creación ≤ implantación ≤ verificación de eficacia ≤ cierre | N | CHECK | CRITICAL |
| C07 | El avance no disminuye con el tiempo y llega al 100 % antes de COMPLETED | N | VALIDACIÓN | CRITICAL |
| C08 | Una acción cerrada como NOT_EFFECTIVE tiene una acción de seguimiento (`parent_action_id`) | P | VALIDACIÓN | WARNING |
| C09 | La fecha límite vigente no es anterior a la inicial (solo se permiten ampliaciones) | P | CHECK | CRITICAL |
| C10 | Acción abierta con la fecha límite superada (acción vencida) | N | VALIDACIÓN | WARNING |
| C11 | Los avances están entre la creación y el cierre de la acción | N | VALIDACIÓN | CRITICAL |

## 7 bis. Lecciones aprendidas (L) — Fase 9

El registro de lecciones aprendidas (`Lessons_Learned`) cierra el ciclo de mejora: lo aprendido al tratar una acción se convierte en un cambio de un documento controlado. Es una **práctica general de gestión de la calidad** que AEROQ MRO aplica de forma voluntaria; **no se presenta como un requisito normativo**.

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| L01 | Una lección solo se propone a partir de una acción **cerrada y con la eficacia verificada**, en su fecha de cierre o después. Las acciones NOT_EFFECTIVE también dejan lección | N | VALIDACIÓN | CRITICAL |
| L02 | Quien aprueba o rechaza una lección no es quien la propuso | P | CHECK | CRITICAL |
| L03 | El estado coincide con la decisión registrada: APPROVED e INCORPORATED tienen aprobación; REJECTED tiene rechazo **con motivo**; INCORPORATED tiene revisión y fecha de incorporación | N | CHECK | CRITICAL |
| L04 | Orden de fechas: propuesta ≤ decisión ≤ incorporación | N | CHECK | CRITICAL |
| L05 | La revisión incorporada pertenece a un documento **controlado** de tipo procedimiento, instrucción de trabajo o formulario | P | VALIDACIÓN | CRITICAL |
| L06 | La revisión incorporada estaba **en vigor** en la fecha de incorporación y entró en vigor **después de la aprobación** de la lección. *Excepción (decisión aprobada en la Fase 9):* la revisión que es el resultado de la propia acción (en vigor entre la creación y el cierre de la acción) | N | VALIDACIÓN | CRITICAL |
| L07 | Lección aprobada sin incorporar a ningún documento más de 90 días después de su aprobación (**política interna ficticia**) | P | VALIDACIÓN | WARNING |

Las reglas generales también cubren la tabla nueva: formato y unicidad de `lesson_number` (G02), fechas válidas (G03), ninguna fecha posterior al corte (G04) ni anterior al inicio del periodo (G05), personas de alta en la fecha en que actúan (G06), autor del registro (G10), auditoría de creación y de cambios de estado (A01, A02, A03) y eventos que apuntan a registros existentes (A05). El borrado físico está bloqueado por trigger (G09).

## 8. Auditoría y trazabilidad (A)

| ID | Regla | Tipo | Mecanismo | Gravedad |
|---|---|---|---|---|
| A01 | Todo registro de operación tiene su evento INSERT en `Audit_Log` | N | VALIDACIÓN | WARNING |
| A02 | Todo cambio de estado de incidencias, acciones, órdenes y lecciones aprendidas tiene su evento UPDATE | N | VALIDACIÓN | WARNING |
| A03 | La cadena de cambios de un campo es coherente: el valor nuevo de un evento es el valor anterior del siguiente, y el último coincide con el valor actual | N | VALIDACIÓN | CRITICAL |
| A04 | No existe ningún evento DELETE | P | VALIDACIÓN | CRITICAL |
| A05 | `Audit_Log.record_id` apunta a un registro existente de `table_name` | E | VALIDACIÓN | CRITICAL |

## 9. Reglas de los indicadores (K)

Se registraron en la Fase 2 para que el diseño las tuviera en cuenta. **Desde la Fase 6** las ejecuta `scripts/run_kpis.py` (K01, K02, K04 y K05); K03 se comprueba en la Fase 9. Detalle en el documento `07_fase6_indicadores.md`.

| ID | Regla | Mecanismo | Gravedad |
|---|---|---|---|
| K01 | Todo porcentaje está entre 0 y 100 | VALIDACIÓN | CRITICAL |
| K02 | Ningún KPI se calcula con denominador 0 sin tratamiento explícito (se muestra "sin datos", no 0 %) | VALIDACIÓN | CRITICAL |
| K03 | El valor de cada KPI en Power BI coincide con su consulta SQL de referencia | Prueba manual documentada (Fase 9) | CRITICAL |
| K04 | La suma por categorías coincide con el total (p. ej. incidencias por categoría = total de incidencias) | VALIDACIÓN | CRITICAL |
| K05 | Cada indicador de "foto a fecha", reconstruido desde la historia y la auditoría, coincide en la fecha de corte con el estado actual de los datos (añadida en la Fase 6) | VALIDACIÓN | CRITICAL |

## 10. Resumen

| Grupo | Reglas | Controladas por la base de datos | Controladas por validación |
|---|---|---|---|
| G — Generales | 11 | 7 | 4 |
| D — Documentos | 12 | 7 | 5 |
| M — Órdenes | 14 | 6 | 8 |
| I — Materiales | 16 | 2 | 14 |
| Q — No conformidades | 13 | 5 | 8 |
| C — CAPA | 11 | 6 | 5 |
| L — Lecciones aprendidas (Fase 9) | 7 | 4 | 3 |
| A — Auditoría | 5 | 0 | 5 |
| K — Indicadores | 5 | 0 | 5 |
| **Total** | **94** | **37** | **57** |

*(En algunas reglas actúan los dos mecanismos; se cuentan en el principal.)*

**Estado tras la Fase 5.** Las 82 reglas de los grupos G a A tienen su propia consulta en `sql/validation/` (un archivo por regla) y aparecen en el informe de validación (`reports/validation_report.md`) con su identificador, su gravedad y los registros que la incumplen. Las reglas que ya impone la base de datos también se comprueban con una consulta: así el control no depende de que el mecanismo de la base de datos esté activo. Las reglas K se implementaron en la Fase 6, junto con los indicadores (K03 se comprobará en la Fase 9); en esa fase se añadió la regla K05. El funcionamiento se explica en el documento `06_fase5_consultas_y_validaciones.md`.

**Estado tras la Fase 9.** Se añaden las 7 reglas del grupo L (lecciones aprendidas). El informe de validación ejecuta ahora **89 reglas** (grupos G a A). Ver `09b_fase9_lecciones_aprendidas.md`.
