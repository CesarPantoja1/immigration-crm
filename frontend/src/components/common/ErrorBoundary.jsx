import { Component } from 'react'
import Button from './Button'

/**
 * ErrorBoundary - Componente para capturar errores de renderizado
 *
 * Captura errores en el arbol de componentes hijo y muestra una UI de fallback
 * amigable en lugar de crashear toda la aplicacion.
 *
 * USO:
 * <ErrorBoundary>
 *   <ComponenteQuePuedeFallar />
 * </ErrorBoundary>
 *
 * Con fallback personalizado:
 * <ErrorBoundary fallback={<MiComponenteDeFallback />}>
 *   <ComponenteQuePuedeFallar />
 * </ErrorBoundary>
 */
export class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorCode: null
    }
  }

  static getDerivedStateFromError(error) {
    // Determinar codigo de error si es un error HTTP
    let errorCode = null
    if (error?.status) {
      errorCode = error.status
    } else if (error?.response?.status) {
      errorCode = error.response.status
    } else if (error?.message?.includes('500')) {
      errorCode = 500
    } else if (error?.message?.includes('404')) {
      errorCode = 404
    } else if (error?.message?.includes('403')) {
      errorCode = 403
    }

    return {
      hasError: true,
      error,
      errorCode
    }
  }

  componentDidCatch(error, errorInfo) {
    // Log para debugging (en produccion enviar a servicio de errores)
    console.error('ErrorBoundary caught an error:', error, errorInfo)

    this.setState({
      errorInfo
    })

    // En produccion, enviar a servicio de monitoreo
    if (import.meta.env.PROD) {
      // TODO: Integrar con servicio como Sentry
      // reportError({ error, errorInfo })
    }
  }

  handleRetry = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorCode: null
    })
  }

  handleGoHome = () => {
    window.location.href = '/'
  }

  handleReload = () => {
    window.location.reload()
  }

  render() {
    if (this.state.hasError) {
      // Si hay un fallback personalizado, usarlo
      if (this.props.fallback) {
        return this.props.fallback
      }

      const { errorCode, error } = this.state
      const isDev = import.meta.env.DEV

      return (
        <div className="min-h-[400px] flex items-center justify-center p-6">
          <div className="max-w-md w-full text-center">
            {/* Icono segun tipo de error */}
            <div className={`w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center ${
              errorCode === 500 ? 'bg-red-100' :
              errorCode === 404 ? 'bg-amber-100' :
              errorCode === 403 ? 'bg-orange-100' :
              'bg-gray-100'
            }`}>
              {errorCode === 500 ? (
                <svg className="w-10 h-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              ) : errorCode === 404 ? (
                <svg className="w-10 h-10 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              ) : errorCode === 403 ? (
                <svg className="w-10 h-10 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              ) : (
                <svg className="w-10 h-10 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              )}
            </div>

            {/* Titulo y mensaje */}
            <h2 className="text-2xl font-bold text-gray-900 mb-2">
              {errorCode === 500 ? 'Error del servidor' :
               errorCode === 404 ? 'Pagina no encontrada' :
               errorCode === 403 ? 'Acceso denegado' :
               'Algo salio mal'}
            </h2>

            <p className="text-gray-600 mb-6">
              {errorCode === 500 ?
                'Hubo un problema en el servidor. Por favor, intenta de nuevo mas tarde.' :
               errorCode === 404 ?
                'La pagina que buscas no existe o ha sido movida.' :
               errorCode === 403 ?
                'No tienes permisos para acceder a este recurso.' :
               'Ha ocurrido un error inesperado. Estamos trabajando para solucionarlo.'}
            </p>

            {/* Detalles del error en desarrollo */}
            {isDev && error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl text-left">
                <p className="text-sm font-mono text-red-800 break-all">
                  {error.toString()}
                </p>
                {this.state.errorInfo && (
                  <details className="mt-2">
                    <summary className="text-xs text-red-600 cursor-pointer">
                      Stack trace
                    </summary>
                    <pre className="mt-2 text-xs text-red-700 overflow-auto max-h-40">
                      {this.state.errorInfo.componentStack}
                    </pre>
                  </details>
                )}
              </div>
            )}

            {/* Botones de accion */}
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <Button variant="secondary" onClick={this.handleRetry}>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Reintentar
              </Button>
              <Button onClick={this.handleGoHome}>
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
                </svg>
                Ir al inicio
              </Button>
            </div>

            {/* Codigo de error */}
            {errorCode && (
              <p className="mt-6 text-sm text-gray-400">
                Codigo de error: {errorCode}
              </p>
            )}
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * ApiErrorHandler - Componente para manejar errores de API de forma consistente
 *
 * USO en componentes funcionales:
 * const { error, handleError, clearError } = useApiError()
 *
 * try {
 *   await apiCall()
 * } catch (e) {
 *   handleError(e)
 * }
 *
 * {error && <ApiErrorDisplay error={error} onDismiss={clearError} />}
 */
export function ApiErrorDisplay({ error, onDismiss, onRetry }) {
  if (!error) return null

  const errorCode = error?.status || error?.response?.status
  const errorMessage = error?.message || error?.data?.error || 'Ha ocurrido un error'

  const getErrorInfo = () => {
    switch (errorCode) {
      case 400:
        return { title: 'Datos invalidos', icon: 'warning', color: 'amber' }
      case 401:
        return { title: 'Sesion expirada', icon: 'lock', color: 'orange' }
      case 403:
        return { title: 'Sin permisos', icon: 'shield', color: 'orange' }
      case 404:
        return { title: 'No encontrado', icon: 'search', color: 'amber' }
      case 500:
        return { title: 'Error del servidor', icon: 'server', color: 'red' }
      default:
        return { title: 'Error', icon: 'alert', color: 'red' }
    }
  }

  const info = getErrorInfo()

  return (
    <div className={`p-4 rounded-xl border ${
      info.color === 'red' ? 'bg-red-50 border-red-200' :
      info.color === 'orange' ? 'bg-orange-50 border-orange-200' :
      'bg-amber-50 border-amber-200'
    }`}>
      <div className="flex items-start gap-3">
        <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
          info.color === 'red' ? 'bg-red-100' :
          info.color === 'orange' ? 'bg-orange-100' :
          'bg-amber-100'
        }`}>
          <svg className={`w-5 h-5 ${
            info.color === 'red' ? 'text-red-600' :
            info.color === 'orange' ? 'text-orange-600' :
            'text-amber-600'
          }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        </div>
        <div className="flex-1">
          <h4 className={`font-semibold ${
            info.color === 'red' ? 'text-red-800' :
            info.color === 'orange' ? 'text-orange-800' :
            'text-amber-800'
          }`}>
            {info.title}
          </h4>
          <p className={`text-sm mt-1 ${
            info.color === 'red' ? 'text-red-700' :
            info.color === 'orange' ? 'text-orange-700' :
            'text-amber-700'
          }`}>
            {errorMessage}
          </p>
        </div>
        <div className="flex gap-2">
          {onRetry && (
            <button
              onClick={onRetry}
              className={`p-1.5 rounded-lg hover:bg-opacity-50 ${
                info.color === 'red' ? 'text-red-600 hover:bg-red-100' :
                info.color === 'orange' ? 'text-orange-600 hover:bg-orange-100' :
                'text-amber-600 hover:bg-amber-100'
              }`}
              title="Reintentar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </button>
          )}
          {onDismiss && (
            <button
              onClick={onDismiss}
              className={`p-1.5 rounded-lg hover:bg-opacity-50 ${
                info.color === 'red' ? 'text-red-600 hover:bg-red-100' :
                info.color === 'orange' ? 'text-orange-600 hover:bg-orange-100' :
                'text-amber-600 hover:bg-amber-100'
              }`}
              title="Cerrar"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

export default ErrorBoundary
