import React, { useEffect, useState } from "react";
import Head from "next/head";
import Link from "next/link";
import { useRouter } from "next/router";
import { ArrowLeft, Sparkles } from "lucide-react";
import ConversationWindow from "../../components/ConversationWindow";

export default function ChatPage() {
  const router = useRouter();
  const { id } = router.query;

  const [customer, setCustomer] = useState(null);
  const [lifeEvent, setLifeEvent] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchChatContext = async () => {
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
      } catch (err) {
        console.error("Error fetching chat context:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchChatContext();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-sbi-blue border-t-transparent rounded-full animate-spin" />
          <p className="text-xs text-text-secondary font-semibold">Connecting to Arya AI Agent...</p>
        </div>
      </div>
    );
  }

  if (!customer) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-6 text-center">
        <div>
          <h2 className="text-2xl font-bold text-sbi-dark">Chat Session Failed</h2>
          <p className="text-sm text-text-secondary mt-1">We couldn't retrieve context for customer ID: {id}</p>
          <Link href="/dashboard" className="inline-block mt-4 text-sm font-semibold text-sbi-blue hover:underline">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 flex flex-col justify-between p-3 sm:p-5 lg:p-6 overflow-hidden">
      <Head>
        <title>Chat with Arya — SBI Financial Companion</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>

      <div className="max-w-4xl mx-auto w-full space-y-4 flex-1 flex flex-col h-full min-h-0">
        {/* Navigation Bar */}
        <div className="flex items-center justify-between gap-4">
          <Link
            href={`/customer/${customer.customer_id}`}
            className="apple-btn-secondary flex items-center justify-center gap-2 text-xs px-4 py-2 border shadow-sm flex-shrink-0"
          >
            <ArrowLeft size={12} /> Back to 360
          </Link>
          
          <span className="text-[10px] sm:text-xs font-semibold text-text-secondary bg-white px-3.5 py-2 border border-slate-200 rounded-xl shadow-sm truncate">
            🔒 Secure Chat Session
          </span>
        </div>

        {/* Info panel */}
        <div className="glass-card-light p-4 rounded-2xl border border-white/40 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="text-2xl flex-shrink-0">💡</span>
            <div className="min-w-0">
              <h4 className="font-bold text-sm text-sbi-dark truncate">Conversational Banking Sandbox</h4>
              <p className="text-xs text-text-secondary truncate">
                Simulating customer engagement flow. Arya uses Gemini function calling for calculations.
              </p>
            </div>
          </div>
          {lifeEvent && (
            <span className="px-3 py-1 bg-orange-50 border border-sbi-orange/20 text-sbi-orange text-[10px] font-bold uppercase rounded-lg tracking-wide self-start sm:self-auto flex items-center gap-1.5 flex-shrink-0">
              <span>💍</span> {lifeEvent.detected_event}
            </span>
          )}
        </div>

        {/* Conversation Chat Window Component */}
        <div className="flex-1 flex flex-col justify-end min-h-0">
          <ConversationWindow
            customerId={customer.customer_id}
            customerName={customer.name}
            lifeEvent={lifeEvent?.detected_event}
          />
        </div>
      </div>
      
      {/* Footer */}
      <footer className="text-center text-[10px] text-text-secondary py-3 max-w-lg mx-auto">
        Arya is SBI's AI Companion. In a live deployment, Arya connects via WhatsApp Business API or YONO App integration.
      </footer>
    </div>
  );
}
