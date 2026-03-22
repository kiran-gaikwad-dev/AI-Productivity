import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Dashboard from './components/Dashboard'
import { LayoutDashboard, Users, ActivitySquare, Settings, Bell, Search, Moon, Sun, Menu, X, LogOut } from 'lucide-react'

function App() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [notifications] = useState(3);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const SidebarItem = ({ icon: Icon, label, active }) => (
    <a href="#" className={`flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-200 mt-2 ${active ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30' : 'text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800'}`}>
      <Icon size={20} className={active ? "opacity-100" : "opacity-70"} />
      <span className="font-semibold text-sm">{label}</span>
      {active && <motion.div layoutId="activeNav" className="absolute left-0 w-1 h-8 bg-indigo-600 rounded-r-full" />}
    </a>
  );

  return (
    <div className="flex h-screen bg-slate-50 dark:bg-slate-900 overflow-hidden font-sans transition-colors duration-300">
      
      {/* Desktop Sidebar Navigation */}
      <aside className="hidden lg:flex flex-col w-72 bg-white dark:bg-slate-950 border-r border-slate-200 dark:border-slate-800 h-full z-20">
        <div className="p-6 flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 shadow-md flex items-center justify-center shrink-0">
            <ActivitySquare className="text-white w-5 h-5" />
          </div>
          <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600 dark:from-white dark:to-slate-400 tracking-tight">
            FocusTrack AI
          </h1>
        </div>
        
        <div className="px-4 py-2 flex-grow">
          <p className="px-4 text-xs font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase mb-4 mt-2">Core Analytics</p>
          <SidebarItem icon={LayoutDashboard} label="Productivity Dashboard" active={true} />
          <SidebarItem icon={ActivitySquare} label="Live Log Stream" active={false} />
          <SidebarItem icon={Users} label="User Segments" active={false} />
          
          <p className="px-4 text-xs font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase mb-4 mt-10">System Settings</p>
          <SidebarItem icon={Settings} label="Model Parameters" active={false} />
        </div>
        
        <div className="p-6 border-t border-slate-200 dark:border-slate-800 mt-auto">
          <div className="flex items-center space-x-3 cursor-pointer p-2 rounded-xl hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors">
            <img src="https://i.pravatar.cc/150?u=a042581f4e29026024d" alt="User" className="w-10 h-10 rounded-full border-2 border-slate-200 dark:border-slate-700" />
            <div className="flex flex-col">
              <span className="text-sm font-bold text-slate-900 dark:text-white">Admin (U102)</span>
              <span className="text-xs font-medium text-slate-500 dark:text-slate-400">Workspace Owner</span>
            </div>
            <LogOut size={16} className="ml-auto text-slate-400" />
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col h-full overflow-hidden relative">
        
        {/* Top Navigation Bar */}
        <header className="h-20 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-6 lg:px-10 z-10 transition-colors duration-300">
          
          {/* Mobile Menu Toggle */}
          <button onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)} className="lg:hidden p-2 -ml-2 text-slate-600 dark:text-slate-300 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-800">
            <Menu size={24} />
          </button>
          
          {/* Global Search Bar */}
          <div className="hidden sm:flex items-center lg:ml-0 bg-slate-100 dark:bg-slate-900 rounded-full px-4 py-2.5 w-96 border border-slate-200/60 dark:border-slate-800 focus-within:ring-2 focus-within:ring-indigo-500/20 focus-within:border-indigo-500 transition-all">
            <Search size={18} className="text-slate-400 shrink-0" />
            <input 
              type="text" 
              placeholder="Search activity logs, sites, or AI metrics..." 
              className="bg-transparent border-none outline-none text-sm w-full ml-3 text-slate-700 dark:text-slate-200 placeholder-slate-400 dark:placeholder-slate-500"
            />
          </div>

          <div className="flex items-center space-x-3 sm:space-x-5 ml-auto">
            {/* Theme Toggle Button */}
            <button 
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2.5 text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 bg-slate-50 dark:bg-slate-900 rounded-full hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors border border-slate-200 dark:border-slate-800 shadow-sm relative overflow-hidden flex items-center justify-center w-10 h-10"
              title="Toggle Dark Mode"
            >
              <AnimatePresence mode="popLayout" initial={false}>
                 {isDarkMode ? (
                   <motion.div key="sun" initial={{ y: -20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: 20, opacity: 0 }} transition={{ duration: 0.2 }}>
                     <Sun size={20} />
                   </motion.div>
                 ) : (
                   <motion.div key="moon" initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} exit={{ y: -20, opacity: 0 }} transition={{ duration: 0.2 }}>
                     <Moon size={20} />
                   </motion.div>
                 )}
              </AnimatePresence>
            </button>
            
            {/* Notifications Panel Icon */}
            <button className="relative p-2.5 text-slate-500 dark:text-slate-400 hover:text-indigo-600 dark:hover:text-indigo-400 bg-slate-50 dark:bg-slate-900 rounded-full hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors border border-slate-200 dark:border-slate-800 shadow-sm w-10 h-10 flex items-center justify-center">
              <Bell size={20} />
              {notifications > 0 && (
                <span className="absolute top-0 right-0 transform translate-x-1/4 -translate-y-1/4 flex h-4 w-4">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-4 w-4 bg-red-500 border-[1.5px] border-white dark:border-slate-900 items-center justify-center text-[9px] font-bold text-white z-10">{notifications}</span>
                </span>
              )}
            </button>
          </div>
        </header>

        {/* Scrollable Dashboard Viewport */}
        <div className="flex-1 overflow-x-hidden overflow-y-auto bg-slate-50/50 dark:bg-slate-900 pt-6 pb-20 sm:py-8 px-4 sm:px-6 md:px-8 lg:px-10 scroll-smooth transition-colors duration-300">
          <div className="max-w-[1600px] mx-auto transition-all duration-300">
            <Dashboard />
          </div>
        </div>
      </main>

      {/* Mobile Drawer (Basic Overlay) */}
      <AnimatePresence>
        {isMobileMenuOpen && (
          <motion.div 
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-50 lg:hidden"
            onClick={() => setIsMobileMenuOpen(false)}
          >
            <motion.div 
              initial={{ x: '-100%' }} animate={{ x: 0 }} exit={{ x: '-100%' }}
              transition={{ type: "spring", bounce: 0, duration: 0.4 }}
              className="w-72 bg-white dark:bg-slate-950 h-full p-6 flex flex-col pt-10 border-r border-slate-800"
              onClick={e => e.stopPropagation()}
            >
              <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-8 px-4">Menu</h2>
              <SidebarItem icon={LayoutDashboard} label="Productivity Dashboard" active={true} />
              <SidebarItem icon={ActivitySquare} label="Live Log Stream" active={false} />
              <SidebarItem icon={Settings} label="System Settings" active={false} />
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export default App
