import { useState } from 'react'
import { useDesign } from '@/hooks/useDesign'
import type { ChatMessage } from '@/lib/api'

interface Props {
  messages: ChatMessage[]
}

export default function ChatRefinement({ messages }: Props) {
  const [input, setInput] = useState('')
  const { refine, refining } = useDesign()

  function handleSend() {
    if (!input.trim()) return
    refine(input)
    setInput('')
  }

  return (
    <div className="border border-gray-800 rounded-xl overflow-hidden bg-gray-900/50">
      <div className="p-3 border-b border-gray-800 bg-gray-800/30">
        <h3 className="text-sm font-medium text-gray-200">Refine Your Design</h3>
        <p className="text-xs text-gray-500">
          Ask for changes: "Make it 30% more efficient" or "Add antibiotic resistance marker"
        </p>
      </div>

      <div className="max-h-64 overflow-y-auto p-3 space-y-3">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                msg.role === 'user'
                  ? 'bg-cyan-600 text-white'
                  : 'bg-gray-800 text-gray-300'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}
        {refining && (
          <div className="flex justify-start">
            <div className="bg-gray-800 rounded-lg px-3 py-2 text-sm text-gray-400">
              <span className="flex items-center gap-2">
                <svg className="animate-spin h-3 w-3" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                Refining design...
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-gray-800 p-3 flex gap-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Make it more efficient..."
          className="flex-1 px-3 py-2 bg-gray-900/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSend()
            }
          }}
        />
        <button
          onClick={handleSend}
          disabled={refining || !input.trim()}
          className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 disabled:opacity-40"
        >
          Send
        </button>
      </div>
    </div>
  )
}
