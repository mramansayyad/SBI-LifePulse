import React, { useState, useEffect, useRef } from "react";
import { Send, Wallet, Percent, Sparkles, PhoneCall } from "lucide-react";

export default function ConversationWindow({ customerId, customerName, lifeEvent }) {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [quickReplies, setQuickReplies] = useState([]);
  
  const messagesEndRef = useRef(null);

  const getQuickReplies = (event) => {
    if (event === "MARRIAGE") {
      return ["Tell me about joint accounts", "What home loan can I get?", "How to start investing together?"];
    } else if (event === "JOB_CHANGE") {
      return ["What is the best SIP for me?", "Tell me about SBI Card ELITE", "Open an SBI Wealth Account"];
    } else if (event === "NEW_BABY") {
      return ["Calculate SIP for child education", "Check family health insurance plans", "What is Smart Champ?"];
    } else if (event === "HOME_PURCHASE") {
      return ["Estimate Home Loan EMI", "Calculate returns for home shield insurance", "Book appointment with RM"];
    } else if (event === "PRE_RETIREMENT") {
      return ["Explain Senior Citizen Savings Scheme", "Tell me about Annuity deposits", "Fixed Deposit laddering ideas"];
    }
    return ["Check my balance", "Calculate SIP returns", "What products do you recommend?"];
  };

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/chat/${customerId}/history`);
        if (response.ok) {
          const data = await response.json();
          if (data && data.length > 0) {
            setMessages(data);
          } else {
            const initMsg = getInitialMessage(customerName, lifeEvent);
            setMessages([{ role: "assistant", message: initMsg, timestamp: new Date().toISOString() }]);
          }
        }
      } catch (err) {
        console.error("Error fetching chat history: ", err);
        const initMsg = getInitialMessage(customerName, lifeEvent);
        setMessages([{ role: "assistant", message: initMsg, timestamp: new Date().toISOString() }]);
      }
    };

    fetchHistory();
    setQuickReplies(getQuickReplies(lifeEvent));
  }, [customerId, customerName, lifeEvent]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isTyping]);

  const getInitialMessage = (name, event) => {
    if (event === "MARRIAGE") {
      return `Hi ${name}! 💍 Congratulations on your recent marriage! I'm Arya, your SBI personal financial companion. I noticed some exciting changes in your account and wanted to reach out. I can help you and your partner plan your joint finances. What would you like to explore today?`;
    }
    if (event === "JOB_CHANGE") {
      return `Hello ${name}! 💼 Congratulations on your new job role! I'm Arya, your SBI personal financial companion. I see a wonderful jump in your salary credits. Let's make sure we direct this new cash flow into high-yield mutual funds or look at premium card options. What's on your mind?`;
    }
    if (event === "NEW_BABY") {
      return `Namaste ${name}! 👶 Congratulations on welcoming a new baby to your family! I'm Arya, your SBI personal advisor. Let's make sure we secure their education and future early. I can calculate potential SIP plans or help you review family floater insurance. How can I help?`;
    }
    if (event === "HOME_PURCHASE") {
      return `Hi ${name}! 🏠 Heartiest congratulations on your new home search! I'm Arya from SBI. Buying a home is a wonderful milestone. I'd love to help you estimate your home loan EMIs or review home shield plans. Would you like to check some numbers?`;
    }
    if (event === "PRE_RETIREMENT") {
      return `Greetings ${name}! 🌅 As you prepare for your upcoming retirement milestone, I'm Arya, your financial companion here to help you structure a secure and steady monthly pension stream. Let's look at Senior Citizen schemes or FD laddering. What's on your mind?`;
    }
    return `Hello ${name}! I'm Arya, your SBI AI Financial Companion. How can I assist you with your accounts, loans, or investments today?`;
  };

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const userTurn = { role: "user", message: text, timestamp: new Date().toISOString() };
    setMessages((prev) => [...prev, userTurn]);
    setInputValue("");
    setIsTyping(true);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/chat/${customerId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ message: text }),
      });

      if (response.ok) {
        const data = await response.json();
        setMessages((prev) => [
          ...prev,
          { role: "assistant", message: data.response, timestamp: new Date().toISOString() },
        ]);
      } else {
        throw new Error("Chat request failed");
      }
    } catch (err) {
      console.error("Chat error: ", err);
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: "assistant",
            message: `I'm currently running in sandbox mode, but I hear you! Let me help you set up that request right away. Shall I book an RM callback or calculate that for you?`,
            timestamp: new Date().toISOString(),
          },
        ]);
      }, 1000);
    } finally {
      setIsTyping(false);
    }
  };

  const resetChat = async () => {
    try {
      await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080'}/chat/${customerId}`, {
        method: "DELETE",
      });
      const initMsg = getInitialMessage(customerName, lifeEvent);
      setMessages([{ role: "assistant", message: initMsg, timestamp: new Date().toISOString() }]);
    } catch (err) {
      console.error("Error resetting chat: ", err);
    }
  };

  return (
    <div className="glass-card-light rounded-2xl shadow-lg border border-white/40 flex flex-col h-[520px] overflow-hidden">
      {/* Top Bar */}
      <div className="bg-gradient-to-r from-sbi-blue to-blue-800 p-4 text-white flex items-center justify-between shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center text-sbi-blue font-bold shadow-sm relative flex-shrink-0">
            <span className="text-xl">🤵</span>
            <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-success rounded-full border-2 border-white" />
          </div>
          <div className="min-w-0">
            <h3 className="font-bold text-sm tracking-wide truncate">Arya Companion</h3>
            <p className="text-[10px] text-blue-200 truncate">
              Chatting as: {customerName} {lifeEvent && `• 💍 ${lifeEvent}`}
            </p>
          </div>
        </div>
        <button
          onClick={resetChat}
          className="text-xs px-2.5 py-1.5 bg-white/10 hover:bg-white/20 transition-colors rounded-lg font-semibold border border-white/10 flex-shrink-0"
        >
          Reset Session
        </button>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50/40 min-h-0">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${
              msg.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-2xl p-3.5 shadow-sm text-sm leading-relaxed ${
                msg.role === "user"
                  ? "bg-white text-sbi-dark rounded-br-none border border-slate-200 prevent-overlap"
                  : "bg-sbi-blue text-white rounded-bl-none prevent-overlap"
              }`}
            >
              <p className="whitespace-pre-line">{msg.message}</p>
            </div>
          </div>
        ))}

        {isTyping && (
          <div className="flex justify-start">
            <div className="bg-sbi-blue text-white max-w-[80%] rounded-2xl rounded-bl-none p-3 shadow-sm flex items-center gap-1.5">
              <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
              <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
              <span className="w-1.5 h-1.5 bg-white rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Quick Action Suggestions - Styled as Scrollbar container */}
      <div className="bg-white border-t border-slate-200/50 p-2 flex gap-2 overflow-x-auto whitespace-nowrap scrollbar-thin">
        <button
          onClick={() => handleSendMessage("Check my balance")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-sbi-light hover:bg-slate-100 text-[11px] font-bold text-sbi-blue rounded-full border border-slate-200 transition-colors flex-shrink-0"
        >
          <Wallet size={12} /> Check Balance
        </button>
        <button
          onClick={() => handleSendMessage("Calculate my SIP returns")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-sbi-light hover:bg-slate-100 text-[11px] font-bold text-sbi-blue rounded-full border border-slate-200 transition-colors flex-shrink-0"
        >
          <Sparkles size={12} /> Calculate SIP
        </button>
        <button
          onClick={() => handleSendMessage("Calculate Home Loan EMI")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-sbi-light hover:bg-slate-100 text-[11px] font-bold text-sbi-blue rounded-full border border-slate-200 transition-colors flex-shrink-0"
        >
          <Percent size={12} /> Calculate EMI
        </button>
        <button
          onClick={() => handleSendMessage("Book an appointment with RM")}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-sbi-light hover:bg-slate-100 text-[11px] font-bold text-sbi-blue rounded-full border border-slate-200 transition-colors flex-shrink-0"
        >
          <PhoneCall size={12} /> Book RM
        </button>
      </div>

      {/* Suggested Quick Replies */}
      <div className="bg-slate-50 border-t border-slate-100 px-3 py-2 flex gap-2 overflow-x-auto whitespace-nowrap scrollbar-thin">
        {quickReplies.map((reply, index) => (
          <button
            key={index}
            onClick={() => handleSendMessage(reply)}
            className="px-3 py-1 bg-white hover:bg-sbi-blue hover:text-white transition-all text-xs text-text-secondary border border-slate-200 rounded-lg shadow-sm flex-shrink-0 font-medium"
          >
            {reply}
          </button>
        ))}
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSendMessage(inputValue);
        }}
        className="bg-white border-t border-slate-200/50 p-3 flex gap-2 items-center"
      >
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Ask Arya anything about your finances..."
          className="flex-1 px-4 py-2 border border-slate-200 rounded-xl text-sm focus:outline-none focus:border-sbi-blue transition-colors min-w-0"
        />
        <button
          type="submit"
          disabled={!inputValue.trim()}
          className="w-10 h-10 rounded-xl bg-sbi-blue hover:bg-blue-800 disabled:bg-slate-100 disabled:text-slate-400 text-white flex items-center justify-center shadow transition-colors flex-shrink-0"
        >
          <Send size={15} />
        </button>
      </form>
    </div>
  );
}
