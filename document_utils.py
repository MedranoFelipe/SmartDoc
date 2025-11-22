import base64
import re
import io
import pandas as pd
import streamlit as st 

def display_pdf(file_bytes):
    """Muestra un PDF en un iframe de HTML usando base64."""
    base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#view=fitH" width="100%" height="500"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def reset_state():
    st.session_state.processed_data = None
    st.session_state.processing_complete = False

def classify_document(text):
    """Clasifica documentos según expresiones clave."""
    patterns = {
        "cedula": "REPÚBLICA DE COLOMBIA IDENTIFICACIÓN PERSONAL CÉDULA DE CIUDADANÍA",
        "acta_seguro": "CERTIFICADO DE COBERTURA Y ACTA DE SEGURO",
        "contrato": "CONTRATO DE PRESTACIÓN DE SERVICIOS PROFESIONALES",
    }
    for label, pattern in patterns.items():
        if pattern in text:
            return label
    return "desconocido"


def get_field_type(key):
    """Determina el tipo de dato esperado basado en la clave. Usa listas estrictas para evitar errores de substring."""
    key_lower = key.lower()
    
    if key_lower in ["estado_poliza", "cobertura_asistencia", "estatura", "ramo", "asegurado", "nombres", "apellidos", "rh", "sexo", "lugar_nacimiento", "lugar_expedicion", "contratante_nombre", "contratista_nombre"]:
        return "text_strict" 
        
    if key_lower in ["objeto_del_contrato_texto"]:
        return "text_long"
            
    if key_lower in ["cobertura_daños", "cobertura_hurto"]:
        return "percentage"
            
    if key_lower in ["identificacion", "cedula", "nit", "telefono", 
                     "numero_poliza", "numero_contrato", "contratista_identificacion", "contratante_nit", "numero_identificacion"]:
        return "numeric_strict"
        
    if any(x in key_lower for x in ["valor", "monto", "cobertura_rc_monto", "valor_contrato_monto"]):
        return "currency"
            
    if any(x in key_lower for x in ["fecha", "vigencia", "nacimiento", "duracion"]):
        return "date"
        
    return "text_long"

def sanitize_value(key, value):
    """Limpia el valor ingresado según el tipo de campo."""
    dtype = get_field_type(key)
    val_str = str(value).strip() 
    
    if dtype == "text_strict":
        val_str = re.sub(r'[^a-zA-Z0-9\s]', '', val_str)        
        return val_str[:50]
    
    if dtype == "text_long":                
        val_str = ' '.join(val_str.split())
        return val_str
        
    if dtype == "numeric_strict": 
        return re.sub(r'[^\d]', '', val_str)
    
    if dtype == "currency": 
        if re.search(r'[a-zA-Z]', val_str):
            return "" 
        val_str = re.sub(r'[^\d\.,]', '', val_str) 
        pure_digits = re.sub(r'[^\d]', '', val_str)

        if not pure_digits:
            return ""
        
        try: 
            formatted_number = "{:,}".format(int(pure_digits)).replace(",", ".")
            return f"${formatted_number}"
            
        except ValueError:
            return ""
            
    if dtype == "percentage":
        return val_str.upper()
    
    if dtype == "date":        
        val_str = re.sub(r'[\.\-]', '/', val_str)         
        val_str = re.sub(r'/+', '/', val_str)
        return re.sub(r'[\,\;]$', '', val_str).strip()
            
    return val_str

def validate_field_format(key, value):
    """Valida formato retornando mensaje de error si falla."""
    if not value or str(value).strip() == "":
        return "⚠️ Campo vacío"

    val_str = str(value).strip()
    dtype = get_field_type(key)
        
    if dtype == "text_strict":
        if len(val_str) > 50:
            return f"El texto excede el límite de 50 caracteres (actual: {len(val_str)})"        
            
    if dtype == "numeric_strict":
        if not val_str.isdigit() or len(val_str) < 4:
            return "Solo debe contener números (mín. 4 dígitos)"
            
    if dtype == "currency":
        if not re.search(r'\d', val_str):
            return "El valor de moneda es inválido"

    if dtype == "percentage":        
        if not re.search(r'(\d+.*%)|(\d+.*VALOR\s*COMERCIAL)', val_str, re.IGNORECASE):
            return "Debe indicar porcentaje (ej: 100% VALOR COMERCIAL)"
            
    if dtype == "date": 
        date_time_pattern = r'^\d{2}/\d{2}/\d{4}(\s\d{2}:\d{2})?$'
        if not re.match(date_time_pattern, val_str):
            return "Formato de fecha/hora inválido. Requerido: dd/mm/aaaa o dd/mm/aaaa hh:mm"

    return None


def revalidate_document(doc_index):
    """Re-ejecuta validaciones en todo el documento."""
    doc = st.session_state.processed_data[doc_index]
    new_validation = []
    
    for key, data in doc["extraccion"].items():
        field_value = data.get("value", "")
        error_msg = validate_field_format(key, field_value)
        
        if error_msg:
            readable_key = key.replace('_', ' ').title()
            new_validation.append(f"{readable_key}: {error_msg}")

    doc["validacion"] = new_validation
    doc["estado"] = "Revisar" if new_validation else "Validado"
    st.session_state.processed_data[doc_index] = doc

def update_extraction_value(doc_index, field_key):
    """Callback ejecutado cuando el usuario cambia un input."""
    widget_key = f"doc{doc_index}-{field_key}"
    
    if widget_key in st.session_state:
        raw_value = st.session_state[widget_key]
                
        clean_value = sanitize_value(field_key, raw_value)
                
        st.session_state.processed_data[doc_index]['extraccion'][field_key]['value'] = clean_value
                
        if raw_value != clean_value:
            st.session_state[widget_key] = clean_value
                    
        revalidate_document(doc_index)




def generate_excel(processed_data):
    """Genera Excel basado en los datos actuales de session_state."""
    output = io.BytesIO()
    
    grouped_data = {
        "Cédulas": [d for d in processed_data if d['tipo'] == 'cedula'],
        "Actas de Seguro": [d for d in processed_data if d['tipo'] == 'acta_seguro'],
        "Contratos": [d for d in processed_data if d['tipo'] == 'contrato'],
        "Otros": [d for d in processed_data if d['tipo'] == 'desconocido']
    }

    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        for sheet_name, data_list in grouped_data.items():
            if not data_list:
                continue 
            
            rows = []
            for d in data_list:                
                row = {"Archivo": d["file_name"], "Estado Validación": d["estado"]}                                
                for k, v in d["extraccion"].items():
                    row[k] = v.get("value")
                    
                rows.append(row)
            
            df = pd.DataFrame(rows)
            
            df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            worksheet = writer.sheets[sheet_name]
            for i, col in enumerate(df.columns):                
                max_len = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_len)

    return output.getvalue()