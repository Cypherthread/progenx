import { useNavigate } from 'react-router-dom'
import { Helmet } from 'react-helmet-async'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from '@/components/AuthModal'
import { billing } from '@/lib/api'
import { toast } from '@/components/Toast'
import { useAnalytics, track } from '@/hooks/useAnalytics'

const SAFE_HOSTS = ['checkout.stripe.com', 'billing.stripe.com']
function isSafeUrl(url: string): boolean {
  try { return SAFE_HOSTS.some(h => new URL(url).hostname.endsWith(h)) }
  catch { return false }
}

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    description: 'Perfect for students and first-time users.',
    features: [
      '5 designs per month',
      '3 chassis organisms (E. coli, P. putida, S. elongatus)',
      'Plasmid maps + FASTA + GenBank export',
      'Safety scoring + biosafety flags',
      'Cloud AI (Groq)',
      'Community support',
    ],
    cta: 'Start Free',
    highlighted: false,
    action: 'free' as const,
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    description: 'For researchers and teams who need the best outputs.',
    features: [
      'Unlimited designs',
      'Claude Sonnet AI (best quality)',
      'LLM function validation on NCBI results',
      'Self-consistency checking (3x runs)',
      'Priority generation queue',
      'Design version history',
      'API access (programmatic)',
      'Email support',
    ],
    cta: 'Upgrade to Pro',
    highlighted: true,
    action: 'pro' as const,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'For organizations with custom compliance needs.',
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
    action: 'enterprise' as const,
  },
]

export default function Pricing() {
  useAnalytics('pricing')
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
      try {
        setLoading(true)
        const { portal_url } = await billing.portal()
        if (isSafeUrl(portal_url)) window.location.href = portal_url
        else toast('Invalid billing URL', 'error')
      } catch {
        toast('Billing portal not available yet', 'info')
      } finally {
        setLoading(false)
      }
      return
    }
    try {
      setLoading(true)
      const { checkout_url } = await billing.checkout()
      if (isSafeUrl(checkout_url)) window.location.href = checkout_url
      else toast('Invalid checkout URL', 'error')
    } catch {
      toast('Pro subscriptions coming soon', 'info')
    } finally {
      setLoading(false)
    }
  }

  function handleEnterprise() {
    window.location.href = 'mailto:hello@progenx.ai?subject=Enterprise%20Inquiry'
  }

  return (
    <>
      <Helmet>
        <title>Progenx Pricing | Free & Pro Plans for Synthetic Biology Design</title>
        <meta name="description" content="Progenx pricing: Free tier with 5 designs/month, Pro at $29/month with unlimited AI-powered gene circuit design, NCBI validation, and metabolic modeling. No credit card for free tier." />
        <link rel="canonical" href="https://progenx.ai/pricing" />
      </Helmet>
      <div className="max-w-5xl mx-auto px-4 py-16">
        <div className="text-center mb-14">
          <h1 className="text-3xl sm:text-4xl font-bold text-white mb-4">
            <span className="gradient-underline">Simple, transparent pricing</span>
          </h1>
          <p className="text-gray-400 max-w-xl mx-auto mt-4 leading-relaxed">
            Start designing custom organisms for free. Upgrade when you need more power.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 items-start">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-xl p-6 flex flex-col ${
                plan.highlighted
                  ? 'pro-card-border bg-[#0F1629] shadow-xl shadow-black/30 relative md:-mt-4 md:pb-8'
                  : plan.action === 'enterprise'
                    ? 'border-2 border-dashed border-gray-700/60 bg-gray-900/20 relative'
                    : 'border border-gray-800 bg-gray-900/30'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-gray-800 text-cyan-400 text-xs font-semibold rounded-full border border-cyan-500/30 badge-pulse">
                  Most Popular
                </div>
              )}
              {plan.action === 'enterprise' && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-gray-800 text-gray-400 text-[10px] font-medium rounded-full border border-gray-700">
                  Coming Soon
                </div>
              )}
              <h3 className={`font-semibold text-lg ${plan.highlighted ? 'text-white' : plan.action === 'enterprise' ? 'text-gray-300' : 'text-white'}`}>{plan.name}</h3>
              <p className="text-xs text-gray-500 mt-1">{plan.description}</p>
              <div className="mt-4 mb-6">
                {plan.action === 'pro' ? (
                  <>
                    <div className="flex items-baseline gap-2">
                      <span className="text-xs text-gray-500 line-through">$99</span>
                    </div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">{plan.price}</span>
                      <span className="text-gray-500 text-sm">/month</span>
                    </div>
                    <p className="text-[10px] text-gray-500 mt-1">Beta pricing — limited time</p>
                  </>
                ) : plan.action === 'enterprise' ? (
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl font-bold text-gray-300">{plan.price}</span>
                    <span className="text-gray-600 text-sm">{plan.period}</span>
                  </div>
                ) : (
                  <div className="flex items-baseline gap-1">
                    <span className="text-3xl sm:text-4xl font-bold text-white">{plan.price}</span>
                    <span className="text-gray-500 text-sm">{plan.period}</span>
                  </div>
                )}
              </div>
              <ul className="space-y-3 mb-8 flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2.5 text-sm text-gray-300 group/feature">
                    <svg className={`w-4 h-4 mt-0.5 shrink-0 ${plan.highlighted ? 'text-green-400' : plan.action === 'enterprise' ? 'text-gray-600' : 'text-gray-500'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                    </svg>
                    <span className={plan.action === 'enterprise' ? 'text-gray-500' : ''}>{f}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={() => {
                  if (plan.action === 'free') {
                    user ? navigate('/studio') : setShowAuth(true)
                  } else if (plan.action === 'pro') {
                    handleUpgrade()
                  } else {
                    handleEnterprise()
                  }
                }}
                disabled={loading && plan.action === 'pro'}
                className={`w-full py-3 rounded-lg text-sm font-semibold transition-all ${
                  plan.highlighted
                    ? 'bg-cyan-600 text-white hover:bg-cyan-500 disabled:opacity-50'
                    : plan.action === 'enterprise'
                      ? 'border border-dashed border-gray-700 text-gray-500 hover:bg-gray-800/50 hover:text-gray-300 hover:border-gray-600'
                      : 'border border-gray-700 text-gray-300 hover:bg-gray-800 disabled:opacity-50'
                }`}
              >
                {loading && plan.action === 'pro' ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none">
                      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" className="opacity-20" />
                      <path d="M12 2a10 10 0 0 1 10 10" stroke="currentColor" strokeWidth="3" strokeLinecap="round" />
                    </svg>
                    Loading...
                  </span>
                ) : user?.tier === 'pro' && plan.action === 'pro' ? 'Manage Subscription' : plan.cta}
              </button>
            </div>
          ))}
        </div>

        {/* Disclaimer as styled info card */}
        <div className="mt-16 max-w-2xl mx-auto">
          <div className="bg-gray-900/30 border border-gray-800/50 rounded-xl px-6 py-4 flex gap-3 items-start">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" className="w-5 h-5 text-gray-600 shrink-0 mt-0.5">
              <path d="M12 16v-4m0-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
            <p className="text-xs text-gray-500 leading-relaxed">
              Free tier uses Groq cloud AI for gene circuit design. Pro tier uses Claude Sonnet
              for higher quality outputs and includes LLM-based NCBI function validation.
              All tiers include real NCBI sequences, COBRApy FBA, and safety scoring.
              No credit card required for the free tier.
            </p>
          </div>
        </div>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
