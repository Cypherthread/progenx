import { useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'
import { useState } from 'react'
import AuthModal from '@/components/AuthModal'

const PLANS = [
  {
    name: 'Free',
    price: '$0',
    period: 'forever',
    features: [
      '5 designs per month',
      'All organism types',
      'Interactive plasmid maps',
      'FASTA download',
      'Safety scoring',
      'Daily challenges',
    ],
    cta: 'Start Free',
    highlighted: false,
  },
  {
    name: 'Pro',
    price: '$29',
    period: '/month',
    features: [
      'Unlimited designs',
      'Priority generation (faster)',
      'Advanced Evo 2 parameters',
      'Batch design generation',
      'Export to GenBank format',
      'Vendor quote integration',
      'Design version history',
      'API access',
    ],
    cta: 'Coming Soon',
    highlighted: true,
  },
  {
    name: 'Team',
    price: '$99',
    period: '/month',
    features: [
      'Everything in Pro',
      '5 team members',
      'Shared design library',
      'Custom safety rules',
      'BLAST integration',
      'Priority support',
      'Custom model fine-tuning',
    ],
    cta: 'Contact Us',
    highlighted: false,
  },
]

export default function Pricing() {
  const navigate = useNavigate()
  const user = useAuth((s) => s.user)
  const [showAuth, setShowAuth] = useState(false)

  return (
    <>
      <div className="max-w-5xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold mb-3">Simple, transparent pricing</h1>
          <p className="text-muted-foreground max-w-xl mx-auto">
            Start designing custom organisms for free. Upgrade when you need more.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {PLANS.map((plan) => (
            <div
              key={plan.name}
              className={`rounded-xl p-6 ${
                plan.highlighted
                  ? 'border-2 border-primary shadow-lg relative'
                  : 'border'
              }`}
            >
              {plan.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-0.5 bg-primary text-white text-xs font-medium rounded-full">
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
                  if (plan.name === 'Free') {
                    user ? navigate('/studio') : setShowAuth(true)
                  }
                }}
                disabled={plan.name !== 'Free'}
                className={`w-full py-2.5 rounded-md text-sm font-medium transition-all ${
                  plan.highlighted
                    ? 'bg-primary text-white hover:opacity-90 disabled:opacity-50'
                    : 'border hover:bg-secondary disabled:opacity-50'
                }`}
              >
                {plan.cta}
              </button>
            </div>
          ))}
        </div>

        <div className="mt-16 text-center">
          <h2 className="text-xl font-semibold mb-4">Open Core Model</h2>
          <p className="text-sm text-muted-foreground max-w-2xl mx-auto">
            ProtoForge is open-source under MIT license. The core design engine, UI, and
            biology integrations are free to use, modify, and deploy. The proprietary safety
            screening layer and Evo 2 fine-tuned models are available exclusively to Pro and
            Team subscribers.
          </p>
        </div>
      </div>

      {showAuth && <AuthModal onClose={() => setShowAuth(false)} />}
    </>
  )
}
