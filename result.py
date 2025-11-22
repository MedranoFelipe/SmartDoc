import streamlit as st
from document_utils import validate_field_format, update_extraction_value

def render_field(label, key, doc_index, col=None):
    """Renderiza un input field conectado al estado con validación visual."""
    widget_key = f"doc{doc_index}-{key}" # Key única estandarizada
    doc = st.session_state.processed_data[doc_index]
    
    # 1. Obtener el valor inicial de la extracción (solo si es la primera carga)
    initial_val = doc["extraccion"].get(key, {}).get("value", "") 
        
    if widget_key not in st.session_state:
        st.session_state[widget_key] = initial_val
        
    # 3. El valor actual para validar es el que está en Session State
    current_val_in_state = st.session_state[widget_key] 
        
    # Detectar errores específicos de este campo para mostrar en UI
    error = validate_field_format(key, current_val_in_state) 
    
    container = col if col else st
    
    # Input Field
    container.text_input(
        label,
        key=widget_key, 
        on_change=update_extraction_value,
        args=(doc_index, key)
    )
    
    # Mostrar mensaje de error debajo del input si existe
    if error:
        container.caption(f":red[{error}]")

# --- RENDERIZADORES DE FORMULARIOS ---

def render_cedula_form(index):
    st.markdown("#### 👤 Información Personal")
    c1, c2, c3 = st.columns(3)
    render_field("Número de Cédula", "numero_identificacion", index, c1)
    render_field("Nombres", "nombres", index, c2)
    render_field("Apellidos", "apellidos", index, c3)
    
    st.markdown("#### 🧬 Datos Biométricos y Expedición")
    c4, c5, c6, c7 = st.columns(4)
    render_field("Fecha Nacimiento", "fecha_nacimiento", index, c4)
    render_field("RH", "rh", index, c5)
    render_field("Estatura", "estatura", index, c6)
    render_field("Sexo", "sexo", index, c7)
    
    c8, c9 = st.columns(2)
    render_field("Lugar Expedición", "lugar_expedicion", index, c8)
    render_field("Fecha Expedición", "fecha_expedicion", index, c9)

def render_seguro_form(index):
    st.markdown("#### 🛡️ Detalles de la Póliza")
    c1, c2, c3 = st.columns(3)
    render_field("No. Póliza", "numero_poliza", index, c1)
    render_field("Ramo", "ramo", index, c2)
    render_field("Estado", "estado_poliza", index, c3) 
    
    st.markdown("#### 📅 Vigencia y Asegurado")
    c4, c5 = st.columns([2, 1])
    render_field("Nombre Asegurado", "asegurado", index, c4)
    render_field("ID Asegurado", "identificacion", index, c5)
    
    c6, c7 = st.columns(2)
    render_field("Inicio Vigencia", "vigencia_inicio", index, c6)
    render_field("Fin Vigencia", "vigencia_fin", index, c7)

    st.markdown("#### 💰 Coberturas")
    c8, c9 = st.columns(2)
    render_field("Resp. Civil", "cobertura_rc_monto", index, c8)
    render_field("Pérdida Daños", "cobertura_daños", index, c9)
    render_field("Pérdida Hurto", "cobertura_hurto", index, c8)
    render_field("Asistencia", "cobertura_asistencia", index, c9) 

def render_contrato_form(index):
    # ... (código previo) ...

    st.markdown("#### 📝 Condiciones del Contrato")
    c3, c4, c5 = st.columns(3)
    render_field("No. Contrato", "numero_contrato", index, c3)
    render_field("Valor Total", "valor_contrato_monto", index, c4)
    render_field("Fecha Firma", "fecha_firma", index, c5)
    
    # --- BLOQUE CORREGIDO PARA text_area ---
    st.caption("Objeto del Contrato")
    
    widget_key = f"doc{index}-objeto_del_contrato_texto"
    doc = st.session_state.processed_data[index]
    initial_val = doc["extraccion"].get("objeto_del_contrato_texto", {}).get("value", "")

    # **1. Inicializar el valor en Session State si no existe**
    # Esto establece el valor inicial y evita el conflicto con 'value=...'
    if widget_key not in st.session_state:
        st.session_state[widget_key] = initial_val
        
    # **2. Renderizar el widget SIN el argumento 'value'**
    # El valor del widget ahora será automáticamente el de st.session_state[widget_key]
    st.text_area("Objeto", height=100, 
                  key=widget_key, # Usa la clave ya definida
                  on_change=update_extraction_value, 
                  args=(index, "objeto_del_contrato_texto"))
    
    # 3. Muestra el error de validación (similar a render_field)
    current_val_in_state = st.session_state[widget_key] 
    error = validate_field_format("objeto_del_contrato_texto", current_val_in_state) 
    if error:
         st.caption(f":red[{error}]")
    
    # --- FIN BLOQUE CORREGIDO ---

    c6, c7 = st.columns(2)
    render_field("Inicio Ejecución", "duracion_inicio", index, c6)
    render_field("Fin Ejecución", "duracion_fin", index, c7)

def render_generic_form(index):
    st.info("ℹ️ El tipo de documento no fue reconocido") 

# --- Generación de Reporte ---