import { useState } from 'react'
import { Card, Badge } from '../../../components/common'
import { useAuth } from '../../../contexts/AuthContext'

// Mock events data
const MOCK_EVENTS = [
  {
    id: 1,
    type: 'interview',
    title: 'Entrevista Real - Embajada',
    date: '2026-02-15',
    time: '09:00',
    location: 'Embajada de Estados Unidos',
    address: 'Av. Principal #456',
    critical: true,
    visaType: 'Trabajo',
    applicationId: 'SOL-2024-001'
  },
  {
    id: 2,
    type: 'simulation_virtual',
    title: 'Simulacro Virtual',
    date: '2026-01-30',
    time: '15:00',
    advisor: 'María González',
    duration: '30 min',
    visaType: 'Trabajo',
    applicationId: 'SOL-2024-001'
  },
  {
    id: 3,
    type: 'simulation_presential',
    title: 'Simulacro Presencial',
    date: '2026-02-05',
    time: '10:00',
    location: 'Oficina MigraFácil',
    address: 'Calle Principal #123',
    advisor: 'María González',
    duration: '45 min',
    visaType: 'Trabajo',
    applicationId: 'SOL-2024-001'
  }
]

const MOCK_TIMELINE = [
  { date: '2026-01-20', event: 'Solicitud enviada a embajada', type: 'milestone' },
  { date: '2026-01-22', event: 'Embajada aprobó solicitud', type: 'milestone' },
  { date: '2026-01-23', event: 'Fecha de entrevista asignada: 15/02/2026', type: 'milestone' },
  { date: '2026-01-24', event: 'Simulacro virtual programado', type: 'event' },
  { date: '2026-01-25', event: 'Simulacro presencial programado', type: 'event' }
]

export default function CalendarPage() {
  const { user } = useAuth()
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(null)
  const [view, setView] = useState('month') // month, list

  const year = currentDate.getFullYear()
  const month = currentDate.getMonth()

  // Get days in month
  const firstDayOfMonth = new Date(year, month, 1)
  const lastDayOfMonth = new Date(year, month + 1, 0)
  const daysInMonth = lastDayOfMonth.getDate()
  const startingDay = firstDayOfMonth.getDay()

  // Navigate months
  const prevMonth = () => setCurrentDate(new Date(year, month - 1, 1))
  const nextMonth = () => setCurrentDate(new Date(year, month + 1, 1))
  const goToToday = () => setCurrentDate(new Date())

  // Get events for a specific date
  const getEventsForDate = (dateStr) => {
    return MOCK_EVENTS.filter(e => e.date === dateStr)
  }

  // Format date to string
  const formatDateStr = (day) => {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  }

  // Get event type styling
  const getEventTypeStyle = (type) => {
    switch (type) {
      case 'interview':
        return { dot: 'bg-red-500', text: 'text-red-700', bg: 'bg-red-100' }
      case 'simulation_virtual':
        return { dot: 'bg-purple-500', text: 'text-purple-700', bg: 'bg-purple-100' }
      case 'simulation_presential':
        return { dot: 'bg-amber-500', text: 'text-amber-700', bg: 'bg-amber-100' }
      default:
        return { dot: 'bg-gray-500', text: 'text-gray-700', bg: 'bg-gray-100' }
    }
  }

  const monthNames = [
    'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
    'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
  ]

  const dayNames = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb']

  const today = new Date()
  const isToday = (day) => {
    return today.getDate() === day && 
           today.getMonth() === month && 
           today.getFullYear() === year
  }

  // Upcoming events sorted by date
  const upcomingEvents = [...MOCK_EVENTS]
    .sort((a, b) => new Date(a.date) - new Date(b.date))
    .filter(e => new Date(e.date) >= new Date(today.toISOString().split('T')[0]))

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Calendario</h1>
          <p className="text-gray-500 mt-1">Tu agenda de hitos y eventos importantes</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="inline-flex items-center gap-1 p-1 bg-gray-100 rounded-xl">
            <button
              onClick={() => setView('month')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                view === 'month' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
              }`}
            >
              Mes
            </button>
            <button
              onClick={() => setView('list')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                view === 'list' ? 'bg-white text-gray-900 shadow-sm' : 'text-gray-600'
              }`}
            >
              Lista
            </button>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Calendar */}
        <div className="lg:col-span-2">
          <Card>
            {/* Calendar Header */}
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-gray-900">
                {monthNames[month]} {year}
              </h2>
              <div className="flex items-center gap-2">
                <button
                  onClick={goToToday}
                  className="px-3 py-1.5 text-sm text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                >
                  Hoy
                </button>
                <button
                  onClick={prevMonth}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <button
                  onClick={nextMonth}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            </div>

            {/* Day Names */}
            <div className="grid grid-cols-7 mb-2">
              {dayNames.map(day => (
                <div key={day} className="text-center text-sm font-medium text-gray-500 py-2">
                  {day}
                </div>
              ))}
            </div>

            {/* Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {/* Empty cells for days before month starts */}
              {Array.from({ length: startingDay }).map((_, i) => (
                <div key={`empty-${i}`} className="aspect-square p-1" />
              ))}

              {/* Days of month */}
              {Array.from({ length: daysInMonth }).map((_, i) => {
                const day = i + 1
                const dateStr = formatDateStr(day)
                const dayEvents = getEventsForDate(dateStr)
                const hasInterview = dayEvents.some(e => e.type === 'interview')
                const isSelected = selectedDate === dateStr

                return (
                  <button
                    key={day}
                    onClick={() => setSelectedDate(dateStr)}
                    className={`aspect-square p-1 rounded-xl transition-all relative ${
                      isToday(day) ? 'bg-primary-50 ring-2 ring-primary-500' :
                      isSelected ? 'bg-gray-100' :
                      'hover:bg-gray-50'
                    }`}
                  >
                    <span className={`text-sm font-medium ${
                      isToday(day) ? 'text-primary-600' : 'text-gray-900'
                    }`}>
                      {day}
                    </span>

                    {/* Event indicators */}
                    {dayEvents.length > 0 && (
                      <div className="absolute bottom-1 left-1/2 -translate-x-1/2 flex gap-0.5">
                        {dayEvents.slice(0, 3).map((event, idx) => (
                          <span
                            key={idx}
                            className={`w-1.5 h-1.5 rounded-full ${getEventTypeStyle(event.type).dot}`}
                          />
                        ))}
                      </div>
                    )}

                    {/* Critical event highlight */}
                    {hasInterview && (
                      <span className="absolute top-0.5 right-0.5 text-xs">🔴</span>
                    )}
                  </button>
                )
              })}
            </div>

            {/* Legend */}
            <div className="flex items-center gap-4 mt-6 pt-4 border-t border-gray-100">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-red-500" />
                <span className="text-sm text-gray-600">Entrevista Real</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-purple-500" />
                <span className="text-sm text-gray-600">Simulacro Virtual</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-amber-500" />
                <span className="text-sm text-gray-600">Simulacro Presencial</span>
              </div>
            </div>
          </Card>

          {/* Selected Date Events */}
          {selectedDate && (
            <Card className="mt-6">
              <h3 className="font-semibold text-gray-900 mb-4">
                Eventos del {new Date(selectedDate + 'T00:00').toLocaleDateString('es-ES', {
                  weekday: 'long',
                  day: 'numeric',
                  month: 'long'
                })}
              </h3>
              {getEventsForDate(selectedDate).length === 0 ? (
                <p className="text-gray-500 text-sm">No hay eventos programados para esta fecha</p>
              ) : (
                <div className="space-y-3">
                  {getEventsForDate(selectedDate).map(event => {
                    const style = getEventTypeStyle(event.type)
                    return (
                      <div 
                        key={event.id}
                        className={`p-4 rounded-xl ${style.bg}`}
                      >
                        <div className="flex items-start justify-between">
                          <div>
                            <h4 className={`font-medium ${style.text}`}>{event.title}</h4>
                            <p className="text-sm text-gray-600 mt-1">{event.time}</p>
                            {event.location && (
                              <p className="text-sm text-gray-500">{event.location}</p>
                            )}
                            {event.advisor && (
                              <p className="text-sm text-gray-500">Asesor: {event.advisor}</p>
                            )}
                          </div>
                          {event.critical && (
                            <Badge variant="danger" size="sm">CRÍTICO</Badge>
                          )}
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </Card>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Upcoming Events */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Próximos Eventos</h3>
            <div className="space-y-4">
              {upcomingEvents.map(event => {
                const style = getEventTypeStyle(event.type)
                const eventDate = new Date(event.date + 'T00:00')
                return (
                  <div key={event.id} className="flex gap-3">
                    <div className={`w-10 h-10 rounded-xl ${style.bg} flex items-center justify-center flex-shrink-0`}>
                      {event.type === 'interview' ? '🔴' :
                       event.type === 'simulation_virtual' ? '📹' : '🏢'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="font-medium text-gray-900 text-sm truncate">{event.title}</p>
                      <p className="text-xs text-gray-500">
                        {eventDate.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })} • {event.time}
                      </p>
                      {event.critical && (
                        <Badge variant="danger" size="sm" className="mt-1">Hito Crítico</Badge>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          </Card>

          {/* Timeline */}
          <Card>
            <h3 className="font-semibold text-gray-900 mb-4">Historial de Cambios</h3>
            <div className="relative">
              <div className="absolute left-[7px] top-2 bottom-2 w-0.5 bg-gray-200" />
              <div className="space-y-4">
                {MOCK_TIMELINE.map((item, index) => (
                  <div key={index} className="flex gap-3 relative">
                    <div className={`w-4 h-4 rounded-full border-2 border-white z-10 flex-shrink-0 ${
                      item.type === 'milestone' ? 'bg-green-500' : 'bg-blue-500'
                    }`} />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-gray-700">{item.event}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        {new Date(item.date + 'T00:00').toLocaleDateString('es-ES', {
                          day: 'numeric',
                          month: 'short',
                          year: 'numeric'
                        })}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
