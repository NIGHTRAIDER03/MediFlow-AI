import { useState, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { createInteraction } from '../store/interactionSlice'
import { fetchHCPs } from '../store/hcpSlice'
import { Calendar as CalendarIcon, Clock, MapPin, Pill, CheckCircle2, ChevronDown } from 'lucide-react'
import toast from 'react-hot-toast'
import ExecutiveSummary from './ExecutiveSummary'
import AIBadge from './AIBadge'
import PoweredByFooter from './PoweredByFooter'

export default function InteractionForm() {
  const dispatch = useDispatch()
  const hcps = useSelector(state => state.hcp.items)
  const { isLoading, currentInteraction } = useSelector(state => state.interactions)
  
  const [formData, setFormData] = useState({
    hcp_id: '',
    interaction_date: new Date().toISOString().split('T')[0],
    interaction_type: 'in-person',
    products_discussed: [],
    key_topics: '',
    sentiment: 'neutral',
    follow_up_date: '',
    follow_up_actions: '',
    duration_minutes: 30,
    location: '',
    notes: '',
  })

  // Mock product list
  const PRODUCT_OPTIONS = ["Cardiolex", "NeuroPro", "OncoShield", "GlucoBalance", "FlexiJoint", "HemaBoost"]

  useEffect(() => {
    if (hcps.length === 0) {
      dispatch(fetchHCPs())
    }
  }, [dispatch, hcps.length])

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleProductToggle = (product) => {
    setFormData(prev => {
      const current = prev.products_discussed
      return {
        ...prev,
        products_discussed: current.includes(product)
          ? current.filter(p => p !== product)
          : [...current, product]
      }
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.hcp_id) {
      toast.error('Please select an HCP')
      return
    }

    // Convert empty strings to null for backend
    const submitData = { ...formData }
    if (!submitData.follow_up_date) delete submitData.follow_up_date
    if (!submitData.duration_minutes) submitData.duration_minutes = 0

    await dispatch(createInteraction(submitData))
    toast.success('Interaction logged successfully')
  }

  const typeOptions = [
    { value: 'in-person', label: 'In Person' },
    { value: 'virtual', label: 'Virtual' },
    { value: 'phone', label: 'Phone' },
    { value: 'email', label: 'Email' },
  ]

  const sentimentOptions = [
    { value: 'positive', emoji: '😊', label: 'Positive', color: 'text-success bg-success/10 border-success/20' },
    { value: 'neutral', emoji: '😐', label: 'Neutral', color: 'text-warning bg-warning/10 border-warning/20' },
    { value: 'negative', emoji: '😟', label: 'Negative', color: 'text-danger bg-danger/10 border-danger/20' },
  ]

  // If successfully submitted, show the AI summary result
  if (currentInteraction && !isLoading) {
    return (
      <div className="max-w-2xl mx-auto mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
        <div className="glass-panel p-6 rounded-xl border border-border">
          <div className="flex items-center justify-center w-12 h-12 rounded-full bg-success/20 text-success mx-auto mb-4">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h2 className="text-xl font-medium text-center mb-1">Interaction Logged</h2>
          <p className="text-muted-foreground text-center text-sm mb-6">
            Successfully recorded visit with {currentInteraction.hcp_name}
          </p>

          <div className="bg-surface border border-border-subtle rounded-lg p-5">
            <div className="flex justify-between items-center mb-4 border-b border-border-subtle pb-3">
              <h3 className="font-medium flex items-center gap-2">
                <span className="text-accent">✨</span> AI Executive Summary
              </h3>
              <AIBadge />
            </div>
            
            <ExecutiveSummary 
              data={currentInteraction.ai_executive_summary} 
              fallbackText={currentInteraction.ai_summary} 
            />
            
            <div className="mt-6 pt-4 border-t border-border-subtle">
              <PoweredByFooter />
            </div>
          </div>

          <div className="mt-6 flex justify-center">
            <button 
              onClick={() => dispatch({ type: 'interactions/setCurrentInteraction', payload: null })}
              className="px-4 py-2 bg-hover hover:bg-surface border border-border rounded-lg text-sm transition-colors"
            >
              Log Another Interaction
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="pb-24">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* Left Column */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-xl border border-border space-y-5">
            <h3 className="font-medium text-lg border-b border-border pb-3">Details</h3>
            
            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Healthcare Professional *</label>
              <div className="relative">
                <select
                  name="hcp_id"
                  value={formData.hcp_id}
                  onChange={handleChange}
                  className="w-full bg-background border border-border rounded-lg px-4 py-2.5 text-sm focus:ring-2 focus:ring-accent appearance-none cursor-pointer"
                  required
                >
                  <option value="" disabled>Select an HCP...</option>
                  {hcps.map(hcp => (
                    <option key={hcp.id} value={hcp.id}>{hcp.name} - {hcp.specialty}</option>
                  ))}
                </select>
                <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-muted-foreground pointer-events-none" />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Date</label>
                <div className="relative">
                  <CalendarIcon className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                  <input
                    type="date"
                    name="interaction_date"
                    value={formData.interaction_date}
                    onChange={handleChange}
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-accent"
                  />
                </div>
              </div>
              <div className="space-y-2">
                <label className="text-sm font-medium text-muted-foreground">Duration (min)</label>
                <div className="relative">
                  <Clock className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                  <input
                    type="number"
                    name="duration_minutes"
                    value={formData.duration_minutes}
                    onChange={handleChange}
                    min="1"
                    className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-accent"
                  />
                </div>
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Interaction Type</label>
              <div className="flex bg-background border border-border rounded-lg p-1">
                {typeOptions.map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, interaction_type: opt.value }))}
                    className={`flex-1 py-1.5 text-xs font-medium rounded-md transition-colors ${
                      formData.interaction_type === opt.value
                        ? 'bg-hover text-primary shadow-sm'
                        : 'text-muted-foreground hover:text-primary'
                    }`}
                  >
                    {opt.label}
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Location</label>
              <div className="relative">
                <MapPin className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  name="location"
                  value={formData.location}
                  onChange={handleChange}
                  placeholder="e.g. Metro General Hospital"
                  className="w-full bg-background border border-border rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-accent"
                />
              </div>
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground flex items-center gap-2">
                <Pill className="w-4 h-4" /> Products Discussed
              </label>
              <div className="flex flex-wrap gap-2 pt-1">
                {PRODUCT_OPTIONS.map(prod => (
                  <button
                    key={prod}
                    type="button"
                    onClick={() => handleProductToggle(prod)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium border transition-colors ${
                      formData.products_discussed.includes(prod)
                        ? 'bg-accent/20 border-accent/30 text-accent'
                        : 'bg-background border-border text-muted-foreground hover:border-border-subtle'
                    }`}
                  >
                    {prod}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div className="glass-panel p-6 rounded-xl border border-border space-y-5">
            <h3 className="font-medium text-lg border-b border-border pb-3">Notes & Outcome</h3>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Key Topics</label>
              <textarea
                name="key_topics"
                value={formData.key_topics}
                onChange={handleChange}
                rows={3}
                placeholder="What was discussed?"
                className="w-full bg-background border border-border rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-accent resize-none placeholder:text-muted-foreground/50"
              />
            </div>

            <div className="space-y-2">
              <label className="text-sm font-medium text-muted-foreground">Sentiment</label>
              <div className="grid grid-cols-3 gap-3">
                {sentimentOptions.map(opt => (
                  <button
                    key={opt.value}
                    type="button"
                    onClick={() => setFormData(prev => ({ ...prev, sentiment: opt.value }))}
                    className={`flex flex-col items-center justify-center p-3 rounded-lg border transition-all ${
                      formData.sentiment === opt.value
                        ? opt.color
                        : 'bg-background border-border text-muted-foreground hover:bg-hover'
                    }`}
                  >
                    <span className="text-2xl mb-1">{opt.emoji}</span>
                    <span className="text-xs font-medium">{opt.label}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="space-y-2 pt-2 border-t border-border-subtle">
              <label className="text-sm font-medium text-muted-foreground">Follow-up Date</label>
              <input
                type="date"
                name="follow_up_date"
                value={formData.follow_up_date}
                onChange={handleChange}
                className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-accent"
              />
            </div>
            
            {formData.follow_up_date && (
              <div className="space-y-2 animate-in fade-in slide-in-from-top-2">
                <label className="text-sm font-medium text-muted-foreground">Follow-up Actions</label>
                <input
                  type="text"
                  name="follow_up_actions"
                  value={formData.follow_up_actions}
                  onChange={handleChange}
                  placeholder="e.g. Send clinical trial data"
                  className="w-full bg-background border border-border rounded-lg px-4 py-2 text-sm focus:ring-2 focus:ring-accent"
                />
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Fixed Bottom Submit Bar */}
      <div className="fixed bottom-0 left-0 lg:left-[240px] right-0 p-4 bg-background/80 backdrop-blur-md border-t border-border z-20 flex justify-end">
        <button
          type="submit"
          disabled={isLoading}
          className="bg-accent hover:bg-accent-hover text-white px-8 py-2.5 rounded-lg text-sm font-medium transition-colors flex items-center gap-2 disabled:opacity-50"
        >
          {isLoading ? (
            <>
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Processing AI Summary...
            </>
          ) : (
            <>
              Save & Analyze
            </>
          )}
        </button>
      </div>
    </form>
  )
}
