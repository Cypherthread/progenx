/**
 * Minimal UI sound effects using Web Audio API.
 * No external files needed — generates tones programmatically.
 * Sounds are subtle and short (< 100ms) to avoid annoyance.
 */

let audioCtx: AudioContext | null = null

function getCtx(): AudioContext {
  if (!audioCtx) {
    audioCtx = new AudioContext()
  }
  return audioCtx
}

function playTone(
  frequency: number,
  duration: number,
  volume: number = 0.08,
  type: OscillatorType = 'sine',
) {
  try {
    const ctx = getCtx()
    const osc = ctx.createOscillator()
    const gain = ctx.createGain()

    osc.type = type
    osc.frequency.setValueAtTime(frequency, ctx.currentTime)

    gain.gain.setValueAtTime(volume, ctx.currentTime)
    gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + duration)

    osc.connect(gain)
    gain.connect(ctx.destination)

    osc.start(ctx.currentTime)
    osc.stop(ctx.currentTime + duration)
  } catch {
    // Audio not supported — fail silently
  }
}

/** Soft click — nav links, buttons */
export function clickSound() {
  playTone(800, 0.06, 0.05, 'sine')
}

/** Positive confirmation — design complete, success */
export function successSound() {
  playTone(523, 0.08, 0.06, 'sine')   // C5
  setTimeout(() => playTone(659, 0.08, 0.06, 'sine'), 80)  // E5
  setTimeout(() => playTone(784, 0.12, 0.06, 'sine'), 160)  // G5
}

/** Welcome tone — page load (very subtle) */
export function welcomeSound() {
  playTone(440, 0.15, 0.03, 'sine')   // A4
  setTimeout(() => playTone(554, 0.15, 0.03, 'sine'), 120)  // C#5
  setTimeout(() => playTone(659, 0.2, 0.03, 'sine'), 240)   // E5
}

/** Error tone — soft descending */
export function errorSound() {
  playTone(440, 0.1, 0.04, 'triangle')
  setTimeout(() => playTone(349, 0.15, 0.04, 'triangle'), 100)
}

/** Hover tick — very subtle */
export function hoverSound() {
  playTone(1200, 0.03, 0.02, 'sine')
}

/**
 * Initialize audio context on first user interaction.
 * Browsers require user gesture before playing audio.
 */
export function initAudio() {
  const handler = () => {
    getCtx()
    document.removeEventListener('click', handler)
    document.removeEventListener('keydown', handler)
  }
  document.addEventListener('click', handler, { once: true })
  document.addEventListener('keydown', handler, { once: true })
}
