import React, { useEffect, useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { ArrowLeft, Send, Sparkles, MessageSquare } from "lucide-react";
import CustomerProfile from "../../components/CustomerProfile";
import EventTimeline from "../../components/EventTimeline";
import LifeEventCard from "../../components/LifeEventCard";

export default function CustomerDetail() {
  const router = useRouter();
  const { id } = router.query;

  const [customer, setCustomer] = useState(null);
  const [lifeEvent, setLifeEvent] = useState(null);
  const [engagementPlan, setEngagementPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [outreachSuccess, setOutreachSuccess] = useState(false);

  const fetchCustomerData = async () => {
    if (!id) return;
    try {
      const apiHost = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
      
      const profRes = await fetch(`${apiHost}/customers/${id}`);
      if (profRes.ok) {
        const profData = await profRes.json();
        setCustomer(profData);
      }
      
      const eventRes = await fetch(`${apiHost}/events/${id}`);
      if (eventRes.ok) {
        const eventData = await eventRes.json();
        setLifeEvent(eventData);
      }

      const planRes = await fetch(`${apiHost}/engage/${id}`);
      if (planRes.ok) {
        const planData = await planRes.json();
        setEngagementPlan(planData);
      }
    } catch (err) {
      console.error("Error fetching customer data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchCustomerData();
  }, [id]);

  const triggerOutreach = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/engage/${id}/trigger`, {
        method: "POST"
      });
      if (response.ok) {
        setOutreachSuccess(true);
        fetchCustomerData();
        setTimeout(() => setOutreachSuccess(false), 4000);
      }
    } catch (err) {
      console.error("Error triggering outreach: ", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-sbi-blue border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-text-secondary font-semibold">Loading Customer 360 profile...</p>
        </div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6 text-center">
        <div>
          <h2 className="text-2xl font-bold text-sbi-dark">Customer Not Found</h2>
          <p className="text-sm text-text-secondary mt-1">We couldn't retrieve profile details for ID: {id}</p>
          <Link href="/dashboard" className="inline-block mt-4 text-sm font-semibold text-sbi-blue hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const spendingCategories = [
    { name: "Rent & Housing", value: 35, color: "bg-sbi-blue" },
    { name: "Groceries", value: 20, color: "bg-indigo-500" },
    { name: "Travel & Fuel", value: 15, color: "bg-sky-400" },
    { name: "Dining & Shopping", value: 22, color: "bg-sbi-orange" },
    { name: "Utilities & Subs", value: 8, color: "bg-slate-400" }
  ];

  return (
    <div className="min-h-screen bg-slate-100 p-4 sm:p-6 lg:p-8 overflow-x-hidden">
      <Head>
        <title>{customer.name} — Customer 360 View</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Navigation Header */}
        <div className="glass-card-light rounded-2xl p-4 sm:p-5 flex items-center gap-4 border border-white/40 shadow-sm">
          <Link 
            href="/dashboard"
            className="p-2.5 bg-white border border-slate-200 hover:border-slate-300 rounded-xl hover:bg-slate-50 transition-colors shadow-sm"
          >
            <ArrowLeft size={16} className="text-sbi-dark" />
          </Link>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-sbi-dark flex flex-wrap items-center gap-2 sm:gap-3 leading-tight">
              <span className="truncate">{customer.name}</span>
              <span className="text-[10px] font-bold px-2 py-0.5 border border-slate-200 rounded bg-slate-50 text-text-secondary uppercase">
                ID: {customer.customer_id}
              </span>
            </h1>
            <p className="text-xs text-text-secondary mt-0.5 truncate">Customer 360 Profile and Action Recommendation Engine</p>
          </div>
        </div>

        {/* Responsive Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
          
          {/* Column 1: Profile Summary */}
          <div className="space-y-6 lg:col-span-1">
            <CustomerProfile customer={customer} />
            
            {lifeEvent && (
              <LifeEventCard 
                eventType={lifeEvent.detected_event}
                confidenceScore={lifeEvent.confidence_score}
                customerName={customer.name}
                urgency={lifeEvent.engagement_urgency}
                keySignals={lifeEvent.key_signals}
              />
            )}
          </div>

          {/* Column 2: Transactions and Spending Categories */}
          <div className="space-y-6 lg:col-span-1">
            <div className="glass-card-light rounded-2xl p-5 shadow-sm space-y-4 border border-white/40">
              <h3 className="font-bold text-sbi-dark border-b border-slate-200/50 pb-3">
                Monthly Spending Distribution
              </h3>
              <div className="space-y-3">
                {spendingCategories.map((cat, idx) => (
                  <div key={idx} className="space-y-1">
                    <div className="flex items-center justify-between text-xs font-semibold">
                      <span className="text-sbi-dark">{cat.name}</span>
                      <span className="text-text-secondary">{cat.value}%</span>
                    </div>
                    <div className="h-2 w-full bg-slate-200/50 rounded-full overflow-hidden">
                      <div className={`h-full rounded-full ${cat.color}`} style={{ width: `${cat.value}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <EventTimeline 
              transactions={customer.transactions} 
              eventType={lifeEvent?.detected_event} 
            />
          </div>

          {/* Column 3: Recommended Action Plan */}
          <div className="space-y-6 lg:col-span-1">
            {engagementPlan ? (
              <div className="glass-card-light rounded-2xl p-6 shadow-md border border-white/40 flex flex-col gap-5 relative overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-1.5 bg-sbi-orange" />
                
                <h3 className="font-bold text-lg text-sbi-dark flex items-center gap-2">
                  <span className="text-xl">🎯</span>
                  Recommended Action Plan
                </h3>

                {/* WhatsApp message bubble preview */}
                <div className="space-y-1.5 min-w-0">
                  <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
                    Empathic Outreach Preview (WhatsApp)
                  </span>
                  <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-2xl rounded-tr-none text-sm text-slate-800 leading-relaxed shadow-sm prevent-overlap">
                    <p className="font-semibold text-emerald-600 text-xs mb-1">Arya (SBI Companion)</p>
                    {engagementPlan.opening_message}
                  </div>
                </div>

                {/* Suggested Starters */}
                {engagementPlan.conversation_starters && (
                  <div className="space-y-2">
                    <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
                      Conversation Starters
                    </span>
                    <ul className="space-y-2">
                      {engagementPlan.conversation_starters.map((starter, idx) => (
                        <li key={idx} className="text-xs bg-white border border-slate-200/70 text-sbi-blue font-semibold p-3 rounded-xl shadow-sm leading-normal prevent-overlap">
                          💡 "{starter}"
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Recommended Products */}
                <div className="space-y-3">
                  <span className="text-[10px] uppercase font-bold text-text-secondary tracking-wider">
                    Matched Products Placement
                  </span>
                  {engagementPlan.product_recommendations.map((prod, idx) => (
                    <div key={idx} className="p-3.5 bg-white border border-slate-200 hover:border-slate-300 rounded-xl shadow-sm space-y-1 transition-all">
                      <div className="flex items-center justify-between gap-2">
                        <h4 className="font-bold text-xs text-sbi-dark truncate">{prod.product_name}</h4>
                        <span className="text-[9px] uppercase font-bold text-sbi-orange bg-orange-50 px-2 py-0.5 rounded border border-orange-100 flex-shrink-0">
                          {prod.product_id}
                        </span>
                      </div>
                      <p className="text-[11px] text-text-secondary leading-normal prevent-overlap">{prod.why_now}</p>
                    </div>
                  ))}
                </div>

                {/* Contact details */}
                <div className="flex justify-between items-center text-[10px] text-text-secondary font-semibold bg-slate-50 p-2.5 rounded-xl border border-slate-100">
                  <span className="truncate pr-2">Priority: {engagementPlan.channel_priority?.join(" → ")}</span>
                  <span className="flex-shrink-0">Time: {engagementPlan.best_contact_time}</span>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2.5 pt-2 border-t border-slate-200/50 mt-2">
                  <button
                    onClick={triggerOutreach}
                    className="apple-btn-primary w-full py-3 text-xs"
                  >
                    Trigger Proactive Outreach
                  </button>
                  <button
                    onClick={() => router.push(`/chat/${customer.customer_id}`)}
                    className="apple-btn-orange w-full py-3 text-xs flex items-center justify-center gap-2"
                  >
                    <Sparkles size={12} /> Start AI Sandbox Chat
                  </button>
                </div>

                {outreachSuccess && (
                  <div className="absolute inset-0 bg-white/95 flex flex-col items-center justify-center p-6 text-center animate-fade-in z-20">
                    <span className="text-4xl">🎉</span>
                    <h4 className="text-lg font-bold text-sbi-dark mt-3">Outreach Triggered!</h4>
                    <p className="text-xs text-text-secondary mt-1 max-w-xs">
                      Empathetic WhatsApp payload successfully routed. Logged activity in banker stream.
                    </p>
                    <button 
                      onClick={() => setOutreachSuccess(false)}
                      className="mt-4 px-4 py-2 bg-sbi-blue text-white rounded-lg text-xs font-semibold"
                    >
                      Close Preview
                    </button>
                  </div>
                )}

              </div>
            ) : (
              <div className="glass-card-light rounded-2xl p-6 shadow-md border border-white/40 flex flex-col items-center justify-center text-center py-20 italic">
                <span className="text-3xl mb-3">🎯</span>
                <p className="text-xs text-text-secondary">No engagement plan has been drafted yet.</p>
                <button
                  onClick={fetchCustomerData}
                  className="mt-4 px-4 py-2 bg-sbi-blue text-white rounded-xl text-xs font-semibold"
                >
                  Generate Plan
                </button>
              </div>
            )}
          </div>

        </div>
      </div>
    </div>
  );
}
