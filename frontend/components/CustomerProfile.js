import React from "react";

export default function CustomerProfile({ customer }) {
  if (!customer) return null;

  const getInitials = (name) => {
    return name
      .split(" ")
      .map((n) => n[0])
      .join("")
      .toUpperCase();
  };

  const getRiskBadgeColor = (risk) => {
    if (risk === "aggressive") return "bg-red-50 text-red-600 border-red-200";
    if (risk === "moderate") return "bg-amber-50 text-amber-600 border-amber-200";
    return "bg-emerald-50 text-emerald-600 border-emerald-200";
  };

  const getStatusBadgeColor = (status) => {
    if (status === "converted") return "bg-success text-white";
    if (status === "engaged") return "bg-sbi-blue text-white";
    if (status === "churned") return "bg-rose-600 text-white";
    return "bg-slate-200 text-slate-700";
  };

  return (
    <div className="glass-card-light rounded-2xl p-5 sm:p-6 shadow-md border border-white/40 flex flex-col gap-5">
      {/* Avatar and Basic Details */}
      <div className="flex items-center gap-4 border-b border-slate-200/50 pb-4">
        <div className="w-14 h-14 sm:w-16 sm:h-16 rounded-2xl bg-gradient-to-tr from-sbi-blue to-blue-500 text-white flex items-center justify-center font-bold text-xl shadow-md flex-shrink-0">
          {getInitials(customer.name)}
        </div>
        <div className="min-w-0">
          <h2 className="text-lg sm:text-xl font-bold text-sbi-dark truncate leading-tight">{customer.name}</h2>
          <p className="text-xs text-text-secondary mt-0.5 truncate">
            {customer.city} • Age {customer.age}
          </p>
          <span className={`inline-block px-2.5 py-0.5 text-[9px] uppercase font-bold tracking-wider rounded-full mt-2 ${getStatusBadgeColor(customer.engagement_status)}`}>
            Status: {customer.engagement_status}
          </span>
        </div>
      </div>

      {/* Account Info Grid */}
      <div className="grid grid-cols-2 gap-4">
        <div className="min-w-0">
          <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
            Account Number
          </span>
          <p className="text-xs sm:text-sm font-bold text-sbi-dark font-mono mt-0.5 truncate">
            {customer.account_number}
          </p>
        </div>
        <div className="min-w-0">
          <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
            Monthly Income
          </span>
          <p className="text-xs sm:text-sm font-bold text-sbi-dark mt-0.5 truncate">
            ₹{customer.monthly_income.toLocaleString("en-IN")}
          </p>
        </div>
        <div className="min-w-0">
          <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
            Risk Profile
          </span>
          <span className={`block w-fit text-xs font-bold px-2 py-0.5 border rounded-md mt-1 capitalize truncate ${getRiskBadgeColor(customer.risk_profile)}`}>
            {customer.risk_profile}
          </span>
        </div>
        <div className="min-w-0">
          <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
            Detected Event
          </span>
          <p className="text-xs sm:text-sm font-bold text-sbi-orange mt-0.5 truncate">
            {customer.detected_life_event || "None"}
          </p>
        </div>
      </div>

      {/* Existing Products */}
      <div className="border-t border-slate-200/50 pt-4">
        <h3 className="text-[10px] uppercase font-bold text-text-secondary tracking-wider mb-2">
          Existing SBI Products
        </h3>
        <div className="flex flex-wrap gap-2">
          {customer.existing_products.map((prod, idx) => (
            <span 
              key={idx}
              className="text-xs font-semibold px-2.5 py-1 bg-white border border-slate-200 text-sbi-dark rounded-lg capitalize shadow-sm hover:shadow-md transition-shadow cursor-default"
            >
              💼 {prod.replace("_", " ")}
            </span>
          ))}
          {customer.existing_products.length === 0 && (
            <span className="text-xs text-text-secondary italic">
              No products active.
            </span>
          )}
        </div>
      </div>
    </div>
  );
}
