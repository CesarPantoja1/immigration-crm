import { useState, useEffect, createContext, useContext, useCallback } from 'react'

const ToastContext = createContext(null)

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([])

  const addToast = useCallback(({ type = 'info', title, message, duration = 5000 }) => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, type, title, message, duration }])
    
    if (duration > 0) {
      setTimeout(() => {
        setToasts(prev => prev.filter(t => t.id !== id))
      }, duration)
    }
    
    return id
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const success = useCallback((title, message) => addToast({ type: 'success', title, message }), [addToast])
  const error = useCallback((title, message) => addToast({ type: 'error', title, message }), [addToast])
  const info = useCallback((title, message) => addToast({ type: 'info', title, message }), [addToast])
  const warning = useCallback((title, message) => addToast({ type: 'warning', title, message }), [addToast])

  return (
    <ToastContext.Provider value={{ addToast, removeToast, success, error, info, warning }}>
      {children}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </ToastContext.Provider>
  )
}

export function useToast() {
  const context = useContext(ToastContext)
  if (!context) {
    throw new Error('useToast must be used within a ToastProvider')
  }
  return context
}

function ToastContainer({ toasts, onRemove }) {
  return (
    <div className="fixed top-4 right-4 z-[100] space-y-3 max-w-sm w-full pointer-events-none">
      {toasts.map(toast => (
        <Toast key={toast.id} {...toast} onClose={() => onRemove(toast.id)} />
      ))}
    </div>
  )
}

function Toast({ type, title, message, onClose }) {
  const styles = {
    success: {
      bg: 'bg-green-50 border-green-200',
      icon: 'text-green-500',
      title: 'text-green-800',
      iconPath: 'M5 13l4 4L19 7'
    },
    error: {
      bg: 'bg-red-50 border-red-200',
      icon: 'text-red-500',
      title: 'text-red-800',
      iconPath: 'M6 18L18 6M6 6l12 12'
    },
    warning: {
      bg: 'bg-amber-50 border-amber-200',
      icon: 'text-amber-500',
      title: 'text-amber-800',
      iconPath: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z'
    },
    info: {
      bg: 'bg-blue-50 border-blue-200',
      icon: 'text-blue-500',
      title: 'text-blue-800',
      iconPath: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z'
    }
  }

  const style = styles[type]

  return (
    <div className={`pointer-events-auto rounded-xl border p-4 shadow-lg animate-slideIn ${style.bg}`}>
      <div className="flex items-start gap-3">
        <svg className={`w-5 h-5 mt-0.5 ${style.icon}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={style.iconPath} />
        </svg>
        <div className="flex-1">
          <p className={`text-sm font-semibold ${style.title}`}>{title}</p>
          {message && <p className="text-sm text-gray-600 mt-1">{message}</p>}
        </div>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  )
}
