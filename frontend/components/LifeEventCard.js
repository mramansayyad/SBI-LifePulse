import React from "react";

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

const EVENT_LABELS = {
  MARRIAGE: "Marriage / Wedding",
  JOB_CHANGE: "Job Change / Promotion",
  NEW_BABY: "New Born Baby",
  HOME_PURCHASE: "Home Purchase",
  PRE_RETIREMENT: "Pre-Retirement Stage",
  SALARY_HIKE: "Salary Hike",
  TRAVEL_PHASE: "Travel Phase",
  NONE: "No Event Detected"
};

export default function LifeEventCard({ 
  eventType, 
  confidenceScore, 
  customerName, 
  urgency, 
  keySignals = [] 
}) {
  const emoji = EVENT_ICONS[eventType] || "AI";
  const label = EVENT_LABELS[eventType] || eventType;
  
  // Circle calculations
  const radius = 28;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference - (confidenceScore * circumference);

  const getUrgencyColor = (urg) => {
    if (urg === "HIGH") return "bg-danger text-white pulse-badge";
    if (urg === "MEDIUM") return "bg-sbi-orange text-white";
    return "bg-slate-200 text-slate-700";
  };

  return (
    <div className="glass-card-light rounded-2xl p-5 sm:p-6 shadow-md border border-white/40 slide-in-up relative overflow-hidden">
      {/* Decorative colored glow on top */}
      <div className={`absolute top-0 left-0 right-0 h-1.5 ${urgency === 'HIGH' ? 'bg-danger' : urgency === 'MEDIUM' ? 'bg-sbi-orange' : 'bg-sbi-blue'}`} />
      
      <div className="flex items-center justify-between gap-4">
        <div className="min-w-0">
          <span className={`inline-block px-2.5 py-0.5 text-[9px] font-bold rounded-full uppercase tracking-wider mb-2.5 ${getUrgencyColor(urgency)}`}>
            {urgency} Urgency
          </span>
          <h3 className="text-lg sm:text-xl font-bold text-sbi-dark flex items-center gap-2 truncate leading-snug">
            <span className="text-2xl flex-shrink-0">{emoji}</span>
            <span className="truncate">{label}</span>
          </h3>
          <p className="text-xs text-text-secondary mt-0.5 truncate">
            Detected for {customerName}
          </p>
        </div>

        {/* Confidence Circle */}
        <div className="flex flex-col items-center flex-shrink-0">
          <div className="relative flex items-center justify-center w-14 h-14 sm:w-16 sm:h-16">
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="50%"
                cy="50%"
                r={radius}
                className="stroke-slate-200"
                strokeWidth="4"
                fill="transparent"
              />
              <circle
                cx="50%"
                cy="50%"
                r={radius}
                className={urgency === 'HIGH' ? 'stroke-danger' : 'stroke-sbi-blue'}
                strokeWidth="4"
                fill="transparent"
                strokeDasharray={circumference}
                strokeDashoffset={offset}
                strokeLinecap="round"
              />
            </svg>
            <span className="absolute text-xs sm:text-sm font-bold text-sbi-dark">
              {Math.round(confidenceScore * 100)}%
            </span>
          </div>
          <span className="text-[9px] uppercase font-bold tracking-wider text-text-secondary mt-1 whitespace-nowrap">
            Confidence
          </span>
        </div>
      </div>

      {/* Signals Section */}
      <div className="mt-5 border-t border-slate-200/50 pt-4">
        <h4 className="text-[10px] uppercase tracking-wider font-bold text-text-secondary mb-2.5">
          Key Transaction Signals
        </h4>
        <div className="flex flex-wrap gap-2">
          {keySignals.map((signal, idx) => (
            <span 
              key={idx} 
              className="px-2.5 py-1 text-xs bg-white border border-slate-200 text-sbi-blue rounded-lg font-semibold shadow-sm truncate max-w-xs hover:bg-slate-50 transition-colors cursor-default"
            >
              🔍 {signal}
            </span>
          ))}
          {keySignals.length === 0 && (
            <span className="text-xs text-text-secondary italic">
              No anomalies detected.
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
