# -*- coding: utf-8 -*-
"""
Helpers para crear instancias de modelos Django SIN persistir en BD.
Se usan para testing de logica pura en los steps BDD.
"""
import os
import sys

# Configurar Django ANTES de importar modelos
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.testing')

import django
django.setup()

from datetime import date, time

from apps.usuarios.models import Usuario
from apps.preparacion.models import Simulacro, Recomendacion, ConfiguracionIA


def crear_usuario_en_memoria(id_usuario: int, nombre: str, apellido: str, rol: str) -> Usuario:
    """
    Crea una instancia de Usuario Django SIN guardar en BD.
    Se usa para testing de logica pura.
    """
    usuario = Usuario(
        id=id_usuario,
        email=f"{nombre.lower()}.{apellido.lower() if apellido else 'test'}@test.com",
        first_name=nombre,
        last_name=apellido,
        rol=rol,
        is_active=True
    )
    return usuario


def crear_simulacro_en_memoria(
    id_sim: int,
    codigo: str,
    asesor: Usuario,
    cliente: Usuario,
    estado: str = 'completado'
) -> Simulacro:
    """
    Crea una instancia de Simulacro Django SIN guardar en BD.
    Asigna las relaciones directamente sin FK real.
    """
    simulacro = Simulacro(
        id=id_sim,
        fecha=date.today(),
        hora=time(10, 0),
        modalidad='virtual',
        estado=estado
    )
    # Asignar relaciones directamente (sin FK real en BD)
    simulacro._asesor = asesor
    simulacro._cliente = cliente
    simulacro._codigo = codigo
    # Override de propiedades para que funcionen sin BD
    simulacro.asesor = asesor
    simulacro.cliente = cliente
    return simulacro


def crear_configuracion_ia_en_memoria(asesor: Usuario, con_api_key: bool = True) -> ConfiguracionIA:
    """
    Crea una instancia de ConfiguracionIA Django SIN guardar en BD.
    """
    config = ConfiguracionIA(
        id=1,
        api_key='test-api-key-12345' if con_api_key else '',
        modelo='gemini-2.0-flash',
        activo=con_api_key
    )
    config._asesor = asesor
    config.asesor = asesor
    return config


def crear_recomendacion_en_memoria(simulacro: Simulacro) -> Recomendacion:
    """
    Crea una instancia de Recomendacion Django SIN guardar en BD.
    Simula lo que la IA generaria.
    """
    recomendacion = Recomendacion(
        id=simulacro.id,
        estado_feedback='generado',
        claridad='alto',
        coherencia='medio',
        seguridad='alto',
        pertinencia='medio',
        nivel_preparacion='medio',
        fortalezas=[
            {
                'categoria': 'Claridad',
                'descripcion': 'Respuestas claras y directas',
                'pregunta_relacionada': 'Proposito del viaje',
                'impacto': 'alto'
            }
        ],
        puntos_mejora=[
            {
                'categoria': 'Seguridad',
                'descripcion': 'Mostrar mas confianza al responder',
                'pregunta_relacionada': 'Vinculos familiares',
                'impacto': 'medio'
            }
        ],
        recomendaciones=[
            {
                'titulo': 'Practicar respuestas',
                'descripcion': 'Ensayar las respuestas frente a un espejo',
                'accion_concreta': 'Dedicar 30 minutos diarios a practicar',
                'impacto': 'alto'
            }
        ],
        accion_sugerida='Reforzar los puntos de mejora identificados',
        publicada=True
    )
    recomendacion.simulacro = simulacro
    # Calcular nivel usando el metodo REAL del modelo
    recomendacion.nivel_preparacion = recomendacion.calcular_nivel_preparacion()
    return recomendacion
