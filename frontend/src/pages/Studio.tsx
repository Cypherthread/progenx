import { useEffect, useState, Component, type ReactNode } from 'react'
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
  const { current, chatMessages, loadChat } = useDesign()
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
          {current ? (
            <ResultsErrorBoundary>
              <ResultsPanel design={current} />
              <ChatRefinement messages={chatMessages} />
            </ResultsErrorBoundary>
          ) : (
            <div className="flex items-center justify-center min-h-[400px] border-2 border-dashed rounded-xl">
              <div className="text-center p-8">
                <div className="text-5xl mb-4">🧬</div>
                <h3 className="font-semibold mb-2">Your design will appear here</h3>
                <p className="text-sm text-muted-foreground max-w-sm">
                  Enter a prompt on the left and hit Generate. You'll get a complete organism
                  design with plasmid map, DNA sequence, safety analysis, and more.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
