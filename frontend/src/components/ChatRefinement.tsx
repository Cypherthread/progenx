import { useState, useRef, useEffect } from 'react'
import { useDesign } from '@/hooks/useDesign'
import type { ChatMessage } from '@/lib/api'

interface Props {
  messages: ChatMessage[]
}

const QUICK_ACTIONS = [
  { label: 'Make it safer', prompt: 'Add a stronger kill switch and improve biocontainment' },
  { label: 'Boost yield', prompt: 'Optimize the pathway for higher product yield' },
  { label: 'Different chassis', prompt: 'Redesign this for Pseudomonas putida instead' },
  { label: 'Simpler design', prompt: 'Reduce to the minimum genes needed for basic function' },
  { label: 'Add reporter', prompt: 'Add a GFP reporter gene so I can see if expression is working' },
  { label: 'Stronger promoters', prompt: 'Use stronger constitutive promoters for higher expression' },
]

export default function ChatRefinement({ messages }: Props) {
  const [input, setInput] = useState('')
  const [expanded, setExpanded] = useState(false)
  const { refine, refining } = useDesign()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages.length, refining])

  function handleSend(text?: string) {
    const msg = text || input.trim()
    if (!msg) return
    refine(msg)
    setInput('')
    setExpanded(true)
  }

  return (
    <div className="border border-gray-800 rounded-xl overflow-hidden bg-gray-900/50">
      {/* Header - clickable to expand/collapse */}
      <button
        onClick={() => { setExpanded(!expanded); if (!expanded) setTimeout(() => inputRef.current?.focus(), 100) }}
        className="w-full p-4 flex items-center justify-between text-left hover:bg-gray-800/30 transition-colors"
      >
        <div>
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            Refine This Design
            {messages.length > 0 && (
              <span className="text-[10px] px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 rounded-full">
                {Math.floor(messages.length / 2)} revision{Math.floor(messages.length / 2) !== 1 ? 's' : ''}
              </span>
            )}
          </h3>
          <p className="text-xs text-gray-500 mt-0.5">
            Tell the AI what to change. Your design updates instantly.
          </p>
        </div>
        <svg
          viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
          className={`w-4 h-4 text-gray-500 transition-transform ${expanded ? 'rotate-180' : ''}`}
        >
          <path d="M6 9l6 6 6-6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>

      {/* Quick actions - always visible when collapsed */}
      {!expanded && (
        <div className="px-4 pb-4 flex flex-wrap gap-2">
          {QUICK_ACTIONS.slice(0, 4).map((action) => (
            <button
              key={action.label}
              onClick={() => handleSend(action.prompt)}
              disabled={refining}
              className="px-3 py-1.5 text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700 rounded-lg hover:border-cyan-500/30 hover:text-cyan-300 transition-all disabled:opacity-40"
            >
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Expanded view */}
      {expanded && (
        <>
          {/* Quick actions row */}
          <div className="px-4 pb-3 flex flex-wrap gap-1.5 border-b border-gray-800">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                onClick={() => handleSend(action.prompt)}
                disabled={refining}
                className="px-2.5 py-1 text-[11px] font-medium bg-gray-800/50 text-gray-500 rounded-md hover:text-cyan-400 hover:bg-gray-800 transition-all disabled:opacity-40"
              >
                {action.label}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="max-h-80 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && !refining && (
              <p className="text-sm text-gray-600 text-center py-4">
                No refinements yet. Try a quick action above or type your own request.
              </p>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
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
                <div className="bg-gray-800 rounded-xl px-4 py-3 text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <svg className="animate-spin h-4 w-4 text-cyan-400" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    <span>Updating your design...</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">This may take 30-60 seconds</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-800 p-3 flex gap-2">
            <input
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="e.g. Switch to a different kill switch, add a reporter gene..."
              disabled={refining}
              className="flex-1 px-4 py-2.5 bg-gray-900/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/50 disabled:opacity-50"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend()
                }
              }}
            />
            <button
              onClick={() => handleSend()}
              disabled={refining || !input.trim()}
              className="px-5 py-2.5 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 disabled:opacity-40 transition-colors shrink-0"
            >
              {refining ? 'Updating...' : 'Refine'}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
