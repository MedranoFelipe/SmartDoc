# 📄 Sistema Inteligente de Procesamiento y Validación de Documentos

## 🎯 Objetivo de la aplicación

El proyecto cumple con los siguientes requisitos funcionales:

1. **Clasificación de Documentos:** Capacidad para identificar y clasificar tres tipos de documentos: **Cédulas**, **Actas de Seguro** y **Contratos**.
2. **Extracción de Datos:** Implementación de lógica de negocio (usando RegEx) para extraer campos estructurados y no estructurados específicos de cada tipo de documento.
    * **Ejemplos de extracción:** Nombre completo, número de identificación, fecha de nacimiento (Cédulas); Número de póliza, nombre del asegurado, tipo de cobertura, fechas de vigencia (Actas de Seguros); Cláusulas clave, partes involucradas, fechas de inicio y fin, montos (Contratos).
3. **Interfaz de Usuario (Front-end):** Creación de una aplicación web interactiva que muestra los documentos cargados, presenta los datos extraídos y permite la validación/corrección.

## 🚀 Arquitectura y Tecnologías

La solución se estructura en un diseño modular en Python, utilizando las siguientes herramientas:

### 🛠️ Stack Tecnológico

| Componente | Tecnología | Rol Principal |
| :--- | :--- | :--- |
| **Front-end / Interfaz** | `Streamlit` | Desarrollo rápido de un dashboard interactivo |
| **OCR / Análisis Documental** | `Azure AI Document Intelligence` (`azure-ai-formrecognizer`) | Servicio de IA para obtener el texto plano de los documentos |
| **Lógica de Extracción** | `Python` (`re`) | Reglas de negocio basadas en expresiones regulares para el *parsing* de datos específicos |
| **Reportes** | `pandas`, `xlsxwriter` | Generación del reporte consolidado en formato Excel |

### 🧠 Flujo de Ejecución

1. **Carga:** El usuario sube los archivos PDF a través del *file uploader* de Streamlit.
2. **Análisis AI:** Los documentos son analizados por el cliente de Azure Document Intelligence para obtener el contenido textual (`analyze_bytes_document`).
3. **Clasificación:** El texto extraído se clasifica como `cedula`, `acta_seguro`, `contrato` o `desconocido` usando palabras clave.
4. **Extracción Estructurada:** Se aplica la lógica específica (`extract_structured_data`) para extraer los campos clave de cada documento.
5. **Revisión Manual y Validación (Bonus):**
    * Los campos extraídos se inicializan en el estado de Streamlit (`st.session_state`).
    * La función `validate_field_format` verifica el formato de cada campo (ej. `date`, `currency`, `numeric_strict`).
    * Si hay errores, el documento se marca como **`Revisar`** y se expande en la interfaz.
6. **Limpieza de Datos:** Al editar un campo, la función *callback* `update_extraction_value` ejecuta la limpieza automática (`sanitize_value`) antes de revalidar el documento.
7. **Exportación:** El botón de descarga del reporte Excel (`generate_excel`) se **deshabilita** si hay documentos en estado `Revisar`.

## ✨ Bonus Implementados

La solución incluye los siguientes puntos opcionales (Bonus) que mejoran la calidad y la experiencia del usuario:

### 1. Manejo de Calidad del Dato y Validación

* **Validación de Formato:** El módulo `document_utils.py` contiene lógica estricta para validar formatos (ej. formato de fecha `dd/mm/aaaa`, campos numéricos solo con dígitos, límites de caracteres para textos).
* **Limpieza Automática:** La función `sanitize_value` limpia y estandariza los datos:
    * Formateo de moneda a `$XXX.XXX.XXX`.
    * Eliminación de caracteres no permitidos en textos estrictos o números.
* **Bloqueo de Exportación:** El reporte solo puede descargarse si `is_data_valid_for_export()` retorna `True`, asegurando que el estado de todos los documentos sea **`Validado`**.

### 2. Generación de Reporte Consolidado

* **Excel Consolidado:** Se utiliza `pandas` y `xlsxwriter` para generar un reporte que consolida los datos extraídos de **todos** los archivos procesados.
* **Organización por Hojas:** El reporte se organiza automáticamente, creando una hoja de cálculo separada para cada tipo de documento (Cédulas, Actas de Seguro, Contratos, Otros).

### 3. Interfaz con Manejo de Estado

* **Persistencia de Edición:** Se usa `st.session_state` y el *callback* `on_change` para actualizar el valor subyacente del documento en tiempo real, asegurando que las correcciones del usuario persistan y desencadenen la revalidación.
* **Manejo de Textos Largos:** El campo `objeto_del_contrato_texto` se renderiza correctamente con `st.text_area`, manteniendo la sincronización con el estado de la aplicación para permitir la edición multi-línea.

## ⚙️ Configuración y Ejecución Local

### Prerrequisitos

* Python 3.10+
* Cuenta de Azure con acceso a **Azure AI Document Intelligence**.

### Pasos

1. **Clonar el repositorio:**

    ```bash
    git clone "https://github.com/MedranoFelipe/SmartDoc.git"
    cd [tu-repo-name]
    ```

2. **Crear y activar el entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    # o .\venv\Scripts\activate # En Windows
    ```

3. **Instalar dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Configurar Azure AI:**

    Crea un archivo llamado **`.env`** en la raíz del proyecto y añade tus credenciales de Azure Document Intelligence:

    ```bash
    ENDPOINT=[Tu ENDPOINT de Azure AI]
    KEY=[Tu CLAVE de Azure AI]
    ```

5. **Ejecutar la aplicación Streamlit:**

    ```bash
    streamlit run app.py
    ```

La aplicación se abrirá automáticamente en tu navegador (normalmente en `http://localhost:8501`).
