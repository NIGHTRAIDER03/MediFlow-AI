import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area
} from 'recharts'
import { Brain, TrendingUp, Users, Activity } from 'lucide-react'

// Mock Data for Analytics
const sentimentData = [
  { name: 'Mon', positive: 4, neutral: 2, negative: 0 },
  { name: 'Tue', positive: 3, neutral: 3, negative: 1 },
  { name: 'Wed', positive: 5, neutral: 1, negative: 0 },
  { name: 'Thu', positive: 2, neutral: 4, negative: 0 },
  { name: 'Fri', positive: 6, neutral: 2, negative: 0 },
]

const productData = [
  { name: 'Cardiolex', value: 45 },
  { name: 'NeuroPro', value: 30 },
  { name: 'OncoShield', value: 15 },
  { name: 'GlucoBal', value: 10 },
]

const relationshipTrend = [
  { month: 'Jan', score: 72 },
  { month: 'Feb', score: 75 },
  { month: 'Mar', score: 78 },
  { month: 'Apr', score: 76 },
  { month: 'May', score: 82 },
  { month: 'Jun', score: 85 },
]

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('week')

  return (
    <div className="max-w-7xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-primary">Territory Analytics</h1>
          <p className="text-sm text-muted-foreground mt-1">AI-driven insights across your HCP network.</p>
        </div>
        
        <div className="flex bg-surface border border-border rounded-lg p-1">
          {['week', 'month', 'quarter'].map(range => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-4 py-1.5 text-xs font-medium rounded-md transition-colors capitalize ${
                timeRange === range
                  ? 'bg-hover text-primary shadow-sm'
                  : 'text-muted-foreground hover:text-primary'
              }`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>

      {/* Top Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-panel p-5 rounded-xl border border-border">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-success/20 text-success rounded-lg">
              <TrendingUp className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-medium text-muted-foreground">Overall Sentiment</h3>
          </div>
          <div className="mt-4 flex items-end justify-between">
            <div>
              <p className="text-3xl font-semibold text-primary">82%</p>
              <p className="text-xs text-success mt-1">↑ +5% from last period</p>
            </div>
            <div className="text-right">
              <p className="text-xs text-muted-foreground">Positive: 65%</p>
              <p className="text-xs text-muted-foreground">Neutral: 25%</p>
              <p className="text-xs text-muted-foreground">Negative: 10%</p>
            </div>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-border bg-gradient-to-br from-accent/10 to-transparent">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-accent/20 text-accent rounded-lg">
              <Brain className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-medium text-accent">AI Next Best Action</h3>
          </div>
          <div className="mt-4">
            <p className="text-sm font-medium text-primary mb-1">Focus on Dr. Sarah Chen</p>
            <p className="text-xs text-muted-foreground line-clamp-2">
              Engagement score dropping. High probability of switching prescribing habits if not contacted this week with new trial data.
            </p>
            <button className="mt-3 text-xs font-medium text-accent hover:underline">
              View Strategy →
            </button>
          </div>
        </div>

        <div className="glass-panel p-5 rounded-xl border border-border">
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 bg-warning/20 text-warning rounded-lg">
              <Users className="w-4 h-4" />
            </div>
            <h3 className="text-sm font-medium text-muted-foreground">Network Health</h3>
          </div>
          <div className="mt-4 flex items-end justify-between">
            <div>
              <p className="text-3xl font-semibold text-primary">7.4/10</p>
              <p className="text-xs text-muted-foreground mt-1">Average Rel. Score</p>
            </div>
            <div className="h-12 w-24">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={relationshipTrend}>
                  <Line type="monotone" dataKey="score" stroke="#3B82F6" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Interaction Sentiment */}
        <div className="glass-panel p-6 rounded-xl border border-border">
          <h3 className="text-lg font-medium mb-6">Interaction Sentiment</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sentimentData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: '#18181B', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Bar dataKey="positive" stackId="a" fill="#22C55E" radius={[0, 0, 4, 4]} />
                <Bar dataKey="neutral" stackId="a" fill="#EAB308" />
                <Bar dataKey="negative" stackId="a" fill="#EF4444" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Product Share of Voice */}
        <div className="glass-panel p-6 rounded-xl border border-border">
          <h3 className="text-lg font-medium mb-6">Product Share of Voice</h3>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={productData} layout="vertical" margin={{ top: 0, right: 0, left: 10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                <XAxis type="number" stroke="rgba(255,255,255,0.3)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis dataKey="name" type="category" stroke="rgba(255,255,255,0.5)" fontSize={12} tickLine={false} axisLine={false} width={80} />
                <RechartsTooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                  contentStyle={{ backgroundColor: '#18181B', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                />
                <Bar dataKey="value" fill="#3B82F6" radius={[0, 4, 4, 0]} barSize={24} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  )
}
