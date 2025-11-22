import re

def clean_number(text):
    """Deja solo dígitos. Ej: '1.234.567' -> '1234567'"""
    if not text: return None
    return re.sub(r'[^\d]', '', text)

def clean_currency(text):
    """Elimina texto como COP/USD pero deja formato moneda. Ej: '$ 10.000 COP' -> '$10.000'"""
    if not text: return None
    return re.sub(r'[^\d\.,\$]', '', text).strip()

def clean_text_basic(text):
    """Elimina espacios múltiples y saltos de línea."""
    if not text: return None
    return ' '.join(text.split())


def find_by_regex(text, pattern, cleaning_func=None):
    """
    Busca patrón y aplica función de limpieza si se especifica.
    """        
    match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
    val = match.group(1).strip() if match and match.group(1) else None
    
    if val and cleaning_func:
        return cleaning_func(val)
    return val

def extract_cedula(text):
    text = text.upper()
    return {
        "numero_identificacion": find_by_regex(text, r"NÚMERO:\s*([\d\.]+)", clean_number),
        "apellidos": find_by_regex(text, r"APELLIDOS:\s*(.+?)NOMBRES:", clean_text_basic),
        "nombres": find_by_regex(text, r"NOMBRES:\s*(.+?)FECHA DE NACIMIENTO:", clean_text_basic),
        "fecha_nacimiento": find_by_regex(text, r"FECHA DE NACIMIENTO:\s*(\d{2}-[A-Z]{3}-\d{4})"),
        "lugar_nacimiento": find_by_regex(text, r"LUGAR DE NACIMIENTO:\s*(.+?)ESTATURA:", clean_text_basic),        
        "estatura": find_by_regex(text, r"ESTATURA:\s*([\d\.]+ M)", clean_number),
        "rh": find_by_regex(text, r"RH:\s*([ABO]{1,2}[\+\-])", clean_text_basic),
        "sexo": find_by_regex(text, r"SEXO:\s*([FM])", clean_text_basic),
        "fecha_expedicion": find_by_regex(text, r"FECHA DE EXPEDICIÓN:\s*(\d{2}-[A-Z]{3}-\d{4})"),
        "lugar_expedicion": find_by_regex(text, r"LUGAR DE EXPEDICIÓN:\s*(.+?)ÍNDICE"),
    }

def extract_acta_seguro(text):
    text = ' '.join(text.upper().split())  
    
    return {
        # Limpiamos guiones o letras de la póliza para validación numérica estricta
        "numero_poliza": find_by_regex(text, r"NÚMERO DE PÓLIZA:\s*([A-Z0-9\-]+)", clean_number),                
        "ramo": find_by_regex(text, r"RAMO:\s*(.+?)\s*(?:[•·]\s*)?TOMADOR", clean_text_basic),        
        "asegurado": find_by_regex(text, r"TOMADOR\s*/\s*ASEGURADO:\s*([A-ZÁÉÍÓÚÜÑ\s\-]+?)\s*(?:[•·]\s*)?IDENTIFICACIÓN:", clean_text_basic),
        "identificacion": find_by_regex(text, r"IDENTIFICACIÓN:\s*([C\.\sE\d\.]+)(?:\s*VIGENCIA)?", clean_number),        
        "vigencia_inicio": find_by_regex(text, r"FECHA DE INICIO:\s*(\d{1,2} DE [A-ZÁÉÍÓÚÜÑ]+ DE \d{4}.*?)(?:[•·]\s*)(?=\s*FECHA DE FIN)"),
        "vigencia_fin": find_by_regex(text, r"FECHA DE FIN:\s*(\d{1,2} DE [A-ZÁÉÍÓÚÜÑ]+ DE \d{4}.*?)(?=\s*RESUMEN|4\.)", ),                        
        "cobertura_rc_monto": find_by_regex(text, r"RESPONSABILIDAD CIVIL EXTRACONTRACTUAL:\s*(.+?COP)", clean_currency),        
        "cobertura_daños": find_by_regex(text, r"PÉRDIDA TOTAL POR DAÑOS:\s*(.+?)3\.", clean_text_basic),
        "cobertura_hurto": find_by_regex(text, r"PÉRDIDA TOTAL POR HURTO:\s*(.+?)4\.", clean_text_basic),
        "cobertura_asistencia": find_by_regex(text, r"ASISTENCIA JURÍDICA:\s*(.+?)ESTADO", clean_text_basic),
        "estado_poliza": find_by_regex(text, r"ESTADO DE LA PÓLIZA:\s*([A-Z]+)", clean_text_basic),
    }

def extract_contrato(text):
    text_processed = ' '.join(text.lower().split())
    return {
        "numero_contrato": find_by_regex(text_processed, r"profesionales no\.?\s*([\d\-]+)", clean_number),
        "contratante_nombre": find_by_regex(text_processed, r"por una parte,\s*(.+?)\s*,\s*sociedad", clean_text_basic),
        "contratante_nit": find_by_regex(text_processed, r"nit\s*([\d\.\-]+)", clean_number),
        "contratista_nombre": find_by_regex(text_processed, r"por otra parte,\s*([a-záéíóúüñ\s]+),\s*identificada", clean_text_basic),
        "contratista_identificacion": find_by_regex(text_processed, r"cédula de ciudadanía no\.?\s*([\d\.]+)", clean_number),
        "valor_contrato_monto": find_by_regex(text_processed, r"valor total.*?(\$[\d\.\,]+\s*cop)", clean_currency),
        "objeto_del_contrato_texto": find_by_regex(text_processed, r"cláusula primera\s*-\s*objeto:\s*(.*?)(?=cláusula segunda)", clean_text_basic),
        "duracion_inicio": find_by_regex(text_processed, r"contados a partir del ([0-9]{1,2} de [a-z]+ de \d{4})"),
        "duracion_fin": find_by_regex(text_processed, r"hasta el ([0-9]{1,2} de [a-z]+ de \d{4})"),
        "fecha_firma": find_by_regex(text_processed, r"a los ([0-9]{1,2} días del mes de [a-z]+ de \d{4})")
    }

def extract_structured_data(document_type, azure_json):
    text = azure_json.get("content", "").lower()
    match document_type:
        case "cedula": extracted_fields = extract_cedula(text)
        case "acta_seguro": extracted_fields = extract_acta_seguro(text)
        case "contrato": extracted_fields = extract_contrato(text)
        case _: extracted_fields = {}

    structured_output = {}
    for key, value in extracted_fields.items():
        if value is not None:
            structured_output[key] = {"value": value}
    return structured_output