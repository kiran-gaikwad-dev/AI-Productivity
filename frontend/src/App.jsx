import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import Dashboard from './components/Dashboard'

function App() {
  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-800 flex flex-col selection:bg-blue-200 overflow-x-hidden">
      {/* Mobile-Responsive Glassmorphism Header */}
      <motion.header 
        initial={{ y: -50, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="sticky top-0 z-50 bg-white/80 backdrop-blur-md shadow-sm border-b border-slate-200 px-4 sm:px-6 md:px-8 py-4 flex flex-col sm:flex-row justify-between items-center gap-4 sm:gap-0"
      >
        <div className="flex items-center space-x-3 w-full sm:w-auto justify-center sm:justify-start">
          <motion.div 
            whileHover={{ rotate: 180 }}
            transition={{ duration: 0.5 }}
            className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-indigo-600 shadow-md flex items-center justify-center shrink-0"
          >
            <div className="w-3 h-3 bg-white rounded-full" />
          </motion.div>
          <h1 className="text-lg sm:text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-slate-900 to-slate-600 tracking-tight text-center sm:text-left">
            AI Productivity Analyzer
          </h1>
        </div>
        
        <motion.div 
          whileHover={{ scale: 1.05 }}
          className="flex items-center"
        >
          <span className="flex items-center text-xs sm:text-sm font-medium text-blue-700 bg-blue-50 px-3 sm:px-4 py-1.5 rounded-full border border-blue-200 shadow-sm whitespace-nowrap">
            <span className="relative flex h-2 w-2 sm:h-2.5 sm:w-2.5 mr-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 sm:h-2.5 sm:w-2.5 bg-blue-500"></span>
            </span>
            Live Monitoring
          </span>
        </motion.div>
      </motion.header>
      
      {/* Fully fluid main content area padding */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 sm:p-6 md:p-8">
        <Dashboard />
      </main>
    </div>
  )
}

export default App
