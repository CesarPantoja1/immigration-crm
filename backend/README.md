# Backend - CRM Migratorio (MigraFácil)

API REST Django para el sistema de gestión de trámites migratorios.

## Requisitos

- Python 3.10+
- pip

## Instalación y Ejecución

### 1. Crear y activar entorno virtual

```bash
# Crear entorno virtual
python -m venv venv

# Activar (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activar (Windows CMD)
.\venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Aplicar migraciones

```bash
python manage.py migrate
```

### 4. Crear superusuario (admin)

```bash
python manage.py createsuperuser
```

### 5. Ejecutar servidor

```bash
python manage.py runserver
```

El servidor se ejecutará en: `http://127.0.0.1:8000`

## URLs Disponibles

| URL | Descripción |
|-----|-------------|
| `http://127.0.0.1:8000/admin/` | Panel de administración |
| `http://127.0.0.1:8000/api/` | API REST |

## Endpoints de la API

### Autenticación

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/auth/registro/` | POST | Registrar nuevo usuario |
| `/api/auth/login/` | POST | Iniciar sesión (retorna JWT) |
| `/api/auth/logout/` | POST | Cerrar sesión |
| `/api/auth/refresh/` | POST | Refrescar token |
| `/api/auth/perfil/` | GET/PATCH | Ver/editar perfil |
| `/api/auth/cambiar-password/` | POST | Cambiar contraseña |

### Usuarios

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/api/usuarios/` | GET | Listar usuarios |
| `/api/usuarios/asesores/` | GET | Listar asesores |
| `/api/usuarios/<id>/` | GET/PATCH | Detalle/editar usuario |

### Solicitudes

| Endpoint | Método | Rol | Descripción |
|----------|--------|-----|-------------|
| `/api/solicitudes/mis-solicitudes/` | GET | Cliente | Mis solicitudes |
| `/api/solicitudes/nueva/` | POST | Cliente | Crear solicitud |
| `/api/solicitudes/<id>/` | GET | Todos | Detalle solicitud |
| `/api/solicitudes/asignadas/` | GET | Asesor | Solicitudes asignadas |
| `/api/solicitudes/pendientes/` | GET | Admin | Sin asignar |
| `/api/solicitudes/<id>/actualizar/` | PATCH | Asesor | Actualizar estado |
| `/api/solicitudes/<id>/asignar/` | POST | Admin | Asignar asesor |
| `/api/solicitudes/estadisticas/cliente/` | GET | Cliente | Stats cliente |
| `/api/solicitudes/estadisticas/asesor/` | GET | Asesor | Stats asesor |

## Estructura del Proyecto

```
backend/
├── apps/
│   ├── core/           # Modelos base, eventos
│   ├── usuarios/       # Autenticación y usuarios
│   ├── solicitudes/    # Gestión de solicitudes
│   ├── preparacion/    # Simulacros y recomendaciones
│   └── notificaciones/ # Seguimiento y alertas
├── config/
│   └── settings/
│       ├── base.py         # Configuración base
│       ├── development.py  # Desarrollo (SQLite)
│       ├── testing.py      # Testing
│       └── production.py   # Producción
├── features/           # Tests BDD (Behave)
├── templates/          # Templates HTML
├── static/             # Archivos estáticos
└── manage.py
```

## Tests

### Ejecutar tests BDD (Behave)

```bash
python manage.py behave
```

### Ejecutar tests unitarios (pytest)

```bash
pytest
```

## Roles de Usuario

| Rol | Descripción |
|-----|-------------|
| `cliente` | Solicitante de visa |
| `asesor` | Revisa y gestiona solicitudes (límite 10/día) |
| `admin` | Administrador del sistema |

## Solución de Problemas

### Error: "No such file or directory: logs/django.log"

Si al ejecutar `python manage.py runserver` recibes un error sobre el directorio `logs/`, asegúrate de que el directorio exista:

```bash
# Windows PowerShell/CMD
mkdir logs

# Linux/Mac
mkdir -p logs
```

El directorio `logs/` ya debería existir en el repositorio con un archivo `.gitignore` que mantiene la estructura pero ignora los archivos de log.

## Creación de Usuarios Asesores

Existen tres formas de crear usuarios con rol de asesor en el sistema:

### Opción 1: Django Shell (Recomendada para desarrollo)

```bash
# Activar entorno virtual primero
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Abrir shell de Django
python manage.py shell
```

Dentro del shell ejecutar:

```python
from apps.usuarios.models import Usuario

# Crear usuario asesor
asesor = Usuario.objects.create_user(
    email='asesor@example.com',
    password='Asesor123!',
    first_name='Carlos',
    last_name='González',
    rol='asesor',
    telefono='+57 300 1234567',
    limite_solicitudes_diarias=10  # Opcional, default: 10
)

print(f'Asesor creado: {asesor.email} (ID: {asesor.id})')
```

### Opción 2: Panel de Administración

1. Acceder a `http://127.0.0.1:8000/admin/`
2. Iniciar sesión con credenciales de superusuario
3. Ir a **Usuarios** → **Agregar Usuario**
4. Completar los campos:
   - Email (requerido)
   - Nombre y Apellido
   - Contraseña
   - **Rol: asesor**
   - Teléfono (opcional)
5. Guardar

### Opción 3: API REST (requiere autenticación de admin)

```bash
# Primero obtener token de admin
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@example.com", "password": "admin123"}'

# Crear asesor con el token obtenido
curl -X POST http://127.0.0.1:8000/api/auth/registro/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <TOKEN>" \
  -d '{
    "email": "nuevo.asesor@example.com",
    "first_name": "María",
    "last_name": "López",
    "password": "Segura123!",
    "password_confirm": "Segura123!",
    "rol": "asesor",
    "telefono": "+57 301 9876543"
  }'
```

### Campos del Usuario Asesor

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `email` | string | Sí | Email único (usado para login) |
| `password` | string | Sí | Contraseña segura |
| `first_name` | string | Sí | Nombre |
| `last_name` | string | Sí | Apellido |
| `rol` | string | Sí | Debe ser `"asesor"` |
| `telefono` | string | No | Número de contacto |
| `limite_solicitudes_diarias` | int | No | Default: 10 |

### Verificar Usuario Creado

```python
# En Django shell
from apps.usuarios.models import Usuario

# Listar todos los asesores
asesores = Usuario.objects.filter(rol='asesor')
for a in asesores:
    print(f'{a.id}: {a.email} - {a.nombre_completo()}')

# Verificar un asesor específico
asesor = Usuario.objects.get(email='asesor@example.com')
print(f'Es asesor: {asesor.es_asesor()}')
print(f'Límite diario: {asesor.limite_solicitudes_diarias}')
```

## Notas de Desarrollo

- Base de datos: SQLite (desarrollo), PostgreSQL (producción)
- Autenticación: JWT (SimpleJWT)
- CORS habilitado para `localhost:3000` y `localhost:5173`
- Los logs se almacenan en `backend/logs/django.log`
