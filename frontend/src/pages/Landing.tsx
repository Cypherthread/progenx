import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState, useEffect, useRef } from 'react'
import AuthModal from '@/components/AuthModal'

const EXAMPLES = [
  'Design a microbe that eats ocean microplastics and converts them to biodegradable PHA bioplastic',
  'Create a cyanobacterium that captures CO2 10x faster than natural photosynthesis',
  'Engineer a soil bacterium that fixes nitrogen for crops without synthetic fertilizer',
  'Design an enzyme that breaks down PFAS forever chemicals in groundwater',
  'Build a probiotic that detects gut inflammation biomarkers',
  'Create a yeast that produces spider silk protein for sustainable textiles',
]

const PIPELINE_STEPS = [
  {
    title: 'Real Gene Circuits',
    desc: 'AI selects verified genes from NCBI GenBank — real proteins, real accessions, no hallucinated biology.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <path d="M12 3c-4.97 0-9 4.03-9 9s4.03 9 9 9 9-4.03 9-9-4.03-9-9-9z" />
        <path d="M12 3v18M3 12h18M5.6 5.6l12.8 12.8M18.4 5.6L5.6 18.4" />
      </svg>
    ),
  },
  {
    title: 'Codon Optimization',
    desc: 'Sequences tuned for your chassis organism. E. coli, P. putida, or S. elongatus codon tables built in.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <path d="M4 6h16M4 12h16M4 18h12" strokeLinecap="round" />
      </svg>
    ),
  },
  {
    title: 'Metabolic Modeling',
    desc: 'COBRApy flux balance analysis with genome-scale models predicts growth rates, yields, and metabolic burden.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <path d="M3 3v18h18" strokeLinecap="round" />
        <path d="M7 14l4-4 4 2 5-6" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: 'Construct Maps',
    desc: 'Circular plasmid maps with real bp positions — genes, promoters, terminators, ori, markers, kill switches.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 3a5 5 0 0 1 0 10 5 5 0 0 1 0-10" />
      </svg>
    ),
  },
  {
    title: 'Safety Scoring',
    desc: 'Dual-use screening, pathogen detection, resistance marker flags. Every design gets a biosafety assessment.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <path d="M12 2l7 4v5c0 5.25-3.5 10-7 11-3.5-1-7-5.75-7-11V6l7-4z" />
        <path d="M9 12l2 2 4-4" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  {
    title: 'Assembly Plans',
    desc: 'Golden Gate or Gibson assembly with ori selection, antibiotic markers, kill switches, and RBS optimization.',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-6 h-6">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
        <polyline points="14 2 14 8 20 8" />
        <line x1="16" y1="13" x2="8" y2="13" />
        <line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
  },
]

const AUDIENCES = [
  { name: 'iGEM Teams', count: '10,000+ participants/year' },
  { name: 'Climate Founders', count: 'Bio-based solutions' },
  { name: 'Biohackers', count: '100+ community labs' },
  { name: 'University Labs', count: '500+ programs' },
]

// Scroll reveal hook
function useReveal() {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) setVisible(true) },
      { threshold: 0.1 }
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [])

  return { ref, className: visible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4' }
}

function RevealSection({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  const reveal = useReveal()
  return (
    <div ref={reveal.ref} className={`transition-all duration-700 ease-out ${reveal.className} ${className}`}>
      {children}
    </div>
  )
}

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

  function handleCTA() {
    if (user) navigate('/studio')
    else setShowAuth(true)
  }

  return (
    <>
      <div className="flex flex-col">
        {/* ─── Hero ─── */}
        <section className="relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-blue-50/30 to-emerald-50/20" />
          <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-20 md:py-28">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              {/* Left: copy */}
              <div>
                <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-emerald-50 border border-emerald-200 rounded-full mb-6">
                  <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
                  <span className="text-xs font-medium text-emerald-700">Free to use — no credit card</span>
                </div>

                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight leading-[1.1] mb-6">
                  Design Microbes{' '}
                  <span className="dna-gradient-text">in Plain English</span>
                </h1>

                <p className="text-lg text-gray-600 leading-relaxed mb-8 max-w-lg">
                  Describe what you want — a plastic-eating bacterium, a carbon-capturing
                  microbe, a drought-resistant helper — and get real gene circuits, DNA
                  sequences, metabolic simulations, and safety scores in seconds.
                </p>

                <div className="flex flex-col sm:flex-row gap-3">
                  <button
                    onClick={handleCTA}
                    className="px-8 py-3.5 dna-gradient text-white rounded-xl text-base font-semibold hover:opacity-90 transition-opacity shadow-lg shadow-blue-500/20"
                  >
                    Start Designing — Free
                  </button>
                  <button
                    onClick={() => navigate('/pricing')}
                    className="px-8 py-3.5 border border-gray-200 bg-white rounded-xl text-base font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    View Plans
                  </button>
                </div>

                <p className="text-xs text-gray-400 mt-4">
                  5 designs/month free. Real NCBI sequences. Not AI-generated biology.
                </p>
              </div>

              {/* Right: product screenshot placeholder */}
              <div className="relative">
                <div className="bg-white rounded-2xl shadow-2xl shadow-gray-200/60 border border-gray-100 overflow-hidden">
                  {/* Placeholder for product screenshot — replace with real screenshot */}
                  <div className="bg-gray-900 px-4 py-2 flex items-center gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-400" />
                    <div className="w-3 h-3 rounded-full bg-yellow-400" />
                    <div className="w-3 h-3 rounded-full bg-green-400" />
                    <span className="text-xs text-gray-400 ml-2 font-mono">protoforge.ai/studio</span>
                  </div>
                  <div className="p-6 bg-gradient-to-b from-gray-50 to-white min-h-[320px] flex items-center justify-center">
                    {/* TODO: Replace with actual product screenshot */}
                    <div className="text-center">
                      <div className="w-20 h-20 mx-auto mb-4 rounded-full dna-gradient opacity-20" />
                      <p className="text-sm text-gray-400 font-medium">Product Screenshot</p>
                      <p className="text-xs text-gray-300 mt-1">Add screenshot of a real design output here</p>
                    </div>
                  </div>
                </div>
                {/* Floating badge */}
                <div className="absolute -bottom-3 -left-3 bg-white rounded-xl shadow-lg border px-4 py-2.5">
                  <p className="text-xs font-semibold text-gray-800">Real NCBI Sequences</p>
                  <p className="text-[10px] text-gray-500">Not AI-generated — verified accessions</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ─── Audience Bar ─── */}
        <section className="border-y border-gray-100 bg-white">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
            <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
              <p className="text-xs font-semibold uppercase tracking-widest text-gray-400">Built for</p>
              {AUDIENCES.map((a) => (
                <div key={a.name} className="text-center">
                  <p className="text-sm font-semibold text-gray-800">{a.name}</p>
                  <p className="text-xs text-gray-500">{a.count}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ─── How It Works ─── */}
        <RevealSection>
          <section className="max-w-6xl mx-auto px-4 sm:px-6 py-20 md:py-24">
            <div className="text-center mb-14">
              <h2 className="text-3xl font-bold mb-3">Three Steps to a Real Design</h2>
              <p className="text-gray-500 max-w-xl mx-auto">
                From plain English to lab-ready output in under a minute
              </p>
            </div>
            <div className="grid md:grid-cols-3 gap-8">
              {[
                {
                  step: '01',
                  title: 'Describe Your Goal',
                  desc: 'Type what you want in plain English. No jargon needed. "Design a microbe that eats plastic" works perfectly.',
                },
                {
                  step: '02',
                  title: 'AI + Real Biology',
                  desc: 'Claude designs the gene circuit. NCBI provides real sequences. COBRApy simulates metabolic performance.',
                },
                {
                  step: '03',
                  title: 'Download & Build',
                  desc: 'Get plasmid maps, FASTA files, assembly plans, safety scores, and vendor links. Refine through conversation.',
                },
              ].map((item) => (
                <div key={item.step} className="relative p-6 rounded-2xl border border-gray-100 bg-white hover:shadow-lg hover:border-gray-200 transition-all">
                  <span className="text-5xl font-bold text-gray-100 absolute top-4 right-5">{item.step}</span>
                  <div className="relative">
                    <h3 className="font-semibold text-lg mb-2">{item.title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{item.desc}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        </RevealSection>

        {/* ─── Pipeline Features ─── */}
        <RevealSection>
          <section className="bg-gray-50/50 border-y border-gray-100">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-20 md:py-24">
              <div className="text-center mb-14">
                <h2 className="text-3xl font-bold mb-3">The Full Pipeline</h2>
                <p className="text-gray-500 max-w-xl mx-auto">
                  Every design goes through six verified stages — no shortcuts, no fake biology
                </p>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                {PIPELINE_STEPS.map((f) => (
                  <div key={f.title} className="p-5 bg-white rounded-xl border border-gray-100 hover:border-gray-200 hover:shadow-md transition-all group">
                    <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-3 group-hover:bg-blue-100 transition-colors">
                      {f.icon}
                    </div>
                    <h3 className="font-semibold mb-1.5">{f.title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </RevealSection>

        {/* ─── Example Prompts ─── */}
        <RevealSection>
          <section className="max-w-6xl mx-auto px-4 sm:px-6 py-20 md:py-24">
            <div className="text-center mb-14">
              <h2 className="text-3xl font-bold mb-3">Try an Example</h2>
              <p className="text-gray-500">Click any prompt to start designing</p>
            </div>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
              {EXAMPLES.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleTryExample(prompt)}
                  className="text-left p-4 bg-white border border-gray-100 rounded-xl hover:border-blue-300 hover:shadow-md transition-all group"
                >
                  <p className="text-sm text-gray-600 group-hover:text-blue-700 transition-colors leading-relaxed">
                    "{prompt}"
                  </p>
                </button>
              ))}
            </div>
          </section>
        </RevealSection>

        {/* ─── Stats ─── */}
        <RevealSection>
          <section className="border-y border-gray-100 bg-white">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-14">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
                {[
                  { value: '19', unit: 'Verified Genes', detail: 'in registry' },
                  { value: '$0', unit: 'Free Tier Cost', detail: 'per design' },
                  { value: '<60s', unit: 'Design Time', detail: 'full pipeline' },
                  { value: '6', unit: 'Pipeline Stages', detail: 'all automated' },
                ].map((s) => (
                  <div key={s.unit} className="text-center">
                    <p className="text-3xl md:text-4xl font-bold dna-gradient-text">{s.value}</p>
                    <p className="text-sm font-medium text-gray-800 mt-1">{s.unit}</p>
                    <p className="text-xs text-gray-400">{s.detail}</p>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </RevealSection>

        {/* ─── Final CTA ─── */}
        <section className="dna-gradient py-16 md:py-20">
          <div className="max-w-3xl mx-auto px-4 text-center text-white">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              The bioeconomy needs better tools
            </h2>
            <p className="text-lg opacity-90 mb-8 max-w-xl mx-auto">
              5 free designs per month. Real sequences from NCBI. Metabolic modeling from COBRApy.
              No credit card required.
            </p>
            <button
              onClick={handleCTA}
              className="px-10 py-4 bg-white text-gray-900 rounded-xl text-base font-semibold hover:bg-gray-100 transition-colors shadow-lg"
            >
              Start Designing — Free
            </button>
          </div>
        </section>

        {/* ─── Footer ─── */}
        <footer className="bg-gray-900 text-gray-400 py-12">
          <div className="max-w-6xl mx-auto px-4 sm:px-6">
            <div className="grid md:grid-cols-4 gap-8 mb-8">
              <div className="md:col-span-2">
                <h3 className="text-white font-bold text-lg mb-2">ProtoForge</h3>
                <p className="text-sm leading-relaxed max-w-sm">
                  AI-powered bioengineering design platform. Describe custom microbes,
                  enzymes, and genetic circuits in plain English. Get real gene circuits,
                  DNA sequences, and metabolic simulations.
                </p>
              </div>
              <div>
                <h4 className="text-white text-sm font-semibold mb-3">Product</h4>
                <ul className="space-y-2 text-sm">
                  <li><button onClick={handleCTA} className="hover:text-white transition-colors">Studio</button></li>
                  <li><button onClick={() => navigate('/pricing')} className="hover:text-white transition-colors">Pricing</button></li>
                </ul>
              </div>
              <div>
                <h4 className="text-white text-sm font-semibold mb-3">Legal</h4>
                <ul className="space-y-2 text-sm">
                  {/* TODO: Add routes for these pages */}
                  <li><span className="cursor-default">Privacy Policy</span></li>
                  <li><span className="cursor-default">Terms of Service</span></li>
                  <li><span className="cursor-default">Biosafety Notice</span></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-800 pt-6 flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-xs">
                EDUCATIONAL/EXPERIMENTAL ONLY — NOT LAB-READY WITHOUT EXPERT REVIEW.
                Designs are computational predictions. Lab implementation requires institutional biosafety review.
              </p>
              <p className="text-xs text-gray-500 shrink-0">
                &copy; {new Date().getFullYear()} ProtoForge
              </p>
            </div>
          </div>
        </footer>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
