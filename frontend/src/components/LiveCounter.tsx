import { useState, useEffect } from 'react'

interface CounterProps {
  end: number
  duration?: number
  prefix?: string
  suffix?: string
  label: string
  sublabel?: string
}

/**
 * Animated counter that counts up from 0 to target value.
 * Triggers when element scrolls into view.
 */
export function AnimatedCounter({ end, duration = 2000, prefix = '', suffix = '', label, sublabel }: CounterProps) {
  const [count, setCount] = useState(0)
  const [started, setStarted] = useState(false)

  useEffect(() => {
    if (!started) return

    const startTime = Date.now()
    const timer = setInterval(() => {
      const elapsed = Date.now() - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease-out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setCount(Math.floor(eased * end))
      if (progress >= 1) clearInterval(timer)
    }, 16)

    return () => clearInterval(timer)
  }, [started, end, duration])

  return (
    <div
      className="text-center"
      ref={(el) => {
        if (!el || started) return
        const obs = new IntersectionObserver(([e]) => {
          if (e.isIntersecting) { setStarted(true); obs.disconnect() }
        }, { threshold: 0.5 })
        obs.observe(el)
      }}
    >
      <p className="text-3xl md:text-4xl font-bold progenx-gradient-text tabular-nums">
        {prefix}{count.toLocaleString()}{suffix}
      </p>
      <p className="text-sm font-medium text-gray-300 mt-1">{label}</p>
      {sublabel && <p className="text-xs text-gray-600">{sublabel}</p>}
    </div>
  )
}

/**
 * Simulated "live" ticker that slowly increments.
 * Creates the impression of real-time platform activity.
 * Starts from a base number and ticks up by 1 every few seconds.
 */
export function LiveTicker({ base, label, suffix = '' }: { base: number; label: string; suffix?: string }) {
  const [value, setValue] = useState(base)

  useEffect(() => {
    const interval = setInterval(() => {
      setValue((v) => v + 1)
    }, 3000 + Math.random() * 5000) // tick every 3-8 seconds
    return () => clearInterval(interval)
  }, [])

  return (
    <div className="flex items-center gap-2">
      <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse" />
      <span className="text-sm text-gray-300 tabular-nums">
        <span className="font-semibold text-white">{value.toLocaleString()}{suffix}</span>{' '}
        <span className="text-gray-500">{label}</span>
      </span>
    </div>
  )
}
