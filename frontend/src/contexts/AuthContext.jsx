import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

// Usuarios de prueba para desarrollo
const MOCK_USERS = {
  'cliente@migrafacil.com': {
    id: 1,
    email: 'cliente@migrafacil.com',
    password: 'cliente123',
    name: 'Juan Pérez García',
    role: 'client',
    avatar: null,
    visaType: 'study',
    simulationsUsed: 1,
    simulationsTotal: 2
  },
  'asesor@migrafacil.com': {
    id: 2,
    email: 'asesor@migrafacil.com',
    password: 'asesor123',
    name: 'María González',
    role: 'advisor',
    avatar: null
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Simular verificación de sesión
    const savedUser = localStorage.getItem('migrafacil_user')
    if (savedUser) {
      setUser(JSON.parse(savedUser))
    }
    setIsLoading(false)
  }, [])

  const login = async (email, password) => {
    // Simular llamada API
    await new Promise(resolve => setTimeout(resolve, 1000))

    const mockUser = MOCK_USERS[email]
    if (mockUser && mockUser.password === password) {
      const userData = { ...mockUser }
      delete userData.password
      setUser(userData)
      localStorage.setItem('migrafacil_user', JSON.stringify(userData))
      return { success: true, user: userData }
    }

    return { success: false, error: 'Credenciales inválidas' }
  }

  const logout = () => {
    setUser(null)
    localStorage.removeItem('migrafacil_user')
  }

  const value = {
    user,
    isLoading,
    isAuthenticated: !!user,
    isClient: user?.role === 'client',
    isAdvisor: user?.role === 'advisor',
    login,
    logout
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
