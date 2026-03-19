import { useState } from 'react'
import { designs } from '@/lib/api'
import { toast } from './Toast'
import { track } from '@/hooks/useAnalytics'

interface Props {
  designId: string
  designName: string
  isPublic: boolean
}

export default function ShareButton({ designId, designName, isPublic: initialPublic }: Props) {
  const [published, setPublished] = useState(initialPublic)

  async function handlePublish() {
    // Confirm before unpublishing
    if (published) {
      if (!confirm('Remove this design from the public gallery?')) return
    }
    try {
      const result = await designs.share(designId)
      setPublished(result.is_public)
      if (result.is_public) {
        track('funnel_step', { page: 'studio', value: 'design_shared' })
        track('feature_use', { page: 'studio', element: 'publish_design' })
        toast('Design published to Explore gallery')
      } else {
        toast('Design removed from gallery', 'info')
      }
    } catch {
      toast('Could not update design visibility', 'error')
    }
  }

  async function handleCopyLink() {
    const url = `${window.location.origin}/explore?design=${designId}`
    try {
      await navigator.clipboard.writeText(url)
      toast('Link copied to clipboard')
    } catch {
      toast('Could not copy link', 'error')
    }
  }

  return (
    <div className="flex gap-2">
      <button
        onClick={handlePublish}
        className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
          published
            ? 'bg-green-500/20 text-green-400 border border-green-500/30'
            : 'bg-gray-800 text-gray-400 border border-gray-700 hover:border-cyan-500/30 hover:text-white'
        }`}
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3 h-3">
          {published
            ? <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z M12 9a3 3 0 100 6 3 3 0 000-6z" strokeLinecap="round" />
            : <path d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" strokeLinecap="round" />
          }
        </svg>
        {published ? 'Published' : 'Publish'}
      </button>
      {published && (
        <button
          onClick={handleCopyLink}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium bg-gray-800 text-gray-400 border border-gray-700 hover:border-cyan-500/30 hover:text-white transition-all"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="w-3 h-3">
            <path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" strokeLinecap="round" />
            <path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" strokeLinecap="round" />
          </svg>
          Copy Link
        </button>
      )}
    </div>
  )
}
