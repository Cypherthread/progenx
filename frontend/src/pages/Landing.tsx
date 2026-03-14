import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from '@/components/AuthModal'

const EXAMPLES = [
  'Design a microbe that eats ocean microplastics and turns them into biodegradable plastic',
  'Create a cyanobacterium that captures CO2 10x faster than natural photosynthesis',
  'Engineer a soil bacterium that helps plants survive drought',
  'Design an enzyme that breaks down PFAS forever chemicals in groundwater',
  'Build a probiotic that detects and treats gut inflammation',
  'Create a yeast that produces spider silk protein for textiles',
]

export default function Landing() {
  const navigate = useNavigate()
  const user = useAuth((s) => s.user)
  const [showAuth, setShowAuth] = useState(false)

  function handleTryExample(prompt: string) {
    if (!user) {
      setShowAuth(true)
      return
    }
    navigate('/studio', { state: { prompt } })
  }

  return (
    <>
      <div className="flex flex-col">
        {/* Hero */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-green-50 via-blue-50 to-purple-50" />
          <div className="relative max-w-5xl mx-auto px-4 py-20 md:py-32 text-center">
            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-primary/10 rounded-full mb-6">
              <span className="w-2 h-2 bg-primary rounded-full animate-pulse" />
              <span className="text-xs font-medium text-primary">Now with Evo 2 genomic AI</span>
            </div>

            <h1 className="text-4xl md:text-6xl font-bold tracking-tight mb-6">
              Bioengineer Anything{' '}
              <span className="dna-gradient-text">in Plain English</span>
            </h1>

            <p className="text-lg md:text-xl text-muted-foreground max-w-3xl mx-auto mb-10">
              We help scientists, climate innovators, bio-hackers, and everyday problem-solvers
              design custom microbes, enzymes, and genetic circuits in plain English so they can
              tackle plastic-eating oceans, carbon-capturing bacteria, personalized medicine, or
              drought-proof crops — without a PhD, wet lab, or million-dollar budget.
            </p>

            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={() => user ? navigate('/studio') : setShowAuth(true)}
                className="px-8 py-3.5 dna-gradient text-white rounded-xl text-base font-semibold hover:opacity-90 transition-opacity shadow-lg"
              >
                Start Designing — Free
              </button>
              <button
                onClick={() => navigate('/pricing')}
                className="px-8 py-3.5 border-2 border-gray-200 rounded-xl text-base font-semibold hover:bg-secondary transition-colors"
              >
                View Plans
              </button>
            </div>
          </div>
        </section>

        {/* How It Works */}
        <section className="max-w-5xl mx-auto px-4 py-20">
          <h2 className="text-2xl font-bold text-center mb-12">How It Works</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: '1',
                title: 'Describe Your Goal',
                desc: 'Type what you want in plain English. No jargon needed. "Design a microbe that eats plastic" works perfectly.',
              },
              {
                step: '2',
                title: 'AI Designs It',
                desc: 'Claude AI + Evo 2 genomic model generate a complete organism design with real genes, promoters, and DNA sequence.',
              },
              {
                step: '3',
                title: 'Download & Refine',
                desc: 'Get interactive plasmid maps, FASTA files, safety scores, and vendor links. Refine through conversation.',
              },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="w-12 h-12 dna-gradient rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-white font-bold text-lg">{item.step}</span>
                </div>
                <h3 className="font-semibold mb-2">{item.title}</h3>
                <p className="text-sm text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Example Prompts */}
        <section className="bg-secondary/30 py-20">
          <div className="max-w-5xl mx-auto px-4">
            <h2 className="text-2xl font-bold text-center mb-3">Try an Example</h2>
            <p className="text-center text-muted-foreground mb-10">
              Click any prompt to start designing
            </p>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
              {EXAMPLES.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleTryExample(prompt)}
                  className="text-left p-4 bg-white border rounded-xl hover:border-primary hover:shadow-md transition-all group"
                >
                  <p className="text-sm group-hover:text-primary transition-colors">"{prompt}"</p>
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="max-w-5xl mx-auto px-4 py-20">
          <h2 className="text-2xl font-bold text-center mb-12">Built for Real Impact</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {[
              {
                title: 'Evo 2 Genomic AI',
                desc: 'Powered by Arc Institute\'s Evo 2 — a 40B parameter genomic foundation model that generates biologically plausible DNA sequences.',
              },
              {
                title: 'Safety First',
                desc: 'Every design is scored for dual-use risk, pathogenic sequences, and antibiotic resistance. Mandatory biosafety disclaimers on all outputs.',
              },
              {
                title: 'Interactive Plasmid Maps',
                desc: 'Visualize your constructs with interactive circular maps showing genes, promoters, and regulatory elements.',
              },
              {
                title: 'Real Biology',
                desc: 'Uses verified genes from iGEM Parts Registry, UniProt, and NCBI. No hallucinated biology — real parts, real sequences.',
              },
              {
                title: 'Chat Refinement',
                desc: '"Make it 30% more efficient" — iterate on designs through natural conversation. Your AI remembers context.',
              },
              {
                title: 'Export Everything',
                desc: 'Download FASTA files, plasmid maps, and one-click order from Twist Bioscience or IDT.',
              },
            ].map((f) => (
              <div key={f.title} className="p-5 border rounded-xl">
                <h3 className="font-semibold mb-1">{f.title}</h3>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* CTA */}
        <section className="dna-gradient py-16">
          <div className="max-w-3xl mx-auto px-4 text-center text-white">
            <h2 className="text-3xl font-bold mb-4">
              The future of biology is open
            </h2>
            <p className="text-lg opacity-90 mb-8">
              5 free designs per month. No credit card required.
            </p>
            <button
              onClick={() => user ? navigate('/studio') : setShowAuth(true)}
              className="px-8 py-3.5 bg-white text-primary rounded-xl text-base font-semibold hover:bg-gray-100 transition-colors"
            >
              Start Designing Now
            </button>
          </div>
        </section>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
