import { CheckCircle2, FileText, CalendarClock } from 'lucide-react'

export default function ToolResultCard({ result }) {
  if (!result || !result.result || typeof result.result !== 'object') return null

  const data = result.result

  if (result.tool_name === 'log_interaction') {
    return (
      <div className="mt-4 bg-surface border border-border-subtle rounded-xl overflow-hidden shadow-sm">
        <div className="bg-accent/10 border-b border-border-subtle px-4 py-2.5 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-accent" />
          <span className="text-sm font-medium text-accent">Interaction Logged Successfully</span>
        </div>
        
        <div className="p-4 space-y-4">
          {/* Executive Summary */}
          {data.ai_executive_summary && (
            <div>
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5" /> Executive Summary
              </h4>
              <div className="space-y-3">
                {data.ai_executive_summary.key_outcomes && (
                  <div>
                    <span className="text-xs font-medium text-success block mb-1">Key Outcomes</span>
                    <ul className="text-sm text-foreground space-y-1 list-disc pl-4">
                      {data.ai_executive_summary.key_outcomes.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                )}
                {data.ai_executive_summary.next_actions && (
                  <div>
                    <span className="text-xs font-medium text-accent block mb-1">Next Actions</span>
                    <ul className="text-sm text-foreground space-y-1 list-disc pl-4">
                      {data.ai_executive_summary.next_actions.map((item, i) => <li key={i}>{item}</li>)}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Follow-ups */}
          {data.suggested_follow_ups && data.suggested_follow_ups.length > 0 && (
            <div className="pt-3 border-t border-border-subtle">
              <h4 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 flex items-center gap-1.5">
                <CalendarClock className="w-3.5 h-3.5" /> Scheduled Follow-ups
              </h4>
              <div className="space-y-2">
                {data.suggested_follow_ups.map((fu, i) => (
                  <div key={i} className="flex justify-between items-center text-sm bg-background border border-border rounded-lg p-2.5">
                    <span>{fu.action}</span>
                    <span className="text-xs text-muted-foreground bg-surface px-2 py-1 rounded">
                      {new Date(fu.due_date).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    )
  }

  return null // Render other tool results differently or not at all inline
}
