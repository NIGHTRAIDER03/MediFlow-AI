import { motion } from 'framer-motion'

export default function StatCard({ title, value, icon: Icon, trend, trendValue, alert, colorClass }) {
  return (
    <div className="glass-panel p-5 rounded-xl border border-border relative overflow-hidden group">
      <div className="absolute right-0 top-0 w-24 h-24 bg-gradient-to-br from-accent/10 to-transparent rounded-bl-full opacity-0 group-hover:opacity-100 transition-opacity" />
      
      <div className="flex justify-between items-start mb-4 relative z-10">
        <p className="text-sm font-medium text-muted-foreground">{title}</p>
        <div className="p-2 rounded-lg bg-surface border border-border-subtle">
          <Icon className="w-4 h-4 text-primary" />
        </div>
      </div>
      
      <div className="flex items-baseline gap-2 relative z-10">
        <h3 className={`text-3xl font-semibold tracking-tight ${colorClass || 'text-primary'}`}>
          {value}
        </h3>
        
        {trend && trendValue && (
          <span className={`text-xs font-medium px-1.5 py-0.5 rounded-md flex items-center ${
            trend === 'up' ? 'bg-success/10 text-success' : 'bg-danger/10 text-danger'
          }`}>
            {trend === 'up' ? '↑' : '↓'} {trendValue}
          </span>
        )}
      </div>

      {alert && (
        <div className="mt-3 text-xs font-medium text-danger flex items-center bg-danger/10 w-fit px-2 py-1 rounded-md">
          <span className="w-1.5 h-1.5 rounded-full bg-danger mr-1.5 animate-pulse" />
          {alert}
        </div>
      )}
    </div>
  )
}
