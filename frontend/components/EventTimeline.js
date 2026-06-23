import React from "react";
import { ArrowUpRight, ArrowDownRight, Tag } from "lucide-react";

export default function EventTimeline({ transactions = [], eventType }) {
  const sortedTxs = [...transactions]
    .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
    .slice(0, 15);

  const isSignalTransaction = (tx) => {
    const desc = (tx.description || "").toLowerCase();
    const merchant = (tx.merchant_name || "").toLowerCase();
    
    if (eventType === "MARRIAGE") {
      return (
        merchant.includes("tanishq") ||
        desc.includes("wedding") ||
        desc.includes("marriage") ||
        desc.includes("resort") ||
        desc.includes("honeymoon") ||
        desc.includes("sarees")
      );
    }
    if (eventType === "JOB_CHANGE") {
      return (
        desc.includes("linkedin") ||
        (desc.includes("salary") && tx.transaction_type === "credit") ||
        merchant.includes("zara") ||
        merchant.includes("raymond") ||
        desc.includes("car loan emi") ||
        desc.includes("macbook")
      );
    }
    if (eventType === "NEW_BABY") {
      return (
        merchant.includes("firstcry") ||
        merchant.includes("mothercare") ||
        desc.includes("maternity") ||
        desc.includes("baby") ||
        desc.includes("delivery") ||
        desc.includes("pharmacy") ||
        desc.includes("family health insurance")
      );
    }
    if (eventType === "HOME_PURCHASE") {
      return (
        desc.includes("developers") ||
        desc.includes("registrar") ||
        desc.includes("stamp duty") ||
        merchant.includes("ikea") ||
        merchant.includes("pepperfry") ||
        desc.includes("home loan valuation")
      );
    }
    if (eventType === "PRE_RETIREMENT") {
      return (
        desc.includes("nps") ||
        desc.includes("pension") ||
        desc.includes("provident") ||
        desc.includes("pilgrimage") ||
        desc.includes("senior citizen") ||
        desc.includes("gratuity")
      );
    }
    if (eventType === "TRAVEL_PHASE") {
      return (
        desc.includes("flight") ||
        desc.includes("airbnb") ||
        desc.includes("niyo") ||
        desc.includes("forex") ||
        desc.includes("uber")
      );
    }
    if (eventType === "SALARY_HIKE") {
      return desc.includes("salary") && tx.transaction_type === "credit";
    }
    
    return false;
  };

  const getFormatDate = (isoString) => {
    try {
      const date = new Date(isoString);
      return date.toLocaleDateString("en-IN", { month: "short", day: "numeric" });
    } catch {
      return isoString;
    }
  };

  return (
    <div className="glass-card-light rounded-2xl p-4 sm:p-5 shadow-sm h-[520px] flex flex-col border border-white/40">
      <h3 className="font-bold text-sbi-dark border-b border-slate-200/50 pb-3 mb-4 flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm sm:text-base">Transactions & Signals</span>
        {eventType && eventType !== "NONE" && (
          <span className="text-[9px] font-bold uppercase tracking-wider bg-orange-100 text-sbi-orange px-2 py-0.5 rounded-md flex-shrink-0">
            {eventType}
          </span>
        )}
      </h3>

      <div className="flex-1 overflow-y-auto pr-1 space-y-3 min-h-0">
        {sortedTxs.map((tx) => {
          const isSignal = isSignalTransaction(tx);
          const isCredit = tx.transaction_type === "credit";
          
          return (
            <div 
              key={tx.transaction_id}
              className={`flex items-start gap-3 p-3 rounded-xl border transition-all duration-200 ${
                isSignal 
                  ? "bg-amber-50/70 border-sbi-orange shadow-sm" 
                  : "bg-white/80 border-slate-100 hover:border-slate-200"
              }`}
            >
              {/* Indicator Icon */}
              <div className={`p-2 rounded-xl flex-shrink-0 ${
                isSignal
                  ? "bg-orange-100 text-sbi-orange"
                  : isCredit
                    ? "bg-emerald-50 text-success"
                    : "bg-slate-100 text-slate-500"
              }`}>
                {isCredit ? (
                  <ArrowDownRight size={14} />
                ) : (
                  <ArrowUpRight size={14} />
                )}
              </div>

              {/* Transaction details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between gap-2">
                  <h4 className="font-bold text-xs sm:text-sm text-sbi-dark truncate">
                    {tx.merchant_name}
                  </h4>
                  <span className={`font-black text-xs sm:text-sm flex-shrink-0 ${isCredit ? "text-success" : "text-sbi-dark"}`}>
                    {isCredit ? "+" : "-"}₹{parseFloat(tx.amount).toLocaleString("en-IN")}
                  </span>
                </div>
                
                <div className="flex items-center justify-between gap-2 mt-1">
                  <p className="text-[11px] text-text-secondary truncate pr-2">
                    {tx.description}
                  </p>
                  <span className="text-[9px] text-text-secondary font-mono whitespace-nowrap flex-shrink-0">
                    {getFormatDate(tx.date)}
                  </span>
                </div>
                
                {isSignal && (
                  <span className="inline-flex items-center gap-1 text-[8px] font-bold uppercase tracking-wider text-sbi-orange mt-1.5 bg-white px-2 py-0.5 border border-sbi-orange/20 rounded">
                    <Tag size={8} /> Signal
                  </span>
                )}
              </div>
            </div>
          );
        })}

        {transactions.length === 0 && (
          <div className="h-full flex items-center justify-center text-text-secondary text-xs italic">
            No transactions found.
          </div>
        )}
      </div>
    </div>
  );
}
