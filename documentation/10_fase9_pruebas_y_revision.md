# AQMI — Fase 9: Pruebas finales y revisión profesional (informe de cierre)

**Proyecto:** Aviation Quality & Maintenance Intelligence (AQMI)
**Documento:** `documentation/10_fase9_pruebas_y_revision.md`
**Fecha:** 19/11/2026
**Estado:** Terminada. **Pendiente de la aprobación de Dani.**

> AEROQ MRO es una empresa ficticia y todos sus datos son sintéticos. Los objetivos de los indicadores son **objetivos internos ficticios**, no requisitos normativos.

---

## 1. Qué se ha hecho en esta fase

| # | Tarea | Resultado |
|---|---|---|
| 0 | Registro de lecciones aprendidas (ampliación aprobada) | Tabla 25, reglas L01–L07, 59 lecciones, KPI LRN-01 y bloque en Power BI. Detalle en `09b_fase9_lecciones_aprendidas.md` |
| 1 | Prueba en el ordenador Windows de Dani | Clon limpio en `C:\Proyectos\…`, pipeline OK, 178 pruebas superadas, RELEASE CHECK PASSED |
| 2 | Revisión profesional del repositorio | 9 hallazgos, todos corregidos (sección 3) |
| 3 | Pulido visual | Títulos de tarjetas, tablas que no cabían, ejes cortados y «Todas» en los filtros, resueltos (sección 4) |
| — | Regla K03 (Power BI = SQL) | Comprobada en Power BI Desktop: **19 de 19 indicadores coinciden** |
| — | Capturas y PDF | Nuevos, exportados desde Power BI Desktop en inglés |
| 4 | Guía para entrevistas | Documento personal, fuera del repositorio público (sección 7) |
| 5 | Release v1.0 en GitHub con el PDF | Sección 8 |

Cifras finales: 25 tablas, 15 vistas, 90 triggers, 89 reglas de validación (0 fallos críticos, Data Quality Score 89,9 %, 9 de 9 discrepancias sembradas detectadas), 19 KPI, 87 medidas DAX, 8 páginas, 179 pruebas automáticas.

## 2. Prueba en Windows

Dani ejecutó un único script (`prueba_windows_fase9.ps1`), que guardó todo lo que salió en pantalla en `prueba_windows_fase9.log`.

| Paso | Resultado |
|---|---|
| Herramientas | Git 2.54 y Python 3.13.7 |
| Clonar desde GitHub en `C:\Proyectos\aviation-quality-maintenance-intelligence` | OK |
| Añadir los commits de la Fase 9 (todavía no publicados) | OK, avance rápido `ff0bae1..8e47607` |
| Entorno virtual y dependencias | OK |
| `run_pipeline.py` | `PIPELINE OK`: 59 lecciones, 89 reglas, LRN-01 76,9 % |
| `pytest` | **178 passed** en 3 minutos |
| `check_release.py` | `RELEASE CHECK PASSED` |
| Abrir `AQMI.pbip` y actualizar | OK: el `DataFolder` publicado ya apunta a esa carpeta |

La ruta de `C:\Proyectos` hace que el proyecto funcione sin cambiar ningún parámetro, como estaba previsto en la Fase 8.

## 3. Revisión profesional: hallazgos y correcciones

| # | Hallazgo | Corrección |
|---|---|---|
| 1 | Comentarios de varios scripts con cifras antiguas (82 reglas, 18 KPI) | Actualizados |
| 2 | La descripción de la medida `Audit Events (Label)` llevaba una cifra fija (17.383) | Sustituida por un ejemplo |
| 3 | Algunos textos de las lecciones afirmaban cómo había funcionado una acción, algo que el generador no sabe | Ahora solo dicen que la acción fue eficaz |
| 4 | Al editar un archivo del proyecto Power BI se perdieron los finales de línea CRLF (error propio, detectado en la revisión) | Corregido. Prueba nueva que vigila las convenciones de Desktop: CRLF, JSON sin salto final y TMDL acabado en línea en blanco |
| 5 | La tabla *Open actions* no cabía en su nueva anchura | Anchuras fijas por columna y ajuste de texto |
| 6 | En la tabla de KPI de la portada no se veían *Target* ni *Status* | Columnas Indicator, Value, Target y Status, con anchuras fijas y orden por áreas |
| 7 | Power BI Desktop guardó dos visuales con el esquema `visualContainer` 2.14.0, que Microsoft aún no ha publicado. El validador los saltaba sin avisar | El validador usa la versión publicada más reciente de la misma serie (2.13.0) y lo indica en el informe. Se añadieron los esquemas oficiales necesarios y una prueba |
| 8 | `pages.json` (esquema 1.1.0) tampoco se comprobaba | Esquema añadido; ahora se comprueban 157 archivos |
| 9 | Los CSV del repositorio podían quedar desalineados con el generador sin que nada lo detectara | Paso nuevo en la integración continua (Linux) que lo comprueba |

## 4. Pulido visual

| Problema (capturas de la Fase 8) | Solución |
|---|---|
| Títulos de tarjeta cortados («Maintenance Order Completio…», «Work Orders Blocked by Mater…», «Actions Pending Implementati…») | Etiquetas cortas: *Order Completion Rate*, *Blocked by Material*, *Blocked by Documentation*, *Pending Implementation*. La medida conserva su nombre completo |
| Categorías cortadas en *Recurring problems by category* y *Verifications with discrepancies, by type* | Más espacio para las etiquetas del eje |
| «Todas» en los filtros | Es el idioma de Power BI Desktop. Se exportó con Desktop en inglés y luego se volvió a dejar en español, con el permiso de Dani |
| Bloque nuevo *Lessons learned* | Revisado en Desktop: tarjetas (76,9 % y 12 pendientes) y tabla con las pendientes primero |

## 5. Capturas y PDF

El informe se abrió, se actualizó y **se guardó en Power BI Desktop**, que es la versión de referencia. Al guardar, Desktop añadió la tabla nueva al diagrama del modelo y los metadatos de idioma, y subió dos visuales al esquema 2.14.0. El PDF se exportó desde Desktop (`assets/AQMI_report.pdf`, 8 páginas) y las 8 capturas se generaron a partir de él, con el mismo tamaño que las anteriores (1522 × 880 px).

## 6. Regla K03

En la página *Audit & Traceability*, la tabla *K03 · Power BI vs SQL reference* muestra «✓ Match» en los 19 indicadores, LRN-01 incluido. Con esto, las cinco reglas K están comprobadas.

## 7. Guía para entrevistas

Es un documento personal de Dani y no forma parte del repositorio público. Está en sus documentos de Claude con el título *AQMI — Guía para entrevistas*, y contiene:

- la presentación del proyecto en 30 segundos y en 2 minutos;
- la relación entre cada tarea de su experiencia real y lo que se ve en AQMI;
- lo que no debe atribuirse y cómo explicar el uso de IA;
- un guion de demostración de 5 minutos;
- las preguntas probables y un vocabulario en español e inglés.

## 8. Release v1.0

- **Etiqueta:** `v1.0`, en la rama `main`, con la integración continua en verde en Linux y Windows.
- **Archivo adjunto:** `AQMI_report.pdf` (el informe completo de Power BI).
- **Notas en inglés:** qué contiene el sistema, cifras de control, cómo ejecutarlo y el aviso de datos sintéticos.
- **Dirección:** https://github.com/DeLabFuente/aviation-quality-maintenance-intelligence/releases/tag/v1.0

## 9. Archivos de esta fase

Además de los de las lecciones aprendidas (`09b`, sección 10):

| Archivo | Cambio |
|---|---|
| `documentation/10_fase9_pruebas_y_revision.md` | Este informe |
| `assets/AQMI_report.pdf`, `assets/screenshots/*.png` | Nuevos, desde Power BI Desktop |
| `powerbi/…` | Guardado por Desktop; visuales pulidos |
| `scripts/build_powerbi_project.py` | Mismos cambios visuales que el proyecto guardado; anchuras de columna |
| `scripts/validate_powerbi.py` | Comprobación con la versión de esquema publicada más reciente |
| `scripts/export_powerbi.py` | `kpi_order` por áreas (Quality primero) |
| `tests/test_powerbi.py`, `tests/schemas/…` | Dos pruebas nuevas y tres esquemas oficiales |
| `.github/workflows/tests.yml` | Comprobación de los CSV frente al generador |

## 10. Cómo comprobarlo

1. En GitHub, la insignia *tests* del README debe estar en verde, y la página *Releases* debe mostrar **v1.0** con el PDF.
2. En tu ordenador, para dejar `C:\Proyectos\aviation-quality-maintenance-intelligence` igual que GitHub, abre PowerShell y ejecuta estas tres líneas:

   ```powershell
   cd C:\Proyectos\aviation-quality-maintenance-intelligence
   git fetch origin
   git reset --hard origin/main
   ```

   No se pierde nada: los únicos cambios locales de esa carpeta son los que ya están publicados.
3. Opcional: `.venv\Scripts\activate`, `python scripts\run_pipeline.py` y `python -m pytest -q`. Debe dar `PIPELINE OK` y 179 pruebas superadas.

## 11. Tareas opcionales que quedan para Dani

- Imagen *Social preview* del repositorio (GitHub → Settings → General → Social preview). Puede servir `assets/screenshots/01_executive_overview.png`.
- Fijar el repositorio en el perfil de GitHub.
- Borrar los PDF sobrantes de `AQMI\assets` en Dropbox (`AQMIAQMI_report.pdf` y `AQMI_report_final.pdf`). La carpeta de Dropbox es la copia antigua; la de trabajo es `C:\Proyectos`.
- Borrar de la carpeta `AQMI` de Dropbox los archivos de la prueba (`AQMI_fase9.bundle`, `prueba_windows_fase9.ps1` y `.log`), si ya no los quieres.

## 12. Limitaciones conocidas

- El aspecto de los cuadros de mando solo se puede juzgar abriéndolos en Power BI Desktop. Esta vez se hizo, pero las pruebas automáticas no lo cubren.
- El esquema `visualContainer` 2.14.0 se comprueba con la versión 2.13.0 hasta que Microsoft publique la nueva.
- La tabla *Open actions* muestra 4 filas a la vista, porque los títulos ocupan dos líneas; las demás se ven al desplazarse.
