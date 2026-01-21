# Guía de Inicio Rápido - CRM Migratorio

## Configuración Inicial

### 1. Instalar Dependencias

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows)
venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Base de Datos

#### Opción A: PostgreSQL (Recomendado para desarrollo)

```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar .env con tus credenciales
# DB_NAME=crm_migratorio
# DB_USER=tu_usuario
# DB_PASSWORD=tu_password
# DB_HOST=localhost
# DB_PORT=5432
```

#### Opción B: SQLite (Para testing rápido)

```bash
# Editar config/settings/development.py
# Cambiar DATABASES a SQLite temporalmente
```

### 3. Ejecutar Migraciones

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate
```

### 4. Crear Superusuario

```bash
python manage.py createsuperuser
```

### 5. Cargar Datos Iniciales

```bash
# Datos de configuración (reglas de embajadas)
python manage.py shell < scripts/init_db.py

# Datos de prueba (cuestionarios, etc.)
python manage.py shell < scripts/seed_data.py
```

### 6. Ejecutar Servidor

```bash
python manage.py runserver
```

Acceder a:
- Aplicación: http://localhost:8000
- Admin: http://localhost:8000/admin

## Estructura del Proyecto

```
backend/
├── apps/                    # Apps Django organizadas por CAPACIDADES
│   ├── core/               # Funcionalidades compartidas
│   ├── usuarios/           # Gestión de usuarios
│   ├── solicitudes/        # Recepción y Agendamiento
│   ├── preparacion/        # Simulación y Recomendaciones
│   └── notificaciones/     # Seguimiento y Coordinación
│
├── config/                  # Configuración Django
│   └── settings/           # Settings por entorno
│
├── features/               # Tests BDD con Behave
│   ├── solicitudes/
│   ├── preparacion/
│   └── notificaciones/
│
├── templates/              # Templates HTML
├── static/                 # CSS, JS, imágenes
└── scripts/                # Scripts útiles
```

## Desarrollo con la Arquitectura

### Agregar una Nueva Característica

1. **Crear modelos en Infrastructure**
   ```python
   # apps/solicitudes/recepcion/infrastructure/models.py
   class MiModelo(TimeStampedModel):
       # campos...
       pass
   ```

2. **Crear lógica de negocio en Domain** (opcional)
   ```python
   # apps/solicitudes/recepcion/domain/entities.py
   # Entidades de dominio puras
   ```

3. **Crear casos de uso en Application** (opcional)
   ```python
   # apps/solicitudes/recepcion/application/use_cases.py
   # Lógica de orquestación
   ```

4. **Crear vistas en Presentation**
   ```python
   # apps/solicitudes/recepcion/presentation/views.py
   class MiVista(ListView):
       # vista...
       pass
   ```

5. **Crear formularios**
   ```python
   # apps/solicitudes/recepcion/presentation/forms.py
   class MiForm(forms.ModelForm):
       # formulario...
       pass
   ```

6. **Configurar URLs**
   ```python
   # apps/solicitudes/recepcion/presentation/urls.py
   urlpatterns = [
       path('lista/', MiVista.as_view(), name='lista'),
   ]
   ```

7. **Crear migraciones**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

### Escribir Tests BDD

1. **Crear archivo .feature**
   ```gherkin
   # features/solicitudes/recepcion/recepcion_solicitudes.feature
   #language: es

   Característica: Recepción de Solicitudes
     Como usuario...

     Escenario: Crear nueva solicitud
       Dado que estoy autenticado
       Cuando lleno el formulario de solicitud
       Entonces la solicitud se crea correctamente
   ```

2. **Implementar steps**
   ```python
   # features/solicitudes/recepcion/steps/recepcion_steps.py
   from behave import given, when, then

   @given('que estoy autenticado')
   def step_autenticado(context):
       # implementación
       pass
   ```

3. **Ejecutar tests**
   ```bash
   behave features/solicitudes/recepcion/
   ```

## Comandos Útiles (Makefile)

```bash
make install      # Instalar dependencias
make migrate      # Crear y aplicar migraciones
make run          # Ejecutar servidor
make test         # Ejecutar todos los tests
make behave       # Solo tests BDD
make pytest       # Solo tests unitarios
make shell        # Shell de Django
make clean        # Limpiar archivos temporales
```

## Docker (Opcional)

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Ejecutar comandos dentro del contenedor
docker-compose exec web python manage.py migrate

# Detener servicios
docker-compose down
```

## Próximos Pasos

1. **Implementar los steps de agendamiento** en:
   - `features/solicitudes/agendamiento/steps/agendamiento_steps.py`

2. **Crear las vistas de agendamiento** en:
   - `apps/solicitudes/agendamiento/presentation/views.py`

3. **Implementar casos de uso** en:
   - `apps/solicitudes/agendamiento/application/use_cases.py`

4. **Agregar lógica de dominio** en:
   - `apps/solicitudes/agendamiento/domain/`

5. **Conectar con eventos** usando Django Signals:
   ```python
   from apps.core.events import entrevista_agendada

   # Enviar evento
   entrevista_agendada.send(sender=self.__class__, entrevista=entrevista)

   # Escuchar evento
   @receiver(entrevista_agendada)
   def on_entrevista_agendada(sender, entrevista, **kwargs):
       # crear notificación
       pass
   ```

## Recursos

- [Documentación de Django](https://docs.djangoproject.com/)
- [Behave - BDD Framework](https://behave.readthedocs.io/)
- [Arquitectura Hexagonal](ARQUITECTURA.md)
- [README Principal](README.md)

## Problemas Comunes

### Error de Migraciones

```bash
# Limpiar migraciones y volver a crear
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Error de ImportError

```bash
# Verificar que el entorno virtual esté activado
# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Base de datos bloqueada (SQLite)

```bash
# Eliminar base de datos y recrear
rm db.sqlite3
python manage.py migrate
```

## Contacto y Soporte

Para dudas o problemas, consultar:
- [README.md](README.md)
- [ARQUITECTURA.md](ARQUITECTURA.md)
