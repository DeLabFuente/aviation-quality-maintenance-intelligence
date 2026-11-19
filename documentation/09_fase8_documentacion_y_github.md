# AQMI — Fase 8: Documentación y presentación en GitHub

**Documento:** `documentation/09_fase8_documentacion_y_github.md`
**Estado:** Propuesta pendiente de aprobación
**Fecha:** 19/11/2026

> AEROQ MRO es una empresa ficticia y todos sus datos son sintéticos. AQMI no está certificado y AEROQ MRO no tiene ninguna aprobación real.

---

## Índice

1. [Qué se ha construido](#1-qué-se-ha-construido)
2. [El README: qué pide el enunciado y dónde está](#2-el-readme-qué-pide-el-enunciado-y-dónde-está)
3. [El caso práctico](#3-el-caso-práctico)
4. [La comprobación previa a la publicación](#4-la-comprobación-previa-a-la-publicación)
5. [La integración continua (GitHub Actions)](#5-la-integración-continua-github-actions)
6. [El proyecto de Power BI en otro ordenador](#6-el-proyecto-de-power-bi-en-otro-ordenador)
7. [Privacidad: rutas personales y datos de autor](#7-privacidad-rutas-personales-y-datos-de-autor)
8. [Cómo se publica en GitHub](#8-cómo-se-publica-en-github)
9. [Después de publicar](#9-después-de-publicar)
10. [Archivos de esta fase](#10-archivos-de-esta-fase)
11. [Cómo comprobarlo](#11-cómo-comprobarlo)

---

## 1. Qué se ha construido

La Fase 8 convierte el proyecto en un repositorio que se puede publicar y que se entiende en pocos minutos:

| Pieza | Para qué sirve |
|---|---|
| **README nuevo, en inglés** | Es la portada del repositorio. Responde en este orden a lo que mira cada lector: qué es, qué demuestra, cómo está hecho, qué resultados da y cómo ejecutarlo |
| **Caso práctico** (`case_study_nonconformity.md`) | Sigue una no conformidad real de los datos desde su detección hasta su cierre verificado, y comprueba con datos que la acción funcionó |
| **Capturas de los 8 cuadros de mando** (`assets/screenshots/`) | Lo primero que ve quien abre el repositorio |
| **Comprobación previa a la publicación** (`scripts/check_release.py`) | 10 reglas que revisan el repositorio antes de hacerlo público |
| **Integración continua** (`.github/workflows/tests.yml`) | GitHub ejecuta todo el proceso y las pruebas en cada cambio, en Linux y en Windows |
| **Herramienta `set_powerbi_data_folder.py`** | Hace que Power BI encuentre los datos en cualquier ordenador |
| **Índice de la documentación** (`documentation/README.md`) | Una tabla con todos los documentos y su contenido |

Además:

- **El proyecto de Power BI de referencia es ahora el que guardó Power BI Desktop** en la primera apertura. El validador se ajustó a su formato, y una prueba comprueba en cada ejecución que esa versión sigue pasando todos los controles (detalle en la Fase 7, apartado 8).
- **Se han quitado las rutas personales** de la documentación (apartado 7).
- `requirements.txt` incluye ahora `jsonschema` y `referencing`, que el validador de Power BI ya usaba.

---

## 2. El README: qué pide el enunciado y dónde está

El enunciado del proyecto (apartado 11) pide un README en inglés con unas secciones concretas. La comprobación previa (regla R02) verifica que todas existen.

| Lo que pide el enunciado | Sección del README |
|---|---|
| Descripción del proyecto | *Overview* y *What this project demonstrates* |
| Objetivos | *Objectives* |
| Arquitectura | *Architecture* (diagrama Mermaid, que GitHub dibuja automáticamente) |
| Tecnologías | *Tech stack*, con el motivo de cada una |
| Funcionalidades | *Features* (módulos A a F) |
| Modelo de datos | *Data model* (diagrama entidad-relación simplificado) |
| Indicadores | *KPIs*: los 18 valores, con sus objetivos marcados como **ficticios** |
| Capturas de pantalla | Imagen principal y *Dashboards (screenshots)* |
| Instrucciones de instalación | *Getting started (installation)* |
| Metodología | *Methodology*: las 9 fases y los principios de trabajo |
| Limitaciones | *Limitations* |
| Aviso sobre datos sintéticos | Aviso al principio y *Synthetic data and disclaimer* al final |

Se han añadido otras cuatro secciones porque responden a lo que busca un responsable de calidad (Fase 1, apartado 13):

- ***Quality controls***: los controles que el proyecto aplica a sus propios datos. Es lo que más lo diferencia de otros portfolios.
- ***Case study*** y ***What the data shows***: demuestran que se entiende el proceso, no solo la herramienta. Los cuatro patrones introducidos a propósito se presentan como tales.
- ***Regulatory context***: la tabla de la Fase 1 que separa el contexto normativo real (con su fuente oficial) de la función demostrativa. Se usa siempre "illustrates", nunca "compliant with".
- ***About the author***: el texto propuesto en la Fase 1, apartado 13.3. Dice lo que hiciste y también lo que **no** eres (ni ingeniero ni técnico certificado).

---

## 3. El caso práctico

`documentation/case_study_nonconformity.md` cuenta, en inglés, la historia de **NC-2025-0021**:

1. Un error de registro detectado en una verificación documental (21/03/2025).
2. Análisis Ishikawa: la causa está en el **método** de trabajo (los registros se pasaban al final del turno).
3. Acción correctiva CA-2025-0028: rediseñar el formulario de cierre FRM-PRD-004.
4. Verificación de eficacia por una persona distinta del responsable y cierre en 60 días, dentro del plazo previsto.
5. **La prueba con datos:** las discrepancias en los registros de cierre pasan del 16,5 % con la revisión R00 al 5,1 % con la R01.
6. El rastro de auditoría completo, tal como lo devuelve la consulta 01 de la Fase 5.

El documento **no está escrito a mano**: lo genera `scripts/build_case_study.py` a partir de la base de datos. Una prueba vuelve a generarlo desde cero y comprueba que el archivo del repositorio es idéntico. Si un día cambian los datos, la prueba falla y obliga a regenerarlo. Así el caso práctico nunca puede contradecir a los datos.

---

## 4. La comprobación previa a la publicación

Antes de publicar, `scripts/check_release.py` aplica al repositorio la misma idea que la puerta de calidad aplica a los datos: una lista de reglas, cada una con su gravedad.

| Regla | Gravedad | Qué comprueba |
|---|---|---|
| R01 | ERROR | Que existen los archivos imprescindibles: README, LICENSE, requirements, .gitignore, el `.pbip`, el flujo de GitHub Actions… |
| R02 | ERROR | Que el README tiene todas las secciones del apartado 2 |
| R03 | ERROR | Que cada enlace e imagen de los archivos Markdown apunta a un archivo que existe |
| R04 | ERROR | Que no queda ningún texto provisional (`YOUR NAME`…) |
| R05 | ERROR | Que no hay rutas personales (`C:\Users\<nombre>\…`) en los archivos de texto |
| R06 | ERROR | Que `.gitignore` excluye la base de datos, el entorno virtual y la caché de Power BI |
| R07 | ERROR | Que ningún archivo supera los 100 MB, el límite de GitHub (aviso desde 50 MB) |
| R08 | ERROR | Que no aparece ninguna marca de clasificación de seguridad, es decir, las palabras en mayúsculas que indican que un documento es de difusión restringida o confidencial |
| R09 | ERROR | Que el README dice que los datos son sintéticos, la empresa ficticia y el sistema no certificado |
| R10 | AVISO | Que existen las 8 capturas |

La única excepción de R05 es el parámetro `DataFolder` del proyecto de Power BI. Tiene que contener la ruta completa del ordenador que lo guardó, así que se anota como información y se explica cómo cambiarlo (apartado 6).

Hay 16 pruebas en `tests/test_release.py`. Crean un repositorio de ejemplo, comprueban que pasa y le introducen después un defecto distinto cada vez, para comprobar que la regla que debe detectarlo lo detecta.

---

## 5. La integración continua (GitHub Actions)

**Qué es.** GitHub puede ejecutar un proceso automático cada vez que se sube un cambio. AQMI lo usa para demostrar que el proyecto funciona en un ordenador limpio, no solo en el tuyo.

**Qué hace** (`.github/workflows/tests.yml`). En cada cambio que se sube a la rama `main`, GitHub prepara dos máquinas nuevas, una Linux y otra Windows, y en cada una:

1. descarga el repositorio;
2. instala Python 3.12 y las dependencias de `requirements.txt`;
3. ejecuta `python scripts/run_pipeline.py`: base de datos, simulación, puerta de calidad, KPI, exportación y control del proyecto de Power BI;
4. ejecuta las 151 pruebas;
5. ejecuta la comprobación previa a la publicación.

**El distintivo.** El README muestra arriba un distintivo, *tests: passing* en verde o *failing* en rojo, que GitHub actualiza solo. Para quien revisa el portfolio es la prueba, a simple vista, de que todo funciona.

**Coste.** Ninguno: GitHub Actions es gratuito en repositorios públicos.

---

## 6. El proyecto de Power BI en otro ordenador

Power BI no acepta rutas relativas: el parámetro `DataFolder` debe contener la ruta **completa** de `data\processed\`. Si el proyecto se mueve de carpeta o se descarga en otro ordenador, esa ruta deja de existir.

`scripts/set_powerbi_data_folder.py` la corrige automáticamente:

```powershell
python scripts/set_powerbi_data_folder.py            # escribe la ruta de este ordenador
python scripts/set_powerbi_data_folder.py --check    # solo muestra la ruta actual y si existe
```

Resultado esperado:

```text
INFO    | DataFolder was: C:\...\ruta antigua\data\processed\
INFO    | DataFolder now: C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence\data\processed\
INFO    | Open powerbi/AQMI.pbip and press Refresh.
```

> **Cierra Power BI Desktop antes de ejecutarlo.** Si el proyecto está abierto, Power BI sobrescribe el cambio la próxima vez que guarde.

Sin Python también se puede: en Power BI, *Transformar datos → Editar parámetros → DataFolder*. El README explica las dos formas.

---

## 7. Privacidad: rutas personales y datos de autor

Varios documentos contenían rutas del tipo `C:\Users\<tu usuario>\Dropbox\…\<tu carpeta>\…`. Al publicarlas se habrían visto tu usuario de Windows y la estructura de tus carpetas. Se han sustituido por `C:\Users\<usuario>\…` o por "la carpeta del proyecto". La regla R05 impide que vuelvan a aparecer.

Los datos de autor que aparecen en el repositorio son solo los que tú decidas: el nombre de la licencia y del apartado *About the author* del README. Hasta que me los indiques, la regla R04 bloquea la publicación.

---

## 8. Cómo se publica en GitHub

### 8.1 Primero, fuera de Dropbox (decisión D7)

En la Fase 1 se aprobó la decisión **D7: el repositorio irá fuera de Dropbox antes de iniciar Git**. El motivo es técnico: Git guarda su historial en una carpeta oculta `.git` con miles de archivos pequeños, y Dropbox puede sincronizarlos a medias y dañarlo. La carpeta actual sigue en Dropbox, así que la publicación se hace de forma que la copia de trabajo con Git quede en `C:\Users\<usuario>\Proyectos\`. Este apartado sustituye a la parte G de la Fase 3 (primer *commit*), que no llegó a hacerse.

### 8.2 Opción A (recomendada): publico yo desde aquí y tú clonas

| Paso | Quién | Qué |
|---|---|---|
| 1 | Tú | En github.com: **New repository** → nombre `aviation-quality-maintenance-intelligence` → **Public** → **sin** README, sin .gitignore y sin licencia (el repositorio debe estar vacío) → **Create repository** |
| 2 | Tú | Me dices que ya está creado y me autorizas a subir el proyecto |
| 3 | Yo | Subo el proyecto completo en un primer *commit* (`AQMI v1.0`) y compruebo en la pestaña **Actions** que las pruebas pasan en Linux y en Windows |
| 4 | Tú | En **GitHub Desktop**: *File → Clone repository* → eliges el repositorio → carpeta `C:\Users\<usuario>\Proyectos` → **Clone** |
| 5 | Tú | En esa carpeta nueva, preparas el entorno de Python (Fase 3, partes B y C) y ejecutas `python scripts/set_powerbi_data_folder.py` |
| 6 | Tú | La carpeta de Dropbox queda como copia antigua: puedes archivarla o borrarla cuando compruebes que la nueva funciona |

Ventajas: no tienes que manejar Git para la primera publicación, el contenido subido es exactamente el que se ha comprobado aquí y el problema de Dropbox desaparece desde el primer momento.

### 8.3 Opción B: lo publicas tú con GitHub Desktop

1. Cierra Power BI Desktop y VS Code.
2. Copia la carpeta `AQMI` a `C:\Users\<usuario>\Proyectos\` y cámbiale el nombre a `aviation-quality-maintenance-intelligence`.
3. En esa carpeta: prepara el entorno de Python (Fase 3, partes B y C), ejecuta `python scripts/run_pipeline.py`, `pytest`, `python scripts/set_powerbi_data_folder.py` y `python scripts/check_release.py`. Debe terminar en `RELEASE CHECK PASSED`.
4. En GitHub Desktop: *File → Add local repository* → elige la carpeta → *create a repository* → **Create repository**.
5. Escribe el resumen del primer *commit* (`AQMI v1.0`) y pulsa **Commit to main**.
6. Pulsa **Publish repository**, **desmarca** *Keep this code private* y confirma.

---

## 9. Después de publicar

Son ajustes de la página del repositorio que solo puede hacer el propietario (rueda dentada junto a *About*):

| Ajuste | Valor propuesto |
|---|---|
| Description | `Quality-management and production-control system for a fictitious civil helicopter MRO: SQLite, 82 validation rules, CAPA, document control, traceability, 18 KPIs and Power BI. Synthetic data.` |
| Topics | `quality-management` `aviation` `mro` `aircraft-maintenance` `capa` `non-conformity` `document-control` `traceability` `data-quality` `power-bi` `dax` `sql` `sqlite` `python` |
| Social preview (*Settings → General*) | `assets/screenshots/01_executive_overview.png` |
| Fijar en el perfil | En tu perfil: *Customize your pins* → marcar AQMI |
| Release v1.0 (opcional) | *Releases → Create a new release* → etiqueta `v1.0` → adjuntar `assets/AQMI_report.pdf` |

---

## 10. Archivos de esta fase

| Archivo o carpeta | Novedad |
|---|---|
| `README.md` | Reescrito por completo, en inglés |
| `LICENSE` | Nombre del autor (pendiente de que me lo indiques) |
| `requirements.txt` | Añadidos `jsonschema` y `referencing` |
| `.gitignore` | Añadidos los archivos locales de Power BI (`.pbi/localSettings.json`, `.pbi/cache.abf`) |
| `.github/workflows/tests.yml` | Nuevo: integración continua en Linux y Windows |
| `scripts/check_release.py` | Nuevo: comprobación previa a la publicación (10 reglas) |
| `scripts/build_case_study.py` | Nuevo: genera el caso práctico desde la base de datos |
| `scripts/set_powerbi_data_folder.py` | Nuevo: ajusta el parámetro `DataFolder` al ordenador |
| `scripts/validate_powerbi.py` | Ajustado al formato que guarda Power BI Desktop |
| `tests/test_release.py` | Nuevo: 16 pruebas |
| `tests/test_powerbi.py` | 2 pruebas nuevas (proyecto guardado por Power BI y línea TMDL no válida) |
| `powerbi/` | Versión guardada por Power BI Desktop en la primera apertura |
| `assets/screenshots/` | Las 8 capturas, obtenidas del PDF exportado desde Power BI |
| `assets/AQMI_report.pdf` | El informe completo exportado desde Power BI |
| `documentation/README.md` | Nuevo: índice de la documentación |
| `documentation/case_study_nonconformity.md` | Nuevo: el caso práctico (en inglés) |
| `documentation/09_fase8_documentacion_y_github.md` | Este documento |
| `documentation/01`, `04`, `06`, `07`, `08` | Rutas personales sustituidas; Fase 7 marcada como aprobada |
| `reports/release_check.md` | Nuevo: resultado de la comprobación previa |

---

## 11. Cómo comprobarlo

Desde la carpeta del proyecto, con el entorno virtual activado:

```powershell
python scripts/run_pipeline.py      # debe terminar en PIPELINE OK
python -m pytest -q                 # debe terminar en 151 passed
python scripts/check_release.py     # debe terminar en RELEASE CHECK PASSED
```

Y sin Python:

1. Abre `README.md` en VS Code y pulsa **Ctrl + Mayús + V** para ver la vista previa. Comprueba que se ven las capturas y que el texto describe tu trayectoria tal como quieres presentarla.
2. Abre `documentation/case_study_nonconformity.md` del mismo modo.
3. Una vez publicado, comprueba en GitHub que los diagramas Mermaid se dibujan y que el distintivo *tests* está en verde.
