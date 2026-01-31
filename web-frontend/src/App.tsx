import { useState, useEffect } from 'react';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement } from 'chart.js';
import { Bar, Doughnut, Line } from 'react-chartjs-2';
import {
  Upload, FileText, Activity, Download,
  LayoutDashboard, History, FileUp, Menu, X,
  AlertTriangle, CheckCircle, Zap, Settings,
  Brain, Wrench, Clock, TrendingUp, Save, RefreshCw,
  Bell, Calendar, Mail, Plus, Trash2, Sun, Moon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

// Register ChartJS components
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement, PointElement, LineElement);

// Chart Global Defaults
ChartJS.defaults.color = '#94a3b8';
ChartJS.defaults.borderColor = '#334155';

const API_URL = 'http://127.0.0.1:8000/api';


// --- Components ---

const SidebarItem = ({
  icon: Icon,
  label,
  isActive,
  onClick
}: any) => (
  <motion.button
    onClick={onClick}
    whileHover={{ x: 4 }}
    whileTap={{ scale: 0.98 }}
    className={clsx(
      "w-full flex items-center gap-4 px-4 py-3.5 rounded-2xl transition-all duration-300 group relative overflow-hidden",
      isActive ? "nav-item-active" : "text-slate-400"
    )}
  >
    {isActive && (
      <motion.div
        layoutId="active-pill"
        className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-transparent z-0 opacity-50"
      />
    )}
    <Icon className={clsx("relative z-10", isActive ? "text-indigo-400" : "text-slate-500")} size={20} />
    <span className="relative z-10 font-semibold text-[15px]">{label}</span>
  </motion.button>
);

const StatCard = ({ title, value, unit, icon: Icon, color, description }: any) => (
  <motion.div
    initial={{ opacity: 0, y: 24 }}
    animate={{ opacity: 1, y: 0 }}
    whileHover={{ y: -6, scale: 1.02 }}
    transition={{ type: "spring", stiffness: 400, damping: 25 }}
    className="stat-card-3d glass-card p-7 rounded-2xl relative overflow-hidden cursor-pointer group card-3d lift-3d"
  >
    {/* Ambient glow */}
    <div className={`absolute -right-8 -top-8 w-36 h-36 bg-gradient-to-br from-${color}-500/15 via-${color}-400/5 to-transparent rounded-full blur-2xl transition-all duration-500 group-hover:scale-110`} />
    <div className={`absolute -left-4 -bottom-4 w-20 h-20 bg-${color}-500/8 rounded-full blur-xl`} />

    <div className="relative z-10">
      <div className="flex justify-between items-start gap-4">
        <div className="flex-1">
          <p className="text-slate-400 text-[11px] font-semibold uppercase tracking-widest mb-2">{title}</p>
          <h3 className="text-3xl font-bold tracking-tight">
            {value}
            {unit && <span className="text-base opacity-60 font-normal ml-1">{unit}</span>}
          </h3>
          {description && (
            <p className="opacity-70 text-sm mt-2.5 leading-relaxed">{description}</p>
          )}
        </div>
        <motion.div
          whileHover={{ rotate: 8, scale: 1.1 }}
          transition={{ type: "spring", stiffness: 400, damping: 20 }}
          className={`p-3.5 rounded-2xl bg-${color}-500/10 text-${color}-600 dark:text-${color}-400 border border-${color}-500/10 shadow-lg`}
        >
          <Icon size={22} strokeWidth={2.5} />
        </motion.div>
      </div>
    </div>
  </motion.div>
);

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [file, setFile] = useState<File | null>(null);
  const [data, setData] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [msg, setMsg] = useState('');
  const [isSidebarOpen, setSidebarOpen] = useState(true);

  // New states for ML Predictions and Thresholds
  const [thresholds, setThresholds] = useState<any>({
    pressure_warning: 70,
    pressure_critical: 80,
    temperature_warning: 130,
    temperature_critical: 150,
    flowrate_min: 10,
    flowrate_max: 200
  });
  const [predictions, setPredictions] = useState<any>(null);
  const [savingSettings, setSavingSettings] = useState(false);
  const [notification, setNotification] = useState<{ type: 'success' | 'error' | 'warning', message: string } | null>(null);

  // NEW FEATURE STATES
  // Historical Trends
  const [trendData, setTrendData] = useState<any>(null);
  const [selectedEquipment, setSelectedEquipment] = useState<string>('');
  const [trendDays, setTrendDays] = useState<number>(30);

  // Alert Settings
  const [alertSettings, setAlertSettings] = useState<any>({
    email_enabled: false,
    email_address: '',
    alert_on_critical: true,
    alert_on_warning: false,
    alert_on_maintenance_due: true,
    alert_frequency: 'immediate',
    maintenance_reminder_days: 3
  });
  const [alertLogs, setAlertLogs] = useState<any[]>([]);

  // Maintenance Scheduling
  const [maintenanceData, setMaintenanceData] = useState<any>(null);
  const [showAddMaintenance, setShowAddMaintenance] = useState(false);
  const [newMaintenance, setNewMaintenance] = useState({
    equipment_name: '',
    equipment_type: '',
    title: '',
    description: '',
    scheduled_date: '',
    scheduled_time: '',
    priority: 'medium',
    assigned_to: '',
    estimated_duration: 60,
    notes: ''
  });

  // Theme State
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const saved = localStorage.getItem('theme');
    return saved === 'dark' || (!saved && window.matchMedia('(prefers-color-scheme: dark)').matches);
  });

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      ChartJS.defaults.color = '#94a3b8';
      ChartJS.defaults.borderColor = 'rgba(255,255,255,0.1)';
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      ChartJS.defaults.color = '#475569';
      ChartJS.defaults.borderColor = 'rgba(0,0,0,0.05)';
    }
  }, [isDarkMode]);

  // Initial Fetch
  useEffect(() => {
    fetchHistory();
    fetchThresholds();
  }, []);

  // Auto-hide notifications
  useEffect(() => {
    if (notification) {
      const timer = setTimeout(() => setNotification(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [notification]);

  const fetchThresholds = async () => {
    try {
      const res = await axios.get(`${API_URL}/thresholds/`);
      setThresholds(res.data);
    } catch (err) {
      console.error('Failed to fetch thresholds:', err);
    }
  };

  const fetchPredictions = async () => {
    try {
      const res = await axios.get(`${API_URL}/predict/`);
      setPredictions(res.data);

      // Show notification for critical items
      const criticalCount = res.data.summary?.critical || 0;
      if (criticalCount > 0) {
        setNotification({
          type: 'warning',
          message: `⚠️ ${criticalCount} equipment require immediate attention!`
        });
      }
    } catch (err) {
      console.error('Failed to fetch predictions:', err);
    }
  };

  const saveThresholds = async () => {
    setSavingSettings(true);
    try {
      await axios.put(`${API_URL}/thresholds/`, thresholds);
      setNotification({ type: 'success', message: '✅ Thresholds saved successfully!' });
      // Re-fetch predictions with new thresholds
      fetchPredictions();
    } catch (err) {
      setNotification({ type: 'error', message: '❌ Failed to save thresholds' });
    }
    setSavingSettings(false);
  };

  const fetchHistory = async () => {
    try {
      const res = await axios.get(`${API_URL}/history/`);
      setHistory(res.data);
      // Auto-load latest data if available for dashboard preview
      if (res.data.length > 0 && !data) {
        // Optionally could load the details of the latest entry if API supported it, 
        // but for now we wait for user upload or leave empty.
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    try {
      setMsg('uploading');
      const res = await axios.post(`${API_URL}/upload/`, formData);
      setData(res.data);
      setMsg('success');
      fetchHistory();
      fetchPredictions();

      // Show notification based on predictions
      const criticalCount = res.data.prediction_summary?.critical_count || 0;
      if (criticalCount > 0) {
        setNotification({
          type: 'warning',
          message: `🚨 ${criticalCount} equipment flagged as critical risk!`
        });
      } else {
        setNotification({
          type: 'success',
          message: '✅ Analysis complete! All equipment within safe parameters.'
        });
      }

      setTimeout(() => setActiveTab('dashboard'), 800);
    } catch (err: any) {
      setMsg('error:' + (err.response?.data?.error || err.message));
      setNotification({ type: 'error', message: '❌ Upload failed: ' + (err.response?.data?.error || err.message) });
    }
  };

  const downloadReport = async () => {
    try {
      const res = await axios.get(`${API_URL}/report_pdf/`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'Chemical_Analysis_Report.pdf');
      document.body.appendChild(link);
      link.click();
    } catch (e) {
      alert("Failed to download PDF");
    }
  };

  // ============= NEW FEATURE API FUNCTIONS =============

  // Historical Trends
  const fetchTrendData = async (equipment?: string, days?: number) => {
    try {
      const params = new URLSearchParams();
      if (equipment) params.append('equipment', equipment);
      if (days) params.append('days', days.toString());

      const res = await axios.get(`${API_URL}/equipment-history/?${params.toString()}`);
      setTrendData(res.data);
    } catch (err) {
      console.error('Failed to fetch trends:', err);
    }
  };

  // Alert Settings
  const fetchAlertSettings = async () => {
    try {
      const res = await axios.get(`${API_URL}/alerts/settings/`);
      setAlertSettings(res.data);
    } catch (err) {
      console.error('Failed to fetch alert settings:', err);
    }
  };

  const saveAlertSettings = async () => {
    setSavingSettings(true);
    try {
      await axios.put(`${API_URL}/alerts/settings/`, alertSettings);
      setNotification({ type: 'success', message: '✅ Alert settings saved!' });
    } catch (err) {
      setNotification({ type: 'error', message: '❌ Failed to save alert settings' });
    }
    setSavingSettings(false);
  };

  const fetchAlertLogs = async () => {
    try {
      const res = await axios.get(`${API_URL}/alerts/logs/`);
      setAlertLogs(res.data);
    } catch (err) {
      console.error('Failed to fetch alert logs:', err);
    }
  };

  const sendTestAlert = async () => {
    try {
      const res = await axios.post(`${API_URL}/alerts/test/`);
      if (res.data.success) {
        setNotification({ type: 'success', message: '✅ Test alert sent!' });
      } else {
        setNotification({ type: 'error', message: res.data.message });
      }
    } catch (err: any) {
      setNotification({ type: 'error', message: err.response?.data?.message || 'Failed to send test alert' });
    }
  };

  // Maintenance Scheduling
  const fetchMaintenance = async () => {
    try {
      const res = await axios.get(`${API_URL}/maintenance/`);
      setMaintenanceData(res.data);
    } catch (err) {
      console.error('Failed to fetch maintenance:', err);
    }
  };

  const createMaintenance = async () => {
    try {
      await axios.post(`${API_URL}/maintenance/`, newMaintenance);
      setNotification({ type: 'success', message: '✅ Maintenance scheduled!' });
      setShowAddMaintenance(false);
      setNewMaintenance({
        equipment_name: '',
        equipment_type: '',
        title: '',
        description: '',
        scheduled_date: '',
        scheduled_time: '',
        priority: 'medium',
        assigned_to: '',
        estimated_duration: 60,
        notes: ''
      });
      fetchMaintenance();
    } catch (err) {
      setNotification({ type: 'error', message: '❌ Failed to schedule maintenance' });
    }
  };

  const updateMaintenanceStatus = async (id: number, status: string) => {
    try {
      await axios.put(`${API_URL}/maintenance/${id}/`, { status });
      setNotification({ type: 'success', message: '✅ Status updated!' });
      fetchMaintenance();
    } catch (err) {
      setNotification({ type: 'error', message: '❌ Failed to update status' });
    }
  };

  const deleteMaintenance = async (id: number) => {
    if (!window.confirm('Are you sure you want to delete this schedule?')) return;
    try {
      await axios.delete(`${API_URL}/maintenance/${id}/`);
      setNotification({ type: 'success', message: '✅ Schedule deleted' });
      fetchMaintenance();
    } catch (err) {
      setNotification({ type: 'error', message: '❌ Failed to delete' });
    }
  };

  const autoScheduleMaintenance = async () => {
    try {
      const res = await axios.post(`${API_URL}/maintenance/auto-schedule/`);
      setNotification({ type: 'success', message: `✅ ${res.data.message}` });
      fetchMaintenance();
    } catch (err) {
      setNotification({ type: 'error', message: '❌ Failed to auto-schedule maintenance' });
    }
  };

  // Chart Data Preparation
  const chartData = data ? {
    labels: Object.keys(data.type_distribution),
    datasets: [
      {
        label: 'Equipment Count',
        data: Object.values(data.type_distribution),
        backgroundColor: [
          'rgba(99, 102, 241, 0.6)',  // Indigo
          'rgba(16, 185, 129, 0.6)',  // Emerald
          'rgba(244, 63, 94, 0.6)',   // Rose
          'rgba(245, 158, 11, 0.6)',  // Amber
        ],
        borderColor: [
          'rgba(99, 102, 241, 1)',
          'rgba(16, 185, 129, 1)',
          'rgba(244, 63, 94, 1)',
          'rgba(245, 158, 11, 1)',
        ],
        borderWidth: 1,
      },
    ],
  } : { labels: [], datasets: [] };

  return (
    <div className="flex min-h-screen text-slate-200 overflow-hidden perspective-container">

      {/* Organic Background Blobs */}
      <div className="fixed -top-24 -left-24 w-96 h-96 bg-indigo-500/10 blur-[120px] blob-shape pointer-events-none z-0" />
      <div className="fixed top-1/2 -right-24 w-[500px] h-[500px] bg-purple-500/10 blur-[150px] blob-shape pointer-events-none z-0" />
      <div className="fixed -bottom-24 left-1/2 w-80 h-80 bg-blue-500/10 blur-[100px] blob-shape pointer-events-none z-0" />

      {/* Sidebar with 3D Depth */}
      <motion.aside
        animate={{ width: isSidebarOpen ? 300 : 80 }}
        className="glass-depth-refined border-r border-white/5 relative flex-shrink-0 z-20"
      >
        {/* Logo - Refined */}
        <div className="p-5 flex items-center gap-3.5 mb-6">
          <motion.div
            whileHover={{ rotate: 5, scale: 1.05 }}
            transition={{ type: "spring", stiffness: 400, damping: 15 }}
            className="w-11 h-11 rounded-xl bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/25"
          >
            <Activity className="text-white" size={22} strokeWidth={2.5} />
          </motion.div>
          {isSidebarOpen && (
            <motion.div
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3 }}
            >
              <h1 className="font-bold text-lg leading-tight text-white tracking-tight">ChemPulse AI</h1>
              <p className="text-[11px] text-indigo-400 font-bold uppercase tracking-widest">Analytics Suite</p>
            </motion.div>
          )}
        </div>

        <nav className="px-4 space-y-2">
          <SidebarItem
            icon={LayoutDashboard}
            label="Dashboard"
            isActive={activeTab === 'dashboard'}
            onClick={() => setActiveTab('dashboard')}
          />
          <SidebarItem
            icon={FileUp}
            label="Upload Data"
            isActive={activeTab === 'upload'}
            onClick={() => setActiveTab('upload')}
          />
          <SidebarItem
            icon={History}
            label="History"
            isActive={activeTab === 'history'}
            onClick={() => setActiveTab('history')}
          />
          <SidebarItem
            icon={Zap}
            label="Visualizer"
            isActive={activeTab === 'visualizer'}
            onClick={() => setActiveTab('visualizer')}
          />
          <SidebarItem
            icon={Brain}
            label="ML Predictions"
            isActive={activeTab === 'predictions'}
            onClick={() => { setActiveTab('predictions'); fetchPredictions(); }}
          />

          {/* NEW FEATURE TABS */}
          <SidebarItem
            icon={TrendingUp}
            label="Trends"
            isActive={activeTab === 'trends'}
            onClick={() => { setActiveTab('trends'); fetchTrendData(selectedEquipment, trendDays); }}
          />
          <SidebarItem
            icon={Bell}
            label="Alerts"
            isActive={activeTab === 'alerts'}
            onClick={() => { setActiveTab('alerts'); fetchAlertSettings(); fetchAlertLogs(); }}
          />
          <SidebarItem
            icon={Calendar}
            label="Maintenance"
            isActive={activeTab === 'maintenance'}
            onClick={() => { setActiveTab('maintenance'); fetchMaintenance(); }}
          />

          <SidebarItem
            icon={Settings}
            label="Thresholds"
            isActive={activeTab === 'settings'}
            onClick={() => setActiveTab('settings')}
          />
        </nav>

        {/* Theme & User Section */}
        <div className="absolute bottom-5 left-0 w-full px-4 space-y-3">
          <motion.button
            onClick={() => setIsDarkMode(!isDarkMode)}
            whileHover={{ scale: 1.02, x: 2 }}
            whileTap={{ scale: 0.98 }}
            className={clsx(
              "w-full glass-card p-3 rounded-xl flex items-center gap-3 border transition-colors",
              !isSidebarOpen && "justify-center"
            )}
          >
            <div className={clsx(
              "p-2 rounded-lg",
              isDarkMode ? "bg-amber-500/10 text-amber-500" : "bg-indigo-500/10 text-indigo-600"
            )}>
              {isDarkMode ? <Sun size={18} /> : <Moon size={18} />}
            </div>
            {isSidebarOpen && (
              <span className="text-sm font-semibold">
                {isDarkMode ? 'Light Mode' : 'Dark Mode'}
              </span>
            )}
          </motion.button>

          <motion.div
            whileHover={{ y: -2, scale: 1.01 }}
            transition={{ type: "spring", stiffness: 400, damping: 25 }}
            className={clsx("glass-card p-3.5 rounded-2xl flex items-center gap-3 border border-indigo-500/10 cursor-pointer", !isSidebarOpen && "justify-center")}
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 via-teal-500 to-cyan-500 flex items-center justify-center shadow-md text-white text-lg">
              🔬
            </div>
            {isSidebarOpen && (
              <div className="overflow-hidden flex-1">
                <p className="text-sm font-medium truncate">Lab Analyst</p>
                <p className="text-xs text-slate-400">Ready to explore</p>
              </div>
            )}
          </motion.div>
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setSidebarOpen(!isSidebarOpen)}
          className="absolute -right-3 top-20 w-7 h-7 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-110 transition-all duration-300 z-50 text-white"
        >
          {isSidebarOpen ? <X size={14} /> : <Menu size={14} />}
        </button>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative scroll-smooth">
        <div className="p-6 lg:p-10 xl:p-12 max-w-7xl mx-auto">

          <AnimatePresence mode="wait">

            {/* DASHBOARD VIEW */}
            {activeTab === 'dashboard' && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
                className="space-y-10 perspective-container"
              >
                <div className="flex flex-col lg:flex-row justify-between lg:items-end gap-6 mb-12">
                  <div className="space-y-2">
                    <motion.div
                      initial={{ opacity: 0, scale: 0.9 }}
                      animate={{ opacity: 1, scale: 1 }}
                      className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-[11px] font-bold uppercase tracking-wider mb-2"
                    >
                      <Activity size={12} /> System Status: Operational
                    </motion.div>
                    <motion.h2
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="text-4xl lg:text-5xl font-extrabold tracking-tight text-premium"
                    >
                      Welcome, <span className="text-indigo-400">Analyst</span>! ✨
                    </motion.h2>
                    <p className="text-slate-400 text-lg lg:text-xl font-medium">Your equipment fleet is performing <span className="text-emerald-500 font-bold">optimally</span> today. No major concerns detected.</p>
                  </div>
                  {data && (
                    <div className="flex items-center gap-4">
                      <motion.button
                        whileHover={{ scale: 1.05, y: -2 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={downloadReport}
                        className="btn-primary"
                      >
                        <Download size={18} /> Export Full PDF
                      </motion.button>
                    </div>
                  )}
                </div>

                {!data ? (
                  <motion.div
                    initial={{ scale: 0.95, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="card-3d glass-depth rounded-3xl p-16 text-center border border-white/5 flex flex-col items-center justify-center min-h-[450px]"
                  >
                    <motion.div
                      animate={{ y: [0, -10, 0] }}
                      transition={{ duration: 3, repeat: Infinity, ease: "easeInOut" }}
                      className="w-24 h-24 rounded-3xl bg-gradient-to-br from-indigo-500/20 to-purple-500/20 flex items-center justify-center mb-8 border border-indigo-500/20"
                    >
                      <LayoutDashboard size={48} className="text-indigo-400" />
                    </motion.div>
                    <h3 className="text-2xl font-semibold text-white mb-3">No data yet — let's fix that! 🚀</h3>
                    <p className="text-slate-400 max-w-md mb-8 leading-relaxed">
                      Upload your equipment CSV file and we'll instantly analyze it, detect anomalies, and show you beautiful visualizations.
                    </p>
                    <motion.button
                      whileHover={{ scale: 1.05, y: -3 }}
                      whileTap={{ scale: 0.95 }}
                      onClick={() => setActiveTab('upload')}
                      className="btn-3d bg-gradient-to-r from-indigo-600 to-purple-600 text-white font-semibold py-4 px-8 rounded-xl flex items-center gap-2"
                    >
                      <Upload size={20} /> Upload Your First Dataset
                    </motion.button>
                  </motion.div>
                ) : (
                  <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                      <StatCard title="Equipment Count" value={data.total_count} unit="units" icon={Activity} color="indigo" description="Total tracked" />
                      <StatCard title="System Health" value={data.health_score || 100} unit="%" icon={data.health_score < 70 ? AlertTriangle : CheckCircle} color={data.health_score < 70 ? "rose" : "emerald"} description={data.health_score < 70 ? "Needs attention" : "Looking great!"} />
                      <StatCard title="Avg Flowrate" value={data.avg_flowrate.toFixed(1)} unit="L/h" icon={Activity} color="cyan" description="Across all units" />
                      <StatCard title="Avg Pressure" value={data.avg_pressure.toFixed(1)} unit="Bar" icon={Activity} color="amber" description="System average" />
                    </div>

                    {(data.critical_items?.length || 0) > 0 && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="lift-3d bg-gradient-to-r from-rose-500/10 to-orange-500/5 border border-rose-500/20 rounded-2xl p-6 flex items-start gap-4"
                      >
                        <motion.div
                          animate={{ rotate: [0, -10, 10, 0] }}
                          transition={{ duration: 2, repeat: Infinity }}
                          className="p-3 bg-rose-500/20 rounded-xl text-rose-400"
                        >
                          <AlertTriangle size={24} />
                        </motion.div>
                        <div>
                          <h3 className="text-lg font-bold text-white flex items-center gap-2">
                            ⚠️ Heads up! Some equipment needs attention
                          </h3>
                          <p className="text-rose-200/80 mb-3">
                            We found {data.critical_items.length} {data.critical_items.length === 1 ? 'unit' : 'units'} operating outside safe parameters. Let's take a look:
                          </p>
                          <div className="flex gap-2 flex-wrap">
                            {data.critical_items.slice(0, 5).map((item: any, idx: number) => (
                              <motion.span
                                key={idx}
                                whileHover={{ scale: 1.05 }}
                                className="px-3 py-1.5 rounded-full bg-rose-500/20 text-rose-200 text-xs font-medium border border-rose-500/30 cursor-pointer hover:bg-rose-500/30 transition-colors"
                              >
                                {item['Equipment Name']} • {item.Pressure} Bar
                              </motion.span>
                            ))}
                            {data.critical_items.length > 5 && (
                              <span className="text-xs text-rose-300 self-center">+{data.critical_items.length - 5} more</span>
                            )}
                          </div>
                        </div>
                      </motion.div>
                    )}

                    {/* Charts with 3D Effect */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                      <motion.div
                        whileHover={{ y: -5, scale: 1.01 }}
                        className="chart-container-3d glass-depth p-6 rounded-2xl border border-white/5"
                      >
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-3">
                          <span className="w-3 h-8 bg-gradient-to-b from-indigo-500 to-purple-500 rounded-full"></span>
                          Equipment Mix
                        </h3>
                        <div className="h-64 flex items-center justify-center">
                          <Doughnut data={chartData} options={{ maintainAspectRatio: false }} />
                        </div>
                      </motion.div>
                      <motion.div
                        whileHover={{ y: -5, scale: 1.01 }}
                        className="chart-container-3d glass-depth p-6 rounded-2xl border border-white/5"
                      >
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-3">
                          <span className="w-3 h-8 bg-gradient-to-b from-emerald-500 to-teal-500 rounded-full"></span>
                          Quantity Overview
                        </h3>
                        <div className="h-64">
                          <Bar data={chartData} options={{ maintainAspectRatio: false, scales: { y: { grid: { color: 'rgba(255,255,255,0.05)' } }, x: { grid: { display: false } } } }} />
                        </div>
                      </motion.div>
                    </div>
                  </>
                )}
              </motion.div>
            )}

            {/* UPLOAD VIEW */}
            {activeTab === 'upload' && (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
                className="max-w-2xl mx-auto py-8 lg:py-12 perspective-container"
              >
                <div className="text-center mb-12">
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.1, type: "spring", stiffness: 400 }}
                    className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-300 text-sm font-medium mb-5"
                  >
                    <FileUp size={14} /> Data Import
                  </motion.div>
                  <motion.h2
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.15 }}
                    className="text-3xl lg:text-4xl font-bold mb-4 text-white tracking-tight"
                  >
                    Upload your equipment data 📁
                  </motion.h2>
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.25 }}
                    className="text-slate-400 text-base lg:text-lg leading-relaxed max-w-lg mx-auto"
                  >
                    Simply drag and drop your CSV file, and we'll handle the rest. Your data will be analyzed instantly.
                  </motion.p>
                </div>

                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: 0.2 }}
                  className="card-3d glass-depth p-10 rounded-3xl text-center relative overflow-hidden upload-gradient-bg border border-white/5"
                >
                  {/* 3D Decorative elements */}
                  <div className="absolute top-0 right-0 w-40 h-40 bg-gradient-to-br from-indigo-500/15 to-purple-500/5 rounded-full blur-3xl"></div>
                  <div className="absolute bottom-0 left-0 w-48 h-48 bg-gradient-to-tr from-purple-500/15 to-pink-500/5 rounded-full blur-3xl"></div>
                  <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl"></div>

                  <input
                    type="file"
                    accept=".csv"
                    onChange={(e) => {
                      if (e.target.files) {
                        setFile(e.target.files[0]);
                        setMsg('');
                      }
                    }}
                    className="hidden"
                    id="fileInput"
                  />
                  <label
                    htmlFor="fileInput"
                    className={clsx(
                      "upload-zone block border-2 border-dashed rounded-2xl p-16 cursor-pointer transition-all duration-300 relative z-10",
                      file
                        ? "border-indigo-500 bg-indigo-500/10 shadow-[0_0_30px_rgba(99,102,241,0.15)]"
                        : "border-slate-600/50 hover:border-indigo-400 hover:bg-slate-800/30"
                    )}
                  >
                    <motion.div
                      className={clsx(
                        "w-20 h-20 mx-auto rounded-2xl flex items-center justify-center mb-6 transition-all duration-300",
                        file
                          ? "bg-gradient-to-br from-indigo-500 to-purple-500 text-white shadow-lg shadow-indigo-500/30"
                          : "bg-slate-800/50 text-indigo-400 border border-slate-700"
                      )}
                      whileHover={{ scale: 1.1, rotate: 5 }}
                    >
                      {file ? <FileText size={36} /> : <Upload size={36} className="file-icon-pulse" />}
                    </motion.div>
                    {file ? (
                      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
                        <p className="text-2xl font-semibold text-white mb-2">📄 {file.name}</p>
                        <div className="flex items-center justify-center gap-3">
                          <span className="px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-sm font-medium">
                            {(file.size / 1024).toFixed(1)} KB
                          </span>
                          <span className="px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-300 text-sm font-medium">
                            ✓ Ready to go!
                          </span>
                        </div>
                      </motion.div>
                    ) : (
                      <div>
                        <p className="text-xl font-medium text-white mb-2">Drop your file here ✨</p>
                        <p className="text-slate-400">or <span className="text-indigo-400 font-medium">click to browse</span></p>
                        <div className="mt-4 flex items-center justify-center gap-2 text-slate-500 text-sm">
                          <span className="w-2 h-2 rounded-full bg-slate-600"></span>
                          Works with .CSV files
                        </div>
                      </div>
                    )}
                  </label>

                  <motion.button
                    onClick={handleUpload}
                    disabled={!file || msg === 'uploading'}
                    whileHover={{ scale: file && msg !== 'uploading' ? 1.02 : 1 }}
                    whileTap={{ scale: file && msg !== 'uploading' ? 0.98 : 1 }}
                    className={clsx(
                      "w-full mt-8 py-4 px-8 text-lg font-semibold rounded-xl transition-all duration-300 relative overflow-hidden z-10",
                      !file || msg === 'uploading'
                        ? "bg-slate-700/50 text-slate-500 cursor-not-allowed"
                        : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/30 btn-glow"
                    )}
                  >
                    {msg === 'uploading' ? (
                      <span className="flex items-center justify-center gap-3">
                        <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Working on it... ⚙️
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        <Zap size={20} /> Analyze Now 🚀
                      </span>
                    )}
                  </motion.button>

                  {/* Status Messages */}
                  <AnimatePresence>
                    {msg && msg !== 'uploading' && (
                      <motion.div
                        initial={{ opacity: 0, y: 10, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: -10, scale: 0.95 }}
                        className={clsx(
                          "mt-6 p-4 rounded-xl border flex items-center gap-3 z-10 relative",
                          msg === 'success' && "status-success",
                          msg.startsWith('error:') && "status-error"
                        )}
                      >
                        {msg === 'success' ? (
                          <>
                            <div className="w-10 h-10 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400">
                              <CheckCircle size={20} />
                            </div>
                            <div className="text-left">
                              <p className="font-semibold text-emerald-300">✨ Analysis Complete!</p>
                              <p className="text-sm text-emerald-400/80">Taking you to your dashboard now...</p>
                            </div>
                          </>
                        ) : (
                          <>
                            <div className="w-10 h-10 rounded-full bg-rose-500/20 flex items-center justify-center text-rose-400">
                              <AlertTriangle size={20} />
                            </div>
                            <div className="text-left">
                              <p className="font-semibold text-rose-300">😔 Oops, something went wrong</p>
                              <p className="text-sm text-rose-400/80">{msg.replace('error:', '')}</p>
                            </div>
                          </>
                        )}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>

                {/* CSV Format Info */}
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  whileHover={{ y: -3 }}
                  className="mt-8 lift-3d glass-card p-6 rounded-2xl border border-white/5"
                >
                  <h4 className="font-semibold text-white mb-4 flex items-center gap-2">
                    <FileText size={18} className="text-indigo-400" />
                    💡 Your CSV should have these columns:
                  </h4>
                  <div className="grid grid-cols-5 gap-3 text-sm">
                    {['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'].map((col) => (
                      <motion.div
                        key={col}
                        whileHover={{ scale: 1.05, y: -2 }}
                        className="px-3 py-2.5 rounded-xl bg-slate-800/50 text-slate-300 text-center border border-slate-700/50 font-mono text-xs hover:border-indigo-500/30 hover:text-white transition-all"
                      >
                        {col}
                      </motion.div>
                    ))}
                  </div>
                </motion.div>
              </motion.div>
            )}

            {/* HISTORY VIEW */}
            {activeTab === 'history' && (
              <motion.div
                key="history"
                initial={{ opacity: 0, y: 20, rotateX: -3 }}
                animate={{ opacity: 1, y: 0, rotateX: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5 }}
                className="perspective-container"
              >
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent mb-1">Your Analysis History 📋</h2>
                    <p className="text-slate-400">All your previous uploads are saved here</p>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={fetchHistory}
                    className="btn-3d bg-slate-700/50 hover:bg-slate-700 text-white font-medium py-2 px-4 rounded-lg flex items-center gap-2"
                  >
                    🔄 Refresh
                  </motion.button>
                </div>

                <motion.div
                  whileHover={{ y: -3 }}
                  className="lift-3d glass-depth overflow-hidden rounded-2xl border border-white/5"
                >
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-gradient-to-r from-slate-800/50 to-slate-700/30 border-b border-white/10 text-slate-400 text-sm uppercase tracking-wider">
                          <th className="p-5 font-semibold">📁 File</th>
                          <th className="p-5 font-semibold">📅 When</th>
                          <th className="p-5 font-semibold">📊 Items</th>
                          <th className="p-5 font-semibold">✓ Status</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5 text-slate-300">
                        {history.map((h, i) => (
                          <motion.tr
                            key={i}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: i * 0.1 }}
                            className="hover:bg-white/5 transition-colors group cursor-pointer"
                          >
                            <td className="p-5 font-medium text-white flex items-center gap-3">
                              <motion.div
                                whileHover={{ rotate: 5, scale: 1.1 }}
                                className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500/20 to-purple-500/10 text-indigo-400 border border-indigo-500/20"
                              >
                                <FileText size={18} />
                              </motion.div>
                              {h.filename}
                            </td>
                            <td className="p-5 text-sm text-slate-400">{new Date(h.upload_date).toLocaleString()}</td>
                            <td className="p-5 font-semibold text-white">{h.summary_data.total_count} units</td>
                            <td className="p-5">
                              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                                Done
                              </span>
                            </td>
                          </motion.tr>
                        ))}
                        {history.length === 0 && (
                          <tr>
                            <td colSpan={4} className="p-16 text-center">
                              <div className="text-slate-500">
                                <span className="text-4xl mb-4 block">📭</span>
                                No analysis history yet. Upload your first file to get started!
                              </div>
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </motion.div>
              </motion.div>
            )}

            {/* VISUALIZER VIEW */}
            {activeTab === 'visualizer' && (
              <motion.div
                key="visualizer"
                initial={{ opacity: 0, scale: 0.95, rotateX: -3 }}
                animate={{ opacity: 1, scale: 1, rotateX: 0 }}
                exit={{ opacity: 0, scale: 1.05 }}
                transition={{ duration: 0.5 }}
                className="h-[calc(100vh-140px)] perspective-container"
              >
                <div className="flex justify-between items-center mb-6">
                  <div>
                    <h2 className="text-3xl font-bold bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent mb-1">Equipment Map 🗺️</h2>
                    <p className="text-slate-400">Interactive view of your equipment — bigger circles = higher flowrate</p>
                  </div>
                  {/* Enhanced Legend */}
                  <div className="flex gap-6 bg-slate-800/30 px-5 py-2.5 rounded-full border border-white/5">
                    <div className="flex items-center gap-2 text-sm text-slate-300"><span className="w-3 h-3 rounded-full bg-emerald-500 shadow-lg shadow-emerald-500/50 animate-pulse"></span> All Good</div>
                    <div className="flex items-center gap-2 text-sm text-slate-300"><span className="w-3 h-3 rounded-full bg-rose-500 shadow-lg shadow-rose-500/50 animate-pulse"></span> Needs Attention</div>
                  </div>
                </div>

                {!data ? (
                  <motion.div
                    initial={{ scale: 0.95 }}
                    animate={{ scale: 1 }}
                    className="flex flex-col items-center justify-center h-full card-3d glass-depth rounded-3xl text-slate-400 border border-white/5"
                  >
                    <motion.div
                      animate={{ y: [0, -15, 0] }}
                      transition={{ duration: 3, repeat: Infinity }}
                    >
                      <Zap size={64} className="mb-6 text-indigo-400/50" />
                    </motion.div>
                    <p className="text-xl font-medium text-white mb-2">No equipment to show yet! ⚡</p>
                    <p className="text-slate-500">Upload a dataset to see your equipment come to life here</p>
                  </motion.div>
                ) : (
                  <div className="glass-panel rounded-3xl p-8 h-full overflow-hidden relative">
                    {/* Grid Background */}
                    <div className="absolute inset-0 opacity-10" style={{
                      backgroundImage: 'radial-gradient(circle, #6366f1 1px, transparent 1px)',
                      backgroundSize: '30px 30px'
                    }}></div>

                    <div className="flex flex-wrap gap-4 justify-center items-center h-full overflow-y-auto content-start py-10 relative z-10">
                      {data.data.slice(0, 50).map((item: any, i: number) => {
                        const isCritical = item.Pressure > thresholds.pressure_critical || item.Temperature > thresholds.temperature_critical;
                        const size = Math.max(40, Math.min(120, item.Flowrate / 2)); // Dynamic size based on flowrate

                        return (
                          <motion.div
                            key={i}
                            whileHover={{ scale: 1.2, zIndex: 50 }}
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: i * 0.02 }}
                            className={clsx(
                              "rounded-full flex items-center justify-center relative cursor-pointer group shadow-lg border",
                              isCritical
                                ? "bg-rose-500/20 border-rose-500/50 shadow-[0_0_20px_rgba(244,63,94,0.3)]"
                                : "bg-emerald-500/20 border-emerald-500/50 shadow-[0_0_20px_rgba(16,185,129,0.2)]"
                            )}
                            style={{ width: size, height: size }}
                          >
                            <div className={clsx("absolute inset-2 rounded-full opacity-50 blur-sm", isCritical ? "bg-rose-500" : "bg-emerald-500")} />
                            <span className="text-[10px] font-bold text-white/80 z-10 truncate max-w-[80%] text-center">
                              {item['Equipment Name'] || `EQ-${i}`}
                            </span>

                            {/* Tooltip */}
                            <div className="absolute bottom-full mb-2 bg-slate-900 border border-slate-700 text-white p-3 rounded-lg text-xs w-48 hidden group-hover:block z-50 pointer-events-none shadow-xl">
                              <div className="font-bold border-b border-slate-800 pb-1 mb-1">{item['Equipment Name']}</div>
                              <div className="grid grid-cols-2 gap-1">
                                <span className="text-slate-400">Pressure:</span> <span>{item.Pressure}</span>
                                <span className="text-slate-400">Temp:</span> <span>{item.Temperature}</span>
                                <span className="text-slate-400">Flow:</span> <span>{item.Flowrate}</span>
                              </div>
                            </div>
                          </motion.div>
                        )
                      })}
                      {data.data.length > 50 && (
                        <div className="w-24 h-24 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 text-xs">
                          +{data.data.length - 50} more
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* ML PREDICTIONS VIEW */}
            {activeTab === 'predictions' && (
              <motion.div
                key="predictions"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
                className="perspective-container space-y-8"
              >
                <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-8 rounded-lg bg-purple-500/15 flex items-center justify-center">
                        <Brain className="text-purple-400" size={18} />
                      </div>
                      <span className="text-purple-400/80 text-sm font-medium">AI-Powered Analysis</span>
                    </div>
                    <h2 className="text-2xl lg:text-3xl font-bold text-white mb-1.5 tracking-tight">
                      Predictive Maintenance
                    </h2>
                    <p className="text-slate-400 text-base leading-relaxed">Intelligent risk assessment and maintenance scheduling based on your data</p>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    transition={{ type: "spring", stiffness: 400, damping: 20 }}
                    onClick={fetchPredictions}
                    className="btn-3d bg-gradient-to-r from-purple-600 to-indigo-600 text-white font-medium py-2.5 px-5 rounded-xl flex items-center gap-2 text-sm"
                  >
                    <RefreshCw size={15} /> Refresh Analysis
                  </motion.button>
                </div>

                {!predictions ? (
                  <motion.div
                    initial={{ scale: 0.95 }}
                    animate={{ scale: 1 }}
                    className="card-3d glass-depth rounded-3xl p-16 text-center border border-white/5 flex flex-col items-center justify-center min-h-[400px]"
                  >
                    <motion.div
                      animate={{ y: [0, -10, 0], rotate: [0, 5, -5, 0] }}
                      transition={{ duration: 3, repeat: Infinity }}
                      className="w-24 h-24 rounded-3xl bg-gradient-to-br from-purple-500/20 to-indigo-500/20 flex items-center justify-center mb-8 border border-purple-500/20"
                    >
                      <Brain size={48} className="text-purple-400" />
                    </motion.div>
                    <h3 className="text-2xl font-semibold text-white mb-3">ML Engine Ready 🤖</h3>
                    <p className="text-slate-400 max-w-md mb-8">
                      Upload equipment data first, then click "Refresh Predictions" to run the ML analysis.
                    </p>
                  </motion.div>
                ) : (
                  <>
                    {/* Prediction Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                      <motion.div
                        whileHover={{ y: -5, scale: 1.02 }}
                        className="stat-card-3d glass-card p-6 rounded-2xl relative overflow-hidden"
                      >
                        <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-rose-500/20 to-transparent rounded-full blur-2xl" />
                        <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Critical Risk</p>
                        <h3 className="text-4xl font-bold text-rose-400">{predictions.summary?.critical || 0}</h3>
                        <p className="text-slate-500 text-sm mt-1">Need immediate action</p>
                      </motion.div>

                      <motion.div
                        whileHover={{ y: -5, scale: 1.02 }}
                        className="stat-card-3d glass-card p-6 rounded-2xl relative overflow-hidden"
                      >
                        <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-amber-500/20 to-transparent rounded-full blur-2xl" />
                        <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Warning</p>
                        <h3 className="text-4xl font-bold text-amber-400">{predictions.summary?.warning || 0}</h3>
                        <p className="text-slate-500 text-sm mt-1">Monitor closely</p>
                      </motion.div>

                      <motion.div
                        whileHover={{ y: -5, scale: 1.02 }}
                        className="stat-card-3d glass-card p-6 rounded-2xl relative overflow-hidden"
                      >
                        <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-emerald-500/20 to-transparent rounded-full blur-2xl" />
                        <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Healthy</p>
                        <h3 className="text-4xl font-bold text-emerald-400">{predictions.summary?.healthy || 0}</h3>
                        <p className="text-slate-500 text-sm mt-1">Operating normally</p>
                      </motion.div>

                      <motion.div
                        whileHover={{ y: -5, scale: 1.02 }}
                        className="stat-card-3d glass-card p-6 rounded-2xl relative overflow-hidden"
                      >
                        <div className="absolute -right-4 -top-4 w-24 h-24 bg-gradient-to-br from-blue-500/20 to-transparent rounded-full blur-2xl" />
                        <p className="text-slate-400 text-xs font-semibold uppercase tracking-wider mb-1">Next Maintenance</p>
                        <h3 className="text-2xl font-bold text-blue-400">{predictions.summary?.next_maintenance_date || 'N/A'}</h3>
                        <p className="text-slate-500 text-sm mt-1">Earliest schedule</p>
                      </motion.div>
                    </div>

                    {/* Predictions Table */}
                    <motion.div
                      whileHover={{ y: -3 }}
                      className="lift-3d glass-depth overflow-hidden rounded-2xl border border-white/5"
                    >
                      <div className="p-6 border-b border-white/5">
                        <h3 className="text-lg font-semibold flex items-center gap-2">
                          <Wrench className="text-indigo-400" size={20} />
                          Equipment Risk Assessment
                        </h3>
                      </div>
                      <div className="overflow-x-auto max-h-[500px] overflow-y-auto">
                        <table className="w-full text-left border-collapse">
                          <thead className="sticky top-0">
                            <tr className="bg-slate-800/80 backdrop-blur text-slate-400 text-sm uppercase tracking-wider">
                              <th className="p-4 font-semibold">Equipment</th>
                              <th className="p-4 font-semibold">Type</th>
                              <th className="p-4 font-semibold">Risk Score</th>
                              <th className="p-4 font-semibold">Status</th>
                              <th className="p-4 font-semibold">Maintenance Due</th>
                              <th className="p-4 font-semibold">Risk Factors</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-white/5 text-slate-300">
                            {predictions.predictions?.map((pred: any, i: number) => (
                              <motion.tr
                                key={i}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: i * 0.03 }}
                                className="hover:bg-white/5 transition-colors"
                              >
                                <td className="p-4 font-medium text-white flex items-center gap-2">
                                  <div className={clsx(
                                    "w-2 h-2 rounded-full",
                                    pred.risk_level === 'critical' && "bg-rose-500 animate-pulse",
                                    pred.risk_level === 'warning' && "bg-amber-500",
                                    pred.risk_level === 'moderate' && "bg-blue-500",
                                    pred.risk_level === 'healthy' && "bg-emerald-500"
                                  )} />
                                  {pred.equipment_name}
                                </td>
                                <td className="p-4 text-slate-400">{pred.type}</td>
                                <td className="p-4">
                                  <div className="flex items-center gap-2">
                                    <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
                                      <div
                                        className={clsx(
                                          "h-full rounded-full transition-all",
                                          pred.risk_score >= 70 && "bg-gradient-to-r from-rose-500 to-red-500",
                                          pred.risk_score >= 40 && pred.risk_score < 70 && "bg-gradient-to-r from-amber-500 to-orange-500",
                                          pred.risk_score < 40 && "bg-gradient-to-r from-emerald-500 to-green-500"
                                        )}
                                        style={{ width: `${pred.risk_score}%` }}
                                      />
                                    </div>
                                    <span className="text-sm font-mono">{pred.risk_score}%</span>
                                  </div>
                                </td>
                                <td className="p-4">
                                  <span className={clsx(
                                    "px-3 py-1 rounded-full text-xs font-medium",
                                    pred.risk_level === 'critical' && "bg-rose-500/20 text-rose-400 border border-rose-500/30",
                                    pred.risk_level === 'warning' && "bg-amber-500/20 text-amber-400 border border-amber-500/30",
                                    pred.risk_level === 'moderate' && "bg-blue-500/20 text-blue-400 border border-blue-500/30",
                                    pred.risk_level === 'healthy' && "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                                  )}>
                                    {pred.risk_level.charAt(0).toUpperCase() + pred.risk_level.slice(1)}
                                  </span>
                                </td>
                                <td className="p-4">
                                  <div className="flex items-center gap-2">
                                    <Clock size={14} className="text-slate-500" />
                                    <span className={clsx(
                                      pred.maintenance_in_days <= 7 && "text-rose-400 font-semibold",
                                      pred.maintenance_in_days > 7 && pred.maintenance_in_days <= 30 && "text-amber-400",
                                      pred.maintenance_in_days > 30 && "text-slate-400"
                                    )}>
                                      {pred.maintenance_in_days} days
                                    </span>
                                  </div>
                                </td>
                                <td className="p-4">
                                  <div className="flex flex-wrap gap-1">
                                    {pred.risk_factors?.length > 0 ? (
                                      pred.risk_factors.slice(0, 2).map((factor: string, fi: number) => (
                                        <span key={fi} className="px-2 py-0.5 rounded bg-slate-700/50 text-xs text-slate-400">
                                          {factor}
                                        </span>
                                      ))
                                    ) : (
                                      <span className="text-slate-500 text-sm">All parameters normal</span>
                                    )}
                                  </div>
                                </td>
                              </motion.tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </motion.div>
                  </>
                )}
              </motion.div>
            )}

            {/* SETTINGS VIEW */}
            {activeTab === 'settings' && (
              <motion.div
                key="settings"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.4, ease: [0.4, 0, 0.2, 1] }}
                className="max-w-2xl mx-auto py-6 lg:py-8"
              >
                <div className="text-center mb-10">
                  <motion.div
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: 0.1, type: "spring", stiffness: 400 }}
                    className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-500/15 text-indigo-300 text-sm font-medium mb-5"
                  >
                    <Settings size={14} /> Configuration
                  </motion.div>
                  <h2 className="text-2xl lg:text-3xl font-bold mb-3 text-white tracking-tight">
                    Threshold Settings
                  </h2>
                  <p className="text-slate-400 text-base leading-relaxed max-w-md mx-auto">
                    Customize the thresholds used for equipment health monitoring and anomaly detection
                  </p>
                </div>

                <motion.div
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className="card-3d glass-depth p-8 rounded-3xl border border-white/5 space-y-8"
                >
                  {/* Pressure Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      <TrendingUp className="text-rose-400" size={20} />
                      Pressure Thresholds (Bar)
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Warning Level</label>
                        <input
                          type="number"
                          value={thresholds.pressure_warning}
                          onChange={(e) => setThresholds({ ...thresholds, pressure_warning: parseFloat(e.target.value) })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 focus:outline-none transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Critical Level</label>
                        <input
                          type="number"
                          value={thresholds.pressure_critical}
                          onChange={(e) => setThresholds({ ...thresholds, pressure_critical: parseFloat(e.target.value) })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-rose-500 focus:outline-none transition-colors"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Temperature Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      <Activity className="text-amber-400" size={20} />
                      Temperature Thresholds (°C)
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Warning Level</label>
                        <input
                          type="number"
                          value={thresholds.temperature_warning}
                          onChange={(e) => setThresholds({ ...thresholds, temperature_warning: parseFloat(e.target.value) })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 focus:outline-none transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Critical Level</label>
                        <input
                          type="number"
                          value={thresholds.temperature_critical}
                          onChange={(e) => setThresholds({ ...thresholds, temperature_critical: parseFloat(e.target.value) })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-rose-500 focus:outline-none transition-colors"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Flowrate Settings */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                      <Zap className="text-cyan-400" size={20} />
                      Flowrate Range (L/h)
                    </h3>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Minimum</label>
                        <input
                          type="number"
                          value={thresholds.flowrate_min}
                          onChange={(e) => setThresholds({ ...thresholds, flowrate_min: parseFloat(e.target.value) })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 focus:outline-none transition-colors"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-slate-400 mb-2">Maximum</label>
                        <input
                          type="number"
                          value={thresholds.flowrate_max}
                          onChange={(e) => setThresholds({ ...thresholds, flowrate_max: parseFloat(e.target.value) })}
                          className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 focus:outline-none transition-colors"
                        />
                      </div>
                    </div>
                  </div>

                  {/* Save Button */}
                  <motion.button
                    onClick={saveThresholds}
                    disabled={savingSettings}
                    whileHover={{ scale: savingSettings ? 1 : 1.02 }}
                    whileTap={{ scale: savingSettings ? 1 : 0.98 }}
                    className={clsx(
                      "w-full py-4 px-8 text-lg font-semibold rounded-xl transition-all duration-300 flex items-center justify-center gap-2",
                      savingSettings
                        ? "bg-slate-700/50 text-slate-500 cursor-not-allowed"
                        : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg shadow-indigo-500/30"
                    )}
                  >
                    {savingSettings ? (
                      <>
                        <RefreshCw size={20} className="animate-spin" />
                        Saving...
                      </>
                    ) : (
                      <>
                        <Save size={20} />
                        Save Thresholds
                      </>
                    )}
                  </motion.button>

                  <p className="text-center text-slate-500 text-sm">
                    Changes will apply to all future analyses and predictions
                  </p>
                </motion.div>
              </motion.div>
            )}

            {/* TRENDS VIEW */}
            {activeTab === 'trends' && (
              <motion.div
                key="trends"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                className="space-y-8"
              >
                <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
                  <div>
                    <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">Historical Trends 📈</h2>
                    <p className="text-slate-400">Track equipment parameters over time to identify long-term patterns</p>
                  </div>
                  <div className="flex gap-3">
                    <select
                      value={selectedEquipment}
                      onChange={(e) => { setSelectedEquipment(e.target.value); fetchTrendData(e.target.value, trendDays); }}
                      className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-white focus:outline-none"
                    >
                      <option value="">All Equipment</option>
                      {trendData?.equipment_list?.map((name: string) => (
                        <option key={name} value={name}>{name}</option>
                      ))}
                    </select>
                    <select
                      value={trendDays}
                      onChange={(e) => { setTrendDays(parseInt(e.target.value)); fetchTrendData(selectedEquipment, parseInt(e.target.value)); }}
                      className="bg-slate-800 border border-slate-700 rounded-xl px-4 py-2 text-white focus:outline-none"
                    >
                      <option value={7}>Last 7 Days</option>
                      <option value={30}>Last 30 Days</option>
                      <option value={90}>Last 90 Days</option>
                    </select>
                  </div>
                </div>

                {!trendData || trendData.history.length === 0 ? (
                  <div className="card-3d glass-depth rounded-3xl p-16 text-center border border-white/5">
                    <TrendingUp size={48} className="text-indigo-400/50 mx-auto mb-6" />
                    <h3 className="text-xl font-medium text-white mb-2">No trend data yet</h3>
                    <p className="text-slate-500">Upload more snapshots over time to see parameter curves</p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 gap-8">
                    {/* Chart Container */}
                    <motion.div className="lift-3d glass-depth p-8 rounded-3xl border border-white/5">
                      <div className="h-[400px]">
                        <Line
                          data={{
                            labels: trendData.history[0]?.data_points.map((p: any) => new Date(p.timestamp).toLocaleDateString()) || [],
                            datasets: [
                              {
                                label: 'Pressure (Bar)',
                                data: trendData.history[0]?.data_points.map((p: any) => p.pressure) || [],
                                borderColor: '#fb7185',
                                backgroundColor: 'rgba(251, 113, 133, 0.1)',
                                tension: 0.4,
                                fill: true
                              },
                              {
                                label: 'Temperature (°C)',
                                data: trendData.history[0]?.data_points.map((p: any) => p.temperature) || [],
                                borderColor: '#fbbf24',
                                backgroundColor: 'rgba(251, 191, 36, 0.1)',
                                tension: 0.4,
                                fill: true
                              }
                            ]
                          }}
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: { legend: { position: 'top' as const } },
                            scales: {
                              y: { grid: { color: 'rgba(255,255,255,0.05)' } },
                              x: { grid: { display: false } }
                            }
                          }}
                        />
                      </div>
                    </motion.div>

                    {/* Trend Summary Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                      {trendData.trends.map((t: any, i: number) => (
                        <div key={i} className="glass-card p-6 rounded-2xl border border-white/5">
                          <h4 className="text-white font-semibold mb-4">{t.equipment_name}</h4>
                          <div className="space-y-3">
                            <div className="flex justify-between items-center text-sm">
                              <span className="text-slate-400">Pressure Trend:</span>
                              <span className={clsx(
                                "font-medium capitalize",
                                t.pressure_trend === 'increasing' ? "text-rose-400" : t.pressure_trend === 'decreasing' ? "text-emerald-400" : "text-slate-300"
                              )}>{t.pressure_trend}</span>
                            </div>
                            <div className="flex justify-between items-center text-sm">
                              <span className="text-slate-400">Temperature Trend:</span>
                              <span className={clsx(
                                "font-medium capitalize",
                                t.temperature_trend === 'increasing' ? "text-amber-400" : t.temperature_trend === 'decreasing' ? "text-emerald-400" : "text-slate-300"
                              )}>{t.temperature_trend}</span>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </motion.div>
            )}

            {/* ALERTS VIEW */}
            {activeTab === 'alerts' && (
              <motion.div
                key="alerts"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                className="max-w-4xl mx-auto space-y-8"
              >
                <div className="text-center mb-10">
                  <h2 className="text-3xl font-bold text-white mb-2">Email Notifications 🔔</h2>
                  <p className="text-slate-400">Configure automated alerts for your equipment</p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                  {/* Settings Panel */}
                  <div className="lg:col-span-1 space-y-6">
                    <div className="glass-card p-8 rounded-3xl border border-indigo-500/20 shadow-xl">
                      <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                        <Mail className="text-indigo-400" size={20} /> Settings
                      </h3>
                      <div className="space-y-6">
                        <div className="flex items-center justify-between">
                          <span className="text-slate-300 font-medium">Enable Alerts</span>
                          <button
                            onClick={() => setAlertSettings({ ...alertSettings, email_enabled: !alertSettings.email_enabled })}
                            className={clsx("w-12 h-6 rounded-full transition-all relative", alertSettings.email_enabled ? "bg-indigo-600" : "bg-slate-700")}
                          >
                            <div className={clsx("absolute top-1 w-4 h-4 bg-white rounded-full transition-all", alertSettings.email_enabled ? "left-7" : "left-1")} />
                          </button>
                        </div>
                        <div>
                          <label className="block text-sm text-slate-400 mb-2">Email Address</label>
                          <input
                            type="email"
                            value={alertSettings.email_address || ''}
                            onChange={(e) => setAlertSettings({ ...alertSettings, email_address: e.target.value })}
                            placeholder="alerts@industry.com"
                            className="w-full bg-slate-800 border border-slate-700 rounded-xl px-4 py-2.5 text-white text-sm focus:border-indigo-500 transition-colors"
                          />
                        </div>
                        <div className="space-y-3 pt-2">
                          <label className="flex items-center gap-3 text-sm text-slate-300 cursor-pointer">
                            <input type="checkbox" checked={alertSettings.alert_on_critical} onChange={(e) => setAlertSettings({ ...alertSettings, alert_on_critical: e.target.checked })} className="rounded bg-slate-800 border-slate-700 text-indigo-500" />
                            Alert on Critical Risk
                          </label>
                          <label className="flex items-center gap-3 text-sm text-slate-300 cursor-pointer">
                            <input type="checkbox" checked={alertSettings.alert_on_warning} onChange={(e) => setAlertSettings({ ...alertSettings, alert_on_warning: e.target.checked })} className="rounded bg-slate-800 border-slate-700 text-indigo-500" />
                            Alert on Warnings
                          </label>
                          <label className="flex items-center gap-3 text-sm text-slate-300 cursor-pointer">
                            <input type="checkbox" checked={alertSettings.alert_on_maintenance_due} onChange={(e) => setAlertSettings({ ...alertSettings, alert_on_maintenance_due: e.target.checked })} className="rounded bg-slate-800 border-slate-700 text-indigo-500" />
                            Maintenance Reminders
                          </label>
                        </div>
                        <button onClick={saveAlertSettings} className="w-full btn-3d bg-indigo-600 py-3 rounded-xl font-bold text-sm shadow-indigo-500/20">
                          Save Changes
                        </button>
                        <button onClick={sendTestAlert} className="w-full bg-slate-800 hover:bg-slate-700 py-3 rounded-xl font-bold text-sm text-slate-400 border border-slate-700">
                          Send Test Email
                        </button>
                      </div>
                    </div>
                  </div>

                  {/* Logs Panel */}
                  <div className="lg:col-span-2">
                    <div className="glass-card p-8 rounded-3xl border border-white/5 h-full">
                      <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white flex items-center gap-2">
                          <History className="text-indigo-400" size={20} /> Alert History
                        </h3>
                        <button onClick={fetchAlertLogs} className="text-indigo-400 font-medium text-sm flex items-center gap-1">
                          <RefreshCw size={14} /> Refresh
                        </button>
                      </div>
                      <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2">
                        {alertLogs.map((log) => (
                          <div key={log.id} className="p-4 rounded-xl bg-slate-800/40 border border-white/5 flex gap-4">
                            <div className={clsx("w-10 h-10 rounded-full flex items-center justify-center shrink-0", log.alert_type === 'critical' ? "bg-rose-500/20 text-rose-400" : "bg-indigo-500/20 text-indigo-400")}>
                              {log.alert_type === 'critical' ? <AlertTriangle size={18} /> : <Bell size={18} />}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex justify-between items-start">
                                <h4 className="font-bold text-white text-sm truncate">{log.equipment_name}</h4>
                                <span className="text-[10px] text-slate-500 tabular-nums">{new Date(log.sent_at).toLocaleString()}</span>
                              </div>
                              <p className="text-xs text-slate-400 mt-1 line-clamp-2">{log.message}</p>
                            </div>
                          </div>
                        ))}
                        {alertLogs.length === 0 && (
                          <div className="text-center py-12 text-slate-500">
                            <Mail size={32} className="mx-auto mb-3 opacity-20" />
                            No alerts sent yet
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {/* MAINTENANCE VIEW */}
            {activeTab === 'maintenance' && (
              <motion.div
                key="maintenance"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                className="space-y-8"
              >
                <div className="flex flex-col lg:flex-row lg:items-end justify-between gap-4">
                  <div>
                    <h2 className="text-3xl font-bold text-white mb-2 tracking-tight">Maintenance Calendar 📅</h2>
                    <p className="text-slate-400">Keep track of scheduled, upcoming, and completed maintenance tasks</p>
                  </div>
                  <div className="flex gap-3">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={autoScheduleMaintenance}
                      className="bg-purple-600/20 hover:bg-purple-600 text-purple-300 hover:text-white border border-purple-500/30 px-6 py-3 rounded-xl font-bold flex items-center gap-2 transition-all"
                    >
                      <Brain size={18} /> Auto-Generate (ML)
                    </motion.button>
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setShowAddMaintenance(true)}
                      className="btn-3d bg-indigo-600 py-3 px-6 rounded-xl font-bold flex items-center gap-2"
                    >
                      <Plus size={20} /> Schedule Task
                    </motion.button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                  <StatCard title="Total Tasks" value={maintenanceData?.summary?.total || 0} icon={Calendar} color="indigo" />
                  <StatCard title="Upcoming (7d)" value={maintenanceData?.summary?.upcoming_7_days || 0} icon={Clock} color="amber" />
                  <StatCard title="Overdue" value={maintenanceData?.summary?.overdue || 0} icon={AlertTriangle} color="rose" />
                  <StatCard title="Completed" value={maintenanceData?.summary?.completed || 0} icon={CheckCircle} color="emerald" />
                </div>

                <div className="lift-3d glass-depth rounded-3xl overflow-hidden border border-white/5">
                  <table className="w-full text-left">
                    <thead>
                      <tr className="bg-slate-800/80 text-slate-400 text-xs uppercase font-bold tracking-widest border-b border-white/5">
                        <th className="p-6">Equipment</th>
                        <th className="p-6">Task Details</th>
                        <th className="p-6">Scheduled</th>
                        <th className="p-6">Priority</th>
                        <th className="p-6">Status</th>
                        <th className="p-6">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-white/5">
                      {maintenanceData?.schedules.map((task: any) => (
                        <tr key={task.id} className="hover:bg-indigo-500/5 group">
                          <td className="p-6">
                            <div className="font-bold text-white">{task.equipment_name}</div>
                            <div className="text-xs text-slate-500">{task.equipment_type}</div>
                          </td>
                          <td className="p-6">
                            <div className="text-white font-medium">{task.title}</div>
                            <div className="text-xs text-slate-400 truncate max-w-xs">{task.description}</div>
                          </td>
                          <td className="p-6">
                            <div className="text-slate-300 font-mono text-sm">{task.scheduled_date}</div>
                            <div className="text-xs text-slate-500">{task.scheduled_time || '--:--'}</div>
                          </td>
                          <td className="p-6">
                            <span className={clsx(
                              "px-3 py-1 rounded-full text-[10px] font-bold uppercase border",
                              task.priority === 'critical' ? "bg-rose-500/20 text-rose-400 border-rose-500/30" :
                                task.priority === 'high' ? "bg-amber-500/20 text-amber-400 border-amber-500/30" :
                                  "bg-blue-500/20 text-blue-400 border-blue-500/30"
                            )}>{task.priority}</span>
                          </td>
                          <td className="p-6">
                            <span className={clsx(
                              "px-3 py-1 rounded-full text-[10px] font-bold uppercase",
                              task.status === 'completed' ? "bg-emerald-500/20 text-emerald-400" :
                                task.status === 'overdue' ? "bg-rose-500/20 text-rose-400" :
                                  "bg-indigo-500/20 text-indigo-400"
                            )}>• {task.status.replace('_', ' ')}</span>
                          </td>
                          <td className="p-6">
                            <div className="flex gap-2">
                              {task.status !== 'completed' && (
                                <button onClick={() => updateMaintenanceStatus(task.id, 'completed')} className="p-2 bg-emerald-500/10 text-emerald-400 rounded-lg hover:bg-emerald-500 text-white transition-all"><CheckCircle size={14} /></button>
                              )}
                              <button onClick={() => deleteMaintenance(task.id)} className="p-2 bg-rose-500/10 text-rose-400 rounded-lg hover:bg-rose-500 text-white transition-all"><Trash2 size={14} /></button>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {maintenanceData?.schedules.length === 0 && (
                        <tr><td colSpan={6} className="p-20 text-center text-slate-500">No maintenance schedules found. Click "Schedule Task" to add one!</td></tr>
                      )}
                    </tbody>
                  </table>
                </div>

                {/* Add Maintenance Modal */}
                <AnimatePresence>
                  {showAddMaintenance && (
                    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-slate-950/80 backdrop-blur-sm">
                      <motion.div
                        initial={{ opacity: 0, scale: 0.9, y: 20 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.9, y: 20 }}
                        className="glass-card max-w-xl w-full p-10 rounded-3xl border border-indigo-500/30 shadow-2xl relative"
                      >
                        <button onClick={() => setShowAddMaintenance(false)} className="absolute top-6 right-6 text-slate-400 hover:text-white"><X size={24} /></button>
                        <h3 className="text-2xl font-bold text-white mb-2">Schedule Maintenance</h3>
                        <p className="text-slate-400 mb-8">Plan and assign maintenance tasks for your equipment fleet.</p>

                        <div className="grid grid-cols-2 gap-6 mb-8">
                          <div className="col-span-2">
                            <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Task Title</label>
                            <input value={newMaintenance.title} onChange={(e) => setNewMaintenance({ ...newMaintenance, title: e.target.value })} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none" placeholder="e.g. Pump Seal Replacement" />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Equipment Name</label>
                            <input value={newMaintenance.equipment_name} onChange={(e) => setNewMaintenance({ ...newMaintenance, equipment_name: e.target.value })} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none" placeholder="Reactor A" />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Scheduled Date</label>
                            <input type="date" value={newMaintenance.scheduled_date} onChange={(e) => setNewMaintenance({ ...newMaintenance, scheduled_date: e.target.value })} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none" />
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Priority</label>
                            <select value={newMaintenance.priority} onChange={(e) => setNewMaintenance({ ...newMaintenance, priority: e.target.value })} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none">
                              <option value="low">Low</option>
                              <option value="medium">Medium</option>
                              <option value="high">High</option>
                              <option value="critical">Critical</option>
                            </select>
                          </div>
                          <div>
                            <label className="block text-xs font-bold text-slate-500 uppercase tracking-widest mb-2">Assigned To</label>
                            <input value={newMaintenance.assigned_to} onChange={(e) => setNewMaintenance({ ...newMaintenance, assigned_to: e.target.value })} className="w-full bg-slate-800/50 border border-slate-700 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none" placeholder="Name or Team" />
                          </div>
                        </div>

                        <div className="flex gap-4">
                          <button onClick={() => setShowAddMaintenance(false)} className="flex-1 bg-slate-800 hover:bg-slate-700 text-slate-300 font-bold py-4 rounded-xl transition-all">Cancel</button>
                          <button onClick={createMaintenance} className="flex-1 btn-3d bg-indigo-600 text-white font-bold py-4 rounded-xl shadow-lg">Schedule Task</button>
                        </div>
                      </motion.div>
                    </div>
                  )}
                </AnimatePresence>
              </motion.div>
            )}

          </AnimatePresence>
        </div>
      </main>

      {/* Toast Notification */}
      <AnimatePresence>
        {notification && (
          <motion.div
            initial={{ opacity: 0, y: 50, x: '-50%' }}
            animate={{ opacity: 1, y: 0, x: '-50%' }}
            exit={{ opacity: 0, y: 50, x: '-50%' }}
            className={clsx(
              "fixed bottom-6 left-1/2 px-6 py-4 rounded-2xl shadow-2xl border flex items-center gap-3 z-50",
              notification.type === 'success' && "bg-emerald-500/20 border-emerald-500/30 text-emerald-300",
              notification.type === 'error' && "bg-rose-500/20 border-rose-500/30 text-rose-300",
              notification.type === 'warning' && "bg-amber-500/20 border-amber-500/30 text-amber-300"
            )}
          >
            {notification.type === 'success' && <CheckCircle size={20} />}
            {notification.type === 'error' && <AlertTriangle size={20} />}
            {notification.type === 'warning' && <AlertTriangle size={20} />}
            <span className="font-medium">{notification.message}</span>
            <button onClick={() => setNotification(null)} className="ml-2 hover:opacity-70">
              <X size={16} />
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}

export default App;
