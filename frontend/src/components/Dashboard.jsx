import React, { useState, useEffect } from 'react';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, AreaChart, Area
} from 'recharts';
import { BrainCircuit, Clock, AlertTriangle, TrendingUp, User, Zap, Activity } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion'; // ADDED: Framer Motion for standard engaging animations

const Dashboard = () => {
  const [globalStats, setGlobalStats] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // We'll hardcode a user ID for demo purposes
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
    // Refresh for the live monitoring feel
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  // ADDED: Framer Motion variants for staggered entrance animations
  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.15,
        delayChildren: 0.2
      }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 30, scale: 0.95 },
    show: { 
      opacity: 1, 
      y: 0, 
      scale: 1,
      transition: { type: "spring", stiffness: 100, damping: 12 }
    }
  };

  if (loading) {
    return (
      // ADDED: Sleek loading state with pulsing gradients
      <div className="flex flex-col justify-center items-center h-full min-h-[60vh] space-y-4">
        <motion.div 
          animate={{ scale: [1, 1.2, 1], rotate: [0, 90, 0] }}
          transition={{ repeat: Infinity, duration: 2, ease: "easeInOut" }}
          className="relative flex items-center justify-center w-16 h-16"
        >
          <div className="absolute inset-0 rounded-full border-4 border-slate-100"></div>
          <div className="absolute inset-0 rounded-full border-4 border-blue-500 border-t-transparent animate-spin"></div>
          <BrainCircuit className="text-blue-500 absolute w-6 h-6 animate-pulse" />
        </motion.div>
        <p className="text-slate-500 font-medium animate-pulse">Initializing AI Core...</p>
      </div>
    );
  }

  // Formatting Data for Charts
  const hourlyData = globalStats?.hourly_distribution ? 
    Object.keys(globalStats.hourly_distribution).map(hour => ({
      hour: `${hour}:00`,
      minutes: globalStats.hourly_distribution[hour]
    })) : [];

  const topDistractions = globalStats?.top_distractions ? 
    Object.keys(globalStats.top_distractions).map(site => ({
      site,
      minutes: globalStats.top_distractions[site]
    })) : [];

  const productivityScore = Math.round((userProfile?.productivity_score || 0) * 100);

  // Custom Tooltip component for Recharts to maintain elegant design
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white/95 backdrop-blur-md border border-slate-100 p-4 rounded-xl shadow-xl">
          <p className="font-semibold text-slate-800 mb-2 border-b border-slate-100 pb-2">{label}</p>
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center space-x-2 text-sm text-slate-600">
              <span className="w-3 h-3 rounded-full shadow-sm" style={{ backgroundColor: entry.color }}></span>
              <span className="font-medium text-slate-900">{entry.value}</span> minutes
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
      className="space-y-8"
    >
      {/* Intro Header */}
      <motion.div variants={itemVariants} className="flex items-center space-x-2 pb-2">
        <div className="bg-blue-100 p-2 rounded-xl text-blue-600 shadow-sm border border-blue-200">
          <Activity size={20} />
        </div>
        <h2 className="text-2xl font-bold text-slate-800 tracking-tight">Overview Dashboard</h2>
      </motion.div>

      {/* Overview Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* ADDED: Interactive hover effects and glassmorphism styling for cards */}
        <motion.div 
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(59, 130, 246, 0.15)" }}
          className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-sm hover:shadow-lg p-6 border border-white flex flex-col justify-between overflow-hidden relative group transition-all duration-300 ring-1 ring-slate-900/5"
        >
          {/* Decorative background element */}
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-blue-400/20 to-indigo-400/20 rounded-full blur-2xl group-hover:bg-blue-400/30 transition-colors"></div>
          
          <div className="flex items-start justify-between relative z-10 mb-4">
            <div className="p-3 bg-gradient-to-br from-blue-100 to-blue-50 text-blue-600 rounded-xl shadow-inner ring-1 ring-blue-500/10">
              <TrendingUp size={24} />
            </div>
            <span className="flex items-center text-xs font-semibold text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-100">
              +12% <TrendingUp size={12} className="ml-1" />
            </span>
          </div>
          <div className="relative z-10">
            <h3 className="text-4xl font-black tracking-tight text-slate-900 bg-clip-text text-transparent bg-gradient-to-r from-blue-700 to-indigo-700">
              {productivityScore}%
            </h3>
            <p className="text-sm font-medium text-slate-500 mt-1">Your Productivity Score</p>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(99, 102, 241, 0.15)" }}
          className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-sm hover:shadow-lg p-6 border border-white flex flex-col justify-between overflow-hidden relative group transition-all duration-300 ring-1 ring-slate-900/5"
        >
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-indigo-400/20 to-purple-400/20 rounded-full blur-2xl group-hover:bg-indigo-400/30 transition-colors"></div>
          
          <div className="flex items-start justify-between relative z-10 mb-4">
            <div className="p-3 bg-gradient-to-br from-indigo-100 to-indigo-50 text-indigo-600 rounded-xl shadow-inner ring-1 ring-indigo-500/10">
              <User size={24} />
            </div>
            <span className="flex items-center text-xs font-semibold text-indigo-600 bg-indigo-50 px-2.5 py-1 rounded-full border border-indigo-100">
              Synced <Zap size={12} className="ml-1 fill-current" />
            </span>
          </div>
          <div className="relative z-10">
            <h3 className="text-2xl font-bold tracking-tight text-slate-900 line-clamp-1">
              {userProfile?.cluster_profile || "Analyzing..."}
            </h3>
            <p className="text-sm font-medium text-slate-500 mt-1">AI Identified Persona</p>
          </div>
        </motion.div>

        <motion.div 
          variants={itemVariants}
          whileHover={{ y: -5, boxShadow: "0 25px 50px -12px rgba(249, 115, 22, 0.15)" }}
          className="bg-white/60 backdrop-blur-xl rounded-2xl shadow-sm hover:shadow-lg p-6 border border-white flex flex-col justify-between overflow-hidden relative group transition-all duration-300 ring-1 ring-slate-900/5"
        >
          <div className="absolute -right-8 -top-8 w-32 h-32 bg-gradient-to-br from-orange-400/20 to-pink-400/20 rounded-full blur-2xl group-hover:bg-orange-400/30 transition-colors"></div>
          
          <div className="flex items-start justify-between relative z-10 mb-4">
            <div className="p-3 bg-gradient-to-br from-orange-100 to-orange-50 text-orange-600 rounded-xl shadow-inner ring-1 ring-orange-500/10">
              <BrainCircuit size={24} />
            </div>
          </div>
          <div className="relative z-10">
            <h3 className="text-4xl font-black tracking-tight text-slate-900">
              {Math.round((globalStats?.overall_productivity_score || 0) * 100)}%
            </h3>
            <p className="text-sm font-medium text-slate-500 mt-1">Global Average Score</p>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* ADDED: Elevated chart containers with Area chart replacing Line for more premium look */}
        <motion.div variants={itemVariants} className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 border border-slate-100 transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-slate-50 rounded-xl">
                <Clock className="text-slate-500" size={20} />
              </div>
              <h3 className="text-lg font-bold text-slate-800 tracking-tight">Activity Heatmap</h3>
            </div>
            <select className="bg-slate-50 border border-slate-200 text-slate-600 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block px-3 py-2 font-medium">
              <option>Today</option>
              <option>Last 7 Days</option>
            </select>
          </div>
          <div className="h-80 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              {/* Used AreaChart for a stunning filled gradient effect */}
              <AreaChart data={hourlyData} margin={{ top: 5, right: 0, bottom: 5, left: -20 }}>
                <defs>
                  <linearGradient id="colorMinutes" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="hour" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 13, fontWeight: 500}} dy={10} />
                <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 13, fontWeight: 500}} />
                <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#cbd5e1', strokeWidth: 1, strokeDasharray: '4 4' }} />
                <Area 
                  type="monotone" 
                  dataKey="minutes" 
                  stroke="#3B82F6" 
                  strokeWidth={4} 
                  fillOpacity={1} 
                  fill="url(#colorMinutes)" 
                  activeDot={{r: 8, strokeWidth: 0, fill: '#2563EB', style: {filter: 'drop-shadow(0px 4px 6px rgba(37, 99, 235, 0.4))'}}} 
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Top Distractions Chart styled with curved bars */}
        <motion.div variants={itemVariants} className="bg-white rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] p-8 border border-slate-100 transition-all duration-500 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]">
          <div className="flex items-center space-x-3 mb-8">
            <div className="p-2.5 bg-red-50 rounded-xl relative">
              <span className="absolute -top-1 -right-1 flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500 border-2 border-white"></span>
              </span>
              <AlertTriangle className="text-red-500" size={20} />
            </div>
            <h3 className="text-lg font-bold text-slate-800 tracking-tight">Time Drains</h3>
          </div>
          <div className="h-80 w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={topDistractions} layout="vertical" margin={{ top: 5, right: 30, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 13}} />
                <YAxis dataKey="site" type="category" axisLine={false} tickLine={false} tick={{fill: '#475569', fontSize: 13, fontWeight: 600}} width={110} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
                {/* Stunning rounded colored bars with drop shadows */}
                <Bar 
                  dataKey="minutes" 
                  fill="#F43F5E" 
                  radius={[0, 8, 8, 0]} 
                  barSize={20}
                  activeBar={{ fill: '#E11D48' }}
                  isAnimationActive={true}
                  animationDuration={1500}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>

      {/* AI Recommendations - Re-styled for premium feel */}
      <motion.div variants={itemVariants} className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-3xl shadow-xl overflow-hidden relative">
        <div className="absolute top-0 right-0 p-12 opacity-10 pointer-events-none">
          <BrainCircuit size={200} className="text-white transform -rotate-12" />
        </div>
        
        <div className="p-8 relative z-10">
          <div className="flex items-center space-x-3 mb-8">
            <div className="p-2 bg-indigo-500/20 backdrop-blur-sm rounded-lg border border-indigo-400/30">
              <Zap className="text-indigo-400 fill-current" size={24} />
            </div>
            <h3 className="text-xl font-bold text-white tracking-tight">AI Insights & Action Plan</h3>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <motion.div 
              whileHover={{ scale: 1.02 }}
              className="p-6 bg-white/10 backdrop-blur-md rounded-2xl border border-white/10 hover:bg-white/15 transition-all cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-full bg-purple-500/20 flex items-center justify-center mb-4 border border-purple-400/30 group-hover:bg-purple-500/30 transition-colors">
                 <span className="text-xl">🌙</span>
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">Optimize Night Routine</h4>
              <p className="text-slate-300 leading-relaxed text-sm font-medium">
                Your profile <span className="text-indigo-300 font-bold px-1 bg-indigo-500/20 rounded">{userProfile?.cluster_profile}</span> indicates heavy device usage post 9 PM. Reducing screen time by 30% could boost tomorrow's scores.
              </p>
            </motion.div>

            <motion.div 
              whileHover={{ scale: 1.02 }}
              className="p-6 bg-white/10 backdrop-blur-md rounded-2xl border border-white/10 hover:bg-white/15 transition-all cursor-pointer group"
            >
              <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center mb-4 border border-emerald-400/30 group-hover:bg-emerald-500/30 transition-colors">
                <span className="text-xl">🎯</span>
              </div>
              <h4 className="text-lg font-semibold text-white mb-2">Peak Focus Window</h4>
              <p className="text-slate-300 leading-relaxed text-sm font-medium">
                Schedule your most intensive work between <span className="text-emerald-300 font-bold">10 AM - 12 PM</span>. Your distraction rate historically drops below 15% during this period.
              </p>
            </motion.div>
          </div>
        </div>
      </motion.div>

    </motion.div>
  );
};

export default Dashboard;
