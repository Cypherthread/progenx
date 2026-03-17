import { useState } from 'react'
import { useDesign } from '@/hooks/useDesign'
import Sliders from './Sliders'

interface Props {
  initialPrompt?: string
}

export default function PromptBox({ initialPrompt }: Props) {
  const [prompt, setPrompt] = useState(initialPrompt || '')
  const [environment, setEnvironment] = useState('ocean')
  const [safetyLevel, setSafetyLevel] = useState(0.7)
  const [complexity, setComplexity] = useState(0.5)
  const { generate, generating } = useDesign()

  function handleGenerate() {
    if (!prompt.trim()) return
    generate(prompt, environment, safetyLevel, complexity)
  }

  return (
    <div className="space-y-4">
      <div className="relative">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Design a microbe that eats ocean microplastics and turns them into biodegradable plastic..."
          className="w-full min-h-[120px] p-4 pr-24 bg-gray-900/50 border border-gray-700 rounded-xl text-sm text-white placeholder-gray-500 resize-none focus:outline-none focus:ring-2 focus:ring-cyan-500/50 focus:border-cyan-500/50"
          onKeyDown={(e) => {
            if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
              handleGenerate()
            }
          }}
        />
        <button
          onClick={handleGenerate}
          disabled={generating || !prompt.trim()}
          className={`absolute right-3 bottom-3 px-4 py-2 rounded-lg text-sm font-medium text-white transition-all ${
            generating
              ? 'bg-cyan-600/50 bio-glow cursor-wait'
              : 'bg-cyan-600 hover:bg-cyan-500 disabled:opacity-40 disabled:hover:bg-cyan-600'
          }`}
        >
          {generating ? (
            <span className="flex items-center gap-2">
              <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
              </svg>
              Designing...
            </span>
          ) : (
            'Generate'
          )}
        </button>
      </div>

      <Sliders
        environment={environment}
        setEnvironment={setEnvironment}
        safetyLevel={safetyLevel}
        setSafetyLevel={setSafetyLevel}
        complexity={complexity}
        setComplexity={setComplexity}
      />

      <p className="text-xs text-gray-600">
        Press Ctrl+Enter to generate. All designs include safety scoring and dual-use assessment.
      </p>
    </div>
  )
}
