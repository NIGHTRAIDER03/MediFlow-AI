import { useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchDashboard } from '../store/dashboardSlice'
import { Users, CheckCircle2, AlertCircle, CalendarClock } from 'lucide-react'
import { motion } from 'framer-motion'
import AIFocusCard from '../components/AIFocusCard'
import SmartFollowUpList from '../components/SmartFollowUpList'
import StatCard from '../components/StatCard'

export default function DashboardPage() {
  const dispatch = useDispatch()
  const { 
    stats, 
    aiFocus, 
    recentActivity, 
    upcomingFollowUps, 
    greeting,
    isLoading 
  } = useSelector(state => state.dashboard)

  useEffect(() => {
    dispatch(fetchDashboard())
  }, [dispatch])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="w-8 h-8 border-4 border-accent border-t-transparent rounded-full animate-spin"></div>
      </div>
    )
  }

  // Current date formatting
  const today = new Date()
  const dateOptions = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }
  const formattedDate = today.toLocaleDateString('en-US', dateOptions)

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  }

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  }

  return (
    <motion.div 
      variants={container}
      initial="hidden"
      animate="show"
      className="max-w-7xl mx-auto space-y-8"
    >
      {/* Header */}
      <div>
        <motion.h1 variants={item} className="text-3xl font-semibold tracking-tight text-primary">
          Good {today.getHours() < 12 ? 'morning' : 'afternoon'}, {greeting}.
        </motion.h1>
        <motion.p variants={item} className="text-muted-foreground mt-1">
          {formattedDate}
        </motion.p>
      </div>

      {/* Stats Grid */}
      <motion.div variants={item} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard 
          title="Today's Visits" 
          value={stats.todays_visits} 
          icon={Users} 
          trend="up" 
          trendValue="12%" 
        />
        <StatCard 
          title="Pending Follow-Ups" 
          value={stats.pending_follow_ups} 
          icon={CalendarClock}
          alert={stats.overdue_follow_ups > 0 ? `${stats.overdue_follow_ups} overdue` : null}
        />
        <StatCard 
          title="This Week" 
          value={stats.weeks_interactions} 
          icon={CheckCircle2} 
        />
        <StatCard 
          title="Avg Sentiment" 
          value={`${stats.avg_sentiment}%`} 
          icon={AlertCircle} 
          trend={stats.avg_sentiment >= 70 ? 'up' : 'down'}
          colorClass={stats.avg_sentiment >= 70 ? 'text-success' : 'text-warning'}
        />
      </motion.div>

      {/* AI Focus Section */}
      <motion.div variants={item} className="space-y-4">
        <div className="flex items-center gap-2">
          <span className="text-lg">⭐</span>
          <h2 className="text-xl font-medium">Today's AI Focus</h2>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {aiFocus.map((focus, index) => (
            <AIFocusCard key={index} data={focus} />
          ))}
          {aiFocus.length === 0 && (
            <div className="col-span-3 glass-panel p-6 rounded-xl flex items-center justify-center text-muted-foreground">
              No immediate focus items for today. You're all caught up!
            </div>
          )}
        </div>
      </motion.div>

      {/* Bottom Grid */}
      <motion.div variants={item} className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Recent Activity */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Recent Activity</h3>
          <div className="glass-panel rounded-xl border border-border overflow-hidden">
            {recentActivity.length > 0 ? (
              <div className="divide-y divide-border">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="p-4 hover:bg-hover transition-colors">
                    <div className="flex justify-between items-start mb-1">
                      <p className="font-medium">{activity.hcp_name}</p>
                      <span className="text-xs text-muted-foreground">
                        {new Date(activity.interaction_date).toLocaleDateString()}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <span className={`text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full ${
                        activity.sentiment === 'positive' ? 'bg-success/20 text-success' :
                        activity.sentiment === 'negative' ? 'bg-danger/20 text-danger' :
                        'bg-warning/20 text-warning'
                      }`}>
                        {activity.sentiment}
                      </span>
                      <span className="text-xs text-muted-foreground capitalize">{activity.interaction_type}</span>
                    </div>
                    <p className="text-sm text-muted-foreground line-clamp-2">{activity.ai_summary}</p>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                No recent activity. Log an interaction to get started.
              </div>
            )}
          </div>
        </div>

        {/* Upcoming Follow-ups */}
        <div className="space-y-4">
          <h3 className="text-lg font-medium">Upcoming Follow-Ups</h3>
          <div className="glass-panel rounded-xl border border-border overflow-hidden">
            {upcomingFollowUps.length > 0 ? (
              <div className="divide-y divide-border">
                {upcomingFollowUps.map((fu) => (
                  <SmartFollowUpList key={fu.id} item={fu} />
                ))}
              </div>
            ) : (
              <div className="p-8 text-center text-muted-foreground">
                No pending follow-ups.
              </div>
            )}
          </div>
        </div>

      </motion.div>
    </motion.div>
  )
}
