import { useState, useEffect } from 'react'
import { Card, Badge, Button, Modal } from '../../../components/common'
import adminService from '../../../services/adminService'

export default function AdminAsesoresPage() {
  const [asesores, setAsesores] = useState([])
  const [loading, setLoading] = useState(true)
  const [filtroActivo, setFiltroActivo] = useState('todos')
  const [busqueda, setBusqueda] = useState('')
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    telefono: ''
  })
  const [formErrors, setFormErrors] = useState({})
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => {
    fetchAsesores()
  }, [filtroActivo])

  const fetchAsesores = async () => {
    try {
      setLoading(true)
      const params = {}
      if (filtroActivo !== 'todos') {
        params.activo = filtroActivo === 'activos'
      }
      if (busqueda) {
        params.busqueda = busqueda
      }
      const data = await adminService.getAsesores(params)
      setAsesores(data)
    } catch (error) {
      console.error('Error fetching asesores:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e) => {
    e.preventDefault()
    fetchAsesores()
  }

  const handleToggleEstado = async (id) => {
    try {
      await adminService.toggleEstadoAsesor(id)
      fetchAsesores()
    } catch (error) {
      console.error('Error toggling estado:', error)
      alert('Error al cambiar el estado del asesor')
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    setFormErrors(prev => ({ ...prev, [name]: '' }))
  }

  const validateForm = () => {
    const errors = {}
    if (!formData.email) errors.email = 'El email es requerido'
    if (!formData.email.includes('@')) errors.email = 'Email inválido'
    if (!formData.password) errors.password = 'La contraseña es requerida'
    if (formData.password.length < 8) errors.password = 'Mínimo 8 caracteres'
    if (formData.password !== formData.password_confirm) {
      errors.password_confirm = 'Las contraseñas no coinciden'
    }
    if (!formData.first_name) errors.first_name = 'El nombre es requerido'
    if (!formData.last_name) errors.last_name = 'El apellido es requerido'
    
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!validateForm()) return

    try {
      setSubmitting(true)
      await adminService.crearAsesor(formData)
      setShowModal(false)
      setFormData({
        email: '',
        password: '',
        password_confirm: '',
        first_name: '',
        last_name: '',
        telefono: ''
      })
      fetchAsesores()
      alert('Asesor creado exitosamente')
    } catch (error) {
      console.error('Error creating asesor:', error)
      if (error.data) {
        setFormErrors(error.data)
      } else {
        alert('Error al crear el asesor')
      }
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gestión de Asesores</h1>
        <p className="text-gray-500 mt-1">Administra los asesores del sistema</p>
      </div>

      {/* Actions Bar */}
      <div className="bg-white rounded-2xl shadow-sm p-4 mb-6">
        <div className="flex flex-col md:flex-row gap-4 justify-between items-center">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex gap-2 flex-1 max-w-md">
            <input
              type="text"
              placeholder="Buscar por nombre o email..."
              value={busqueda}
              onChange={(e) => setBusqueda(e.target.value)}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <Button type="submit" variant="secondary">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </Button>
          </form>

          {/* Filters */}
          <div className="flex gap-2">
            {['todos', 'activos', 'inactivos'].map(filtro => (
              <button
                key={filtro}
                onClick={() => setFiltroActivo(filtro)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-colors ${
                  filtroActivo === filtro
                    ? 'bg-primary-100 text-primary-700'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {filtro.charAt(0).toUpperCase() + filtro.slice(1)}
              </button>
            ))}
          </div>

          {/* Add Button */}
          <Button onClick={() => setShowModal(true)}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Nuevo Asesor
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">👔</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Total Asesores</p>
              <p className="text-2xl font-bold text-gray-900">{asesores.length}</p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-green-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">✅</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Activos</p>
              <p className="text-2xl font-bold text-green-600">
                {asesores.filter(a => a.is_active).length}
              </p>
            </div>
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center">
              <span className="text-2xl">⏸️</span>
            </div>
            <div>
              <p className="text-sm text-gray-500">Inactivos</p>
              <p className="text-2xl font-bold text-red-600">
                {asesores.filter(a => !a.is_active).length}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Asesores List */}
      <Card>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Asesor
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Teléfono
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-4 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Registro
                </th>
                <th className="px-6 py-4 text-right text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {loading ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center">
                    <div className="flex justify-center">
                      <svg className="animate-spin h-8 w-8 text-primary-500" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                    </div>
                  </td>
                </tr>
              ) : asesores.length === 0 ? (
                <tr>
                  <td colSpan="6" className="px-6 py-12 text-center text-gray-500">
                    No hay asesores registrados
                  </td>
                </tr>
              ) : (
                asesores.map((asesor) => (
                  <tr key={asesor.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary-100 rounded-full flex items-center justify-center">
                          <span className="text-primary-600 font-semibold">
                            {asesor.first_name?.[0]}{asesor.last_name?.[0]}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">
                            {asesor.first_name} {asesor.last_name}
                          </p>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {asesor.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-600">
                      {asesor.telefono || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <Badge variant={asesor.is_active ? 'success' : 'danger'}>
                        {asesor.is_active ? 'Activo' : 'Inactivo'}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-sm">
                      {new Date(asesor.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right">
                      <button
                        onClick={() => handleToggleEstado(asesor.id)}
                        className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                          asesor.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {asesor.is_active ? 'Desactivar' : 'Activar'}
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Modal Crear Asesor */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Crear Nuevo Asesor"
      >
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre *
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  formErrors.first_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Juan"
              />
              {formErrors.first_name && (
                <p className="mt-1 text-sm text-red-500">{formErrors.first_name}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Apellido *
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  formErrors.last_name ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="Pérez"
              />
              {formErrors.last_name && (
                <p className="mt-1 text-sm text-red-500">{formErrors.last_name}</p>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleInputChange}
              className={`w-full px-4 py-2 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                formErrors.email ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="asesor@migrafacil.com"
            />
            {formErrors.email && (
              <p className="mt-1 text-sm text-red-500">{formErrors.email}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Teléfono
            </label>
            <input
              type="tel"
              name="telefono"
              value={formData.telefono}
              onChange={handleInputChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="+57 300 123 4567"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña *
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  formErrors.password ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              {formErrors.password && (
                <p className="mt-1 text-sm text-red-500">{formErrors.password}</p>
              )}
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Confirmar Contraseña *
              </label>
              <input
                type="password"
                name="password_confirm"
                value={formData.password_confirm}
                onChange={handleInputChange}
                className={`w-full px-4 py-2 border rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-transparent ${
                  formErrors.password_confirm ? 'border-red-500' : 'border-gray-300'
                }`}
                placeholder="••••••••"
              />
              {formErrors.password_confirm && (
                <p className="mt-1 text-sm text-red-500">{formErrors.password_confirm}</p>
              )}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <Button
              type="button"
              variant="secondary"
              className="flex-1"
              onClick={() => setShowModal(false)}
            >
              Cancelar
            </Button>
            <Button
              type="submit"
              className="flex-1"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <svg className="animate-spin w-4 h-4 mr-2" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Creando...
                </>
              ) : (
                'Crear Asesor'
              )}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  )
}
