import { useState } from 'react'
import { designs } from '@/lib/api'

interface Props {
  designId: string
  designName: string
  generationTime: number
}

export default function ShareButton({ designId, designName, generationTime }: Props) {
  const [shared, setShared] = useState(false)
  const [copying, setCopying] = useState(false)

  async function handleShare() {
    try {
      await designs.share(designId)

      const shareText = `I just designed "${designName}" in ${Math.round(generationTime)} seconds with Progenx! 🧬🔬\n\nDesign microbes, enzymes & genetic circuits in plain English. No PhD required.\n\n#Progenx #SynBio #BioEngineering`

      if (navigator.share) {
        await navigator.share({
          title: `Progenx: ${designName}`,
          text: shareText,
        })
      } else {
        await navigator.clipboard.writeText(shareText)
        setCopying(true)
        setTimeout(() => setCopying(false), 2000)
      }
      setShared(true)
    } catch {
      // user cancelled share
    }
  }

  return (
    <button
      onClick={handleShare}
      className={`px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
        shared
          ? 'bg-green-100 text-green-700'
          : 'bg-accent text-white hover:opacity-90'
      }`}
    >
      {copying ? 'Copied!' : shared ? 'Shared!' : 'Share Design'}
    </button>
  )
}
