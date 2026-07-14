import { CheckCircle2, AlertTriangle, ArrowRight } from 'lucide-react'

export default function ExecutiveSummary({ data, fallbackText }) {
  if (!data) {
    return (
      <p className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
        {fallbackText || "No summary available."}
      </p>
    )
  }

  const { key_outcomes, next_actions, risks } = data

  return (
    <div className="space-y-5">
      {/* Key Outcomes */}
      {key_outcomes && key_outcomes.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
            <CheckCircle2 className="w-3.5 h-3.5 text-success" /> Key Outcomes
          </h4>
          <ul className="space-y-1.5 pl-5 list-disc text-sm text-foreground marker:text-success/50">
            {key_outcomes.map((item, i) => (
              <li key={i} className="leading-snug">{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Next Actions */}
      {next_actions && next_actions.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
            <ArrowRight className="w-3.5 h-3.5 text-accent" /> Next Actions
          </h4>
          <ul className="space-y-1.5 pl-5 list-disc text-sm text-foreground marker:text-accent/50">
            {next_actions.map((item, i) => (
              <li key={i} className="leading-snug">{item}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Risks */}
      {risks && risks.length > 0 && (
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-2 flex items-center gap-1.5">
            <AlertTriangle className="w-3.5 h-3.5 text-warning" /> Risks & Concerns
          </h4>
          <ul className="space-y-1.5 pl-5 list-disc text-sm text-foreground marker:text-warning/50">
            {risks.map((item, i) => (
              <li key={i} className="leading-snug">{item}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
