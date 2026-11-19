# AQMI — Fase 3: Guía paso a paso del entorno y la base de datos

**Documento:** `documentation/04_fase3_entorno_y_base_de_datos.md`
**Para quién:** para ti, partiendo de cero. Cada paso indica qué hacer, qué escribir y qué deberías ver.
**Tiempo estimado:** 45–60 minutos la primera vez.

---

## Índice

- Parte A — Mover el proyecto fuera de Dropbox
- Parte B — Instalar las herramientas (solo la primera vez)
- Parte C — Abrir el proyecto y crear el entorno virtual
- Parte D — Crear la base de datos
- Parte E — Ejecutar las pruebas automáticas
- Parte F — Ver la base de datos con DB Browser
- Parte G — Primer commit y subida a GitHub
- Parte H — Problemas frecuentes
- Parte I — Qué hace cada archivo
- Parte J — Lista de comprobación final

> **Convención:** el texto en `este formato` dentro de un recuadro gris es lo que hay que **escribir en el terminal** y pulsar **Intro**. Escríbelo exactamente igual.

---

## Parte A — Mover el proyecto fuera de Dropbox

**Por qué:** lo acordamos en la decisión D7. Dropbox sincroniza los archivos mientras se están escribiendo, y eso puede estropear la base de datos o el historial de Git. GitHub será tu copia de seguridad.

1. Cierra cualquier programa que tenga abierto algún archivo del proyecto.
2. Abre el **Explorador de archivos** y ve a `C:\Users\<usuario>`.
3. Crea una carpeta nueva llamada `Proyectos` (botón derecho → Nuevo → Carpeta).
4. Ve a `C:\Users\<usuario>\Dropbox\...\PROYECTO\`.
5. Selecciona la carpeta `AQMI`, pulsa **Ctrl + X** (cortar), entra en `C:\Users\<usuario>\Proyectos` y pulsa **Ctrl + V** (pegar).
6. Cambia el nombre de la carpeta `AQMI` a `aviation-quality-maintenance-intelligence` (botón derecho → Cambiar nombre).

Resultado: el proyecto queda en
`C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence`

> En el próximo chat conmigo, conecta esta carpeta nueva en lugar de la de Dropbox, para que pueda seguir escribiendo en ella.

---

## Parte B — Instalar las herramientas (solo la primera vez)

### B1. Python

1. Entra en **https://www.python.org/downloads/windows/**.
2. Descarga el instalador **Windows installer (64-bit)** de **Python 3.13** (también sirve la 3.12).
3. Ejecuta el instalador y, **antes de pulsar "Install Now"**, marca la casilla **"Add python.exe to PATH"**. Es importante.
4. Pulsa **Install Now** y espera a que termine.

**Comprobación:** abre el menú Inicio, escribe `PowerShell`, ábrelo y escribe:

```
py --version
```

Deberías ver algo como `Python 3.13.x`.

### B2. Visual Studio Code (el editor)

1. Entra en **https://code.visualstudio.com/** y descarga la versión para Windows.
2. Instálalo con las opciones por defecto. Marca también **"Agregar la acción 'Abrir con Code' al menú contextual"**: te permitirá abrir carpetas con el botón derecho.
3. Abre VS Code, pulsa el icono de **Extensiones** en la barra izquierda (cuatro cuadrados) e instala:
   - **Python** (de Microsoft).
   - **Markdown Preview Mermaid Support** (para ver los diagramas de la documentación).

### B3. Git (control de versiones)

1. Entra en **https://git-scm.com/download/win** y descarga el instalador de 64 bits.
2. Instálalo dejando **todas las opciones por defecto**.
3. Cierra y vuelve a abrir PowerShell, y comprueba:

```
git --version
```

Deberías ver algo como `git version 2.xx`.

4. Dile a Git quién eres. Sustituye los datos por los tuyos:

```
git config --global user.name "Tu Nombre y Apellido"
git config --global user.email "tu_correo@ejemplo.com"
git config --global init.defaultBranch main
```

> **Privacidad:** el correo aparecerá en el historial público del repositorio. GitHub ofrece una dirección privada del tipo `12345678+usuario@users.noreply.github.com` (en GitHub: *Settings → Emails*). Puedes usar esa en lugar de tu correo personal.

### B4. DB Browser for SQLite (ver la base de datos)

1. Entra en **https://sqlitebrowser.org/dl/**.
2. Descarga **"DB Browser for SQLite – Standard installer for 64-bit Windows"**, **versión 3.13 o posterior**. Las versiones anteriores no leen bien las tablas STRICT que usa el proyecto.
3. Instálalo con las opciones por defecto.

### B5. Cuenta de GitHub

Si no la tienes, créala en **https://github.com/signup**. Elige un nombre de usuario profesional (por ejemplo, tu nombre y apellido), porque formará parte de la dirección de tu portfolio.

---

## Parte C — Abrir el proyecto y crear el entorno virtual

### C1. Abrir la carpeta en VS Code

1. Abre VS Code.
2. Menú **File → Open Folder…** (Archivo → Abrir carpeta).
3. Elige `C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence` y pulsa **Seleccionar carpeta**.
4. Si pregunta *"Do you trust the authors of the files in this folder?"*, pulsa **Yes, I trust the authors**.

### C2. Abrir el terminal dentro de VS Code

Menú **Terminal → New Terminal**. Abajo aparece una ventana con un texto parecido a:

```
PS C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence>
```

Esa ruta indica **dónde estás**. Todos los comandos del proyecto se escriben desde esta carpeta.

### C3. Crear el entorno virtual

**Qué es:** una "caja" privada para las librerías de Python de este proyecto. Así no se mezclan con las de otros programas y cualquiera puede reproducir exactamente tu entorno.

```
py -3.13 -m venv .venv
```

(Si instalaste Python 3.12, escribe `py -3.12 -m venv .venv`.)

Tarda unos segundos y no muestra nada. Aparecerá una carpeta nueva llamada `.venv`.

### C4. Activar el entorno virtual

```
.venv\Scripts\Activate.ps1
```

Si funciona, el texto del terminal empieza ahora por **`(.venv)`**:

```
(.venv) PS C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence>
```

> **Si aparece un error en rojo** que dice que *"la ejecución de scripts está deshabilitada en este sistema"*, escribe esto una sola vez, responde `S` (o `Y`) y vuelve a activar:
>
> ```
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

**Recuerda:** cada vez que abras un terminal nuevo para trabajar en el proyecto tienes que activar el entorno (paso C4). Si no ves `(.venv)`, no está activo.

### C5. Instalar las librerías

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Verás varias líneas de descarga y al final `Successfully installed ...`.

### C6. Elegir el intérprete en VS Code

Si VS Code muestra un aviso para seleccionar el intérprete de Python, elige el que contiene `.venv`. Si no lo muestra: pulsa **Ctrl + Shift + P**, escribe `Python: Select Interpreter` y elige el de `.venv`.

---

## Parte D — Crear la base de datos

Con el entorno activo (`(.venv)` al principio de la línea), escribe:

```
python scripts/build_database.py
```

**Resultado esperado:**

```
INFO    | SQLite version 3.xx.x
INFO    | Running sql\schema\01_tables.sql
INFO    | Running sql\schema\02_indexes.sql
INFO    | Generated sql\schema\03_triggers.sql
INFO    | Running sql\schema\04_reference_data.sql
INFO    | System parameters written (AS_OF_DATE = 2026-10-31)
INFO    | Integrity check: ok | Foreign key check: ok
INFO    | Database built: 24 tables, 62 indexes, 86 triggers, 6 departments, 8 incident categories, 5 system parameters
INFO    | BUILD OK -> C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence\database\aqmi.db
```

Lo importante es la última línea: **`BUILD OK`**. Se ha creado el archivo `database\aqmi.db`.

**Qué ha pasado:**

| Paso | Qué hace |
|---|---|
| 01_tables.sql | Crea las 24 tablas del diccionario de datos, con todas sus restricciones |
| 02_indexes.sql | Crea los índices que hacen rápidas las consultas |
| 03_triggers.sql | Se **genera automáticamente** y crea 86 triggers: impiden borrar datos, protegen los registros inalterables y anotan cada cambio en `Audit_Log` |
| 04_reference_data.sql | Carga los 6 departamentos y las 8 categorías de no conformidad |
| Parámetros | Guarda la fecha de corte y la semilla en `System_Parameters` |
| Comprobaciones | SQLite revisa la integridad del archivo y de las claves externas |

Cada ejecución queda también registrada en `logs\aqmi.log`.

> **Puedes ejecutar este comando tantas veces como quieras.** Cada vez borra la base de datos anterior y la crea de nuevo desde los archivos SQL. Por eso `aqmi.db` no se guarda en Git: siempre se puede regenerar.

---

## Parte E — Ejecutar las pruebas automáticas

```
pytest -v
```

**Resultado esperado** (resumido):

```
tests/test_database_schema.py::test_all_24_tables_exist PASSED
tests/test_database_schema.py::test_every_table_is_strict PASSED
...
tests/test_database_schema.py::test_physical_delete_is_blocked PASSED
...
============================== 25 passed in X.XXs ==============================
```

**Qué comprueban las 25 pruebas.** Cada una crea su propia base de datos temporal, así que nunca tocan `aqmi.db`.

| Grupo | Qué se comprueba |
|---|---|
| Estructura | Existen las 24 tablas, todas son STRICT, la integridad es correcta y las claves externas están activadas |
| Datos de referencia | 6 departamentos, 8 categorías, fecha de corte correcta y su registro en la auditoría |
| Formatos | Se rechazan un departamento inexistente, una fecha imposible (30 de febrero), un código mal escrito, un texto en un campo numérico y un correo que no es ficticio |
| Reglas de negocio | Se rechazan dos revisiones vigentes del mismo documento, una revisión aprobada por su autor, una recepción que pasa directamente a disponible sin cuarentena, una acción verificada por su propio responsable y una acción correctiva sin incidencia |
| Auditoría | Se impide borrar datos y modificar la auditoría. Se impide modificar un registro sin indicar quién y cuándo, o con una fecha anterior a la del cambio previo. Cada campo modificado deja su rastro con el valor anterior, el nuevo, el autor y la fecha |

> Si ejecutas `pytest` **antes** de crear la base de datos, verás `24 passed, 1 skipped`. Es normal: la prueba que abre `aqmi.db` se salta si el archivo aún no existe.

---

## Parte F — Ver la base de datos con DB Browser

1. Abre **DB Browser for SQLite**.
2. **Open Database** → elige `database\aqmi.db` dentro de la carpeta del proyecto.
3. Pestaña **Database Structure**: verás las 24 tablas, los índices y los triggers.
4. Pestaña **Browse Data**: en el desplegable *Table* elige:
   - `Departments` → 6 filas.
   - `Incident_Categories` → 8 filas, con nombres en español y en inglés.
   - `System_Parameters` → fecha de corte, semilla y aviso de datos sintéticos.
   - `Audit_Log` → 6 filas: la creación de cada departamento quedó registrada automáticamente.
5. **Experimento: la base de datos se defiende sola.** Ve a la pestaña **Execute SQL**, escribe:

   ```sql
   DELETE FROM Departments WHERE department_code = 'DIR';
   ```

   y pulsa el botón ▶ (Execute). Aparecerá el error:
   *"AQMI G09: physical deletes are not allowed on Departments. Cancel or deactivate the record instead."*

6. Pulsa **Revert Changes** (deshacer cambios) y **cierra DB Browser**.

> **Importante:** cierra siempre DB Browser antes de volver a ejecutar `build_database.py`. Windows no permite borrar un archivo que otro programa tiene abierto (ver la Parte H).

---

## Parte G — Primer commit y subida a GitHub

### G1. Poner tu nombre en la licencia

Abre el archivo `LICENSE` en VS Code y sustituye `YOUR NAME` por tu nombre. Guarda con **Ctrl + S**.

### G2. Crear el repositorio local

```
git init
```

Respuesta: `Initialized empty Git repository in ...`

### G3. Comprobar qué se va a guardar (control de calidad)

```
git status
```

Verás en rojo la lista de archivos nuevos. **Comprueba que NO aparecen** la carpeta `.venv`, el archivo `database/aqmi.db` ni `logs/aqmi.log`. El archivo `.gitignore` los excluye a propósito: son archivos que se regeneran o que solo sirven en tu ordenador.

### G4. Guardar la primera versión (commit)

```
git add .
git commit -m "Phases 1-3: architecture, data model and SQLite database schema"
```

Respuesta: una línea con el número de archivos guardados (unos 30).

### G5. Crear el repositorio en GitHub

1. Entra en **https://github.com/new**.
2. **Repository name:** `aviation-quality-maintenance-intelligence`
3. **Description:** `Quality management information system for a fictitious helicopter MRO — SQL, Python, Power BI (synthetic data)`
4. Marca **Private**. Lo haremos público en la Fase 8, cuando esté terminado.
5. **No marques** "Add a README", ".gitignore" ni "license": ya los tienes.
6. Pulsa **Create repository**.

### G6. Subir el proyecto

GitHub te mostrará unos comandos. Usa los de la sección **"…or push an existing repository from the command line"**. Serán así, con tu usuario en lugar de `TU_USUARIO`:

```
git remote add origin https://github.com/TU_USUARIO/aviation-quality-maintenance-intelligence.git
git push -u origin main
```

La primera vez se abrirá una ventana del navegador para iniciar sesión en GitHub. Autoriza el acceso.

**Comprobación:** recarga la página del repositorio en GitHub. Verás todas las carpetas, y en `documentation` los diagramas Mermaid se mostrarán dibujados.

---

## Parte H — Problemas frecuentes

| Mensaje o síntoma | Causa | Solución |
|---|---|---|
| `py : El término 'py' no se reconoce…` | Python no está instalado o no se marcó "Add to PATH" | Reinstala Python marcando la casilla (B1) y abre un terminal nuevo |
| `…la ejecución de scripts está deshabilitada…` al activar | Política de seguridad de PowerShell | Paso C4: `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` |
| `ModuleNotFoundError: No module named 'config'` | El terminal no está en la carpeta del proyecto | Escribe `cd C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence` y repite |
| `pytest : El término 'pytest' no se reconoce…` | El entorno virtual no está activo | Paso C4 (debe verse `(.venv)`) |
| `BUILD FAILED: [WinError 32] El proceso no tiene acceso al archivo…` | DB Browser (u otro programa) tiene abierta la base de datos | Cierra DB Browser y vuelve a ejecutar |
| `BUILD FAILED: SQLite 3.xx is too old…` | Versión de Python antigua | Instala Python 3.12 o 3.13 y crea de nuevo el entorno (borra `.venv` y repite C3–C5) |
| `git push` pide una contraseña | GitHub no acepta la contraseña de la cuenta en el terminal | Cierra la ventana y repite: debe abrirse el navegador para iniciar sesión. Si no, instala Git de nuevo con las opciones por defecto (incluyen *Git Credential Manager*) |
| `error: remote origin already exists` | Ya ejecutaste `git remote add` antes | Escribe `git remote set-url origin https://github.com/TU_USUARIO/aviation-quality-maintenance-intelligence.git` |

Si aparece cualquier otro error, copia el texto completo del terminal y pégamelo en el chat.

---

## Parte I — Qué hace cada archivo

| Archivo | Qué es |
|---|---|
| `README.md` | Portada del repositorio (en inglés; versión provisional hasta la Fase 8) |
| `LICENSE` | Licencia MIT: permite ver y reutilizar el código citando la autoría |
| `requirements.txt` | Lista de librerías de Python que necesita el proyecto |
| `.gitignore` | Archivos que Git no debe guardar |
| `pytest.ini` | Configuración de las pruebas |
| `config/settings.py` | **Único lugar** con rutas, fecha de corte, semilla y requisitos. Si algo cambia, se cambia aquí |
| `scripts/common.py` | Funciones compartidas: abrir la base de datos con las claves externas activas y escribir el registro |
| `scripts/trigger_builder.py` | Genera los triggers de control y auditoría a partir de la estructura real de las tablas |
| `scripts/build_database.py` | Crea la base de datos completa con un solo comando |
| `sql/schema/01_tables.sql` | Las 24 tablas y sus restricciones (el diccionario de datos convertido en SQL) |
| `sql/schema/02_indexes.sql` | Los índices |
| `sql/schema/03_triggers.sql` | Los triggers. **Archivo generado: no se edita a mano** |
| `sql/schema/04_reference_data.sql` | Departamentos y categorías de no conformidad |
| `tests/conftest.py` | Prepara una base de datos temporal para cada prueba |
| `tests/test_database_schema.py` | Las 25 pruebas |
| Carpetas con `.gitkeep` | Archivo vacío que permite guardar en Git carpetas que todavía no tienen contenido |

### Tres conceptos que conviene entender

**Tabla STRICT.** Por defecto, SQLite acepta casi cualquier cosa en cualquier campo: puedes guardar la palabra "dos mil" en un campo numérico. Con `STRICT`, la base de datos rechaza el dato. Es la primera barrera de calidad.

**Trigger.** Una instrucción que la base de datos ejecuta sola cuando ocurre algo. En AQMI hay cinco tipos:

| Trigger | Cuándo actúa | Qué hace |
|---|---|---|
| `_no_delete` | Al intentar borrar | Lo impide (regla G09) |
| `_no_update` | Al intentar modificar un movimiento, un avance o la auditoría | Lo impide (regla G08) |
| `_update_guard` | Antes de cualquier modificación | Exige indicar quién y cuándo, en orden cronológico |
| `_audit_insert` | Después de crear un registro | Anota la creación en `Audit_Log` |
| `_audit_update` | Después de modificar un registro | Anota cada campo cambiado: valor anterior, valor nuevo, quién y cuándo |

**La auditoría usa la fecha del propio registro, no la del ordenador.** Cuando en la Fase 4 el generador simule que una incidencia se cerró el 12/03/2025, la auditoría registrará el 12/03/2025. Así el historial simulado es realista y lo escribe el mismo mecanismo que funcionaría en un sistema real.

---

## Parte J — Lista de comprobación final

Marca cada punto cuando lo hayas completado:

- [ ] El proyecto está en `C:\Users\<usuario>\Proyectos\aviation-quality-maintenance-intelligence` (fuera de Dropbox)
- [ ] `py --version` muestra Python 3.12 o 3.13
- [ ] `git --version` responde
- [ ] El terminal muestra `(.venv)` al activar el entorno
- [ ] `python scripts/build_database.py` termina con `BUILD OK`
- [ ] `pytest -v` muestra `25 passed`
- [ ] DB Browser muestra 24 tablas y el experimento del DELETE da el error G09
- [ ] `git status` no muestra `.venv`, `aqmi.db` ni `aqmi.log`
- [ ] El repositorio privado está en GitHub con todos los archivos

Cuando todos los puntos estén marcados, la Fase 3 está completa.
