# Frontend - MigraFácil

Landing page y frontend del sistema CRM migratorio.

## Requisitos

- Node.js (opcional, solo para servidor de desarrollo)
- Cualquier navegador moderno

## Métodos de Ejecución

### Opción 1: Con http-server (Recomendado)

```bash
# Instalar dependencias
npm install

# Ejecutar servidor de desarrollo (abre automáticamente en el navegador)
npm run dev

# O ejecutar sin abrir el navegador
npm start
```

El frontend estará disponible en: `http://localhost:3000`

### Opción 2: Con Python (sin Node.js)

```bash
# Desde el directorio frontend
python -m http.server 3000
```

Luego abre en tu navegador: `http://localhost:3000`

### Opción 3: Abrir directamente el archivo

Simplemente abre el archivo `index.html` en tu navegador favorito.

**Nota:** Algunas funcionalidades pueden requerir un servidor para funcionar correctamente debido a políticas CORS.

## Configuración

El archivo `.env` contiene la configuración de la aplicación:

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000/api
VITE_API_TIMEOUT=30000

# Application Configuration
VITE_APP_NAME=CRM Migratorio
VITE_APP_VERSION=1.0.0
```

## Estructura

```
frontend/
├── index.html          # Página principal
├── css/
│   └── landing.css    # Estilos personalizados
├── js/
│   └── landing.js     # JavaScript principal
└── .env               # Variables de entorno
```

## Integración con Backend

Asegúrate de que el backend esté ejecutándose en `http://localhost:8000` antes de usar las funcionalidades que requieran API.

Para levantar el backend, consulta las instrucciones en `backend/README.md`.

