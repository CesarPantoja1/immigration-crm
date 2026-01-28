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

## Notas de Desarrollo

- Base de datos: SQLite (desarrollo), PostgreSQL (producción)
- Autenticación: JWT (SimpleJWT)
- CORS habilitado para `localhost:3000` y `localhost:5173`
