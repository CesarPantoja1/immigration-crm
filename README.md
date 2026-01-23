# CRM Migratorio - MigraFácil

Sistema CRM para gestión de procesos migratorios.

## Estructura del Proyecto

```
immigration-crm/
├── backend/           # API REST Django
└── frontend/          # Landing page y UI
```

## Inicio Rápido

### 1. Levantar el Backend

```bash
# Ir al directorio backend
cd backend

# Crear y activar entorno virtual
python -m venv venv
source venv/Scripts/activate  # En Windows Git Bash
# O: .\venv\Scripts\activate  # En Windows CMD
# O: source venv/bin/activate # En Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

El backend estará disponible en: `http://localhost:8000`

### 2. Levantar el Frontend

```bash
# Abrir una nueva terminal
# Ir al directorio frontend
cd frontend

# Opción A: Con http-server (Recomendado)
npm install
npm run dev

# Opción B: Con Python (sin Node.js)
python -m http.server 3000

# Opción C: Abrir directamente
# Abre el archivo index.html en tu navegador
```

El frontend estará disponible en: `http://localhost:3000`

## Documentación Detallada

- **Backend**: Ver `backend/README.md` y `backend/QUICKSTART.md`
- **Frontend**: Ver `frontend/README.md`
- **Arquitectura**: Ver `backend/ARQUITECTURA.md`

## Tecnologías

### Backend
- Python 3.11+
- Django 5.0+
- Django REST Framework
- PostgreSQL / SQLite

### Frontend
- HTML5, CSS3, JavaScript
- Tailwind CSS
- Diseño responsive

## Desarrollo

Para más detalles sobre la configuración de desarrollo, estructura del proyecto y convenciones de código, consulta los README específicos de cada módulo.

