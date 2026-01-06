# Backend - CRM Migratorio

API REST Django para el sistema CRM migratorio.

## Ejecución

```bash
# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
.\venv\Scripts\activate

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
