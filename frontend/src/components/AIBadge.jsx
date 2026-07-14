import { Sparkles } from 'lucide-react'

export default function AIBadge() {
  return (
    <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-accent/10 border border-accent/20 text-[10px] font-medium text-accent tracking-wide uppercase">
      <Sparkles className="w-3 h-3" />
      AI Enhanced ✓
    </div>
  )
}
