# Backend - CRM Migratorio

API REST Django para el sistema CRM migratorio.

## Ejecución del Backend

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual (Windows - Git Bash)
source venv/Scripts/activate

# Activar entorno virtual (Windows - CMD)
.\venv\Scripts\activate

# Activar entorno virtual (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

El servidor se ejecutará en: `http://127.0.0.1:8000`

Admin panel: `http://127.0.0.1:8000/admin`

## Ejecución del Frontend

El frontend se encuentra en el directorio `../frontend/`. Para levantarlo:

### Opción 1: Con http-server (Recomendado)

```bash
# Ir al directorio frontend
cd ../frontend

# Instalar dependencias (solo la primera vez)
npm install

# Ejecutar servidor de desarrollo
npm run dev
```

El frontend estará disponible en: `http://localhost:3000`

### Opción 2: Con Python (sin Node.js)

```bash
# Ir al directorio frontend
cd ../frontend

# Ejecutar servidor HTTP simple
python -m http.server 3000
```

Luego abre en tu navegador: `http://localhost:3000`

### Opción 3: Abrir directamente

Abre el archivo `../frontend/index.html` en tu navegador.

**Nota:** Para funcionalidad completa, asegúrate de tener el backend ejecutándose antes de usar el frontend.

