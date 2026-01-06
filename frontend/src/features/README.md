# Features Directory

Este directorio contiene todos los modulos funcionales del CRM.

## Estructura de cada Feature

Cada feature sigue esta estructura organizacional:

```
feature-name/
├── components/          # Componentes especificos del feature
├── hooks/              # Hooks personalizados del feature
├── services/           # Servicios API especificos del feature
├── pages/              # Paginas/vistas del feature
├── types/              # Tipos/interfaces del feature (si se usa TypeScript)
└── index.js            # Barrel export
```

## Principios

1. **Autonomia**: Cada feature debe ser lo mas independiente posible
2. **Cohesion**: Todo lo relacionado al feature vive dentro de su carpeta
3. **Reutilizacion**: Usa componentes de `shared/` cuando sea posible
4. **Naming**: Usa nombres descriptivos y consistentes

## Ejemplo de Features futuros

- `auth/` - Autenticacion y registro
- `dashboard/` - Panel principal
- `solicitudes/` - Gestion de solicitudes migratorias
- `clientes/` - Gestion de clientes
- `documentos/` - Gestion documental
- `comunicacion/` - Mensajeria y notificaciones

## Importante

NO crear carpetas anticipadamente. Solo crear cuando se vaya a implementar la funcionalidad.

