import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { fetchInteractions } from '../store/interactionSlice'
import { Search, Filter, Calendar as CalendarIcon, FileText, Activity } from 'lucide-react'
import ExecutiveSummary from '../components/ExecutiveSummary'

export default function InteractionHistoryPage() {
  const dispatch = useDispatch()
  const { items, isLoading, total } = useSelector(state => state.interactions)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedItem, setSelectedItem] = useState(null)

  useEffect(() => {
    dispatch(fetchInteractions({ limit: 50, skip: 0 }))
  }, [dispatch])

  // Client-side filter for demo
  const filteredItems = items.filter(item => 
    item.hcp_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    item.ai_summary?.toLowerCase().includes(searchTerm.toLowerCase())
  )

  return (
    <div className="h-full flex flex-col max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex justify-between items-center mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-primary">Interaction History</h1>
          <p className="text-sm text-muted-foreground">View and analyze past HCP engagements.</p>
        </div>
      </div>

      <div className="flex gap-6 h-[calc(100vh-160px)]">
        
        {/* Left Column: List */}
        <div className="w-1/3 flex flex-col glass-panel rounded-xl border border-border overflow-hidden">
          <div className="p-4 border-b border-border-subtle space-y-3 shrink-0">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search interactions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full bg-background border border-border rounded-lg pl-9 pr-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-accent transition-all"
              />
            </div>
            <div className="flex justify-between items-center">
              <span className="text-xs text-muted-foreground font-medium">{filteredItems.length} records</span>
              <button className="text-xs flex items-center gap-1.5 text-muted-foreground hover:text-primary transition-colors">
                <Filter className="w-3.5 h-3.5" /> Filter
              </button>
            </div>
          </div>

          <div className="flex-1 overflow-y-auto">
            {isLoading ? (
              <div className="p-8 text-center text-muted-foreground flex flex-col items-center">
                <div className="w-6 h-6 border-2 border-accent border-t-transparent rounded-full animate-spin mb-2" />
                <p className="text-sm">Loading history...</p>
              </div>
            ) : filteredItems.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground text-sm">
                No interactions found.
              </div>
            ) : (
              <div className="divide-y divide-border">
                {filteredItems.map(item => (
                  <div 
                    key={item.id}
                    onClick={() => setSelectedItem(item)}
                    className={`p-4 cursor-pointer hover:bg-hover transition-colors ${
                      selectedItem?.id === item.id ? 'bg-accent/5 border-l-2 border-l-accent' : 'border-l-2 border-l-transparent'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-1">
                      <h4 className="font-medium text-sm text-primary">{item.hcp_name}</h4>
                      <span className="text-xs text-muted-foreground whitespace-nowrap">
                        {new Date(item.interaction_date).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground line-clamp-2 leading-relaxed">
                      {item.ai_summary}
                    </p>
                    <div className="mt-2 flex gap-2">
                      <span className={`text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-sm ${
                        item.sentiment === 'positive' ? 'bg-success/20 text-success' :
                        item.sentiment === 'negative' ? 'bg-danger/20 text-danger' :
                        'bg-warning/20 text-warning'
                      }`}>
                        {item.sentiment}
                      </span>
                      {item.ai_executive_summary && (
                        <span className="text-[9px] uppercase font-bold tracking-wider px-1.5 py-0.5 rounded-sm bg-accent/20 text-accent">
                          AI Analyzed
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Details */}
        <div className="flex-1 glass-panel rounded-xl border border-border overflow-hidden flex flex-col bg-surface">
          {selectedItem ? (
            <div className="flex-1 overflow-y-auto">
              {/* Detail Header */}
              <div className="p-6 border-b border-border-subtle bg-background">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h2 className="text-2xl font-semibold text-primary">{selectedItem.hcp_name}</h2>
                    <p className="text-sm text-muted-foreground mt-1 flex items-center gap-4">
                      <span className="flex items-center gap-1.5">
                        <CalendarIcon className="w-4 h-4" /> 
                        {new Date(selectedItem.interaction_date).toLocaleDateString()}
                      </span>
                      <span className="flex items-center gap-1.5 capitalize">
                        <Activity className="w-4 h-4" /> 
                        {selectedItem.interaction_type}
                      </span>
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-semibold uppercase tracking-wider ${
                    selectedItem.sentiment === 'positive' ? 'bg-success/20 text-success' :
                    selectedItem.sentiment === 'negative' ? 'bg-danger/20 text-danger' :
                    'bg-warning/20 text-warning'
                  }`}>
                    {selectedItem.sentiment}
                  </span>
                </div>
                
                {/* Products Tags */}
                {selectedItem.products_discussed?.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-4">
                    {selectedItem.products_discussed.map((p, i) => (
                      <span key={i} className="px-2 py-1 bg-surface border border-border rounded-md text-xs font-medium text-foreground">
                        {p}
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Detail Content */}
              <div className="p-6 space-y-8">
                
                {/* AI Executive Summary */}
                <section>
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-4 flex items-center gap-2">
                    <span className="text-accent">✨</span> Executive Summary
                  </h3>
                  <div className="bg-background rounded-lg border border-border-subtle p-5 shadow-sm">
                    <ExecutiveSummary 
                      data={selectedItem.ai_executive_summary} 
                      fallbackText={selectedItem.ai_summary} 
                    />
                  </div>
                </section>

                {/* Raw Notes */}
                <section>
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-muted-foreground mb-3 flex items-center gap-2">
                    <FileText className="w-4 h-4" /> Rep Notes
                  </h3>
                  <div className="bg-background rounded-lg border border-border-subtle p-4">
                    <p className="text-sm text-foreground whitespace-pre-wrap leading-relaxed">
                      {selectedItem.key_topics || "No detailed notes provided."}
                    </p>
                  </div>
                </section>

              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
              <FileText className="w-12 h-12 mb-4 opacity-20" />
              <p>Select an interaction to view details</p>
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
