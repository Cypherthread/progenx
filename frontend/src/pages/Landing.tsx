import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'
import { useState, useEffect, useRef } from 'react'
import AuthModal from '@/components/AuthModal'
import { AnimatedCounter, LiveStat } from '@/components/LiveCounter'
import { stats as statsApi } from '@/lib/api'
import { useAnalytics, track } from '@/hooks/useAnalytics'
import { openCookieSettings } from '@/components/CookieConsent'

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
    desc: 'AI selects verified genes from NCBI GenBank. Real proteins, real accessions, no hallucinated biology.',
  },
  {
    title: 'Codon Optimization',
    desc: 'Sequences tuned for your chassis organism. E. coli, P. putida, or S. elongatus codon tables built in.',
  },
  {
    title: 'Metabolic Modeling',
    desc: 'COBRApy flux balance analysis with genome-scale models predicts growth rates, yields, and metabolic burden.',
  },
  {
    title: 'Construct Maps',
    desc: 'Circular plasmid maps with real bp positions: genes, promoters, terminators, ori, markers, kill switches.',
  },
  {
    title: 'Safety Scoring',
    desc: 'Dual-use screening, pathogen detection, resistance marker flags. Every design gets a biosafety assessment.',
  },
  {
    title: 'Assembly Plans',
    desc: 'Golden Gate or Gibson assembly with primer design, Tm calculation, ori selection, and kill switch.',
  },
]

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
  useAnalytics('landing')
  const navigate = useNavigate()
  const user = useAuth((s) => s.user)
  const [showAuth, setShowAuth] = useState(false)
  const [liveStats, setLiveStats] = useState({ users: 0, designs: 0 })

  useEffect(() => {
    statsApi.get().then(setLiveStats).catch(() => {})
  }, [])

  function handleTryExample(prompt: string) {
    track('click', { page: 'landing', element: 'example_prompt', value: prompt.slice(0, 60) })
    if (!user) { setShowAuth(true); return }
    navigate('/studio', { state: { prompt } })
  }

  function handleCTA() {
    track('click', { page: 'landing', element: 'cta_start_designing' })
    track('funnel_step', { page: 'landing', value: 'cta_click' })
    if (user) navigate('/studio')
    else setShowAuth(true)
  }

  return (
    <>
      <Helmet>
        <title>Progenx | AI Bioengineering Design Tool | Design Microbes in Plain English</title>
        <meta name="description" content="Design custom gene circuits, plasmid maps, and DNA sequences with AI. Real NCBI sequences, COBRApy metabolic modeling, safety scoring. Free for students and iGEM teams. No PhD required." />
        <link rel="canonical" href="https://progenx.ai" />
      </Helmet>
      <div className="flex flex-col">
        {/* ─── Hero (Dark) ─── */}
        <section className="relative overflow-hidden bg-[#080C14] min-h-[90vh] flex items-center">
          {/* Background DNA image */}
          <div className="absolute inset-0">
            <img
              src="/images/hero-dna.png"
              alt="Progenx AI bioengineering design platform. Glowing DNA helix visualization"
              className="w-full h-full object-cover opacity-40"
            />
            <div className="absolute inset-0 bg-gradient-to-b from-[#080C14]/60 via-transparent to-[#080C14]" />
          </div>
          {/* Floating particles */}
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {Array.from({ length: 20 }).map((_, i) => (
              <div
                key={i}
                className="particle"
                style={{
                  left: `${Math.random() * 100}%`,
                  bottom: `-${Math.random() * 20}%`,
                  animationDuration: `${8 + Math.random() * 12}s`,
                  animationDelay: `${Math.random() * 10}s`,
                  width: `${1 + Math.random() * 3}px`,
                  height: `${1 + Math.random() * 3}px`,
                }}
              />
            ))}
          </div>

          <div className="relative max-w-6xl mx-auto px-4 sm:px-6 py-20 sm:py-28 lg:py-36">
            <div className="max-w-3xl">
              <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-cyan-500/10 border border-cyan-500/20 rounded-full mb-8">
                <span className="w-1.5 h-1.5 bg-cyan-400 rounded-full animate-pulse" />
                <span className="text-xs font-medium text-cyan-300">Free to use, no credit card</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-7xl font-bold leading-[1.05] mb-6 text-white" style={{ letterSpacing: '-0.02em' }}>
                Design Microbes{' '}
                <span className="progenx-gradient-text">in Plain English</span>
              </h1>

              <p className="text-base sm:text-lg lg:text-xl text-gray-400 leading-relaxed mb-10 max-w-2xl">
                Stop spending weeks on NCBI searches, manual circuit sketches, and
                guesswork assembly plans. Describe your organism in one sentence.
                get verified gene circuits, real DNA sequences, metabolic simulations,
                and safety scores back in under a minute.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleCTA}
                  className="cta-glow px-8 py-4 progenx-gradient text-white rounded-xl text-base font-semibold hover:opacity-90 transition-all duration-200 shadow-lg shadow-cyan-500/25"
                >
                  Start Designing Free
                </button>
                <button
                  onClick={() => navigate('/pricing')}
                  className="px-8 py-4 border border-gray-700 rounded-xl text-base font-medium text-gray-400 hover:text-gray-200 hover:border-gray-500 transition-all duration-200"
                >
                  View Plans
                </button>
              </div>

              <p className="text-xs text-gray-600 mt-6">
                5 designs/month free. 26 verified gene accessions from NCBI. 3 chassis with genome-scale FBA models.
                Computational predictions. Lab validation required.
              </p>
            </div>
          </div>
        </section>

        {/* ─── Gradient divider ─── */}
        <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />

        {/* ─── Audience Bar ─── */}
        <section className="bg-[#0B1120] border-b border-gray-800/50">
          <div className="max-w-6xl mx-auto px-4 sm:px-6 py-6">
            <div className="flex flex-wrap items-center justify-center gap-8 md:gap-12">
              <p className="text-xs font-semibold uppercase tracking-widest text-gray-600">Built for</p>
              {[
                { name: 'iGEM Teams', count: '10,000+ participants/year' },
                { name: 'Climate Founders', count: 'Bio-based solutions' },
                { name: 'Biohackers', count: '100+ community labs' },
                { name: 'University Labs', count: '500+ programs' },
              ].map((a) => (
                <div key={a.name} className="text-center">
                  <p className="text-sm font-semibold text-gray-200">{a.name}</p>
                  <p className="text-xs text-gray-500">{a.count}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#0B1120] to-[#0B1120]" />

        {/* ─── How It Works ─── */}
        <RevealSection>
          <section className="bg-[#0B1120] py-16 sm:py-24">
            <div className="max-w-6xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-3 text-white">Three Steps to a Real Design</h2>
                <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto">From plain English to lab-ready output in under a minute</p>
              </div>
              <div className="grid md:grid-cols-3 gap-6">
                {[
                  { step: '01', title: 'Describe Your Goal', desc: 'Type what you want in plain English. No jargon needed. "Design a microbe that eats plastic" works perfectly.' },
                  { step: '02', title: 'AI + Real Biology', desc: 'Claude designs the gene circuit. NCBI provides real sequences. COBRApy simulates metabolic performance.' },
                  { step: '03', title: 'Download & Build', desc: 'Get plasmid maps, FASTA + GenBank files, assembly plans with primers, safety scores, and vendor links.' },
                ].map((item) => (
                  <div key={item.step} className="relative p-6 rounded-2xl border border-gray-800 bg-gray-900/50 hover:border-cyan-900/50 transition-all duration-300 will-change-transform hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-500/5">
                    <span className="text-5xl font-bold text-gray-800/50 absolute top-4 right-5">{item.step}</span>
                    <div className="relative">
                      <h3 className="font-semibold text-lg mb-2 text-white">{item.title}</h3>
                      <p className="text-sm text-gray-400 leading-relaxed">{item.desc}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        </RevealSection>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#0B1120] to-[#080C14]" />

        {/* ─── Demo Video Section ─── */}
        <RevealSection>
          <section className="bg-[#080C14] py-16 sm:py-24">
            <div className="max-w-5xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-10">
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-3 text-white">See It in Action</h2>
                <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto">From a single sentence to a complete bioengineering design</p>
              </div>
              {/* Video placeholder — replace with real demo recording */}
              <div className="relative aspect-video rounded-2xl overflow-hidden border border-gray-800 bg-gray-900/50 group cursor-pointer"
                onClick={handleCTA}>
                <img src="/images/hero-dna.png" alt="Progenx DNA helix background" className="absolute inset-0 w-full h-full object-cover opacity-30 group-hover:opacity-40 transition-opacity" />
                <div className="absolute inset-0 bg-gradient-to-t from-[#080C14] via-transparent to-transparent" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="w-20 h-20 rounded-full bg-cyan-500/20 border-2 border-cyan-400/50 flex items-center justify-center group-hover:scale-110 group-hover:bg-cyan-500/30 transition-all">
                    <svg viewBox="0 0 24 24" fill="currentColor" className="w-8 h-8 text-cyan-300 ml-1">
                      <path d="M8 5v14l11-7z" />
                    </svg>
                  </div>
                </div>
                <div className="absolute bottom-6 left-6 right-6">
                  <p className="text-white font-semibold text-lg">Watch: "Design a plastic-eating microbe" in 60 seconds</p>
                  <p className="text-gray-400 text-sm mt-1">Full pipeline demo: gene circuit, NCBI sequences, FBA simulation, plasmid map</p>
                </div>
              </div>
            </div>
          </section>
        </RevealSection>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#080C14] to-[#080C14]" />

        {/* ─── Pipeline Features ─── */}
        <RevealSection>
          <section className="bg-[#080C14]">
            <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
              <div className="text-center mb-14">
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-3 text-white">The Full Pipeline</h2>
                <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto">Every design goes through six verified stages. No shortcuts, no fake biology</p>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {PIPELINE_STEPS.map((f, i) => (
                  <div key={f.title} className="p-5 bg-gray-900/30 rounded-xl border border-gray-800 border-l-2 border-l-cyan-500/40 hover:border-cyan-800/40 hover:border-l-cyan-400/60 hover:bg-gray-900/60 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-cyan-500/5 transition-all duration-300 will-change-transform group">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-cyan-500/20 to-cyan-600/10 text-cyan-400 flex items-center justify-center mb-3 text-sm font-bold group-hover:from-cyan-500/30 group-hover:to-cyan-600/20 transition-all duration-300 ring-1 ring-cyan-500/20">
                      {i + 1}
                    </div>
                    <h3 className="font-semibold mb-1.5 text-white">{f.title}</h3>
                    <p className="text-sm text-gray-500 leading-relaxed">{f.desc}</p>
                  </div>
                ))}
              </div>
            </div>
            <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
          </section>
        </RevealSection>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#080C14] to-[#0B1120]" />

        {/* ─── Example Prompts ─── */}
        <RevealSection>
          <section className="bg-[#0B1120] py-16 sm:py-24">
            <div className="max-w-6xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-14">
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-3 text-white">Try an Example</h2>
                <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto">Click any prompt to start designing</p>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {EXAMPLES.map((prompt) => (
                  <button
                    key={prompt}
                    onClick={() => handleTryExample(prompt)}
                    className="text-left p-4 bg-gray-900/30 border border-gray-800 rounded-xl hover:border-cyan-700/40 hover:bg-gray-900/60 transition-all duration-300 group flex items-start gap-3"
                  >
                    <p className="text-sm text-gray-400 group-hover:text-cyan-300 transition-colors duration-200 leading-relaxed flex-1">
                      "{prompt}"
                    </p>
                    <svg
                      viewBox="0 0 20 20"
                      fill="currentColor"
                      className="w-4 h-4 text-gray-700 group-hover:text-cyan-400 opacity-0 group-hover:opacity-100 translate-x-0 group-hover:translate-x-1 transition-all duration-200 mt-0.5 shrink-0"
                    >
                      <path fillRule="evenodd" d="M7.21 14.77a.75.75 0 01.02-1.06L11.168 10 7.23 6.29a.75.75 0 111.04-1.08l4.5 4.25a.75.75 0 010 1.08l-4.5 4.25a.75.75 0 01-1.06-.02z" clipRule="evenodd" />
                    </svg>
                  </button>
                ))}
              </div>
            </div>
          </section>
        </RevealSection>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#0B1120] to-[#080C14]" />

        {/* ─── Platform Stats (all real, all verifiable) ─── */}
        <RevealSection>
          <section className="bg-[#080C14]">
            <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-16 sm:py-24">
              {/* Live platform stats — real numbers from the database */}
              <div className="flex flex-wrap items-center justify-center gap-6 mb-12">
                <LiveStat value={liveStats.designs} label={liveStats.designs === 1 ? 'design generated' : 'designs generated'} />
                <LiveStat value={liveStats.users} label={liveStats.users === 1 ? 'researcher signed up' : 'researchers signed up'} />
              </div>
              {/* Verified facts — each number is traceable to source code */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[
                  { end: 26, label: 'Verified Genes', sublabel: 'curated NCBI accessions' },
                  { end: 56, label: 'Regression Tests', sublabel: 'passing on every deploy' },
                  { end: 6, label: 'Pipeline Stages', sublabel: 'automated end-to-end' },
                  { end: 3, label: 'Chassis Organisms', sublabel: 'with genome-scale models' },
                ].map((stat) => (
                  <div key={stat.label} className="backdrop-blur-sm bg-white/[0.02] border border-white/[0.05] rounded-xl p-5 transition-all duration-300 hover:bg-white/[0.04] hover:border-white/[0.08]">
                    <AnimatedCounter end={stat.end} label={stat.label} sublabel={stat.sublabel} />
                  </div>
                ))}
              </div>
            </div>
            <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/20 to-transparent" />
          </section>
        </RevealSection>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#080C14] to-[#0B1120]" />

        {/* ─── Final CTA ─── */}
        <section className="relative overflow-hidden bg-[#0B1120] py-16 sm:py-24">
          <div className="absolute inset-0 opacity-20">
            <img src="/images/hero-dna.png" alt="Progenx DNA helix background" className="w-full h-full object-cover" />
          </div>
          <div className="relative max-w-3xl mx-auto px-4 text-center">
            <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-4 text-white">
              The bioeconomy needs better tools
            </h2>
            <p className="text-base sm:text-lg text-gray-400 mb-10 max-w-xl mx-auto">
              5 free designs per month. Real sequences from NCBI. Metabolic modeling from COBRApy. No credit card required.
            </p>
            <button
              onClick={handleCTA}
              className="cta-glow px-10 py-4 progenx-gradient text-white rounded-xl text-base font-semibold hover:opacity-90 transition-all duration-200 shadow-lg shadow-cyan-500/25"
            >
              Start Designing Free
            </button>
          </div>
        </section>

        {/* ─── Gradient transition ─── */}
        <div className="h-16 sm:h-24 bg-gradient-to-b from-[#0B1120] to-[#0B1120]" />

        {/* ─── Contact ─── */}
        <RevealSection>
          <section id="contact" className="bg-[#0B1120] py-16 sm:py-24">
            <div className="max-w-2xl mx-auto px-4 sm:px-6">
              <div className="text-center mb-10">
                <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-3 text-white">Get in Touch</h2>
                <p className="text-base sm:text-lg text-gray-400 max-w-2xl mx-auto">Questions, partnerships, enterprise inquiries, or just say hi.</p>
              </div>
              <div className="grid sm:grid-cols-2 gap-8">
                {/* Direct contact */}
                <div className="space-y-4">
                  <div>
                    <p className="text-sm font-medium text-gray-300 mb-1">Email</p>
                    <a href="mailto:hello@progenx.ai" className="text-cyan-400 hover:text-cyan-300 text-sm transition-colors">
                      hello@progenx.ai
                    </a>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-300 mb-1">For enterprise</p>
                    <a href="mailto:enterprise@progenx.ai" className="text-cyan-400 hover:text-cyan-300 text-sm transition-colors">
                      enterprise@progenx.ai
                    </a>
                  </div>
                  <div>
                    <p className="text-sm font-medium text-gray-300 mb-1">Response time</p>
                    <p className="text-sm text-gray-500">Usually within 24 hours</p>
                  </div>
                </div>
                {/* Quick contact form */}
                <form
                  onSubmit={(e) => {
                    e.preventDefault()
                    const form = e.target as HTMLFormElement
                    const data = new FormData(form)
                    const subject = encodeURIComponent(`Progenx: ${data.get('subject')}`)
                    const body = encodeURIComponent(`${data.get('message')}\n\nFrom: ${data.get('email')}`)
                    window.location.href = `mailto:hello@progenx.ai?subject=${subject}&body=${body}`
                    form.reset()
                  }}
                  className="space-y-3"
                >
                  <input
                    name="email"
                    type="email"
                    required
                    placeholder="Your email"
                    className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                  />
                  <input
                    name="subject"
                    type="text"
                    required
                    placeholder="Subject"
                    className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50"
                  />
                  <textarea
                    name="message"
                    required
                    rows={4}
                    placeholder="Your message"
                    className="w-full px-4 py-2.5 bg-gray-900/50 border border-gray-700 rounded-lg text-sm text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500/50 resize-none"
                  />
                  <button
                    type="submit"
                    className="w-full py-2.5 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-sm font-medium transition-all duration-200"
                  >
                    Send Message
                  </button>
                </form>
              </div>
            </div>
          </section>
        </RevealSection>

        {/* ─── Footer ─── */}
        <div className="h-px bg-gradient-to-r from-transparent via-cyan-500/15 to-transparent" />
        <footer className="bg-[#060A12] text-gray-500 py-16 sm:py-20">
          <div className="max-w-6xl mx-auto px-4 sm:px-6">
            <div className="grid md:grid-cols-4 gap-10 mb-12">
              <div className="md:col-span-2">
                <img src="/images/logo-progenx.png" alt="Progenx" className="h-8 mb-4" />
                <p className="text-sm leading-relaxed max-w-sm text-gray-600">
                  AI-powered bioengineering design platform. Describe custom microbes,
                  enzymes, and genetic circuits in plain English. Get real gene circuits,
                  DNA sequences, and metabolic simulations.
                </p>
              </div>
              <div>
                <h4 className="text-gray-300 text-sm font-semibold mb-4">Product</h4>
                <ul className="space-y-2.5 text-sm">
                  <li><button onClick={handleCTA} className="hover:text-cyan-400 transition-all duration-200">Studio</button></li>
                  <li><button onClick={() => navigate('/pricing')} className="hover:text-cyan-400 transition-all duration-200">Pricing</button></li>
                </ul>
              </div>
              <div>
                <h4 className="text-gray-300 text-sm font-semibold mb-4">Company</h4>
                <ul className="space-y-2.5 text-sm">
                  <li><a href="#contact" className="hover:text-cyan-400 transition-all duration-200">Contact</a></li>
                  <li><button onClick={() => navigate('/terms')} className="hover:text-cyan-400 transition-all duration-200">Terms of Service</button></li>
                  <li><button onClick={() => navigate('/privacy')} className="hover:text-cyan-400 transition-all duration-200">Privacy Policy</button></li>
                  <li><button onClick={openCookieSettings} className="hover:text-cyan-400 transition-all duration-200">Cookie Settings</button></li>
                </ul>
              </div>
            </div>
            <div className="border-t border-gray-800/50 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
              <p className="text-xs text-gray-700/70 leading-relaxed max-w-lg">
                EDUCATIONAL/EXPERIMENTAL ONLY. NOT LAB-READY WITHOUT EXPERT REVIEW.
                Designs are computational predictions. Lab implementation requires institutional biosafety review.
              </p>
              <p className="text-xs text-gray-700/70 shrink-0">
                &copy; {new Date().getFullYear()} Progenx
              </p>
            </div>
          </div>
        </footer>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
