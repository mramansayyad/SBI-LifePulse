import React, { useEffect, useState } from "react";
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from "recharts";
import { Sparkles, Users, MessageSquare, TrendingUp } from "lucide-react";

export default function MetricsDashboard({ customers = [] }) {
  const [revenue, setRevenue] = useState(0);

  useEffect(() => {
    let start = 0;
    const end = 2.4;
    const duration = 1200;
    const range = end - start;
    const increment = range / (duration / 10);
    
    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setRevenue(end);
        clearInterval(timer);
      } else {
        setRevenue(parseFloat(start.toFixed(2)));
      }
    }, 10);

    return () => clearInterval(timer);
  }, []);

  const totalCustomers = customers.length;
  const eventsDetected = customers.filter(c => c.detected_life_event && c.detected_life_event !== "NONE").length;
  const activeConversations = customers.filter(c => c.engagement_status === "engaged" || c.engagement_status === "converted").length;

  const eventCounts = {};
  customers.forEach(c => {
    const ev = c.detected_life_event || "NONE";
    if (ev !== "NONE") {
      eventCounts[ev] = (eventCounts[ev] || 0) + 1;
    }
  });

  const pieData = Object.keys(eventCounts).map(ev => ({
    name: ev,
    value: eventCounts[ev]
  }));

  const COLORS = ["#1B4F8E", "#F7941D", "#22C55E", "#A855F7", "#06B6D4", "#F43F5E", "#EAB308"];

  const barData = [
    { name: "WhatsApp", count: Math.ceil(eventsDetected * 0.8) },
    { name: "App Notification", count: Math.ceil(eventsDetected * 0.6) },
    { name: "Call", count: Math.ceil(eventsDetected * 0.3) },
    { name: "Email", count: Math.ceil(eventsDetected * 0.1) }
  ];

  return (
    <div className="space-y-6">
      {/* 4 KPI Cards Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Card 1 */}
        <div className="glass-card-light p-4 rounded-2xl shadow-sm border border-white/40 flex items-center gap-3">
          <div className="p-2 sm:p-3 bg-blue-50 text-sbi-blue rounded-xl flex-shrink-0">
            <Users size={18} />
          </div>
          <div className="min-w-0">
            <span className="text-[9px] uppercase font-bold text-text-secondary tracking-wider block truncate">
              Customers
            </span>
            <h4 className="text-base sm:text-lg font-black text-sbi-dark truncate">{totalCustomers}</h4>
          </div>
        </div>

        {/* Card 2 */}
        <div className="glass-card-light p-4 rounded-2xl shadow-sm border border-white/40 flex items-center gap-3">
          <div className="p-2 sm:p-3 bg-orange-50 text-sbi-orange rounded-xl flex-shrink-0">
            <Sparkles size={18} />
          </div>
          <div className="min-w-0">
            <span className="text-[9px] uppercase font-bold text-text-secondary tracking-wider block truncate">
              Detected
            </span>
            <h4 className="text-base sm:text-lg font-black text-sbi-dark truncate">{eventsDetected}</h4>
          </div>
        </div>

        {/* Card 3 */}
        <div className="glass-card-light p-4 rounded-2xl shadow-sm border border-white/40 flex items-center gap-3">
          <div className="p-2 sm:p-3 bg-green-50 text-success rounded-xl flex-shrink-0">
            <MessageSquare size={18} />
          </div>
          <div className="min-w-0">
            <span className="text-[9px] uppercase font-bold text-text-secondary tracking-wider block truncate">
              Engaged
            </span>
            <h4 className="text-base sm:text-lg font-black text-sbi-dark truncate">{activeConversations}</h4>
          </div>
        </div>

        {/* Card 4 */}
        <div className="glass-card-light p-4 rounded-2xl shadow-sm border border-white/40 flex items-center gap-3">
          <div className="p-2 sm:p-3 bg-purple-50 text-purple-600 rounded-xl flex-shrink-0">
            <TrendingUp size={18} />
          </div>
          <div className="min-w-0">
            <span className="text-[9px] uppercase font-bold text-text-secondary tracking-wider block truncate">
              Est Revenue
            </span>
            <h4 className="text-base sm:text-lg font-black text-sbi-dark truncate">₹{revenue} Cr</h4>
          </div>
        </div>
      </div>

      {/* 2 Charts Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
        {/* Pie Chart: Life Events */}
        <div className="glass-card-light rounded-2xl p-5 shadow-sm border border-white/40">
          <h3 className="font-bold text-sbi-dark border-b border-slate-200/50 pb-3 mb-4">
            Life Event Distribution
          </h3>
          <div className="h-[200px] w-full">
            {pieData.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={65}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value) => [`${value} Profile(s)`, "Count"]} />
                  <Legend verticalAlign="bottom" height={36} iconType="circle" wrapperStyle={{ fontSize: '10px' }} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="h-full flex items-center justify-center text-text-secondary text-xs italic">
                No events detected yet. Click "Scan Transaction Streams" to begin.
              </div>
            )}
          </div>
        </div>

        {/* Bar Chart: Outreach Channel Effectiveness */}
        <div className="glass-card-light rounded-2xl p-5 shadow-sm border border-white/40">
          <h3 className="font-bold text-sbi-dark border-b border-slate-200/50 pb-3 mb-4">
            Outreach Channels Utilized
          </h3>
          <div className="h-[200px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#6B7280" fontSize={9} tickLine={false} />
                <YAxis stroke="#6B7280" fontSize={9} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: "rgba(241, 245, 249, 0.4)" }} />
                <Bar dataKey="count" fill="#1B4F8E" radius={[6, 6, 0, 0]}>
                  {barData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.name === "WhatsApp" ? "#22C55E" : "#1B4F8E"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
