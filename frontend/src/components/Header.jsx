import { useSelector, useDispatch } from 'react-redux'
import { useLocation } from 'react-router-dom'
import { Sparkles, LogOut, User as UserIcon } from 'lucide-react'
import { logout } from '../store/authSlice'
import { setAskMediFlowOpen } from '../store/uiSlice'

export default function Header() {
  const { user } = useSelector(state => state.auth)
  const location = useLocation()
  const dispatch = useDispatch()

  // Generate breadcrumb from path
  const pathParts = location.pathname.split('/').filter(Boolean)
  const currentPage = pathParts.length === 0 
    ? 'Dashboard' 
    : pathParts[0].charAt(0).toUpperCase() + pathParts[0].slice(1)

  return (
    <header className="h-14 border-b border-border bg-surface/50 backdrop-blur-md sticky top-0 z-30 flex items-center justify-between px-6">
      
      {/* Breadcrumbs / Title */}
      <div className="flex items-center text-sm">
        <span className="text-muted-foreground mr-2">MediFlow</span>
        <span className="text-muted-foreground mr-2">/</span>
        <span className="font-medium text-primary">{currentPage.replace('-', ' ')}</span>
      </div>

      <div className="flex items-center gap-4">
        {/* Global Ask MediFlow Button */}
        <button 
          onClick={() => dispatch(setAskMediFlowOpen(true))}
          className="flex items-center h-8 px-3 rounded-full bg-accent/10 hover:bg-accent/20 border border-accent/20 text-accent text-xs font-medium transition-all group"
        >
          <Sparkles className="w-3.5 h-3.5 mr-2 group-hover:animate-pulse" />
          Ask MediFlow
          <kbd className="ml-2 hidden sm:inline-flex h-5 items-center gap-1 rounded bg-accent/20 px-1.5 font-mono text-[10px] text-accent">
            <span className="text-xs">⌘</span>K
          </kbd>
        </button>

        {/* User Dropdown (Simplified for now) */}
        <div className="relative group">
          <button className="flex items-center justify-center w-8 h-8 rounded-full bg-card border border-border hover:border-border-subtle transition-colors overflow-hidden">
            <span className="text-xs font-medium">
              {user?.full_name?.split(' ').map(n => n[0]).join('') || 'U'}
            </span>
          </button>
          
          <div className="absolute right-0 mt-2 w-48 rounded-md bg-elevated border border-border shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all transform origin-top-right">
            <div className="px-4 py-2 border-b border-border">
              <p className="text-sm font-medium truncate">{user?.full_name}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.email}</p>
            </div>
            <div className="p-1">
              <button 
                onClick={() => dispatch(logout())}
                className="flex items-center w-full px-3 py-2 text-sm text-danger hover:bg-hover rounded-sm transition-colors"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Sign out
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
