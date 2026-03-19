import { create } from 'zustand'

interface ToastItem {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

interface ToastStore {
  toasts: ToastItem[]
  add: (message: string, type?: 'success' | 'error' | 'info') => void
  remove: (id: number) => void
}

let nextId = 0

export const useToast = create<ToastStore>((set) => ({
  toasts: [],
  add: (message, type = 'success') => {
    const id = nextId++
    // Deduplicate: don't add if same message is already showing
    const existing = useToast.getState().toasts
    if (existing.some(t => t.message === message && t.type === type)) return
    set((s) => ({ toasts: [...s.toasts, { id, message, type }] }))
    setTimeout(() => {
      set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) }))
    }, 4000)
  },
  remove: (id) => set((s) => ({ toasts: s.toasts.filter((t) => t.id !== id) })),
}))

export function toast(message: string, type: 'success' | 'error' | 'info' = 'success') {
  useToast.getState().add(message, type)
}

export default function ToastContainer() {
  const { toasts, remove } = useToast()

  if (toasts.length === 0) return null

  return (
    <div
      className="fixed bottom-6 right-6 z-[100] flex flex-col gap-2 pointer-events-none"
      role="status"
      aria-live="polite"
    >
      {toasts.map((t) => (
        <div
          key={t.id}
          className={`pointer-events-auto px-4 py-3 rounded-lg shadow-lg border backdrop-blur-sm text-sm font-medium flex items-center gap-2 max-w-sm animate-[slideUp_0.3s_ease-out] ${
            t.type === 'success' ? 'bg-green-500/10 border-green-500/30 text-green-400' :
            t.type === 'error' ? 'bg-red-500/10 border-red-500/30 text-red-400' :
            'bg-cyan-500/10 border-cyan-500/30 text-cyan-400'
          }`}
        >
          {t.type === 'success' && (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 shrink-0">
              <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          )}
          {t.type === 'error' && (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-4 h-4 shrink-0">
              <circle cx="12" cy="12" r="10" />
              <path d="M12 8v4M12 16h.01" strokeLinecap="round" />
            </svg>
          )}
          <span>{t.message}</span>
          <button onClick={() => remove(t.id)} className="ml-auto text-gray-500 hover:text-white shrink-0" aria-label="Dismiss">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3.5 h-3.5">
              <path d="M18 6L6 18M6 6l12 12" strokeLinecap="round" />
            </svg>
          </button>
        </div>
      ))}
    </div>
  )
}
