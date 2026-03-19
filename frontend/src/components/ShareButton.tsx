import { useState } from 'react'
import { designs } from '@/lib/api'
import { toast } from './Toast'

interface Props {
  designId: string
  designName: string
  generationTime: number
}

export default function ShareButton({ designId, designName, generationTime }: Props) {
  const [published, setPublished] = useState(false)

  async function handlePublish() {
    try {
      const result = await designs.share(designId)
      setPublished(result.is_public)
      if (result.is_public) {
        toast('Design published to Explore gallery')
      } else {
        toast('Design removed from gallery', 'info')
      }
    } catch {
      toast('Could not publish design', 'error')
    }
  }

  async function handleCopyLink() {
    const url = `${window.location.origin}/explore`
    await navigator.clipboard.writeText(url)
    toast('Link copied to clipboard')
  }

  return (
    <div className="flex gap-2">
      <button
        onClick={handlePublish}
        className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
          published
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-cyan-500/30 hover:text-white'
        }`}
      >
        {published ? 'Published' : 'Publish'}
      </button>
      <button
        onClick={handleCopyLink}
        className="px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700 hover:border-cyan-500/30 hover:text-white transition-all"
      >
        Share Link
      </button>
    </div>
  )
}
