import { useState, useEffect, useRef } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { motion, AnimatePresence } from 'framer-motion'
import { Sparkles, X, Search, Loader2 } from 'lucide-react'
import { setAskMediFlowOpen } from '../store/uiSlice'
import { sendMessage } from '../store/chatSlice'
import api from '../api/axios'

export default function AskMediFlow() {
  const { askMediFlowOpen } = useSelector(state => state.ui)
  const dispatch = useDispatch()
  const [query, setQuery] = useState('')
  const [isSearching, setIsSearching] = useState(false)
  const [results, setResults] = useState(null)
  const inputRef = useRef(null)

  // Handle keyboard shortcut (Cmd/Ctrl + K)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault()
        dispatch(setAskMediFlowOpen(!askMediFlowOpen))
      }
      if (e.key === 'Escape' && askMediFlowOpen) {
        dispatch(setAskMediFlowOpen(false))
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [askMediFlowOpen, dispatch])

  useEffect(() => {
    if (askMediFlowOpen) {
      setTimeout(() => inputRef.current?.focus(), 100)
    } else {
      setQuery('')
      setResults(null)
    }
  }, [askMediFlowOpen])

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setIsSearching(true)
    try {
      // Create a fresh thread for this query
      const threadId = `ask-${Date.now()}`
      const response = await api.post('/chat', { message: query, thread_id: threadId })
      setResults(response.data)
    } catch (error) {
      console.error(error)
      setResults({ error: "Failed to get an answer. Please try again." })
    } finally {
      setIsSearching(false)
    }
  }

  const SUGGESTIONS = [
    "Show doctors needing follow-up",
    "Which HCPs discussed Cardiolex?",
    "Summarize this week's visits",
    "Prepare me for Dr. Chen",
  ]

  return (
    <AnimatePresence>
      {askMediFlowOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 bg-background/80 backdrop-blur-sm"
            onClick={() => dispatch(setAskMediFlowOpen(false))}
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.2 }}
            className="fixed left-1/2 top-[10%] z-50 w-full max-w-2xl -translate-x-1/2"
          >
            <div className="bg-elevated border border-border rounded-xl shadow-2xl overflow-hidden flex flex-col max-h-[80vh]">
              {/* Input Header */}
              <form onSubmit={handleSubmit} className="relative flex items-center border-b border-border p-4 shrink-0">
                <Sparkles className="absolute left-4 w-5 h-5 text-accent" />
                <input
                  ref={inputRef}
                  type="text"
                  placeholder="Ask MediFlow... (e.g. 'Show doctors needing follow-up')"
                  className="w-full bg-transparent border-none focus:outline-none focus:ring-0 text-lg placeholder:text-muted-foreground pl-8 pr-12"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
                <button
                  type="button"
                  onClick={() => dispatch(setAskMediFlowOpen(false))}
                  className="absolute right-4 p-1 rounded-md text-muted-foreground hover:bg-hover hover:text-primary transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </form>

              {/* Content Area */}
              <div className="overflow-y-auto p-4 flex-1">
                {isSearching ? (
                  <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
                    <Loader2 className="w-8 h-8 animate-spin mb-4 text-accent" />
                    <p>MediFlow AI is thinking...</p>
                  </div>
                ) : results ? (
                  <div className="space-y-4">
                    {results.error ? (
                      <div className="p-4 bg-danger/10 border border-danger/20 rounded-lg text-danger">
                        {results.error}
                      </div>
                    ) : (
                      <div className="prose prose-invert max-w-none text-sm">
                        {/* Simple rendering of markdown/text response */}
                        <div className="whitespace-pre-wrap">{results.response}</div>
                        
                        {/* Tool results visualization if any */}
                        {results.tool_results && results.tool_results.length > 0 && (
                          <div className="mt-6 pt-4 border-t border-border space-y-2">
                            <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">Data Sources</p>
                            {results.tool_results.map((tr, i) => (
                              <div key={i} className="text-xs bg-surface p-2 rounded border border-border-subtle flex items-center">
                                <span className="font-mono text-accent mr-2">{tr.tool_name}</span>
                                <span className="text-muted-foreground truncate flex-1">Executed successfully</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                ) : (
                  <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider mb-3">Suggestions</p>
                    <div className="space-y-1">
                      {SUGGESTIONS.map((sug, i) => (
                        <button
                          key={i}
                          onClick={() => {
                            setQuery(sug)
                            // Auto-submit after setting query requires slight delay or triggering handleSubmit manually
                            setTimeout(() => {
                              const form = inputRef.current?.closest('form')
                              if (form) form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }))
                            }, 50)
                          }}
                          className="w-full text-left px-3 py-2 rounded-lg text-sm hover:bg-hover text-primary transition-colors flex items-center"
                        >
                          <Search className="w-4 h-4 mr-3 text-muted-foreground" />
                          {sug}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Footer */}
              <div className="border-t border-border p-2 bg-surface/50 flex justify-between items-center shrink-0">
                <div className="flex items-center text-xs text-muted-foreground">
                  <span className="font-medium text-accent mr-1">AI Enhanced ✓</span>
                  Powered by {results?.model || 'Llama-3.3-70B'}
                  {results?.elapsed_time && <span className="ml-2">· {results.elapsed_time}s</span>}
                </div>
                <div className="text-xs text-muted-foreground hidden sm:flex items-center">
                  <span className="mr-2">Close</span>
                  <kbd className="h-5 items-center gap-1 rounded bg-hover px-1.5 font-mono text-[10px]">Esc</kbd>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  )
}
