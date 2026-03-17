import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from '@/components/AuthModal'
import { billing } from '@/lib/api'

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    features: [
      '5 designs per month',
      '3 supported chassis (E. coli, P. putida, S. elongatus)',
      'Plasmid maps + FASTA + GenBank export',
      'Safety scoring + biosafety flags',
      'Powered by local AI',
      'Community support',
    ],
    cta: 'Start Free',
    highlighted: false,
    action: 'free',
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    features: [
      'Unlimited designs',
      'Claude Sonnet AI (best quality)',
      'LLM function validation on NCBI results',
      'Priority generation queue',
      'Design version history',
      'API access',
      'Export to GenBank format',
      'Email support',
    ],
    cta: 'Upgrade to Pro',
    highlighted: true,
    action: 'pro',
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    features: [
      'Everything in Pro',
      'Team workspaces',
      'SSO / SAML',
      'Private gene registries',
      'Custom safety rules',
      'On-prem deployment',
      'Dedicated support',
    ],
    cta: 'Contact Us',
    highlighted: false,
    action: 'enterprise',
  },
]

export default function Pricing() {
  const navigate = useNavigate()
  const user = useAuth((s) => s.user)
  const [showAuth, setShowAuth] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleUpgrade() {
    if (!user) {
      setShowAuth(true)
      return
    }
    if (user.tier === 'pro') {
      // Already pro — open portal to manage subscription
      try {
        setLoading(true)
        const { portal_url } = await billing.portal()
        window.location.href = portal_url
      } catch (e: any) {
        alert(e.message || 'Failed to open billing portal')
      } finally {
        setLoading(false)
      }
      return
    }
    try {
      setLoading(true)
      const { checkout_url } = await billing.checkout()
      window.location.href = checkout_url
    } catch (e: any) {
      alert(e.message || 'Stripe not configured yet. Coming soon!')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Helmet>
        <title>Progenx Pricing — Free & Pro Plans for Synthetic Biology Design</title>
        <meta name="description" content="Progenx pricing: Free tier with 5 designs/month, Pro at $29/month with unlimited AI-powered gene circuit design, NCBI validation, and metabolic modeling. No credit card for free tier." />
        <link rel="canonical" href="https://progenx.ai/pricing" />
      </Helmet>
      <div className="max-w-5xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-3">Simple, transparent pricing</h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Start designing custom organisms for free. Upgrade when you need more power.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-xl p-6 bg-gray-900/30 ${
                plan.highlighted
                  ? 'border-2 border-cyan-500/50 shadow-lg shadow-cyan-500/10 relative'
                  : 'border border-gray-800'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-cyan-600 text-white text-xs font-medium rounded-full">
                  Most Popular
                </div>
              )}
              <h3 className="font-semibold text-lg">{plan.name}</h3>
              <div className="mt-2 mb-6">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className="text-muted-foreground text-sm">{plan.period}</span>
              </div>
              <ul className="space-y-2.5 mb-8">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2 text-sm">
                    <svg className="w-4 h-4 text-primary mt-0.5 shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    {f}
                  </li>
                ))}
              </ul>
              <button
                onClick={() => {
                  if (plan.action === 'free') {
                    user ? navigate('/studio') : setShowAuth(true)
                  } else if (plan.action === 'pro') {
                    handleUpgrade()
                  }
                  // enterprise = no action yet
                }}
                disabled={plan.action === 'enterprise' || loading}
                className={`w-full py-2.5 rounded-md text-sm font-medium transition-all ${
                  plan.highlighted
                    ? 'bg-cyan-600 text-white hover:opacity-90 disabled:opacity-50'
                    : 'border border-gray-700 text-gray-300 hover:bg-gray-800 disabled:opacity-50'
                }`}
              >
                {loading && plan.action === 'pro' ? 'Loading...' : plan.cta}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <p className="text-xs text-muted-foreground max-w-2xl mx-auto">
            Free tier uses Ollama (local AI) for gene circuit design. Pro tier uses Claude Sonnet
            for higher quality outputs and includes LLM-based NCBI function validation.
            All tiers include real NCBI sequences, COBRApy FBA, and safety scoring.
          </p>
        </div>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
