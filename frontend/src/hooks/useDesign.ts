import { create } from 'zustand'
import { designs, type DesignResponse, type ChatMessage } from '@/lib/api'

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
    set({ generating: true, error: null })
    try {
      const result = await designs.generate({ prompt, environment, safety_level, complexity })
      set({ current: result, generating: false })
    } catch (e: any) {
      set({ error: e.message, generating: false })
    }
  },

  refine: async (message) => {
    const { current } = get()
    if (!current) return
    set({ refining: true, error: null })
    try {
      const result = await designs.refine(current.id, message)
      set({ current: result, refining: false })
      // Reload chat
      const chat = await designs.chat(current.id)
      set({ chatMessages: chat })
    } catch (e: any) {
      set({ error: e.message, refining: false })
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
