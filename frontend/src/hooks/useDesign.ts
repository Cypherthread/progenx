import { create } from 'zustand'
import { designs, type DesignResponse, type ChatMessage } from '@/lib/api'
import { useAuth } from './useAuth'
import { toast } from '@/components/Toast'

interface DesignState {
  current: DesignResponse | null
  history: DesignResponse[]
  chatMessages: ChatMessage[]
  generating: boolean
  refining: boolean
  error: string | null
  generate: (prompt: string, environment: string, safety_level: number, complexity: number) => Promise<void>
  refine: (message: string) => Promise<void>
  loadHistory: () => Promise<void>
  loadDesign: (id: string) => Promise<void>
  loadChat: (id: string) => Promise<void>
  clear: () => void
}

export const useDesign = create<DesignState>((set, get) => ({
  current: null,
  history: [],
  chatMessages: [],
  generating: false,
  refining: false,
  error: null,

  generate: async (prompt, environment, safety_level, complexity) => {
    // Double-click protection: don't fire if already generating
    if (get().generating) return

    set({ generating: true, error: null })
    try {
      const result = await designs.generate({ prompt, environment, safety_level, complexity })
      set({ current: result, generating: false })
      // Refresh user data to update design count
      useAuth.getState().loadUser()
    } catch (e: any) {
      const msg = e.message || 'Design generation failed'
      // Make rate limit errors user-friendly
      let friendlyMsg = msg
      if (msg.includes('429') || msg.includes('limit') || msg.includes('Free tier')) {
        friendlyMsg = 'You\'ve used all 5 free designs this month. Upgrade to Pro for unlimited designs, or come back next month.'
      } else if (msg.includes('unavailable') || msg.includes('starting up') || msg.includes('Connection')) {
        friendlyMsg = 'The design engine is warming up. This happens after periods of inactivity. Try again in about 30 seconds.'
      } else if (msg.includes('unexpected response') || msg.includes('parse')) {
        friendlyMsg = 'Your idea was tricky for the AI this time. Try again, or simplify your description a bit.'
      } else if (msg.includes('busy') || msg.includes('503')) {
        friendlyMsg = 'Lots of people designing right now. Pro users get priority access. Try again in a moment.'
      } else if (msg.includes('safety') || msg.includes('blocked') || msg.includes('denied')) {
        friendlyMsg = 'This design triggered a safety flag. Try adjusting your idea or pick one of the example prompts.'
      } else if (msg.includes('not found') || msg.includes('No known gene')) {
        friendlyMsg = 'We couldn\'t find real building blocks for that exact idea yet. Try rephrasing, or pick a well-known application like plastic degradation or nitrogen fixation.'
      }
      set({ error: friendlyMsg, generating: false })
    }
  },

  refine: async (message) => {
    const { current, refining } = get()
    if (!current || refining) return
    set({ refining: true, error: null })
    try {
      const result = await designs.refine(current.id, message)
      set({ current: result, refining: false })
      const chat = await designs.chat(current.id)
      set({ chatMessages: chat })
    } catch (e: any) {
      const msg = e.message || 'Refinement failed'
      let friendlyMsg = msg
      if (msg.includes('unavailable') || msg.includes('Connection')) {
        friendlyMsg = 'Design engine is warming up. Try again in a moment.'
      } else if (msg.includes('parse') || msg.includes('unexpected')) {
        friendlyMsg = 'The AI had trouble with that refinement. Try rephrasing your request.'
      }
      set({ error: friendlyMsg, refining: false })
      toast(friendlyMsg, 'error')
    }
  },

  loadHistory: async () => {
    try {
      const list = await designs.history()
      set({ history: list })
    } catch {
      // ignore
    }
  },

  loadDesign: async (id) => {
    try {
      const d = await designs.get(id)
      set({ current: d })
    } catch (e: any) {
      set({ error: e.message })
    }
  },

  loadChat: async (id) => {
    try {
      const chat = await designs.chat(id)
      set({ chatMessages: chat })
    } catch {
      // ignore
    }
  },

  clear: () => set({ current: null, chatMessages: [], error: null }),
}))
