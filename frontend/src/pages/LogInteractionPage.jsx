import { useSelector, useDispatch } from 'react-redux'
import { motion, AnimatePresence } from 'framer-motion'
import { toggleMode } from '../store/uiSlice'
import InteractionForm from '../components/InteractionForm'
import ChatWindow from '../components/ChatWindow'

export default function LogInteractionPage() {
  const dispatch = useDispatch()
  const { activeMode } = useSelector(state => state.ui)

  return (
    <div className="h-full flex flex-col max-w-7xl mx-auto">
      {/* Header & Toggle */}
      <div className="flex justify-between items-center mb-6 shrink-0">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-primary">Log Interaction</h1>
          <p className="text-sm text-muted-foreground">Record your HCP visit details.</p>
        </div>
        
        {/* Mode Toggle */}
        <div className="bg-surface border border-border p-1 rounded-lg flex relative">
          {/* Sliding Background */}
          <motion.div
            className="absolute bg-hover rounded-md inset-y-1 z-0"
            initial={false}
            animate={{ 
              x: activeMode === 'form' ? 0 : '100%',
              width: '50%'
            }}
            transition={{ type: "spring", stiffness: 400, damping: 30 }}
          />
          
          <button
            onClick={() => activeMode !== 'form' && dispatch(toggleMode())}
            className={`relative z-10 px-4 py-1.5 text-sm font-medium rounded-md w-32 transition-colors ${
              activeMode === 'form' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            Structured Form
          </button>
          <button
            onClick={() => activeMode !== 'copilot' && dispatch(toggleMode())}
            className={`relative z-10 px-4 py-1.5 text-sm font-medium rounded-md w-32 transition-colors flex items-center justify-center gap-1.5 ${
              activeMode === 'copilot' ? 'text-primary' : 'text-muted-foreground'
            }`}
          >
            <span className="text-accent">✧</span> AI Copilot
          </button>
        </div>
      </div>

      {/* Content Area */}
      <div className="flex-1 relative overflow-hidden">
        <AnimatePresence mode="wait">
          {activeMode === 'form' ? (
            <motion.div
              key="form"
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0 overflow-y-auto"
            >
              <InteractionForm />
            </motion.div>
          ) : (
            <motion.div
              key="copilot"
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 20 }}
              transition={{ duration: 0.2 }}
              className="absolute inset-0"
            >
              <ChatWindow />
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  )
}
