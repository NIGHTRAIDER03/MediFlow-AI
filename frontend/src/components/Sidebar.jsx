import { NavLink } from 'react-router-dom'
import { useSelector, useDispatch } from 'react-redux'
import { LayoutDashboard, PenSquare, Clock, BarChart3, ChevronLeft, ChevronRight, Settings } from 'lucide-react'
import { toggleSidebar } from '../store/uiSlice'
import { cn } from '../lib/utils'

const NAV_ITEMS = [
  { name: 'Dashboard', path: '/', icon: LayoutDashboard },
  { name: 'Log Interaction', path: '/log', icon: PenSquare },
  { name: 'History', path: '/history', icon: Clock },
  { name: 'Analytics', path: '/analytics', icon: BarChart3 },
]

export default function Sidebar() {
  const { sidebarCollapsed } = useSelector(state => state.ui)
  const dispatch = useDispatch()

  return (
    <aside className={cn(
      "fixed left-0 top-0 bottom-0 z-40 bg-surface border-r border-border flex flex-col transition-all duration-300 ease-in-out",
      sidebarCollapsed ? "w-[64px]" : "w-[240px]"
    )}>
      {/* Header/Logo */}
      <div className="h-14 flex items-center px-4 border-b border-border">
        <div className="w-8 h-8 rounded-lg bg-card border border-border-subtle shadow-sm flex items-center justify-center shrink-0">
          <span className="text-sm font-bold bg-gradient-to-br from-white to-white/50 bg-clip-text text-transparent">MF</span>
        </div>
        {!sidebarCollapsed && (
          <span className="ml-3 font-semibold text-sm tracking-tight text-primary whitespace-nowrap overflow-hidden">
            MediFlow AI
          </span>
        )}
      </div>

      {/* Nav Links */}
      <div className="flex-1 overflow-y-auto py-4 flex flex-col gap-1 px-2">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) => cn(
                "flex items-center h-9 px-2 rounded-md text-sm transition-colors relative group",
                isActive 
                  ? "bg-accent/10 text-accent font-medium" 
                  : "text-muted-foreground hover:bg-hover hover:text-primary",
                sidebarCollapsed && "justify-center"
              )}
              title={sidebarCollapsed ? item.name : undefined}
            >
              {({ isActive }) => (
                <>
                  {isActive && !sidebarCollapsed && (
                    <div className="absolute left-0 top-1 bottom-1 w-[3px] bg-accent rounded-r-full" />
                  )}
                  <Icon className={cn("shrink-0", sidebarCollapsed ? "w-5 h-5" : "w-4 h-4 mr-3")} strokeWidth={isActive ? 2.5 : 2} />
                  {!sidebarCollapsed && (
                    <span className="truncate">{item.name}</span>
                  )}
                </>
              )}
            </NavLink>
          )
        })}
      </div>

      {/* Footer / Toggle */}
      <div className="p-2 border-t border-border mt-auto">
        {!sidebarCollapsed && (
          <button className="w-full flex items-center h-9 px-2 rounded-md text-sm text-muted-foreground hover:bg-hover hover:text-primary transition-colors mb-1">
            <Settings className="w-4 h-4 mr-3 shrink-0" />
            <span className="truncate">Settings</span>
          </button>
        )}
        <button 
          onClick={() => dispatch(toggleSidebar())}
          className={cn(
            "flex items-center h-9 px-2 rounded-md text-sm text-muted-foreground hover:bg-hover hover:text-primary transition-colors",
            sidebarCollapsed ? "w-full justify-center" : "w-full"
          )}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-5 h-5 shrink-0" />
          ) : (
            <>
              <ChevronLeft className="w-4 h-4 mr-3 shrink-0" />
              <span className="truncate">Collapse</span>
            </>
          )}
        </button>
      </div>
    </aside>
  )
}
