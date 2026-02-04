"""
Constantes y mapeos para la app de Solicitudes.

Este módulo centraliza las constantes usadas en la app de solicitudes,
derivándolas de los modelos Django para evitar duplicación.

Uso:
    from apps.solicitudes.constants import (
        TIPO_VISA_FEATURE_A_DJANGO,
        EMBAJADA_FEATURE_A_DJANGO,
        ESTADO_FEATURE_A_DJANGO,
        ESTADO_DOC_FEATURE_A_DJANGO,
        CHECKLISTS_DOCUMENTOS,
    )
"""

# ==============================================================================
# MAPEOS DE TIPOS DE VISA
# ==============================================================================
# Mapea nombres usados en features BDD a valores Django
TIPO_VISA_FEATURE_A_DJANGO = {
    'VIVIENDA': 'vivienda',
    'TRABAJO': 'trabajo',
    'ESTUDIO': 'estudio',
}

# Mapeo inverso
TIPO_VISA_DJANGO_A_FEATURE = {v: k for k, v in TIPO_VISA_FEATURE_A_DJANGO.items()}


# ==============================================================================
# MAPEOS DE EMBAJADAS
# ==============================================================================
# Mapea nombres usados en features BDD a valores Django
EMBAJADA_FEATURE_A_DJANGO = {
    'ESTADOUNIDENSE': 'usa',
    'BRASILENA': 'brasil',
    'CANADIENSE': 'canada',
    'ESPANOLA': 'espana',
}

# Mapeo inverso
EMBAJADA_DJANGO_A_FEATURE = {v: k for k, v in EMBAJADA_FEATURE_A_DJANGO.items()}


# ==============================================================================
# MAPEOS DE ESTADOS DE SOLICITUD
# ==============================================================================
# Mapea estados usados en features BDD a valores Django
ESTADO_FEATURE_A_DJANGO = {
    'BORRADOR': 'borrador',
    'PENDIENTE': 'pendiente',
    'EN_REVISION': 'en_revision',
    'APROBADO': 'aprobada',
    'APROBADA': 'aprobada',
    'DESAPROBADO': 'rechazada',
    'RECHAZADO': 'rechazada',
    'RECHAZADA': 'rechazada',
    'ENVIADA_EMBAJADA': 'enviada_embajada',
    'ESPERANDO_DECISION_EMBAJADA': 'esperando_decision_embajada',
    'APROBADA_EMBAJADA': 'aprobada_embajada',
    'RECHAZADA_EMBAJADA': 'rechazada_embajada',
    'ENTREVISTA_AGENDADA': 'entrevista_agendada',
    'COMPLETADA': 'completada',
}

# Mapeo inverso
ESTADO_DJANGO_A_FEATURE = {v: k for k, v in ESTADO_FEATURE_A_DJANGO.items()}


# ==============================================================================
# MAPEOS DE ESTADOS DE DOCUMENTOS
# ==============================================================================
# Mapea estados usados en features BDD a valores Django
ESTADO_DOC_FEATURE_A_DJANGO = {
    'PENDIENTE': 'pendiente',
    'EN_REVISION': 'pendiente',  # En Django, pendiente significa que está para revisión
    'APROBADO': 'aprobado',
    'DESAPROBADO': 'rechazado',
    'RECHAZADO': 'rechazado',
}

# Mapeo inverso
ESTADO_DOC_DJANGO_A_FEATURE = {
    'pendiente': 'PENDIENTE',
    'aprobado': 'APROBADO',
    'rechazado': 'RECHAZADO',
}


# ==============================================================================
# CHECKLISTS DE DOCUMENTOS POR TIPO DE VISA
# ==============================================================================
# Define los documentos obligatorios para cada tipo de visa
CHECKLISTS_DOCUMENTOS = {
    'vivienda': [
        'Pasaporte',
        'Antecedentes penales',
        'Foto',
        'Escritura de propiedad',
    ],
    'trabajo': [
        'Pasaporte',
        'Antecedentes penales',
        'Foto',
        'Contrato de trabajo',
    ],
    'estudio': [
        'Pasaporte',
        'Antecedentes penales',
        'Foto',
        'Certificado de matricula',
    ],
}

# Documentos base requeridos para todos los tipos de visa
DOCUMENTOS_BASE = [
    'Pasaporte',
    'Antecedentes penales',
    'Foto',
]


# ==============================================================================
# FUNCIONES AUXILIARES
# ==============================================================================

def normalizar_estado_solicitud(estado_feature: str) -> str:
    """
    Convierte estado del feature a estado Django.
    
    Args:
        estado_feature: Estado en formato feature (ej: 'EN_REVISION')
    
    Returns:
        Estado en formato Django (ej: 'en_revision')
    """
    return ESTADO_FEATURE_A_DJANGO.get(estado_feature.upper(), estado_feature.lower())


def normalizar_estado_documento(estado_feature: str) -> str:
    """
    Convierte estado del feature a estado Django para documentos.
    
    Args:
        estado_feature: Estado en formato feature (ej: 'APROBADO')
    
    Returns:
        Estado en formato Django (ej: 'aprobado')
    """
    return ESTADO_DOC_FEATURE_A_DJANGO.get(estado_feature.upper(), estado_feature.lower())


def normalizar_tipo_visa(tipo_visa_feature: str) -> str:
    """
    Convierte tipo de visa del feature a formato Django.
    
    Args:
        tipo_visa_feature: Tipo de visa en formato feature (ej: 'VIVIENDA')
    
    Returns:
        Tipo de visa en formato Django (ej: 'vivienda')
    """
    return TIPO_VISA_FEATURE_A_DJANGO.get(tipo_visa_feature.upper(), tipo_visa_feature.lower())


def normalizar_embajada(embajada_feature: str) -> str:
    """
    Convierte embajada del feature a formato Django.
    
    Args:
        embajada_feature: Embajada en formato feature (ej: 'ESTADOUNIDENSE')
    
    Returns:
        Embajada en formato Django (ej: 'usa')
    """
    return EMBAJADA_FEATURE_A_DJANGO.get(embajada_feature.upper(), embajada_feature.lower())


def obtener_checklist(tipo_visa: str) -> list:
    """
    Obtiene el checklist de documentos para un tipo de visa.
    
    Args:
        tipo_visa: Tipo de visa (puede ser feature o Django format)
    
    Returns:
        Lista de documentos requeridos
    """
    tipo_normalizado = normalizar_tipo_visa(tipo_visa)
    return CHECKLISTS_DOCUMENTOS.get(tipo_normalizado, DOCUMENTOS_BASE)
