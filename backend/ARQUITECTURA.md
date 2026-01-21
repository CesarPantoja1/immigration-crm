# Arquitectura del CRM Migratorio

## Introducción

Este documento describe la arquitectura hexagonal simplificada implementada en el CRM Migratorio, organizada por **CAPACIDADES** y **CARACTERÍSTICAS**.

## Principios de Diseño

### Arquitectura Hexagonal Simplificada

Cada característica se estructura en cuatro capas:

1. **Domain (Dominio)**: Lógica de negocio pura, independiente de frameworks
2. **Infrastructure (Infraestructura)**: Implementación con Django ORM
3. **Application (Aplicación)**: Casos de uso y orquestación
4. **Presentation (Presentación)**: Vistas, formularios y URLs de Django

### Organización por Capacidades

El sistema se organiza en **CAPACIDADES** de negocio, cada una con múltiples **CARACTERÍSTICAS**:

```
CAPACIDAD 1: Solicitudes
├── CARACTERÍSTICA 1.1: Recepción
└── CARACTERÍSTICA 1.2: Agendamiento

CAPACIDAD 2: Preparación
├── CARACTERÍSTICA 2.1: Simulación
└── CARACTERÍSTICA 2.2: Recomendaciones

CAPACIDAD 3: Notificaciones
├── CARACTERÍSTICA 3.1: Seguimiento
└── CARACTERÍSTICA 3.2: Coordinación
```

## Estructura de Directorios

```
backend/
│
├── config/                          # Configuración Django
│   ├── settings/
│   │   ├── base.py                 # Settings compartidos
│   │   ├── development.py          # Settings de desarrollo
│   │   ├── testing.py              # Settings de testing
│   │   └── production.py           # Settings de producción
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│   └── celery.py                   # Configuración de Celery
│
├── apps/                            # Apps Django
│   ├── core/                       # Funcionalidades compartidas
│   │   ├── models.py               # Modelos abstractos base
│   │   ├── events.py               # Event Bus (Django Signals)
│   │   └── middleware/
│   │
│   ├── usuarios/                   # Gestión de usuarios
│   │   ├── domain/
│   │   ├── infrastructure/
│   │   │   └── models.py
│   │   ├── application/
│   │   └── presentation/
│   │       ├── views.py
│   │       ├── forms.py
│   │       └── urls.py
│   │
│   ├── solicitudes/                # CAPACIDAD 1
│   │   ├── recepcion/              # CARACTERÍSTICA 1.1
│   │   │   ├── domain/
│   │   │   ├── infrastructure/
│   │   │   │   └── models.py      # Modelo: Solicitud
│   │   │   ├── application/
│   │   │   └── presentation/
│   │   │
│   │   └── agendamiento/           # CARACTERÍSTICA 1.2
│   │       ├── domain/
│   │       ├── infrastructure/
│   │       │   └── models.py      # Modelos: Entrevista, HorarioDisponible, ReglaEmbajada
│   │       ├── application/
│   │       └── presentation/
│   │
│   ├── preparacion/                # CAPACIDAD 2
│   │   ├── simulacion/             # CARACTERÍSTICA 2.1
│   │   │   ├── domain/
│   │   │   ├── infrastructure/
│   │   │   │   └── models.py      # Modelos: Simulacro, PreguntaSimulacro, etc.
│   │   │   ├── application/
│   │   │   └── presentation/
│   │   │
│   │   └── recomendaciones/        # CARACTERÍSTICA 2.2
│   │       ├── domain/
│   │       ├── infrastructure/
│   │       │   └── models.py      # Modelos: DocumentoRecomendaciones, etc.
│   │       ├── application/
│   │       └── presentation/
│   │
│   └── notificaciones/             # CAPACIDAD 3
│       ├── seguimiento/            # CARACTERÍSTICA 3.1
│       │   ├── domain/
│       │   ├── infrastructure/
│       │   │   └── models.py      # Modelos: EstadoSolicitud, Notificacion
│       │   ├── application/
│       │   └── presentation/
│       │
│       └── coordinacion/           # CARACTERÍSTICA 3.2
│           ├── domain/
│           ├── infrastructure/
│           │   └── models.py      # Modelos: Recordatorio, ComunicacionExterna
│           ├── application/
│           └── presentation/
│
├── features/                        # Tests BDD con Behave
│   ├── environment.py              # Configuración de Behave
│   ├── steps/                      # Steps compartidos
│   │   ├── common_steps.py
│   │   ├── auth_steps.py
│   │   └── data_steps.py
│   │
│   ├── solicitudes/
│   │   └── agendamiento/
│   │       ├── agendamiento_entrevista.feature
│   │       └── steps/
│   │
│   ├── preparacion/
│   │   ├── simulacion/
│   │   │   ├── simulacion_entrevista.feature
│   │   │   └── steps/
│   │   └── recomendaciones/
│   │       ├── generacion_recomendaciones.feature
│   │       └── steps/
│   │
│   └── notificaciones/
│       ├── seguimiento/
│       └── coordinacion/
│
├── templates/                       # Templates globales
├── static/                          # Archivos estáticos globales
├── media/                           # Archivos subidos
├── logs/                            # Logs del sistema
└── scripts/                         # Scripts útiles
    ├── init_db.py
    └── seed_data.py
```

## Modelos de Datos Principales

### Capacidad 1: Solicitudes

#### Recepción
- **Solicitud**: Solicitud migratoria del usuario

#### Agendamiento
- **Entrevista**: Entrevista agendada en embajada
- **HorarioDisponible**: Horarios disponibles por embajada
- **ReglaEmbajada**: Reglas específicas de cada embajada

### Capacidad 2: Preparación

#### Simulación
- **Simulacro**: Simulacro de entrevista
- **PreguntaSimulacro**: Preguntas del simulacro
- **CuestionarioPractica**: Cuestionarios de auto-práctica
- **PreguntaPractica**: Preguntas de práctica

#### Recomendaciones
- **DocumentoRecomendaciones**: Documento generado por IA
- **IndicadorDesempeno**: Indicadores evaluados
- **RecomendacionEspecifica**: Recomendaciones por categoría

### Capacidad 3: Notificaciones

#### Seguimiento
- **EstadoSolicitud**: Historial de estados
- **Notificacion**: Notificaciones del sistema

#### Coordinación
- **Recordatorio**: Recordatorios programados
- **ComunicacionExterna**: Comunicaciones con embajadas

## Event Bus (Django Signals)

El sistema utiliza Django Signals como Event Bus para la comunicación entre apps:

### Eventos Disponibles

```python
# Solicitudes
solicitud_creada
solicitud_aprobada
solicitud_rechazada

# Entrevistas
entrevista_agendada
entrevista_reprogramada
entrevista_cancelada
entrevista_completada

# Simulación
simulacro_iniciado
simulacro_completado

# Recomendaciones
recomendaciones_generadas

# Notificaciones
notificacion_enviada
notificacion_fallida
```

## Flujo de Trabajo Típico

### 1. Agendamiento de Entrevista

```
Usuario → Presentation (views.py)
       → Application (use cases)
       → Domain (reglas de negocio)
       → Infrastructure (models.py - guardar en BD)
       → Event: entrevista_agendada
       → Notificaciones (listener)
```

### 2. Simulacro y Recomendaciones

```
Simulacro completado
       → Event: simulacro_completado
       → Recomendaciones (listener)
       → IA analiza transcripción
       → Genera DocumentoRecomendaciones
       → Event: recomendaciones_generadas
       → Notificaciones (listener)
```

## Testing

### BDD con Behave

- Features organizadas por CAPACIDAD → CARACTERÍSTICA
- Steps compartidos en `features/steps/`
- Steps específicos en cada característica

### Ejecución

```bash
# Todas las features
behave

# Una característica específica
behave features/solicitudes/agendamiento/
```

## Mejoras Futuras

1. Implementar capa de Application (casos de uso)
2. Agregar capa de Domain (entidades y value objects)
3. Implementar API REST con DRF
4. Agregar autenticación JWT
5. Implementar cache con Redis
6. Agregar monitoreo con Sentry
7. Implementar CI/CD con GitHub Actions

## Convenciones de Código

- Modelos en español (nombres de campos y verbose_name)
- Código y comentarios en español
- Usar type hints cuando sea posible
- Seguir PEP 8 para estilo de código
- Tests BDD en español (Gherkin)
