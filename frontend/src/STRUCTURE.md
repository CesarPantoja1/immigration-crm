/**
 * Estructura de Carpetas - Frontend MigraFácil
 * =============================================
 * 
 * src/
 * ├── assets/              # Recursos estáticos (imágenes, fuentes, etc.)
 * │   ├── images/
 * │   └── icons/
 * │
 * ├── components/          # Componentes reutilizables
 * │   ├── common/          # Componentes genéricos (Button, Input, Modal, etc.)
 * │   ├── layout/          # Componentes de layout (Header, Footer, Sidebar)
 * │   └── landing/         # Componentes específicos del landing
 * │
 * ├── features/            # Módulos por funcionalidad (Feature-based)
 * │   ├── auth/            # Autenticación
 * │   │   ├── components/  # Componentes específicos de auth
 * │   │   ├── hooks/       # Hooks personalizados de auth
 * │   │   ├── services/    # Servicios/API de auth
 * │   │   └── pages/       # Páginas de auth (Login, Register)
 * │   ├── dashboard/       # Dashboard del usuario
 * │   ├── documents/       # Gestión de documentos
 * │   └── ...
 * │
 * ├── hooks/               # Hooks personalizados globales
 * │
 * ├── lib/                 # Utilidades y configuraciones
 * │   ├── api.js           # Cliente API (axios/fetch config)
 * │   ├── constants.js     # Constantes globales
 * │   └── utils.js         # Funciones utilitarias
 * │
 * ├── routes/              # Configuración de rutas
 * │   └── index.jsx        # Definición de rutas
 * │
 * ├── styles/              # Estilos globales
 * │   └── index.css        # Tailwind + estilos custom
 * │
 * ├── App.jsx              # Componente principal
 * └── main.jsx             # Entry point
 * 
 * 
 * Principios:
 * - Feature-first: Agrupa por funcionalidad, no por tipo de archivo
 * - Componentes reutilizables en /components
 * - Cada feature es autocontenida
 * - Lazy loading para features grandes
 */
