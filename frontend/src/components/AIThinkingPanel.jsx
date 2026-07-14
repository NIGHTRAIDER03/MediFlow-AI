import { Brain, Check, ChevronDown, ChevronRight, Activity, Database, Sparkles, Clock, AlertTriangle } from 'lucide-react'
import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import PoweredByFooter from './PoweredByFooter'
import { cn } from '../lib/utils'

export default function AIThinkingPanel({ isLoading, toolResults = [] }) {
  const [expanded, setExpanded] = useState(true)

  return (
    <div className="glass-panel rounded-xl border border-border flex flex-col h-full overflow-hidden">
      
      {/* Header */}
      <div 
        className="px-4 py-3 border-b border-border-subtle flex items-center justify-between cursor-pointer hover:bg-hover transition-colors"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-2">
          <Brain className={cn("w-4 h-4", isLoading ? "text-accent animate-pulse" : "text-muted-foreground")} />
          <h3 className="text-sm font-medium">AI Processing</h3>
        </div>
        {expanded ? <ChevronDown className="w-4 h-4 text-muted-foreground" /> : <ChevronRight className="w-4 h-4 text-muted-foreground" />}
      </div>

      {/* Content */}
      <AnimatePresence>
        {expanded && (
          <motion.div 
            initial={{ height: 0 }}
            animate={{ height: 'auto' }}
            exit={{ height: 0 }}
            className="flex-1 overflow-y-auto"
          >
            <div className="p-4 space-y-4">
              
              {/* Status Indicator */}
              <div className="flex items-center gap-3">
                <div className="relative flex items-center justify-center">
                  {isLoading ? (
                    <>
                      <div className="absolute w-8 h-8 rounded-full border-2 border-accent/30 border-t-accent animate-spin" />
                      <div className="w-2 h-2 rounded-full bg-accent animate-pulse" />
                    </>
                  ) : toolResults.length > 0 ? (
                    <div className="w-8 h-8 rounded-full bg-success/20 text-success flex items-center justify-center">
                      <Check className="w-4 h-4" />
                    </div>
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-surface border border-border flex items-center justify-center text-muted-foreground">
                      <Activity className="w-4 h-4" />
                    </div>
                  )}
                </div>
                <div>
                  <p className="text-sm font-medium">
                    {isLoading ? 'Analyzing request...' : toolResults.length > 0 ? 'Analysis complete' : 'Ready'}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {isLoading ? 'Running agent graph execution' : 'Waiting for input'}
                  </p>
                </div>
              </div>

              {/* Tool Execution Timeline */}
              {toolResults.length > 0 && (
                <div className="mt-6 pt-4 border-t border-border-subtle">
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">Graph Execution</h4>
                  <div className="space-y-4 pl-2 border-l border-border-subtle ml-2 relative">
                    
                    {/* Mock intent detection step */}
                    <div className="relative pl-6">
                      <div className="absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full bg-surface border-2 border-accent" />
                      <p className="text-xs font-medium text-foreground">Intent Detected</p>
                      <p className="text-[10px] text-muted-foreground">Routing to appropriate tools</p>
                    </div>

                    {/* Actual Tool Results */}
                    {toolResults.map((result, i) => (
                      <div key={i} className="relative pl-6">
                        <div className="absolute -left-[5px] top-1 w-2.5 h-2.5 rounded-full bg-surface border-2 border-success" />
                        <p className="text-xs font-medium text-foreground flex items-center gap-1.5">
                          {result.tool_name === 'log_interaction' && <Database className="w-3 h-3 text-accent" />}
                          {result.tool_name === 'smart_hcp_search' && <Sparkles className="w-3 h-3 text-accent" />}
                          {result.tool_name === 'interaction_timeline' && <Clock className="w-3 h-3 text-accent" />}
                          {result.tool_name}
                        </p>
                        <p className="text-[10px] text-muted-foreground line-clamp-1 mt-0.5">
                          {typeof result.result === 'string' ? result.result : 'Execution successful'}
                        </p>
                        
                        {/* Tool Data Preview (if JSON) */}
                        {typeof result.result === 'object' && result.result !== null && (
                          <div className="mt-2 bg-background border border-border-subtle rounded p-2 overflow-hidden">
                            <pre className="text-[9px] font-mono text-muted-foreground overflow-x-auto">
                              {JSON.stringify(result.result, null, 2)}
                            </pre>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Footer */}
      <div className="mt-auto px-4 py-3 bg-surface/50 border-t border-border-subtle">
        <PoweredByFooter />
      </div>
    </div>
  )
}
