import { useState } from 'react'
import { useDesign } from '@/hooks/useDesign'
import Sliders from './Sliders'
import { track, getPrefs, setPrefs } from '@/hooks/useAnalytics'

interface Props {
  initialPrompt?: string
}

export default function PromptBox({ initialPrompt }: Props) {
  const prefs = getPrefs()
  const [prompt, setPrompt] = useState(initialPrompt || '')
  const [environment, setEnvironment] = useState(prefs.lastEnvironment || 'ocean')
  const [safetyLevel, setSafetyLevel] = useState(prefs.lastSafetyLevel ?? 0.7)
  const [complexity, setComplexity] = useState(prefs.lastComplexity ?? 0.5)
  const { generate, generating } = useDesign()

  function handleEnvironment(v: string) {
    setEnvironment(v)
    setPrefs({ lastEnvironment: v })
  }

  function handleSafety(v: number) {
    setSafetyLevel(v)
    setPrefs({ lastSafetyLevel: v })
  }

  function handleComplexity(v: number) {
    setComplexity(v)
    setPrefs({ lastComplexity: v })
  }

  function handleGenerate() {
    if (!prompt.trim()) return
    track('click', { page: 'studio', element: 'generate_button' })
    track('funnel_step', { page: 'studio', value: 'generate_clicked' })
    generate(prompt, environment, safetyLevel, complexity)
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Design a microbe that eats ocean microplastics and turns them into biodegradable plastic..."
          className="w-full min-h-[140px] p-4 pb-14 bg-gray-900/50 border border-gray-700/60 rounded-xl text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500/40 focus:border-cyan-500/40 transition-shadow"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              handleGenerate()
            }
          }}
        />
        {/* Character count */}
        {prompt.length > 0 && (
          <span className="absolute left-4 bottom-4 text-[11px] text-gray-600 tabular-nums">
            {prompt.length}
          </span>
        )}
        <button
          onClick={handleGenerate}
          disabled={generating || !prompt.trim()}
          className={`absolute right-3 bottom-3 px-5 py-2.5 rounded-lg text-sm font-medium text-white transition-all generate-glow ${
            generating
              ? 'bg-cyan-600/50 bio-glow cursor-wait'
              : 'bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:hover:bg-cyan-600'
          }`}
        >
          {generating ? (
            <span className="flex items-center gap-2">
              <div className="elegant-spinner" style={{ width: 14, height: 14, borderWidth: 2 }} />
              Designing...
            </span>
          ) : (
            <span className="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
              </svg>
              Generate
            </span>
          )}
        </button>
      </div>

      <Sliders
        environment={environment}
        setEnvironment={handleEnvironment}
        safetyLevel={safetyLevel}
        setSafetyLevel={handleSafety}
        complexity={complexity}
        setComplexity={handleComplexity}
      />

      <p className="text-[11px] text-gray-600">
        <kbd className="px-1.5 py-0.5 bg-gray-800/60 border border-gray-700/50 rounded text-[10px] text-gray-500 font-mono">Ctrl</kbd>{' '}
        <span className="text-gray-700">+</span>{' '}
        <kbd className="px-1.5 py-0.5 bg-gray-800/60 border border-gray-700/50 rounded text-[10px] text-gray-500 font-mono">Enter</kbd>{' '}
        <span className="text-gray-600">to generate</span>
        <span className="text-gray-700 mx-1.5">|</span>
        <span className="text-gray-600">All designs include safety scoring</span>
      </p>
    </div>
  )
}
