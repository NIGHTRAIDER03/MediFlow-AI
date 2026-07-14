import { CheckCircle2, Circle } from 'lucide-react'
import { useDispatch } from 'react-redux'
import api from '../api/axios'
import { fetchDashboard } from '../store/dashboardSlice'
import toast from 'react-hot-toast'

export default function SmartFollowUpList({ item }) {
  const dispatch = useDispatch()
  
  const handleComplete = async () => {
    try {
      await api.put(`/follow-ups/${item.id}`, { status: 'completed' })
      toast.success('Follow-up marked as completed')
      dispatch(fetchDashboard())
    } catch (error) {
      toast.error('Failed to complete follow-up')
    }
  }

  const priorityColors = {
    high: 'bg-danger/20 text-danger border-danger/20',
    medium: 'bg-warning/20 text-warning border-warning/20',
    low: 'bg-surface text-muted-foreground border-border',
  }

  const isOverdue = item.status === 'overdue'

  return (
    <div className="p-4 hover:bg-hover transition-colors group">
      <div className="flex gap-3">
        <button 
          onClick={handleComplete}
          className="mt-0.5 text-border hover:text-success transition-colors shrink-0"
        >
          <Circle className="w-5 h-5 group-hover:hidden" />
          <CheckCircle2 className="w-5 h-5 hidden group-hover:block" />
        </button>
        
        <div className="flex-1 min-w-0">
          <div className="flex justify-between items-start mb-1">
            <p className="font-medium truncate pr-2">{item.hcp_name}</p>
            <div className="flex items-center gap-2 shrink-0">
              {isOverdue && (
                <span className="text-[10px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded bg-danger/10 text-danger">
                  Overdue
                </span>
              )}
              <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full border ${priorityColors[item.priority]}`}>
                {item.priority}
              </span>
            </div>
          </div>
          
          <p className="text-sm text-foreground mb-1">{item.action}</p>
          <p className="text-xs text-muted-foreground">
            Due {new Date(item.due_date).toLocaleDateString()}
          </p>

          {/* AI Suggested Actions */}
          {item.ai_suggested_actions && item.ai_suggested_actions.length > 0 && (
            <div className="mt-3 bg-surface border border-border-subtle rounded-lg p-2.5">
              <div className="flex items-center gap-1.5 mb-2">
                <span className="text-xs font-medium text-accent">AI Suggested Actions</span>
              </div>
              <ul className="space-y-1.5">
                {item.ai_suggested_actions.map((action, i) => (
                  <li key={i} className="text-xs text-muted-foreground flex items-start gap-2">
                    <span className="text-accent/50 mt-0.5">✦</span>
                    <span className="leading-tight">{action}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
