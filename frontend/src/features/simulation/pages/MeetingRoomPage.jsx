import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button, Card } from '../../../components/common'

export default function MeetingRoomPage() {
  const { id } = useParams()
  const navigate = useNavigate()
  const videoRef = useRef(null)
  const [deviceCheck, setDeviceCheck] = useState({
    camera: false,
    microphone: false,
    lighting: false,
    quiet: false,
    documents: false
  })
  const [isReady, setIsReady] = useState(false)
  const [hasJoined, setHasJoined] = useState(false)
  const [micLevel, setMicLevel] = useState(0)

  // Simular detección de cámara
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        if (videoRef.current) {
          videoRef.current.srcObject = stream
        }
        setDeviceCheck(prev => ({ ...prev, camera: true, microphone: true }))
        
        // Simular nivel de micrófono
        const interval = setInterval(() => {
          setMicLevel(Math.random() * 100)
        }, 100)

        return () => {
          clearInterval(interval)
          stream.getTracks().forEach(track => track.stop())
        }
      } catch (err) {
        console.error('Error accessing media devices:', err)
      }
    }

    startCamera()
  }, [])

  useEffect(() => {
    const allChecked = Object.values(deviceCheck).every(v => v)
    setIsReady(allChecked)
  }, [deviceCheck])

  const handleJoinMeeting = () => {
    setHasJoined(true)
  }

  // Pre-sala de verificación
  if (!hasJoined) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Pre-sala de Verificación</h1>
            <p className="text-gray-400">Verifica tus dispositivos antes de unirte al simulacro</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            {/* Camera Preview */}
            <div className="space-y-4">
              <div className="aspect-video bg-gray-800 rounded-2xl overflow-hidden relative">
                <video 
                  ref={videoRef} 
                  autoPlay 
                  muted 
                  playsInline
                  className="w-full h-full object-cover"
                />
                {!deviceCheck.camera && (
                  <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
                    <div className="text-center text-gray-400">
                      <svg className="w-16 h-16 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                      <p>Accediendo a la cámara...</p>
                    </div>
                  </div>
                )}
              </div>

              {/* Mic Level */}
              <div className="bg-gray-800 rounded-xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-400">Nivel de micrófono</span>
                  <svg className={`w-5 h-5 ${micLevel > 20 ? 'text-green-500' : 'text-gray-500'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                </div>
                <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-100"
                    style={{ width: `${micLevel}%` }}
                  />
                </div>
              </div>

              {/* Device Selector */}
              <div className="flex gap-3">
                <select className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-gray-300 focus:ring-2 focus:ring-primary-500">
                  <option>Cámara integrada</option>
                </select>
                <select className="flex-1 px-4 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-gray-300 focus:ring-2 focus:ring-primary-500">
                  <option>Micrófono integrado</option>
                </select>
              </div>
            </div>

            {/* Checklist */}
            <div className="space-y-4">
              <div className="bg-gray-800 rounded-2xl p-6">
                <h3 className="text-lg font-semibold text-white mb-4">Lista de Verificación</h3>
                <div className="space-y-3">
                  {[
                    { key: 'camera', label: '¿Tu cámara funciona correctamente?', auto: true },
                    { key: 'microphone', label: '¿Tu micrófono detecta audio?', auto: true },
                    { key: 'lighting', label: '¿Tienes buena iluminación?' },
                    { key: 'quiet', label: '¿Estás en un lugar tranquilo?' },
                    { key: 'documents', label: '¿Tienes tus documentos a mano?' }
                  ].map((item) => (
                    <label 
                      key={item.key}
                      className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                        deviceCheck[item.key] ? 'bg-green-900/30' : 'bg-gray-700/50 hover:bg-gray-700'
                      }`}
                    >
                      <input
                        type="checkbox"
                        checked={deviceCheck[item.key]}
                        onChange={(e) => !item.auto && setDeviceCheck(prev => ({ 
                          ...prev, 
                          [item.key]: e.target.checked 
                        }))}
                        disabled={item.auto}
                        className="w-5 h-5 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-green-500"
                      />
                      <span className={`text-sm ${deviceCheck[item.key] ? 'text-green-400' : 'text-gray-300'}`}>
                        {item.label}
                      </span>
                      {deviceCheck[item.key] && (
                        <svg className="w-5 h-5 text-green-500 ml-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                      )}
                    </label>
                  ))}
                </div>
              </div>

              {/* Info Card */}
              <div className="bg-blue-900/30 border border-blue-800 rounded-xl p-4">
                <div className="flex gap-3">
                  <svg className="w-5 h-5 text-blue-400 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <p className="text-sm text-blue-300 font-medium">Información del Simulacro</p>
                    <p className="text-xs text-blue-400 mt-1">
                      Simulacro #{id} • Visa de Estudio • Con María González
                    </p>
                  </div>
                </div>
              </div>

              {/* Join Button */}
              <Button
                onClick={handleJoinMeeting}
                disabled={!isReady}
                className="w-full py-4 text-lg"
                size="lg"
              >
                <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                </svg>
                Unirse al Simulacro
              </Button>

              {!isReady && (
                <p className="text-center text-sm text-gray-500">
                  Completa la lista de verificación para continuar
                </p>
              )}

              <button
                onClick={() => navigate('/simulacros')}
                className="w-full py-2 text-gray-400 hover:text-white text-sm transition-colors"
              >
                Cancelar y volver
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // Sala de reunión (Jitsi placeholder)
  return (
    <div className="h-screen bg-gray-900 flex flex-col">
      {/* Meeting Header */}
      <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center justify-between px-4">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <span className="text-white font-medium">Simulacro #{id}</span>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-green-400">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-sm">En vivo</span>
          </div>
          <div className="px-3 py-1 bg-gray-700 rounded-lg text-white text-sm font-mono">
            00:15:32
          </div>
        </div>

        <button
          onClick={() => navigate('/simulacros/2/resumen')}
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg text-sm font-medium transition-colors"
        >
          Finalizar
        </button>
      </div>

      {/* Meeting Area (Jitsi Placeholder) */}
      <div className="flex-1 flex items-center justify-center bg-gray-900">
        <div className="text-center text-gray-400">
          <div className="w-32 h-32 bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-16 h-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-white mb-2">Sala de Simulacro</h2>
          <p className="text-gray-500 max-w-md mx-auto">
            Aquí se integrará Jitsi Meet. La videollamada ocupará toda esta área.
          </p>
        </div>
      </div>

      {/* Meeting Controls */}
      <div className="h-20 bg-gray-800 border-t border-gray-700 flex items-center justify-center gap-4">
        <button className="w-14 h-14 bg-gray-700 hover:bg-gray-600 rounded-full flex items-center justify-center text-white transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        </button>
        <button className="w-14 h-14 bg-gray-700 hover:bg-gray-600 rounded-full flex items-center justify-center text-white transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        </button>
        <button className="w-14 h-14 bg-gray-700 hover:bg-gray-600 rounded-full flex items-center justify-center text-white transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        </button>
        <button className="w-14 h-14 bg-gray-700 hover:bg-gray-600 rounded-full flex items-center justify-center text-white transition-colors">
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
        </button>
        <button 
          onClick={() => navigate('/simulacros/2/resumen')}
          className="w-14 h-14 bg-red-600 hover:bg-red-700 rounded-full flex items-center justify-center text-white transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 8l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2M5 3a2 2 0 00-2 2v1c0 8.284 6.716 15 15 15h1a2 2 0 002-2v-3.28a1 1 0 00-.684-.948l-4.493-1.498a1 1 0 00-1.21.502l-1.13 2.257a11.042 11.042 0 01-5.516-5.517l2.257-1.128a1 1 0 00.502-1.21L9.228 3.683A1 1 0 008.279 3H5z" />
          </svg>
        </button>
      </div>
    </div>
  )
}
