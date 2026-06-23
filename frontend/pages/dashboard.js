import React, { useEffect, useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { Users, Play, Sparkles, BarChart2, Menu, X } from "lucide-react";
import EngagementFeed from "../components/EngagementFeed";
import MetricsDashboard from "../components/MetricsDashboard";

const EVENT_ICONS = {
  MARRIAGE: "💍",
  JOB_CHANGE: "💼",
  NEW_BABY: "👶",
  HOME_PURCHASE: "🏠",
  PRE_RETIREMENT: "🌅",
  SALARY_HIKE: "📈",
  TRAVEL_PHASE: "✈️",
  NONE: "🔍"
};

const EVENT_COLORS = {
  MARRIAGE: "bg-indigo-50/80 border-indigo-200 text-indigo-700",
  JOB_CHANGE: "bg-emerald-50/80 border-emerald-200 text-emerald-700",
  NEW_BABY: "bg-pink-50/80 border-pink-200 text-pink-700",
  HOME_PURCHASE: "bg-amber-50/80 border-amber-200 text-amber-700",
  PRE_RETIREMENT: "bg-yellow-50/80 border-yellow-200 text-yellow-700",
  SALARY_HIKE: "bg-emerald-50/80 border-emerald-200 text-emerald-700",
  TRAVEL_PHASE: "bg-sky-50/80 border-sky-200 text-sky-700",
  NONE: "bg-slate-50 border-slate-200 text-slate-500"
};

export default function Dashboard() {
  const router = useRouter();
  const [customers, setCustomers] = useState([]);
  const [feed, setFeed] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const apiHost = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      const custRes = await fetch(`${apiHost}/customers`);
      if (custRes.ok) {
        const custData = await custRes.json();
        setCustomers(custData);
      }

      const feedRes = await fetch(`${apiHost}/engage/feed`);
      if (feedRes.ok) {
        const feedData = await feedRes.json();
        setFeed(feedData);
      }
    } catch (err) {
      console.error("Error fetching dashboard data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 8000);
    return () => clearInterval(interval);
  }, []);

  const triggerDetection = async () => {
    setLoading(true);
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/events/detect-all`, {
        method: "POST"
      });
      fetchDashboardData();
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score) => {
    if (score >= 0.9) return "bg-success";
    if (score >= 0.7) return "bg-sbi-orange";
    return "bg-slate-400";
  };

  const activeEventsCount = customers.filter(c => c.detected_life_event && c.detected_life_event !== "NONE").length;

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col md:flex-row overflow-x-hidden">
      <Head>
        <title>SBI LifePulse Banker Command Center</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      {/* Mobile Top Bar */}
      <header className="md:hidden w-full bg-sbi-dark text-white px-5 py-4 flex items-center justify-between z-30 shadow-md">
        <Link href="/" className="flex items-center gap-2">
          <div className="w-8 h-8 bg-white text-sbi-blue rounded-lg flex items-center justify-center font-black text-lg">
            S
          </div>
          <span className="font-bold text-sm uppercase tracking-wider">
            SBI <span className="text-sbi-orange">LifePulse</span>
          </span>
        </Link>
        <button 
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          className="p-1 text-slate-300 hover:text-white transition-colors"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </header>

      {/* Mobile Navigation Drawer */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 top-[60px] bg-sbi-dark text-white z-20 flex flex-col justify-between p-6 animate-fade-in">
          <div className="space-y-6">
            <nav className="space-y-2">
              <div className="flex items-center gap-3 px-4 py-3 bg-white/10 rounded-xl font-semibold text-sm">
                <BarChart2 size={18} /> Overview Dashboard
              </div>
              <button 
                onClick={() => {
                  triggerDetection();
                  setMobileMenuOpen(false);
                }}
                className="w-full text-left flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-white/5 hover:text-white rounded-xl transition-all font-medium text-sm"
              >
                <Users size={18} /> Analyze Accounts
              </button>
            </nav>
          </div>
          <div className="border-t border-white/10 pt-4">
            <div className="p-4 bg-white/5 border border-white/10 rounded-xl text-center">
              <span className="text-[9px] uppercase font-bold text-slate-400 tracking-wider">Active Alerts</span>
              <div className="text-2xl font-black text-sbi-orange mt-1">{activeEventsCount}</div>
            </div>
          </div>
        </div>
      )}

      {/* Desktop Sidebar */}
      <aside className="hidden md:flex w-64 bg-sbi-dark text-white p-6 flex-col justify-between flex-shrink-0 z-10 shadow-lg">
        <div className="space-y-8">
          <Link href="/" className="flex items-center gap-2">
            <div className="w-8 h-8 bg-white text-sbi-blue rounded-lg flex items-center justify-center font-black text-lg">
              S
            </div>
            <span className="font-bold text-sm uppercase tracking-wider">
              SBI <span className="text-sbi-orange">LifePulse</span>
            </span>
          </Link>

          <nav className="space-y-2">
            <div className="flex items-center gap-3 px-4 py-3 bg-white/10 rounded-xl font-semibold text-sm">
              <BarChart2 size={18} /> Overview Dashboard
            </div>
            <button 
              onClick={triggerDetection}
              className="w-full text-left flex items-center gap-3 px-4 py-3 text-slate-300 hover:bg-white/5 hover:text-white rounded-xl transition-all font-medium text-sm"
            >
              <Users size={18} /> Analyze Accounts
            </button>
          </nav>
        </div>

        <div className="pt-6 border-t border-white/10">
          <div className="p-4 bg-white/5 border border-white/10 rounded-2xl text-center relative overflow-hidden">
            <span className="text-[9px] uppercase font-bold text-slate-400 tracking-wider">Active Alerts</span>
            <div className="text-3xl font-black text-sbi-orange mt-1 pulse-glowing-orange w-fit mx-auto px-4 py-0.5 rounded-full">
              {activeEventsCount}
            </div>
            <p className="text-[10px] text-slate-400 mt-2">Milestone signals detected</p>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 p-4 sm:p-6 lg:p-8 space-y-6 overflow-y-auto">
        {/* Top Header Panel */}
        <div className="glass-card-light rounded-2xl p-5 sm:p-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4 border border-white/40 shadow-md">
          <div>
            <h1 className="text-xl sm:text-2xl font-bold text-sbi-dark">SBI Banker Command Center</h1>
            <p className="text-xs text-text-secondary mt-0.5">
              Proactive Financial Life Intelligence & Cross-sell Automation
            </p>
          </div>
          <button
            onClick={triggerDetection}
            disabled={loading}
            className="apple-btn-primary px-5 py-2.5 text-xs font-bold flex items-center justify-center gap-2 self-start sm:self-auto disabled:opacity-50"
          >
            <Play size={12} fill="currentColor" /> Scan Transaction Streams
          </button>
        </div>

        {/* Section A: Feed and metrics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2">
            <MetricsDashboard customers={customers} />
          </div>
          <div>
            <EngagementFeed activities={feed} />
          </div>
        </div>

        {/* Section B: Customer Cards Grid */}
        <div className="space-y-4">
          <h2 className="text-lg font-bold text-sbi-dark flex items-center gap-2">
            <span>👥</span> Customer Pipeline
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {customers.map((cust) => {
              const event = cust.detected_life_event || "NONE";
              const emoji = EVENT_ICONS[event] || "🔔";
              const detail = cust.life_event_details || {};
              const confidence = detail.confidence_score || 0.0;
              
              return (
                <div 
                  key={cust.customer_id}
                  className="glass-card-light glass-card-light-hover rounded-2xl p-5 flex flex-col justify-between gap-4 border border-white/40"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0">
                      <h3 className="font-bold text-sbi-dark text-base truncate">{cust.name}</h3>
                      <p className="text-xs text-text-secondary mt-0.5 truncate">{cust.city} • Age {cust.age}</p>
                    </div>
                    {/* Event Badge */}
                    <span className={`px-2.5 py-1 text-xs border rounded-lg font-semibold flex items-center gap-1.5 capitalize flex-shrink-0 ${EVENT_COLORS[event]}`}>
                      <span>{emoji}</span> {event.replace("_", " ").toLowerCase()}
                    </span>
                  </div>

                  {/* Confidence Progress Bar */}
                  {event !== "NONE" && (
                    <div className="space-y-1">
                      <div className="flex items-center justify-between text-[10px] font-semibold text-text-secondary uppercase">
                        <span>Detection Confidence</span>
                        <span>{Math.round(confidence * 100)}%</span>
                      </div>
                      <div className="h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full ${getConfidenceColor(confidence)}`}
                          style={{ width: `${confidence * 100}%` }}
                        />
                      </div>
                    </div>
                  )}

                  {/* Actions */}
                  <div className="flex gap-2 border-t border-slate-200/50 pt-4 mt-2">
                    <button
                      onClick={() => router.push(`/customer/${cust.customer_id}`)}
                      className="apple-btn-secondary flex-1 py-2 text-xs font-bold text-center"
                    >
                      View 360
                    </button>
                    {event !== "NONE" && (
                      <button
                        onClick={() => router.push(`/chat/${cust.customer_id}`)}
                        className="apple-btn-orange flex-1 py-2 text-xs font-bold text-center flex items-center justify-center gap-1"
                      >
                        <Sparkles size={11} /> Start Chat
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
            
            {customers.length === 0 && (
              <div className="col-span-full py-16 text-center text-text-secondary italic text-sm">
                No customer profiles loaded. Run seed_firestore script.
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
