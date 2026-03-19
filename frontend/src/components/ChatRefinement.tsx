import { useState, useRef, useEffect } from 'react'
import { useDesign } from '@/hooks/useDesign'
import type { ChatMessage } from '@/lib/api'
import { track } from '@/hooks/useAnalytics'

interface Props {
  messages: ChatMessage[]
}

const QUICK_ACTIONS = [
  { label: 'Make it safer', prompt: 'Add a stronger kill switch and improve biocontainment', icon: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
  )},
  { label: 'Boost yield', prompt: 'Optimize the pathway for higher product yield', icon: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 19V6l12-3v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
  )},
  { label: 'Different chassis', prompt: 'Redesign this for Pseudomonas putida instead', icon: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="17 1 21 5 17 9"/><path d="M3 11V9a4 4 0 014-4h14"/><polyline points="7 23 3 19 7 15"/><path d="M21 13v2a4 4 0 01-4 4H3"/></svg>
  )},
  { label: 'Simpler design', prompt: 'Reduce to the minimum genes needed for basic function', icon: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
  )},
  { label: 'Add reporter', prompt: 'Add a GFP reporter gene so I can see if expression is working', icon: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
  )},
  { label: 'Stronger promoters', prompt: 'Use stronger constitutive promoters for higher expression', icon: (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
  )},
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
    track('feature_use', { page: 'studio', element: text ? 'quick_action' : 'refine_custom', value: msg.slice(0, 60) })
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
          {QUICK_ACTIONS.map((action) => (
            <button
              key={action.label}
              onClick={() => handleSend(action.prompt)}
              disabled={refining}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700/60 rounded-lg hover:border-cyan-500/30 hover:text-cyan-300 transition-all disabled:opacity-40"
            >
              <span className="text-gray-500">{action.icon}</span>
              {action.label}
            </button>
          ))}
        </div>
      )}

      {/* Expanded view */}
      {expanded && (
        <>
          {/* Quick actions row */}
          <div className="px-4 pb-3 flex flex-wrap gap-1.5 border-b border-gray-800/60">
            {QUICK_ACTIONS.map((action) => (
              <button
                key={action.label}
                onClick={() => handleSend(action.prompt)}
                disabled={refining}
                className="flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium bg-gray-800/50 text-gray-500 rounded-md hover:text-cyan-400 hover:bg-gray-800 transition-all disabled:opacity-40"
              >
                <span className="opacity-60">{action.icon}</span>
                {action.label}
              </button>
            ))}
          </div>

          {/* Messages */}
          <div className="max-h-48 sm:max-h-80 overflow-y-auto p-4 space-y-3">
            {messages.length === 0 && !refining && (
              <p className="text-sm text-gray-600 text-center py-4">
                No refinements yet. Try a quick action above or type your own request.
              </p>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start gap-2'}`}
              >
                {msg.role !== 'user' && (
                  <div className="shrink-0 w-6 h-6 rounded-full bg-gray-800 border border-gray-700/60 flex items-center justify-center mt-1">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-400">
                      <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1.27a7 7 0 01-12.46 0H6a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2z"/><circle cx="9" cy="13" r="1" fill="currentColor"/><circle cx="15" cy="13" r="1" fill="currentColor"/><path d="M9 17c.85.63 1.885 1 3 1s2.15-.37 3-1"/>
                    </svg>
                  </div>
                )}
                <div
                  className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm leading-relaxed ${
                    msg.role === 'user'
                      ? 'chat-user-msg text-white'
                      : 'bg-gray-800 text-gray-300 border border-gray-700/40'
                  }`}
                >
                  {msg.content}
                </div>
              </div>
            ))}

            {refining && (
              <div className="flex justify-start gap-2">
                <div className="shrink-0 w-6 h-6 rounded-full bg-gray-800 border border-gray-700/60 flex items-center justify-center mt-1">
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-cyan-400">
                    <path d="M12 2a2 2 0 012 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 017 7h1a1 1 0 011 1v3a1 1 0 01-1 1h-1.27a7 7 0 01-12.46 0H6a1 1 0 01-1-1v-3a1 1 0 011-1h1a7 7 0 017-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 012-2z"/><circle cx="9" cy="13" r="1" fill="currentColor"/><circle cx="15" cy="13" r="1" fill="currentColor"/><path d="M9 17c.85.63 1.885 1 3 1s2.15-.37 3-1"/>
                  </svg>
                </div>
                <div className="bg-gray-800 border border-gray-700/40 rounded-xl px-4 py-3 text-sm text-gray-400">
                  <div className="flex items-center gap-2">
                    <div className="elegant-spinner" style={{ width: 14, height: 14, borderWidth: 1.5 }} />
                    <span>Updating your design...</span>
                  </div>
                  <p className="text-xs text-gray-600 mt-1">Re-running the full design pipeline</p>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-gray-800/60 p-3 space-y-1.5">
            <div className="flex gap-2">
              <input
                ref={inputRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="e.g. Switch to a different kill switch, add a reporter gene..."
                disabled={refining}
                className="flex-1 px-4 py-3 bg-gray-900/50 border border-gray-700/60 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/40 disabled:opacity-50 transition-shadow"
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
                className="px-5 py-3 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 disabled:opacity-40 transition-colors shrink-0"
              >
                {refining ? 'Updating...' : 'Refine'}
              </button>
            </div>
            <p className="text-[10px] text-gray-600 px-1">
              Press <kbd className="px-1 py-0.5 bg-gray-800/60 border border-gray-700/50 rounded text-[9px] text-gray-500 font-mono">Enter</kbd> to send
            </p>
          </div>
        </>
      )}
    </div>
  )
}
