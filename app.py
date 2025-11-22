import streamlit as st
from azure_client import analyze_bytes_document
from extractors import extract_structured_data
from document_utils import *
from result import *

st.set_page_config(page_title="Gestión Documental IA | Seguros Bolívar", page_icon="👨‍👩‍👦", layout="wide")

st.markdown("""
    <style>
    .main .block-container { max-width: 1200px; padding-top: 2rem; padding-bottom: 3rem; }
    h1, h2, h3 { font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; font-weight: 700; }
    
    /* Tarjetas limpias */
    .stExpander {
        border: 1px solid rgba(128, 128, 128, 0.2);
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        background-color: transparent;
    }
    
    /* Botones estilizados */
    .stButton>button { border-radius: 8px; height: 3rem; font-weight: 600; transition: transform 0.2s; }
    .stButton>button:active { transform: scale(0.98); }
    
    /* Métricas */
    div[data-testid="metric-container"] {
        background-color: rgba(128, 128, 128, 0.1);
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #00C853;
    }
    </style>
""", unsafe_allow_html=True)

if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'processing_complete' not in st.session_state:
    st.session_state.processing_complete = False


c_logo, c_title = st.columns([0.5, 5])
with c_title:
    st.title("Solución Prueba técnica - Joven Talento de Analítica - Felipe Medrano Caicedo")    

st.divider()

col_upload, col_instruct = st.columns([2, 1])

with col_upload:
    st.subheader("📂 Carga de Documentos")
    uploaded_files = st.file_uploader(
        "Arrastre aquí sus archivos (PDF). Maximo 4 archivos por lote.",
        type=["pdf"],
        accept_multiple_files=True,
        on_change=reset_state
    )

    if uploaded_files and len(uploaded_files) > 4:
        st.error("❌ Solo puede subir hasta **4 archivos** PDF.")
        uploaded_files = []   

with col_instruct:
    st.info("**Instrucciones:**\n1. Suba los archivos.\n2. El sistema clasificará automáticamente.\n3. Valide los campos extraídos.\n4. Exporte el reporte organizado.")

if uploaded_files and not st.session_state.processing_complete:
    if st.button("⚡ Iniciar Procesamiento con Azure AI Document Intelligence", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        results = []
        
        for i, archivo in enumerate(uploaded_files):
            status_text.text(f"Analizando: {archivo.name}...")
            archivo.seek(0)
            bytes_data = archivo.read()
            
            try:
                azure_json = analyze_bytes_document(bytes_data)
                texto = azure_json.get("content", "")
                tipo = classify_document(texto)
                extraccion = extract_structured_data(tipo, azure_json)
                
                results.append({
                    "file_name": archivo.name, "bytes": bytes_data,
                    "tipo": tipo, "extraccion": extraccion,
                    "raw_json": azure_json, "estado": "Revisar", "validacion": []
                })
            except Exception as e:
                st.error(f"Error en {archivo.name}: {str(e)}")
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.session_state.processed_data = results
        st.session_state.processing_complete = True
        status_text.empty()
        for i in range(len(results)): revalidate_document(i)
        st.rerun()

# ASUME que la función 'is_data_valid_for_export()' está definida previamente,
# y que 'generate_excel()' también lo está.

def is_data_valid_for_export():
    """
    Verifica si todos los documentos en el estado tienen el estado 'Validado'.
    Retorna True si todos son válidos, False si hay al menos uno en 'Revisar'.
    """
    # Si no hay datos, asumimos que no es válido para exportar (o manejamos según el flujo)
    if 'processed_data' not in st.session_state or not st.session_state.processed_data:
        return False 

    # Revisa si ALGÚN documento está en estado 'Revisar'
    documents_to_review = [d for d in st.session_state.processed_data if d.get("estado") == "Revisar"]
    
    return len(documents_to_review) == 0

if st.session_state.processing_complete and st.session_state.processed_data:
    
    # 1. Verificar el estado global de la data
    # (Necesitas que is_data_valid_for_export esté disponible en este script)
    data_is_ok = is_data_valid_for_export()
    
    # Contar documentos a revisar para mostrar en métrica
    docs_to_review = sum(1 for d in st.session_state.processed_data if d.get("estado") == "Revisar")

    st.markdown("### 📊 Resumen del Lote")
    m1, m2, m3, m4, m5, m6 = st.columns(6) # Aumentamos columnas para la métrica de revisión
    m1.metric("Total Documentos", len(st.session_state.processed_data))
    m2.metric("Cédulas", sum(1 for d in st.session_state.processed_data if d['tipo'] == 'cedula'))
    m3.metric("Actas de Seguro", sum(1 for d in st.session_state.processed_data if d['tipo'] == 'acta_seguro'))
    m4.metric("Contratos", sum(1 for d in st.session_state.processed_data if d['tipo'] == 'contrato'))
    m5.metric("Desconocidos", sum(1 for d in st.session_state.processed_data if d['tipo'] == 'desconocido'))
    m6.metric("🚨 Pendientes Revisión", docs_to_review) # Nueva métrica clave
    
    st.divider()
    
    # --- Lógica del Botón de Descarga ---
    c_tools_1, c_tools_2 = st.columns([3, 1])
    with c_tools_1:
        st.subheader("🔍 Validación Detallada")
        if not data_is_ok:
            st.warning("⚠️ **Bloqueado:** No se puede descargar el reporte. Existen **documentos con errores** que requieren corrección y validación completa.")
        else:
            st.success("✅ Todos los documentos han sido **validados** y están listos para la exportación.")

    with c_tools_2:
        try:
            excel_data = generate_excel(st.session_state.processed_data)
            
            # La clave es usar 'data_is_ok' para deshabilitar el botón
            st.download_button(
                label="📥 Descargar Reporte Excel",
                data=excel_data,
                file_name="Reporte_Extraccion_Consolidado.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True,
                # 🔥 DESHABILITAR si la data NO está OK (hay documentos en 'Revisar')
                disabled=not data_is_ok 
            )
        except Exception as e:
            st.error(f"Error generando Excel: {e}")    

    st.divider()
    
    for i, doc in enumerate(st.session_state.processed_data):
        
        icon_map = {
            "cedula": "🆔",
            "acta_seguro": "🚗",
            "contrato": "⚖️",
            "desconocido": "❓"
        }
    
        tipo = doc['tipo']
        icon = icon_map.get(tipo, "📄")

        if tipo == "desconocido":
            col_tipo = "red"
        else:
            col_tipo = "blue"
        
        # Actualizamos el color según el ESTADO de validación
        if doc.get('estado') == 'Revisar':
            col_status = "red"
            status_text = "🚨 REVISAR"
        elif doc.get('estado') == 'Validado':
            col_status = "green"
            status_text = "✅ VALIDADO"
        else:
            col_status = "blue"
            status_text = tipo.upper() # Estado inicial o desconocido
            
        with st.expander(
            f"{icon} {doc['file_name']} | Tipo: **:{col_tipo}[{tipo.upper()}]**  Estado: **:{col_status}[{status_text}]**",
            expanded=(doc.get('estado') == 'Revisar') # Expandir automáticamente si requiere revisión
        ):
            
            col_pdf, col_form = st.columns([0.45, 0.55], gap="large")
            
            with col_pdf:
                st.caption("📄 Vista Previa")
                display_pdf(doc["bytes"])
                
            with col_form:
                st.markdown("---")
                
                # Mostrar advertencias si existen
                if doc.get('validacion'):
                    st.error("Documento con errores de validación en los siguientes campos:")
                    for error_msg in doc['validacion']:
                        field_name = error_msg.split(':')[0].strip()
                        st.text(f"- **{field_name}**") # Usamos ** para negrita
                
                # Renderizar formulario (sin cambios)
                if doc['tipo'] == 'cedula':
                    render_cedula_form(i)
                elif doc['tipo'] == 'acta_seguro':
                    render_seguro_form(i)
                elif doc['tipo'] == 'contrato':
                    render_contrato_form(i)
                else:
                    render_generic_form(i)
