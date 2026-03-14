import { create } from 'zustand'
import { auth, type UserProfile } from '@/lib/api'

interface AuthState {
  user: UserProfile | null
  token: string | null
  loading: boolean
  error: string | null
  login: (email: string, password: string) => Promise<void>
  signup: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  loadUser: () => Promise<void>
}

export const useAuth = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('pf_token'),
  loading: false,
  error: null,

  login: async (email, password) => {
    set({ loading: true, error: null })
    try {
      const res = await auth.login(email, password)
      localStorage.setItem('pf_token', res.token)
      set({
        token: res.token,
        user: { id: res.user_id, email: res.email, name: res.name, tier: res.tier, designs_this_month: 0, monthly_limit: 5 },
        loading: false,
      })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  signup: async (email, password, name) => {
    set({ loading: true, error: null })
    try {
      const res = await auth.signup(email, password, name)
      localStorage.setItem('pf_token', res.token)
      set({
        token: res.token,
        user: { id: res.user_id, email: res.email, name: res.name, tier: res.tier, designs_this_month: 0, monthly_limit: 5 },
        loading: false,
      })
    } catch (e: any) {
      set({ error: e.message, loading: false })
    }
  },

  logout: () => {
    localStorage.removeItem('pf_token')
    set({ user: null, token: null })
  },

  loadUser: async () => {
    const token = localStorage.getItem('pf_token')
    if (!token) return
    try {
      const user = await auth.me()
      set({ user, token })
    } catch {
      localStorage.removeItem('pf_token')
      set({ user: null, token: null })
    }
  },
}))
