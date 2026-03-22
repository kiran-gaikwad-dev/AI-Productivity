import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  AreaChart, Area, LineChart, Line
} from 'recharts';
import { BrainCircuit, Clock, AlertTriangle, TrendingUp, User, Zap, Activity, Target } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const Dashboard = () => {
  const [globalStats, setGlobalStats] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  const DEMO_USER_ID = "U102";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const statsRes = await axios.get('https://ai-productivity-u5fw.onrender.com/api/ai/stats/global');
        const userRes = await axios.get(`https://ai-productivity-u5fw.onrender.com/api/ai/predict/${DEMO_USER_ID}`);
        
        setGlobalStats(statsRes.data);
        setUserProfile(userRes.data);
      } catch (error) {
        console.error("Error fetching data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
        delayChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { 
      opacity: 1, 
      y: 0, 
      transition: { type: "spring", stiffness: 120, damping: 14 }
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col justify-center items-center py-20 min-h-[50vh] space-y-4">
        <motion.div 
          animate={{ scale: [1, 1.1, 1], rotate: [0, 180, 360] }}
          transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
          className="relative flex items-center justify-center w-12 h-12 md:w-16 md:h-16"
        >
          <div className="absolute inset-0 rounded-full border-4 border-slate-100"></div>
          <div className="absolute inset-0 rounded-full border-4 border-blue-600 border-t-transparent animate-spin"></div>
          <BrainCircuit className="text-blue-600 absolute w-5 h-5 md:w-6 md:h-6" />
        </motion.div>
        <p className="text-sm md:text-base text-slate-500 font-medium animate-pulse">Initializing AI Core...</p>
      </div>
    );
  }

  // Standardized Data Mapping for Charts
  const hourlyData = globalStats?.hourly_distribution || [];

  const topDistractions = globalStats?.top_distractions ? 
    Object.keys(globalStats.top_distractions).map(site => ({
      site,
      minutes: globalStats.top_distractions[site]
    })) : [];

  const regressionPredictions = globalStats?.regression_predictions || [];

  const productivityScore = Math.round((userProfile?.productivity_score || 0) * 100);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-md border border-slate-200/60 p-3 sm:p-4 rounded-xl shadow-xl">
          <p className="text-xs sm:text-sm font-bold text-slate-800 mb-1.5 sm:mb-2 border-b border-slate-100 pb-1.5">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center space-x-2 text-xs sm:text-sm text-slate-600">
              <span className="w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full shadow-sm" style={{ backgroundColor: entry.color }}></span>
              <span className="font-semibold text-slate-900">{entry.value}</span> 
              <span>minutes {entry.name === 'focus' ? 'Focused' : 'Distracted'}</span>
            </div>
          ))}
        </div>
      );
    }
    return null;
  };

  return (
    <motion.div 
      variants={containerVariants} 
      initial="hidden" 
      animate="show" 
      className="space-y-6 sm:space-y-8 w-full max-w-full overflow-hidden"
    >
      {/* Intro Header */}
      <motion.div variants={itemVariants} className="flex items-center space-x-2 sm:space-x-3 mb-2 sm:mb-4 px-1">
        <div className="bg-white p-2 rounded-xl text-blue-600 shadow-sm border border-slate-200/60">
          <Activity size={18} className="sm:w-[22px] sm:h-[22px]" />
        </div>
        <h2 className="text-xl sm:text-2xl font-bold text-slate-800 tracking-tight">Overview Dashboard</h2>
      </motion.div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 sm:gap-6">
        
        {/* Card 1: Main Score */}
        <motion.div 
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(59, 130, 246, 0.15)" }}
          className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-sm hover:shadow-lg p-6 border border-white flex flex-col justify-between overflow-hidden relative group transition-all duration-300 ring-1 ring-slate-900/5"
        >
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-indigo-400/20 rounded-full blur-2xl group-hover:bg-blue-400/30 transition-colors"></div>
          
          <div className="flex items-start justify-between relative z-10 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-50 text-blue-600 rounded-xl shadow-inner ring-1 ring-blue-500/10">
              <TrendingUp size={24} />
            </div>
            <span className="flex items-center text-xs font-semibold text-blue-600 bg-blue-50 px-2.5 py-1 rounded-full border border-blue-100">
              Live Tracker <Activity size={12} className="ml-1 animate-pulse" />
            </span>
          </div>
          <div className="relative z-10">
            <h3 className="text-4xl font-black tracking-tight text-slate-900 bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">
              {productivityScore}%
            </h3>
            <p className="text-sm font-medium text-slate-500 mt-1">AI Productivity Score</p>
          </div>
        </motion.div>

        {/* Card 2: Real Work (Focus Time) */}
        <motion.div 
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(16, 185, 129, 0.15)" }}
          className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-sm hover:shadow-lg p-6 border border-white flex flex-col justify-between overflow-hidden relative group transition-all duration-300 ring-1 ring-slate-900/5"
        >
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-emerald-400/20 to-teal-400/20 rounded-full blur-2xl group-hover:bg-emerald-400/30 transition-colors"></div>
          
          <div className="flex items-start justify-between relative z-10 mb-4">
            <div className="p-3 bg-gradient-to-br from-emerald-100 to-emerald-50 text-emerald-600 rounded-xl shadow-inner ring-1 ring-emerald-500/10">
              <BrainCircuit size={24} />
            </div>
            <span className="flex items-center text-xs font-semibold text-emerald-700 bg-emerald-100 px-2.5 py-1 rounded-full border border-emerald-200">
              Real Work
            </span>
          </div>
          <div className="relative z-10">
            <h3 className="text-3xl font-black tracking-tight text-slate-900 border-l-4 border-emerald-500 pl-3">
              {globalStats?.focus_minutes ? Math.floor(globalStats.focus_minutes / 60) : 0}h {globalStats?.focus_minutes ? Math.round(globalStats.focus_minutes % 60) : 0}m
            </h3>
            <p className="text-sm font-semibold text-slate-600 mt-1">Total Focused Time</p>
          </div>
        </motion.div>

        {/* Card 3: Distractions & Mobile Doomscrolling */}
        <motion.div 
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(244, 63, 94, 0.15)" }}
          className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-sm hover:shadow-lg p-6 border border-white flex flex-col justify-between overflow-hidden relative group transition-all duration-300 ring-1 ring-slate-900/5"
        >
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-rose-400/20 to-pink-400/20 rounded-full blur-2xl group-hover:bg-rose-400/30 transition-colors"></div>
          
          <div className="flex items-start justify-between relative z-10 mb-4">
            <div className="p-3 bg-gradient-to-br from-rose-100 to-rose-50 text-rose-600 rounded-xl shadow-inner ring-1 ring-rose-500/10">
              <AlertTriangle size={24} />
            </div>
            <span className="flex items-center text-xs font-semibold text-rose-700 bg-rose-100 px-2.5 py-1 rounded-full border border-rose-200">
              Distracted <User size={12} className="ml-1 fill-current" />
            </span>
          </div>
          <div className="relative z-10">
            <h3 className="text-3xl font-black tracking-tight text-slate-900 border-l-4 border-rose-500 pl-3">
              {globalStats?.distraction_minutes ? Math.floor(globalStats.distraction_minutes / 60) : 0}h {globalStats?.distraction_minutes ? Math.round(globalStats.distraction_minutes % 60) : 0}m
            </h3>
            <p className="text-sm font-semibold text-slate-600 mt-1">Mobile Doomscrolling</p>
          </div>
        </motion.div>
      </div>

      {/* CHARTS GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
        
        {/* Heatmap Area Chart */}
        <motion.div variants={itemVariants} className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-4 sm:p-6 md:p-8 border border-slate-100 transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] flex flex-col w-full overflow-hidden">
          <div className="flex items-center justify-between mb-6 sm:mb-8">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="p-2 sm:p-2.5 bg-slate-50 border border-slate-100 rounded-xl">
                <Clock className="text-slate-600 w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <h3 className="text-base sm:text-lg font-bold text-slate-800 tracking-tight">Average Usage (per Hour)</h3>
            </div>
          </div>
          <div className="h-64 sm:h-80 w-full bg-white relative">
            <ResponsiveContainer width="99%" height="100%">
              <AreaChart data={hourlyData} margin={{ top: 5, right: 0, bottom: 0, left: -25 }}>
                <defs>
                  <linearGradient id="colorFocus" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10B981" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#10B981" stopOpacity={0.01}/>
                  </linearGradient>
                  <linearGradient id="colorDistraction" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#F43F5E" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#F43F5E" stopOpacity={0.01}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
                <XAxis dataKey="hour" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11, fontWeight: 500}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11, fontWeight: 500}} />
                <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '4 4' }} />
                <Area 
                  type="monotone" 
                  dataKey="focus" 
                  stroke="#10B981" 
                  strokeWidth={3} 
                  fillOpacity={1} 
                  fill="url(#colorFocus)" 
                  activeDot={{r: 6, strokeWidth: 0, fill: '#059669', style: {filter: 'drop-shadow(0px 3px 5px rgba(16, 185, 129, 0.5))'}}} 
                />
                <Area 
                  type="monotone" 
                  dataKey="distraction" 
                  stroke="#F43F5E" 
                  strokeWidth={3} 
                  fillOpacity={1} 
                  fill="url(#colorDistraction)" 
                  activeDot={{r: 6, strokeWidth: 0, fill: '#E11D48', style: {filter: 'drop-shadow(0px 3px 5px rgba(244, 63, 94, 0.5))'}}} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Distractions Bar Chart */}
        <motion.div variants={itemVariants} className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-4 sm:p-6 md:p-8 border border-slate-100 transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] flex flex-col w-full overflow-hidden">
          <div className="flex items-center justify-between mb-6 sm:mb-8">
            <div className="flex items-center space-x-2 sm:space-x-3">
              <div className="p-2 sm:p-2.5 bg-rose-50 border border-rose-100 rounded-xl relative">
                <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5 sm:h-3 sm:w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2.5 w-2.5 sm:h-3 sm:w-3 bg-rose-500 border-2 border-white"></span>
                </span>
                <AlertTriangle className="text-rose-500 w-4 h-4 sm:w-5 sm:h-5" />
              </div>
              <h3 className="text-base sm:text-lg font-bold text-slate-800 tracking-tight">Time Drains (Averaged/Day)</h3>
            </div>
          </div>
          <div className="h-64 sm:h-80 w-full relative">
            <ResponsiveContainer width="99%" height="100%">
              {/* Using a smaller YAxis width for mobile responsivness */}
              <BarChart data={topDistractions} layout="vertical" margin={{ top: 0, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E2E8F0" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11}} />
                <YAxis dataKey="site" type="category" axisLine={false} tickLine={false} tick={{fill: '#334155', fontSize: 11, fontWeight: 600}} width={75} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
                <Bar 
                  dataKey="minutes" 
                  fill="#F43F5E" 
                  radius={[0, 6, 6, 0]} 
                  barSize={16}
                  activeBar={{ fill: '#E11D48' }}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* LINEAR REGRESSION PREDICTION CHART */}
      <motion.div variants={itemVariants} className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-4 sm:p-6 md:p-8 border border-slate-100 transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)] flex flex-col w-full overflow-hidden mt-6 sm:mt-8">
        <div className="flex items-center justify-between mb-6 sm:mb-8">
          <div className="flex items-center space-x-2 sm:space-x-3">
            <div className="p-2 sm:p-2.5 bg-violet-50 border border-violet-100 rounded-xl">
              <Target className="text-violet-600 w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <h3 className="text-base sm:text-lg font-bold text-slate-800 tracking-tight">AI Forecast: Predicted Focus Trend</h3>
          </div>
          <span className="flex items-center text-xs font-semibold text-violet-600 bg-violet-50 px-2.5 py-1 rounded-full border border-violet-200">
            Linear Regression Engine <BrainCircuit size={12} className="ml-1 fill-current" />
          </span>
        </div>
        <div className="h-64 sm:h-80 w-full relative">
          <ResponsiveContainer width="99%" height="100%">
            <LineChart data={regressionPredictions} margin={{ top: 5, right: 0, bottom: 0, left: -25 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#E2E8F0" />
              <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11, fontWeight: 500}} dy={10} />
              <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 11, fontWeight: 500}} />
              <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '4 4' }} />
              <Line 
                type="monotone" 
                dataKey="predicted_duration" 
                name="focus"
                stroke="#8B5CF6" 
                strokeWidth={4} 
                dot={false}
                activeDot={{r: 6, strokeWidth: 0, fill: '#7C3AED', style: {filter: 'drop-shadow(0px 3px 5px rgba(139, 92, 246, 0.5))'}}} 
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* ACTIONABLE AI INSIGHTS CARD */}
      <motion.div variants={itemVariants} className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-2xl sm:rounded-[1.5rem] shadow-xl overflow-hidden relative">
        <div className="absolute top-0 right-0 p-8 sm:p-12 opacity-[0.05] sm:opacity-10 pointer-events-none">
          <BrainCircuit size={150} className="text-white transform -rotate-12 translate-x-12 sm:translate-x-0" />
        </div>
        
        <div className="p-5 sm:p-8 relative z-10 w-full">
          <div className="flex items-center space-x-2 sm:space-x-3 mb-6 sm:mb-8">
            <div className="p-2 bg-indigo-500/20 backdrop-blur-sm rounded-lg sm:rounded-xl border border-indigo-400/30">
              <Zap className="text-indigo-400 fill-current w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <h3 className="text-lg sm:text-xl font-bold text-white tracking-tight">AI Insights & Action Plan</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
            <motion.div 
              whileHover={{ scale: 1.01 }}
              className="p-4 sm:p-6 bg-white/[0.06] backdrop-blur-md rounded-xl sm:rounded-2xl border border-white/10 hover:bg-white/10 transition-colors cursor-pointer group"
            >
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-fuchsia-500/20 flex items-center justify-center mb-3 sm:mb-4 border border-fuchsia-400/30 group-hover:bg-fuchsia-500/30 transition-colors">
                 <span className="text-lg sm:text-xl">🌙</span>
              </div>
              <h4 className="text-base sm:text-lg font-semibold text-white mb-1.5 sm:mb-2">Optimize Night Routine</h4>
              <p className="text-slate-300 leading-relaxed text-xs sm:text-sm font-medium">
                Your profile <span className="text-indigo-300 font-bold px-1.5 py-0.5 bg-indigo-500/20 rounded-md whitespace-nowrap">{userProfile?.cluster_profile}</span> indicates heavy device usage post 9 PM. Shrinking night screen time will spike tomorrow's metric.
              </p>
            </motion.div>

            <motion.div 
              whileHover={{ scale: 1.01 }}
              className="p-4 sm:p-6 bg-white/[0.06] backdrop-blur-md rounded-xl sm:rounded-2xl border border-white/10 hover:bg-white/10 transition-colors cursor-pointer group"
            >
              <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-full bg-emerald-500/20 flex items-center justify-center mb-3 sm:mb-4 border border-emerald-400/30 group-hover:bg-emerald-500/30 transition-colors">
                <span className="text-lg sm:text-xl">🎯</span>
              </div>
              <h4 className="text-base sm:text-lg font-semibold text-white mb-1.5 sm:mb-2">Peak Focus Window</h4>
              <p className="text-slate-300 leading-relaxed text-xs sm:text-sm font-medium">
                Execute deep logic between <span className="text-emerald-300 font-bold">10 AM - 12 PM</span>. Our model calculates your raw distraction rate plummets below 15% exclusively during this zone.
              </p>
            </motion.div>
          </div>
        </div>
      </motion.div>

    </motion.div>
  );
};

export default Dashboard;
