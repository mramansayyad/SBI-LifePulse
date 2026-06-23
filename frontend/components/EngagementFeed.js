import React, { useState } from "react";

export default function EngagementFeed({ activities = [] }) {
  const [filter, setFilter] = useState("ALL");

  const filteredActivities = activities.filter((act) => {
    if (filter === "ALL") return true;
    return act.urgency === filter;
  });

  const getUrgencyIndicator = (urgency) => {
    if (urgency === "HIGH") return "bg-danger shadow-danger/50";
    if (urgency === "MEDIUM") return "bg-sbi-orange shadow-sbi-orange/50";
    return "bg-sbi-blue shadow-sbi-blue/50";
  };

  const formatTime = (isoString) => {
    if (!isoString) return "Just now";
    try {
      const date = new Date(isoString);
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    } catch {
      return "Just now";
    }
  };

  return (
    <div className="glass-panel rounded-2xl p-5 shadow-md flex flex-col h-[320px]">
      <div className="flex items-center justify-between border-b border-slate-100 pb-3 mb-3">
        <h3 className="font-bold text-sbi-dark flex items-center gap-2">
          <span className="w-2.5 h-2.5 rounded-full bg-sbi-orange animate-ping" />
          Live Engagement Stream
        </h3>
        {/* Filters */}
        <div className="flex bg-slate-100 p-0.5 rounded-lg text-xs font-semibold">
          {["ALL", "HIGH", "MEDIUM", "LOW"].map((lvl) => (
            <button
              key={lvl}
              onClick={() => setFilter(lvl)}
              className={`px-2.5 py-1 rounded-md transition-all ${
                filter === lvl
                  ? "bg-white text-sbi-blue shadow-sm"
                  : "text-text-secondary hover:text-sbi-blue"
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Scrolling List */}
      <div className="flex-1 overflow-y-auto space-y-3 pr-1">
        {filteredActivities.map((act, index) => (
          <div 
            key={act.id || index}
            className="flex items-start gap-3 p-3 bg-white/70 hover:bg-white rounded-xl transition-all duration-200 shadow-sm border border-slate-100/50"
          >
            {/* Urgency Dot */}
            <span className={`w-3 h-3 rounded-full mt-1.5 flex-shrink-0 shadow-sm ${getUrgencyIndicator(act.urgency)}`} />
            
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between gap-2 mb-0.5">
                <span className="font-semibold text-sm text-sbi-dark truncate">
                  {act.customer_name}
                </span>
                <span className="text-[10px] text-text-secondary font-mono flex-shrink-0">
                  {formatTime(act.timestamp)}
                </span>
              </div>
              <p className="text-xs text-text-secondary line-clamp-2">
                {act.message}
              </p>
            </div>
          </div>
        ))}

        {filteredActivities.length === 0 && (
          <div className="h-full flex flex-col items-center justify-center text-text-secondary py-12 italic text-xs">
            No live activities matches this filter.
          </div>
        )}
      </div>
    </div>
  );
}
