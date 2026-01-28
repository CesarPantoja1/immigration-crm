import { useState, useEffect } from 'react'
import { Card, Button, Badge } from '../../../components/common'
import { simulacrosService } from '../../../services/simulacrosService'

export default function IAConfigPage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [testing, setTesting] = useState(false)
  const [configurado, setConfigurado] = useState(false)
  const [modelosDisponibles, setModelosDisponibles] = useState({})
  const [testResult, setTestResult] = useState(null)
  
  const [formData, setFormData] = useState({
    api_key: '',
    modelo: 'gemini-2.5-flash',
    activo: true
  })
  
  const [configActual, setConfigActual] = useState(null)

  useEffect(() => {
    fetchConfiguracion()
  }, [])

  const fetchConfiguracion = async () => {
    try {
      setLoading(true)
      const response = await simulacrosService.getConfiguracionIA()
      
      setConfigurado(response.configurado)
      setModelosDisponibles(response.modelos_disponibles || {})
      
      if (response.configurado && response.configuracion) {
        setConfigActual(response.configuracion)
        setFormData({
          api_key: '', // No mostrar la API key real
          modelo: response.configuracion.modelo,
          activo: response.configuracion.activo
        })
      }
    } catch (error) {
      console.error('Error fetching config:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleTestApiKey = async () => {
    if (!formData.api_key) {
      setTestResult({ valida: false, mensaje: 'Ingresa una API key para probar' })
      return
    }
    
    try {
      setTesting(true)
      setTestResult(null)
      const response = await simulacrosService.testAPIKey(formData.api_key, formData.modelo)
      setTestResult(response)
    } catch (error) {
      setTestResult({
        valida: false,
        mensaje: error.response?.data?.mensaje || 'Error al probar la API key'
      })
    } finally {
      setTesting(false)
    }
  }

  const handleSave = async () => {
    if (!formData.api_key && !configurado) {
      setTestResult({ valida: false, mensaje: 'La API key es requerida' })
      return
    }
    
    try {
      setSaving(true)
      
      const dataToSend = {
        modelo: formData.modelo,
        activo: formData.activo
      }
      
      // Solo enviar api_key si se proporcionó una nueva
      if (formData.api_key) {
        dataToSend.api_key = formData.api_key
      }
      
      if (configurado) {
        await simulacrosService.actualizarConfiguracionIA(dataToSend)
      } else {
        await simulacrosService.guardarConfiguracionIA({
          ...dataToSend,
          api_key: formData.api_key
        })
      }
      
      setTestResult({ valida: true, mensaje: '¡Configuración guardada exitosamente!' })
      fetchConfiguracion()
      setFormData(prev => ({ ...prev, api_key: '' })) // Limpiar API key del form
    } catch (error) {
      setTestResult({
        valida: false,
        mensaje: error.response?.data?.mensaje || 'Error al guardar la configuración'
      })
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async () => {
    if (!confirm('¿Estás seguro de eliminar la configuración de IA?')) return
    
    try {
      setSaving(true)
      await simulacrosService.eliminarConfiguracionIA()
      setConfigurado(false)
      setConfigActual(null)
      setFormData({
        api_key: '',
        modelo: 'gemini-2.5-flash',
        activo: true
      })
      setTestResult({ valida: true, mensaje: 'Configuración eliminada' })
    } catch (error) {
      setTestResult({
        valida: false,
        mensaje: error.response?.data?.mensaje || 'Error al eliminar'
      })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Configuración de IA</h1>
        <p className="text-gray-500">Configura tu API key de Google Gemini para generar recomendaciones con IA</p>
      </div>

      {/* Status Card */}
      <Card className={configurado ? 'border-green-200 bg-green-50/50' : 'border-amber-200 bg-amber-50/50'}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
              configurado ? 'bg-green-100' : 'bg-amber-100'
            }`}>
              {configurado ? (
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              )}
            </div>
            <div>
              <p className={`font-medium ${configurado ? 'text-green-800' : 'text-amber-800'}`}>
                {configurado ? 'IA Configurada' : 'IA No Configurada'}
              </p>
              <p className={`text-sm ${configurado ? 'text-green-600' : 'text-amber-600'}`}>
                {configurado 
                  ? `Usando modelo ${configActual?.modelo_display || configActual?.modelo}` 
                  : 'Configura tu API key para usar el análisis con IA'}
              </p>
            </div>
          </div>
          {configurado && (
            <Badge variant="success">Activo</Badge>
          )}
        </div>
        
        {configurado && configActual && (
          <div className="mt-4 pt-4 border-t border-green-200 grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-green-600">API Key</p>
              <p className="font-mono text-green-800">{configActual.api_key_masked}</p>
            </div>
            <div>
              <p className="text-green-600">Análisis realizados</p>
              <p className="font-semibold text-green-800">{configActual.total_analisis || 0}</p>
            </div>
          </div>
        )}
      </Card>

      {/* Configuration Form */}
      <Card>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {configurado ? 'Actualizar Configuración' : 'Nueva Configuración'}
        </h2>
        
        <div className="space-y-4">
          {/* API Key Input */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API Key de Google AI Studio
              {configurado && <span className="text-gray-400 ml-2">(deja vacío para mantener la actual)</span>}
            </label>
            <div className="relative">
              <input
                type="password"
                value={formData.api_key}
                onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                placeholder={configurado ? '••••••••••••••••' : 'AIzaSy...'}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 font-mono"
              />
              <button
                type="button"
                onClick={handleTestApiKey}
                disabled={testing || !formData.api_key}
                className="absolute right-2 top-1/2 -translate-y-1/2 px-3 py-1.5 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {testing ? (
                  <span className="flex items-center gap-1">
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Probando...
                  </span>
                ) : 'Probar'}
              </button>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Obtén tu API key en{' '}
              <a 
                href="https://aistudio.google.com/apikey" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-primary-600 hover:underline"
              >
                Google AI Studio
              </a>
            </p>
          </div>

          {/* Model Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Modelo de IA
            </label>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {Object.entries(modelosDisponibles).map(([value, label]) => (
                <label
                  key={value}
                  className={`relative flex items-center p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    formData.modelo === value
                      ? 'border-primary-500 bg-primary-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="modelo"
                    value={value}
                    checked={formData.modelo === value}
                    onChange={(e) => setFormData({ ...formData, modelo: e.target.value })}
                    className="sr-only"
                  />
                  <div className="flex-1">
                    <p className={`font-medium ${formData.modelo === value ? 'text-primary-700' : 'text-gray-900'}`}>
                      {value}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5">{label}</p>
                  </div>
                  {formData.modelo === value && (
                    <svg className="w-5 h-5 text-primary-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  )}
                </label>
              ))}
            </div>
          </div>

          {/* Test Result */}
          {testResult && (
            <div className={`p-4 rounded-xl ${
              testResult.valida 
                ? 'bg-green-50 border border-green-200' 
                : 'bg-red-50 border border-red-200'
            }`}>
              <div className="flex items-center gap-2">
                {testResult.valida ? (
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                )}
                <p className={`font-medium ${testResult.valida ? 'text-green-800' : 'text-red-800'}`}>
                  {testResult.mensaje}
                </p>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-3 pt-4">
            {configurado && (
              <Button
                variant="secondary"
                onClick={handleDelete}
                disabled={saving}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                Eliminar
              </Button>
            )}
            <Button
              onClick={handleSave}
              disabled={saving || (!formData.api_key && !configurado)}
              className="flex-1"
            >
              {saving ? (
                <span className="flex items-center justify-center gap-2">
                  <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Guardando...
                </span>
              ) : (
                configurado ? 'Actualizar Configuración' : 'Guardar Configuración'
              )}
            </Button>
          </div>
        </div>
      </Card>

      {/* Info Card */}
      <Card className="bg-blue-50 border-blue-200">
        <div className="flex gap-3">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
            <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <h3 className="font-medium text-blue-800">Sobre los modelos</h3>
            <ul className="mt-2 text-sm text-blue-700 space-y-1">
              <li><strong>Gemini 2.5 Pro:</strong> Mayor precisión y análisis más detallado. Ideal para casos complejos.</li>
              <li><strong>Gemini 2.5 Flash:</strong> Balance entre velocidad y calidad. Recomendado para uso general.</li>
              <li><strong>Gemini 2.0 Flash:</strong> Versión estable anterior. Buena confiabilidad.</li>
              <li><strong>Gemini 2.5 Flash Lite:</strong> Más económico y rápido. Ideal para alto volumen.</li>
            </ul>
          </div>
        </div>
      </Card>
    </div>
  )
}
