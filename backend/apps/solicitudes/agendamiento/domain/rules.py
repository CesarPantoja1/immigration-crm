"""
Reglas de negocio del dominio de Agendamiento.
Re-exporta las reglas desde value_objects para compatibilidad.
"""
from .value_objects import (
    ReglaEmbajada,
    REGLAS_EMBAJADAS,
    obtener_regla_embajada
)

__all__ = [
    'ReglaEmbajada',
    'REGLAS_EMBAJADAS',
    'obtener_regla_embajada',
]
