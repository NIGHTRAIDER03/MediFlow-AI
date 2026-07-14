import { Outlet } from 'react-router-dom'
import { useSelector } from 'react-redux'
import Sidebar from './Sidebar'
import Header from './Header'
import AskMediFlow from './AskMediFlow'
import { cn } from '../lib/utils'

export default function Layout() {
  const { sidebarCollapsed } = useSelector(state => state.ui)

  return (
    <div className="flex h-screen bg-background overflow-hidden selection:bg-accent/30 text-foreground font-sans">
      <Sidebar />
      <div className={cn(
        "flex flex-col flex-1 transition-all duration-300 ease-in-out",
        sidebarCollapsed ? "ml-[64px]" : "ml-[240px]"
      )}>
        <Header />
        <main className="flex-1 overflow-y-auto overflow-x-hidden p-6 relative">
          <Outlet />
        </main>
      </div>
      <AskMediFlow />
    </div>
  )
}
