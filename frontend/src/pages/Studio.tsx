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

class ResultsErrorBoundary extends Component<{ children: ReactNode }, { error: string | null }> {
  state = { error: null as string | null }
  static getDerivedStateFromError(error: Error) { return { error: error.message } }
  render() {
    if (this.state.error) {
      return (
        <div className="p-6 border-2 border-destructive/30 rounded-xl bg-red-50">
          <h3 className="font-semibold text-destructive mb-2">Rendering error</h3>
          <p className="text-sm text-muted-foreground mb-3">{this.state.error}</p>
          <button
            onClick={() => this.setState({ error: null })}
            className="px-4 py-2 bg-primary text-white rounded-md text-sm"
          >
            Retry
          </button>
        </div>
      )
    }
    return this.props.children
  }
}

export default function Studio() {
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

  if (!user) {
    return (
      <>
        <div className="max-w-3xl mx-auto px-4 py-20 text-center">
          <h1 className="text-2xl font-bold mb-4">Sign in to access the Design Studio</h1>
          <p className="text-muted-foreground mb-6">
            Create an account to start designing custom organisms for free.
          </p>
          <button
            onClick={() => setShowAuth(true)}
            className="px-6 py-3 bg-primary text-white rounded-xl font-medium hover:opacity-90"
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
        <div className="mb-6 flex items-center justify-between bg-cyan-500/5 border border-cyan-500/20 rounded-lg px-4 py-2.5">
          <div className="flex items-center gap-3">
            <div className="flex gap-1">
              {Array.from({ length: user.monthly_limit }).map((_, i) => (
                <div
                  key={i}
                  className={`w-2.5 h-2.5 rounded-full ${
                    i < user.designs_this_month ? 'bg-cyan-500' : 'bg-gray-700'
                  }`}
                />
              ))}
            </div>
            <span className="text-sm text-gray-300">
              {user.monthly_limit - user.designs_this_month} of {user.monthly_limit} free designs remaining
            </span>
          </div>
          {user.designs_this_month >= user.monthly_limit && (
            <button
              onClick={() => navigate('/pricing')}
              className="px-3 py-1 bg-cyan-600 text-white rounded-md text-xs font-medium hover:bg-cyan-500"
            >
              Upgrade to Pro
            </button>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left: Input + Challenges */}
        <div className="lg:col-span-1 space-y-6">
          <div>
            <h1 className="text-xl font-bold mb-1">Design Studio</h1>
            <p className="text-sm text-muted-foreground">
              Describe what you want to build in plain English.
            </p>
          </div>

          <PromptBox key={selectedPrompt} initialPrompt={selectedPrompt} />

          <DailyChallenge onSelect={(prompt) => setSelectedPrompt(prompt)} />
        </div>

        {/* Right: Results */}
        <div className="lg:col-span-2 space-y-6">
          {/* Error display with contextual actions */}
          {error && (
            <div className="p-5 border border-red-500/20 rounded-xl bg-red-500/5">
              <h3 className="font-semibold text-red-400 mb-2">Let's fix this</h3>
              <p className="text-sm text-gray-300 leading-relaxed">{error}</p>
              <div className="mt-4 flex flex-wrap gap-2">
                {(error.includes('limit') || error.includes('5 free') || error.includes('month')) ? (
                  <>
                    <button onClick={() => navigate('/pricing')} className="px-4 py-2.5 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500">
                      Upgrade to Pro
                    </button>
                    <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2.5 border border-gray-700 text-gray-400 rounded-lg text-sm hover:bg-gray-800">
                      Maybe later
                    </button>
                  </>
                ) : (error.includes('building blocks') || error.includes('rephrasing')) ? (
                  <>
                    <button onClick={() => { useDesign.setState({ error: null }); setSelectedPrompt('Design a microbe that eats ocean microplastics') }} className="px-4 py-2.5 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500">
                      Try an example instead
                    </button>
                    <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2.5 border border-gray-700 text-gray-400 rounded-lg text-sm hover:bg-gray-800">
                      Edit my idea
                    </button>
                  </>
                ) : (
                  <>
                    <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2.5 bg-cyan-600 text-white rounded-lg text-sm font-medium hover:bg-cyan-500">
                      Try again
                    </button>
                    <button onClick={() => useDesign.setState({ error: null })} className="px-4 py-2.5 border border-gray-700 text-gray-400 rounded-lg text-sm hover:bg-gray-800">
                      Dismiss
                    </button>
                  </>
                )}
              </div>
            </div>
          )}

          {/* Generating state with progress steps */}
          {generating && (
            <div className="p-6 border border-cyan-500/20 rounded-xl bg-cyan-500/5">
              <div className="flex items-center gap-3 mb-4">
                <svg className="animate-spin h-5 w-5 text-cyan-400" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                </svg>
                <h3 className="font-semibold text-cyan-300">Designing your organism...</h3>
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
            <div className="flex items-center justify-center min-h-[400px] border border-dashed border-gray-700 rounded-xl bg-gray-900/30">
              <div className="text-center p-8">
                <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-800 flex items-center justify-center">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-8 h-8 text-gray-500">
                    <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9z" />
                    <path d="M12 3v18M3 12h18" />
                  </svg>
                </div>
                <h3 className="font-semibold mb-2 text-gray-200">Your design will appear here</h3>
                <p className="text-sm text-gray-500 max-w-sm">
                  Enter a prompt on the left and hit Generate. You'll get a complete organism
                  design with real gene circuits, DNA sequences, plasmid maps, and safety analysis.
                </p>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
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
    <div className="space-y-2">
      {steps.map((s, i) => (
        <div key={i} className={`flex items-start gap-3 transition-opacity duration-500 ${
          i <= step ? 'opacity-100' : 'opacity-30'
        }`}>
          <div className={`mt-0.5 w-5 h-5 rounded-full flex items-center justify-center shrink-0 text-xs ${
            i < step ? 'bg-cyan-600 text-white' :
            i === step ? 'bg-cyan-500/20 text-cyan-400 animate-pulse' :
            'bg-gray-800 text-gray-600'
          }`}>
            {i < step ? (
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" className="w-3 h-3">
                <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
            ) : (
              <span>{i + 1}</span>
            )}
          </div>
          <div>
            <p className={`text-sm font-medium ${i <= step ? 'text-cyan-300' : 'text-gray-600'}`}>{s.label}</p>
            {i === step && (
              <p className="text-xs text-cyan-500 mt-0.5">{s.desc}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
