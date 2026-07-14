import { useState, useRef, useEffect } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Send, Bot, User, Loader2 } from 'lucide-react'
import { sendMessage, clearChat, setThreadId } from '../store/chatSlice'
import AIThinkingPanel from './AIThinkingPanel'
import ToolResultCard from './ToolResultCard'
import { cn } from '../lib/utils'

export default function ChatWindow() {
  const [input, setInput] = useState('')
  const dispatch = useDispatch()
  const { messages, isLoading, threadId, toolResults, error } = useSelector(state => state.chat)
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (!threadId) {
      dispatch(setThreadId(`thread-${Date.now()}`))
    }
  }, [threadId, dispatch])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, toolResults, isLoading])

  const handleSend = async (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')
    
    // Add user message immediately
    dispatch({ 
      type: 'chat/addMessage', 
      payload: { role: 'user', content: userMessage, timestamp: new Date().toISOString() } 
    })

    // Send to API
    dispatch(sendMessage({ message: userMessage, threadId }))
  }

  return (
    <div className="h-full flex gap-6">
      
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col glass-panel rounded-xl border border-border overflow-hidden">
        
        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-4">
              <div className="w-16 h-16 bg-accent/10 text-accent rounded-2xl flex items-center justify-center mb-4 border border-accent/20">
                <Bot className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-medium mb-2">MediFlow Copilot</h3>
              <p className="text-muted-foreground text-sm max-w-sm">
                Describe your interaction naturally. "I met Dr. Chen today at Metro Hospital. Discussed Cardiolex..."
              </p>
            </div>
          ) : (
            <>
              {messages.map((msg, i) => (
                <div key={i} className={cn(
                  "flex gap-4 max-w-[85%]",
                  msg.role === 'user' ? "ml-auto flex-row-reverse" : ""
                )}>
                  <div className={cn(
                    "w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1",
                    msg.role === 'user' ? "bg-card border border-border" : "bg-accent text-white"
                  )}>
                    {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
                  </div>
                  <div className={cn(
                    "p-4 rounded-2xl",
                    msg.role === 'user' 
                      ? "bg-surface border border-border-subtle text-foreground rounded-tr-sm" 
                      : "bg-transparent border-none p-0 pt-1" // AI messages have no bubble background for cleaner look
                  )}>
                    {msg.role === 'user' ? (
                      <p className="text-sm whitespace-pre-wrap leading-relaxed">{msg.content}</p>
                    ) : (
                      <div className="space-y-4">
                        <div className="prose prose-invert prose-sm max-w-none">
                          <div className="whitespace-pre-wrap leading-relaxed text-[15px]">{msg.content}</div>
                        </div>
                        {/* Render tool results directly after the AI message if it's the latest one */}
                        {i === messages.length - 1 && toolResults.map((tr, idx) => (
                          <ToolResultCard key={idx} result={tr} />
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isLoading && (
                <div className="flex gap-4 max-w-[85%]">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-1 bg-accent/20 text-accent border border-accent/30">
                    <Loader2 className="w-4 h-4 animate-spin" />
                  </div>
                  <div className="pt-2">
                    <div className="flex space-x-1.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-accent/50 animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-1.5 h-1.5 rounded-full bg-accent/50 animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-1.5 h-1.5 rounded-full bg-accent/50 animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
          <div ref={messagesEndRef} />
        </div>

        {error && (
          <div className="mx-4 mb-2 p-3 text-sm bg-danger/10 border border-danger/20 text-danger rounded-lg flex justify-between items-center">
            <span>{error}</span>
            <button onClick={() => dispatch({ type: 'chat/sendMessage/pending' })} className="underline">Retry</button>
          </div>
        )}

        {/* Input Area */}
        <div className="p-4 bg-surface border-t border-border">
          <form onSubmit={handleSend} className="relative flex items-end bg-background border border-border rounded-xl focus-within:ring-2 focus-within:ring-accent focus-within:border-accent transition-all p-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSend(e)
                }
              }}
              placeholder="Message MediFlow AI..."
              className="w-full bg-transparent border-none resize-none max-h-32 focus:outline-none focus:ring-0 text-sm py-3 px-4"
              rows={input.split('\n').length > 1 ? Math.min(input.split('\n').length, 5) : 1}
            />
            <button
              type="submit"
              disabled={!input.trim() || isLoading}
              className="m-1.5 p-2 bg-accent hover:bg-accent-hover text-white rounded-lg disabled:opacity-50 disabled:bg-surface disabled:text-muted-foreground transition-colors shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
          <div className="flex justify-between items-center mt-2 px-2">
            <p className="text-xs text-muted-foreground">Press <kbd className="font-mono bg-hover px-1 rounded">Enter</kbd> to send</p>
            <button 
              type="button"
              onClick={() => { dispatch(clearChat()); dispatch(setThreadId(`thread-${Date.now()}`)) }}
              className="text-xs text-muted-foreground hover:text-primary transition-colors"
            >
              Clear Chat
            </button>
          </div>
        </div>
      </div>

      {/* Right Side Panels */}
      <div className="w-[320px] hidden xl:flex flex-col gap-6 shrink-0">
        <AIThinkingPanel isLoading={isLoading} toolResults={toolResults} />
      </div>

    </div>
  )
}
