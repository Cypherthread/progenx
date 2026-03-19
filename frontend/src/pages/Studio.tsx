import { useEffect, useState, Component, type ReactNode } from 'react'
import { Helmet } from 'react-helmet-async'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useDesign } from '@/hooks/useDesign'
import PromptBox from '@/components/PromptBox'
import ResultsPanel from '@/components/ResultsPanel'
import ChatRefinement from '@/components/ChatRefinement'
import DailyChallenge from '@/components/DailyChallenge'
import AuthModal from '@/components/AuthModal'
import { useAnalytics, track } from '@/hooks/useAnalytics'

class ResultsErrorBoundary extends Component<{ children: ReactNode }, { error: string | null }> {
  state = { error: null as string | null }
  static getDerivedStateFromError(error: Error) { return { error: error.message } }
  render() {
    if (this.state.error) {
      return (
        <div className="p-6 border border-amber-500/20 rounded-xl bg-amber-500/5">
          <div className="flex items-start gap-3">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-amber-400 mt-0.5 shrink-0">
              <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>
            </svg>
            <div>
              <h3 className="font-semibold text-amber-400 mb-1.5 text-sm">Rendering error</h3>
              <p className="text-sm text-gray-400 mb-3">{this.state.error}</p>
              <button
                onClick={() => this.setState({ error: null })}
                className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        </div>
      )
    }
    return this.props.children
  }
}

export default function Studio() {
  useAnalytics('studio')
  const location = useLocation()
  const navigate = useNavigate()
  const user = useAuth((s) => s.user)
  const { current, generating, error, chatMessages, loadChat } = useDesign()
  const [showAuth, setShowAuth] = useState(false)
  const [selectedPrompt, setSelectedPrompt] = useState(
    (location.state as any)?.prompt || ''
  )

  useEffect(() => {
    if (current?.id) {
      loadChat(current.id)
    }
  }, [current?.id, loadChat])

  // Track funnel: design generated
  useEffect(() => {
    if (current?.id) {
      track('funnel_step', { page: 'studio', value: 'design_generated' })
    }
  }, [current?.id])

  if (!user) {
    return (
      <>
        <div className="max-w-3xl mx-auto px-4 py-20 text-center">
          <h1 className="text-2xl font-bold mb-4">Sign in to access the Design Studio</h1>
          <p className="text-gray-500 mb-6">
            Create an account to start designing custom organisms for free.
          </p>
          <button
            onClick={() => setShowAuth(true)}
            className="px-6 py-3 bg-cyan-600 text-white rounded-xl font-medium hover:bg-cyan-500"
          >
            Sign in
          </button>
        </div>
        {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
      </>
    )
  }

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <Helmet>
        <title>Design Studio | Progenx</title>
        <meta name="robots" content="noindex" />
      </Helmet>
      {/* Remaining designs banner */}
      {user.tier === 'free' && (
        <div className="mb-6 flex items-center justify-between bg-gray-900/60 border border-gray-800 rounded-xl px-5 py-3 backdrop-blur-sm">
          <div className="flex items-center gap-3">
            <div className="flex gap-1.5">
              {Array.from({ length: user.monthly_limit }).map((_, i) => (
                <div
                  key={i}
                  className={`w-2 h-2 rounded-full transition-colors ${
                    i < user.designs_this_month ? 'bg-cyan-400' : 'bg-gray-700/60'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-400">
              {user.monthly_limit - user.designs_this_month} of {user.monthly_limit} free designs remaining
            </span>
          </div>
          {user.designs_this_month >= user.monthly_limit && (
            <button
              onClick={() => navigate('/pricing')}
              className="px-4 py-1.5 bg-cyan-600/90 text-white rounded-lg text-xs font-medium hover:bg-cyan-500 transition-colors"
            >
              Upgrade to Pro
            </button>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Input + Challenges */}
        <div className="lg:col-span-1 space-y-6 lg:border-r lg:border-gray-800/60 lg:pr-8">
          <div>
            <h1 className="text-3xl font-bold text-white tracking-tight flex items-center gap-3">
              <svg width="28" height="28" viewBox="0 0 28 28" fill="none" className="shrink-0 opacity-80">
                <path d="M14 2C14 2 10 6 10 10C10 12 11 14 14 14C17 14 18 12 18 10C18 6 14 2 14 2Z" fill="url(#dna-drop)" opacity="0.6"/>
                <path d="M7 8C9.5 8 11 9.5 11 12C11 14.5 9 17 7 19" stroke="url(#dna-strand1)" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
                <path d="M21 8C18.5 8 17 9.5 17 12C17 14.5 19 17 21 19" stroke="url(#dna-strand2)" strokeWidth="1.5" strokeLinecap="round" fill="none"/>
                <line x1="9" y1="10" x2="19" y2="10" stroke="rgba(6,182,212,0.3)" strokeWidth="1" strokeDasharray="2 2"/>
                <line x1="8" y1="13" x2="20" y2="13" stroke="rgba(6,182,212,0.25)" strokeWidth="1" strokeDasharray="2 2"/>
                <line x1="9" y1="16" x2="19" y2="16" stroke="rgba(6,182,212,0.2)" strokeWidth="1" strokeDasharray="2 2"/>
                <circle cx="14" cy="22" r="3" fill="none" stroke="url(#dna-strand1)" strokeWidth="1.5"/>
                <circle cx="14" cy="22" r="1" fill="rgba(6,182,212,0.5)"/>
                <defs>
                  <linearGradient id="dna-drop" x1="14" y1="2" x2="14" y2="14">
                    <stop offset="0%" stopColor="#06B6D4"/>
                    <stop offset="100%" stopColor="#22D3EE"/>
                  </linearGradient>
                  <linearGradient id="dna-strand1" x1="7" y1="8" x2="7" y2="19">
                    <stop offset="0%" stopColor="#06B6D4"/>
                    <stop offset="100%" stopColor="#0EA5E9"/>
                  </linearGradient>
                  <linearGradient id="dna-strand2" x1="21" y1="8" x2="21" y2="19">
                    <stop offset="0%" stopColor="#22D3EE"/>
                    <stop offset="100%" stopColor="#06B6D4"/>
                  </linearGradient>
                </defs>
              </svg>
              Design <span className="progenx-gradient-text">Studio</span>
            </h1>
            <p className="text-sm text-gray-500 mt-1">
              Describe what you want to build in plain English.
            </p>
          </div>

          <PromptBox key={selectedPrompt} initialPrompt={selectedPrompt} />

          <DailyChallenge onSelect={(prompt) => setSelectedPrompt(prompt)} />
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-2 space-y-6">
          {/* Error display with contextual actions */}
          {error && (() => {
            const isRecoverable = error.includes('limit') || error.includes('5 free') || error.includes('month') || error.includes('building blocks') || error.includes('rephrasing')
            const borderColor = isRecoverable ? 'border-amber-500/20' : 'border-red-500/20'
            const bgColor = isRecoverable ? 'bg-amber-500/5' : 'bg-red-500/5'
            const headingColor = isRecoverable ? 'text-amber-400' : 'text-red-400'
            const iconColor = isRecoverable ? 'text-amber-400' : 'text-red-400'
            return (
            <div className={`p-5 border ${borderColor} rounded-xl ${bgColor}`}>
              <div className="flex items-start gap-3">
                <div className={`mt-0.5 shrink-0 ${iconColor}`}>
                  {isRecoverable ? (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                  ) : (
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"/><line x1="15" y1="9" x2="9" y2="15"/><line x1="9" y1="9" x2="15" y2="15"/>
                    </svg>
                  )}
                </div>
                <div className="flex-1">
                  <h3 className={`font-semibold ${headingColor} mb-1.5 text-sm`}>
                    {isRecoverable ? "Let's try something else" : "Something went wrong"}
                  </h3>
                  <p className="text-sm text-gray-400 leading-relaxed">{error}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    {(error.includes('limit') || error.includes('5 free') || error.includes('month')) ? (
                      <>
                        <button onClick={() => navigate('/pricing')} className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 transition-colors">
                          Upgrade to Pro
                        </button>
                        <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2 border border-gray-700/60 text-gray-400 rounded-lg text-sm hover:bg-gray-800/50 transition-colors">
                          Maybe later
                        </button>
                      </>
                    ) : (error.includes('building blocks') || error.includes('rephrasing')) ? (
                      <>
                        <button onClick={() => { useDesign.setState({ error: null }); setSelectedPrompt('Design a microbe that eats ocean microplastics') }} className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 transition-colors">
                          Try an example instead
                        </button>
                        <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2 border border-gray-700/60 text-gray-400 rounded-lg text-sm hover:bg-gray-800/50 transition-colors">
                          Edit my idea
                        </button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500 transition-colors">
                          Try again
                        </button>
                        <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2 border border-gray-700/60 text-gray-400 rounded-lg text-sm hover:bg-gray-800/50 transition-colors">
                          Dismiss
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
            )
          })()}

          {/* Generating state with progress steps */}
          {generating && (
            <div className="p-6 border border-cyan-500/15 rounded-xl bg-gradient-to-b from-cyan-500/5 to-transparent">
              <div className="flex items-center gap-3 mb-5">
                <div className="elegant-spinner shrink-0" />
                <GeneratingPhrase />
              </div>
              <ProgressSteps />
            </div>
          )}

          {current && !generating ? (
            <ResultsErrorBoundary>
              <ResultsPanel design={current} />
              <ChatRefinement messages={chatMessages} />
            </ResultsErrorBoundary>
          ) : !generating && !error ? (
            <div className="flex items-center justify-center min-h-[250px] sm:min-h-[400px] border border-gray-800/50 rounded-xl bg-gray-900/20">
              <div className="flex flex-col items-center gap-3">
                <span className="text-sm text-gray-600 font-medium tracking-wide">
                  Waiting to generate...
                </span>
                <div className="flex gap-1">
                  {[0, 1, 2, 3, 4].map(i => (
                    <span
                      key={i}
                      className="w-1 h-4 bg-gray-700 rounded-full"
                      style={{
                        animation: 'waveBar 1.2s ease-in-out infinite',
                        animationDelay: `${i * 0.1}s`,
                      }}
                    />
                  ))}
                </div>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  )
}


const BIO_PHRASES = [
  'Ligating your construct...',
  'Transforming competent cells...',
  'Screening colonies...',
  'Inducing expression...',
  'Running the gel... looks clean',
  'Checking the OD600...',
  'Miniprepping overnight cultures...',
  'Aligning reading frames...',
  'Picking the right ori...',
  'Gibson assembling fragments...',
  'Codon-optimizing for your chassis...',
  'Flipping through the parts registry...',
  'Calculating metabolic burden...',
  'Adding the kill switch...',
  'Designing your RBS library...',
  'Verifying no overlap with threat sequences...',
  'Growing up a starter culture...',
  'Nanodropping the final construct...',
]

function GeneratingPhrase() {
  const [index, setIndex] = useState(() => Math.floor(Math.random() * BIO_PHRASES.length))

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex(prev => (prev + 1) % BIO_PHRASES.length)
    }, 4000)
    return () => clearInterval(timer)
  }, [])

  return (
    <h3 className="font-semibold text-cyan-300 transition-opacity duration-300">
      {BIO_PHRASES[index]}
    </h3>
  )
}


function ProgressSteps() {
  const [step, setStep] = useState(0)

  useEffect(() => {
    const steps = [
      { delay: 0 },      // step 0: designing circuit
      { delay: 3000 },   // step 1: fetching sequences
      { delay: 8000 },   // step 2: optimizing codons
      { delay: 12000 },  // step 3: running FBA
      { delay: 16000 },  // step 4: planning assembly
      { delay: 20000 },  // step 5: generating map
    ]

    const timers = steps.map((s, i) =>
      setTimeout(() => setStep(i), s.delay)
    )
    return () => timers.forEach(clearTimeout)
  }, [])

  const steps = [
    { label: 'Picking the right building blocks', desc: 'Selecting real genes and control elements for your design' },
    { label: 'Finding verified parts', desc: 'Pulling real protein sequences from trusted databases' },
    { label: 'Tuning the DNA for your organism', desc: 'Optimizing the code so it works in the target species' },
    { label: 'Simulating growth and yield', desc: 'Predicting how well the organism will perform' },
    { label: 'Planning how to build it', desc: 'Choosing assembly method, safety switches, and designing primers' },
    { label: 'Drawing the construct map', desc: 'Building a visual map of your complete design' },
  ]

  return (
    <div className="space-y-1 progress-timeline relative">
      {steps.map((s, i) => (
        <div key={i} className={`flex items-start gap-3 py-1 transition-all duration-500 ${
          i <= step ? 'opacity-100' : 'opacity-30'
        }`}>
          <div className={`relative z-10 mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0 text-xs transition-all duration-300 ${
            i < step ? 'bg-cyan-600 text-white' :
            i === step ? 'bg-cyan-500/20 text-cyan-400 ring-2 ring-cyan-500/30' :
            'bg-gray-800 text-gray-600'
          }`}>
            {i < step ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="w-3 h-3">
                <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            ) : i === step ? (
              <div className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
            ) : (
              <span className="text-[10px]">{i + 1}</span>
            )}
          </div>
          <div className="min-w-0 pb-1">
            <p className={`text-sm font-medium transition-colors duration-300 ${i < step ? 'text-cyan-400/70' : i === step ? 'text-white' : 'text-gray-600'}`}>{s.label}</p>
            {i === step && (
              <p className="text-xs text-gray-500 mt-0.5">{s.desc}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
