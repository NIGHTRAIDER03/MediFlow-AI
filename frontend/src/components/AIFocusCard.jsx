export default function AIFocusCard({ data }) {
  const { type, icon, title, description } = data

  const typeConfig = {
    priority: {
      bg: 'bg-accent/10',
      border: 'border-accent/20',
      iconBg: 'bg-accent/20',
      text: 'text-accent',
    },
    opportunity: {
      bg: 'bg-success/10',
      border: 'border-success/20',
      iconBg: 'bg-success/20',
      text: 'text-success',
    },
    warning: {
      bg: 'bg-warning/10',
      border: 'border-warning/20',
      iconBg: 'bg-warning/20',
      text: 'text-warning',
    }
  }

  const config = typeConfig[type] || typeConfig.priority

  return (
    <div className={`p-4 rounded-xl border ${config.bg} ${config.border} flex flex-col h-full`}>
      <div className="flex items-center gap-2 mb-3">
        <div className={`w-8 h-8 rounded-lg ${config.iconBg} flex items-center justify-center text-lg`}>
          {icon}
        </div>
        <h4 className="font-medium text-primary line-clamp-1">{title}</h4>
      </div>
      <p className="text-sm text-muted-foreground flex-1">
        {description}
      </p>
      
      {/* Footer indicator */}
      <div className="mt-4 pt-3 border-t border-border-subtle flex items-center text-xs text-muted-foreground">
        <span className="font-medium text-accent mr-1">AI Generated</span>
        · Insight
      </div>
    </div>
  )
}
