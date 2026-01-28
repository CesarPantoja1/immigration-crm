import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Card, Badge, Button, Modal } from '../../../components/common'
import { simulacrosService } from '../../../services/simulacrosService'

export default function AdvisorSimulationsPage() {
  const [activeTab, setActiveTab] = useState('upcoming')
  const [showProposalModal, setShowProposalModal] = useState(false)
  const [selectedProposal, setSelectedProposal] = useState(null)
  const [selectedTime, setSelectedTime] = useState('')
  const [simulations, setSimulations] = useState([])
  const [proposals, setProposals] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchSimulationsData()
  }, [])

  const fetchSimulationsData = async () => {
    try {
      setLoading(true)
      const [simulacionesResponse, propuestasResponse] = await Promise.all([
        simulacrosService.getSimulacros().catch(() => []),
        simulacrosService.getPropuestasPendientes().catch(() => [])
      ])

      // Handle both array and object with results
      const simulacionesData = Array.isArray(simulacionesResponse)
        ? simulacionesResponse
        : (simulacionesResponse?.results || [])
      
      const propuestasData = Array.isArray(propuestasResponse)
        ? propuestasResponse
        : (propuestasResponse?.results || [])

      // Transform simulaciones
      const simList = simulacionesData.map(s => ({
        id: s.id,
        client: s.cliente_nombre || s.cliente?.nombre || 'Cliente',
        date: formatDateForDisplay(s.fecha_propuesta || s.fecha),
        time: s.hora_propuesta || s.hora || '10:00 AM',
        visaType: s.tipo_visa || 'Visa',
        status: s.estado || 'upcoming',
        clientAvatar: getInitials(s.cliente_nombre || s.cliente?.nombre || 'C')
      }))

      // Transform propuestas
      const propList = propuestasData.map(p => ({
        id: p.id,
        client: p.cliente_nombre || p.cliente?.nombre || 'Cliente',
        proposedDate: formatDateForDisplay(p.fecha_propuesta),
        proposedTime: p.hora_propuesta || '10:00 AM - 11:00 AM',
        visaType: p.tipo_visa || 'Visa',
        note: p.nota || ''
      }))

      setSimulations(simList)
      setProposals(propList)
    } catch (error) {
      console.error('Error fetching simulations:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatDateForDisplay = (dateStr) => {
    if (!dateStr) return ''
    const date = new Date(dateStr + 'T00:00')
    return date.toLocaleDateString('es-ES', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    })
  }

  const getInitials = (name) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)
  }

  const todayStr = new Date().toLocaleDateString('es-ES', { day: 'numeric', month: 'long', year: 'numeric' })
  const todaySimulations = simulations.filter(s => s.date === todayStr)
  const upcomingSimulations = simulations.filter(s => s.date !== todayStr)

  const handleAcceptProposal = async () => {
    if (!selectedTime || !selectedProposal) return
    try {
      await simulacrosService.aceptarPropuesta(selectedProposal.id)
      fetchSimulationsData()
    } catch (error) {
      console.error('Error accepting proposal:', error)
    }
    setShowProposalModal(false)
    setSelectedProposal(null)
    setSelectedTime('')
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Simulacros</h1>
          <p className="text-gray-500">Gestiona tus sesiones de simulacro con clientes</p>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-blue-50 border-blue-200">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-700">{todaySimulations.length}</div>
            <div className="text-sm text-blue-600">Hoy</div>
          </div>
        </Card>
        <Card className="bg-purple-50 border-purple-200">
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-700">{upcomingSimulations.length}</div>
            <div className="text-sm text-purple-600">Esta Semana</div>
          </div>
        </Card>
        <Card className="bg-amber-50 border-amber-200">
          <div className="text-center">
            <div className="text-3xl font-bold text-amber-700">{proposals.length}</div>
            <div className="text-sm text-amber-600">Propuestas</div>
          </div>
        </Card>
        <Card className="bg-green-50 border-green-200">
          <div className="text-center">
            <div className="text-3xl font-bold text-green-700">{simulations.length}</div>
            <div className="text-sm text-green-600">Este Mes</div>
          </div>
        </Card>
      </div>

      {/* Proposals Section */}
      {proposals.length > 0 && (
        <Card className="border-amber-200 bg-amber-50/50">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
              <h2 className="text-lg font-semibold text-gray-900">Propuestas Pendientes</h2>
            </div>
            <Badge variant="warning">{proposals.length} nuevas</Badge>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {proposals.map((proposal) => (
              <div 
                key={proposal.id}
                className="bg-white rounded-xl p-4 border border-amber-200"
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-amber-100 rounded-full flex items-center justify-center text-amber-600 font-semibold">
                      {proposal.client.charAt(0)}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{proposal.client}</p>
                      <p className="text-sm text-gray-500">{proposal.visaType}</p>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <span className="text-gray-600">{proposal.proposedDate}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="text-gray-600">{proposal.proposedTime}</span>
                  </div>
                  {proposal.note && (
                    <div className="bg-gray-50 rounded-lg p-2 text-sm text-gray-600 italic">
                      "{proposal.note}"
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button 
                    variant="secondary" 
                    size="sm" 
                    className="flex-1"
                    onClick={() => {/* Reject */}}
                  >
                    Rechazar
                  </Button>
                  <Button 
                    size="sm" 
                    className="flex-1"
                    onClick={() => {
                      setSelectedProposal(proposal)
                      setShowProposalModal(true)
                    }}
                  >
                    Aceptar
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Tabs */}
      <div className="flex gap-4 border-b border-gray-200">
        <button
          onClick={() => setActiveTab('upcoming')}
          className={`pb-3 px-1 font-medium transition-colors relative ${
            activeTab === 'upcoming' 
              ? 'text-primary-600' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Simulacros de Hoy
          {activeTab === 'upcoming' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600" />
          )}
        </button>
        <button
          onClick={() => setActiveTab('scheduled')}
          className={`pb-3 px-1 font-medium transition-colors relative ${
            activeTab === 'scheduled' 
              ? 'text-primary-600' 
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Próximos
          {activeTab === 'scheduled' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary-600" />
          )}
        </button>
      </div>

      {/* Simulations List */}
      <div className="space-y-4">
        {(activeTab === 'upcoming' ? todaySimulations : upcomingSimulations).map((sim) => (
          <Card key={sim.id} className="hover:shadow-md transition-shadow">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-bold">
                  {sim.clientAvatar}
                </div>
                <div>
                  <p className="font-semibold text-gray-900">{sim.client}</p>
                  <p className="text-sm text-gray-500">{sim.visaType}</p>
                </div>
              </div>

              <div className="flex items-center gap-6">
                <div className="text-right">
                  <p className="font-medium text-gray-900">{sim.time}</p>
                  <p className="text-sm text-gray-500">{sim.date}</p>
                </div>

                <div className="flex gap-2">
                  <Link to={`/asesor/solicitudes/${sim.id}`}>
                    <Button variant="secondary" size="sm">
                      Ver Expediente
                    </Button>
                  </Link>
                  {activeTab === 'upcoming' && (
                    <Link to={`/asesor/simulacros/${sim.id}/room`}>
                      <Button size="sm">
                        Iniciar Sesión
                      </Button>
                    </Link>
                  )}
                </div>
              </div>
            </div>
          </Card>
        ))}

        {(activeTab === 'upcoming' ? todaySimulations : upcomingSimulations).length === 0 && (
          <Card className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-1">
              No hay simulacros {activeTab === 'upcoming' ? 'para hoy' : 'programados'}
            </h3>
            <p className="text-gray-500">
              Los nuevos simulacros aparecerán aquí cuando sean agendados
            </p>
          </Card>
        )}
      </div>

      {/* Accept Proposal Modal */}
      <Modal
        isOpen={showProposalModal}
        onClose={() => {
          setShowProposalModal(false)
          setSelectedProposal(null)
          setSelectedTime('')
        }}
        title="Confirmar Simulacro"
        size="md"
      >
        {selectedProposal && (
          <div className="space-y-4">
            <div className="bg-gray-50 rounded-xl p-4">
              <div className="flex items-center gap-3 mb-3">
                <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center text-primary-600 font-semibold">
                  {selectedProposal.client.charAt(0)}
                </div>
                <div>
                  <p className="font-medium text-gray-900">{selectedProposal.client}</p>
                  <p className="text-sm text-gray-500">{selectedProposal.visaType}</p>
                </div>
              </div>
              <p className="text-sm text-gray-600">
                Fecha solicitada: <strong>{selectedProposal.proposedDate}</strong>
              </p>
              <p className="text-sm text-gray-600">
                Horario preferido: <strong>{selectedProposal.proposedTime}</strong>
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Selecciona la hora exacta
              </label>
              <select
                value={selectedTime}
                onChange={(e) => setSelectedTime(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">Seleccionar hora</option>
                <option value="10:00">10:00 AM</option>
                <option value="10:30">10:30 AM</option>
                <option value="11:00">11:00 AM</option>
                <option value="14:00">02:00 PM</option>
                <option value="14:30">02:30 PM</option>
                <option value="15:00">03:00 PM</option>
                <option value="15:30">03:30 PM</option>
              </select>
            </div>

            <div className="flex gap-3 pt-4">
              <Button 
                variant="secondary" 
                className="flex-1"
                onClick={() => {
                  setShowProposalModal(false)
                  setSelectedProposal(null)
                  setSelectedTime('')
                }}
              >
                Cancelar
              </Button>
              <Button 
                className="flex-1"
                onClick={handleAcceptProposal}
                disabled={!selectedTime}
              >
                Confirmar
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}
