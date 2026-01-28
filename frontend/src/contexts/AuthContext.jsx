import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authService } from '../services'

const AuthContext = createContext(null)

/**
 * Transforma el usuario del backend al formato del frontend
 */
function transformUser(backendUser) {
  if (!backendUser) return null
  
  return {
    id: backendUser.id,
    email: backendUser.email,
    name: backendUser.nombre_completo || `${backendUser.first_name} ${backendUser.last_name}`,
    firstName: backendUser.first_name,
    lastName: backendUser.last_name,
    // Mapear roles: backend usa 'cliente'/'asesor', frontend usa 'client'/'advisor'
    role: backendUser.rol === 'cliente' ? 'client' : 
          backendUser.rol === 'asesor' ? 'advisor' : 
          backendUser.rol,
    backendRole: backendUser.rol,
    telefono: backendUser.telefono,
    avatar: backendUser.foto_perfil,
    isActive: backendUser.is_active,
    createdAt: backendUser.created_at,
    // Estos campos se obtienen de otros endpoints
    simulationsUsed: 0,
    simulationsTotal: 2
  }
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  /**
   * Verifica la sesión al cargar la aplicación
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Primero verificar si hay tokens guardados
        const hasTokens = authService.hasTokens()
        const savedUser = authService.getStoredUser()
        
        if (hasTokens && savedUser) {
          // Cargar usuario guardado inmediatamente para evitar flash
          setUser(transformUser(savedUser))
          
          // Intentar verificar/refrescar en background
          try {
            const result = await authService.verifySession()
            if (result.isValid) {
              setUser(transformUser(result.user))
            }
          } catch (verifyError) {
            console.warn('Error verificando sesión, usando datos guardados:', verifyError)
            // Mantener el usuario guardado si la verificación falla
            // (puede ser error de red temporal)
          }
        } else if (savedUser && !hasTokens) {
          // Hay usuario guardado pero no tokens - limpiar todo
          localStorage.removeItem('migrafacil_user')
        }
      } catch (err) {
        console.error('Error al inicializar auth:', err)
      } finally {
        setIsLoading(false)
      }
    }

    initAuth()
  }, [])

  /**
   * Inicia sesión con email y contraseña
   */
  const login = useCallback(async (email, password) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await authService.login(email, password)
      const userData = transformUser(response.usuario)
      setUser(userData)
      return { success: true, user: userData }
    } catch (err) {
      const errorMessage = err.data?.error || err.message || 'Error al iniciar sesión'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Registra un nuevo usuario
   */
  const register = useCallback(async (userData) => {
    setIsLoading(true)
    setError(null)
    
    try {
      const response = await authService.register({
        email: userData.email,
        password: userData.password,
        password_confirm: userData.passwordConfirm,
        first_name: userData.firstName,
        last_name: userData.lastName,
        telefono: userData.phone || '',
        rol: 'cliente' // Por defecto se registran como clientes
      })
      
      const newUser = transformUser(response.usuario)
      setUser(newUser)
      return { success: true, user: newUser }
    } catch (err) {
      const errorMessage = err.data?.error || err.message || 'Error al registrarse'
      setError(errorMessage)
      return { success: false, error: errorMessage }
    } finally {
      setIsLoading(false)
    }
  }, [])

  /**
   * Cierra la sesión
   */
  const logout = useCallback(async () => {
    setIsLoading(true)
    try {
      await authService.logout()
    } catch (err) {
      console.error('Error durante logout:', err)
    } finally {
      setUser(null)
      setError(null)
      setIsLoading(false)
    }
  }, [])

  /**
   * Actualiza el perfil del usuario
   */
  const updateProfile = useCallback(async (profileData) => {
    try {
      const response = await authService.updateProfile({
        first_name: profileData.firstName,
        last_name: profileData.lastName,
        telefono: profileData.phone,
        foto_perfil: profileData.avatar
      })
      
      const updatedUser = transformUser(response.usuario)
      setUser(updatedUser)
      return { success: true, user: updatedUser }
    } catch (err) {
      const errorMessage = err.data?.error || err.message || 'Error al actualizar perfil'
      return { success: false, error: errorMessage }
    }
  }, [])

  /**
   * Cambia la contraseña
   */
  const changePassword = useCallback(async (currentPassword, newPassword, confirmPassword) => {
    try {
      await authService.changePassword(currentPassword, newPassword, confirmPassword)
      return { success: true }
    } catch (err) {
      const errorMessage = err.data?.error || err.message || 'Error al cambiar contraseña'
      return { success: false, error: errorMessage }
    }
  }, [])

  /**
   * Refresca los datos del usuario
   */
  const refreshUser = useCallback(async () => {
    try {
      const profile = await authService.getProfile()
      const updatedUser = transformUser(profile)
      setUser(updatedUser)
      return updatedUser
    } catch (err) {
      console.error('Error al refrescar usuario:', err)
      return null
    }
  }, [])

  const value = {
    // Estado
    user,
    isLoading,
    error,
    isAuthenticated: !!user,
    
    // Helpers de rol
    isClient: user?.role === 'client',
    isAdvisor: user?.role === 'advisor',
    isAdmin: user?.role === 'admin',
    
    // Acciones
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    refreshUser,
    
    // Limpiar error
    clearError: () => setError(null)
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
