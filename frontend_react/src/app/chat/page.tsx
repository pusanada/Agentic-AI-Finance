'use client';

import React, { useState, useRef, useEffect } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/store/translations';
import { Bot, User, Send, Sparkles, MessageSquare, HelpCircle, Loader2, ArrowLeft } from 'lucide-react';
import Link from 'next/link';

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: Date;
}

export default function TaxChatPage() {
  const { language, theme, setTheme } = useAppStore();
  const t = translations[language];

  // Set theme to dark or keep user theme. Let's make it look like a sleek dashboard.
  // We can let the user theme persist, but make the interface feel premium on both.
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Suggested questions based on language
  const suggestedQuestions = language === 'TH' ? [
    "เงื่อนไขการลดหย่อนภาษีของ ThaiESG คืออะไร?",
    "สิทธิ์ซื้อสูงสุดคำนวณจากอะไร และหักลดหย่อนได้เท่าไหร่?",
    "กองทุนรวม ThaiESG ต้องถือครองกี่ปีจึงจะไม่ผิดกฎ?",
    "สามารถสลับกองทุน ThaiESG ระหว่างทางได้หรือไม่?",
    "กองทุนตราสารหนี้สีเขียว (Green Bonds) ลดหย่อนภาษีได้เท่ากันไหม?"
  ] : [
    "What are the tax deduction rules for ThaiESG?",
    "How is the maximum deduction limit calculated?",
    "How many years must I hold ThaiESG to avoid tax penalties?",
    "Can I switch between different ThaiESG funds mid-way?",
    "Do green bond funds qualify for the same tax deductions?"
  ];

  // Initialize messages
  useEffect(() => {
    setMessages([
      {
        id: 'welcome-full',
        sender: 'ai',
        text: t.chatWelcome,
        timestamp: new Date(),
      },
    ]);
  }, [t.chatWelcome]);

  // Auto scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSendMessage = async (text: string) => {
    if (!text.trim() || isLoading) return;

    // Append user message
    const userMsg: Message = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: text,
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const response = await fetch('http://127.0.0.1:8080/api/v1/tax/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: text }),
      });

      if (!response.ok) {
        throw new Error('API returned an error');
      }

      const data = await response.json();
      
      const aiMsg: Message = {
        id: `ai-${Date.now()}`,
        sender: 'ai',
        text: data.answer || 'Sorry, I couldn\'t generate an answer.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error(err);
      const errorMsg: Message = {
        id: `ai-err-${Date.now()}`,
        sender: 'ai',
        text: language === 'TH'
          ? 'ขออภัยครับ เกิดข้อผิดพลาดในการเชื่อมต่อกับบริการ AI ของระบบ กรุณาตรวจสอบให้แน่ใจว่าได้เปิด Backend แล้ว'
          : 'Sorry, unable to connect to the tax query engine. Please verify the backend is running.',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const onSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim()) return;
    handleSendMessage(inputValue);
    setInputValue('');
  };

  return (
    <div className="h-[calc(100vh-10rem)] min-h-[500px] flex flex-col md:flex-row gap-6 animate-slide-up">
      
      {/* Left Sidebar: Suggestions */}
      <div className="w-full md:w-80 shrink-0 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-2xl p-5 flex flex-col shadow-sm">
        <div className="flex items-center gap-2 mb-4">
          <HelpCircle className="w-5 h-5 text-teal-500" />
          <h2 className="text-sm font-bold text-slate-800 dark:text-white uppercase tracking-wider">
            {language === 'TH' ? 'หัวข้อที่แนะนำ' : 'Suggested Topics'}
          </h2>
        </div>
        <p className="text-xs text-slate-400 dark:text-slate-500 leading-relaxed mb-4">
          {language === 'TH' 
            ? 'คลิกข้อคำถามด้านล่างเพื่อส่งหา AI โดยตรง ช่วยประหยัดเวลาและครอบคลุมประเด็นสำคัญ' 
            : 'Click on any query card below to ask our Tax AI assistant instantly.'}
        </p>

        <div className="flex-1 space-y-2.5 overflow-y-auto max-h-[300px] md:max-h-none pr-1">
          {suggestedQuestions.map((q, idx) => (
            <button
              key={idx}
              onClick={() => handleSendMessage(q)}
              disabled={isLoading}
              className="w-full text-left p-3 rounded-xl bg-slate-50 hover:bg-teal-50/40 dark:bg-slate-950 dark:hover:bg-slate-800 border border-slate-200 dark:border-slate-800/60 hover:border-teal-400 dark:hover:border-teal-600 transition-all text-xs text-slate-700 dark:text-slate-300 font-medium focus:outline-none disabled:opacity-50"
            >
              {q}
            </button>
          ))}
        </div>
      </div>

      {/* Right Column: Chat Dialog Box */}
      <div className="flex-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-2xl flex flex-col overflow-hidden shadow-sm">
        
        {/* Chat Title bar */}
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-800/80 bg-slate-50/50 dark:bg-slate-950/20 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-teal-500/10 text-teal-600 dark:text-teal-400 flex items-center justify-center">
              <Bot className="w-5 h-5" />
            </div>
            <div>
              <h2 className="text-sm font-bold text-slate-800 dark:text-white">{t.chatTitle}</h2>
              <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">{t.chatSubtitle}</p>
            </div>
          </div>
          <span className="flex items-center gap-1.5 text-xs text-emerald-500 font-semibold bg-emerald-500/10 px-2.5 py-0.5 rounded-full">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping"></span>
            TaxAI Active
          </span>
        </div>

        {/* Message Logs */}
        <div className="flex-1 p-5 overflow-y-auto space-y-4 bg-slate-50/30 dark:bg-slate-950/10">
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex gap-3 max-w-[85%] ${msg.sender === 'user' ? 'ml-auto flex-row-reverse' : ''}`}
            >
              <div
                className={`w-8 h-8 rounded-xl shrink-0 flex items-center justify-center text-xs ${
                  msg.sender === 'user' 
                    ? 'bg-teal-500 text-white shadow-md shadow-teal-500/10' 
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200/40 dark:border-slate-700/40'
                }`}
              >
                {msg.sender === 'user' ? <User className="w-4.5 h-4.5" /> : <Bot className="w-4.5 h-4.5 text-teal-500" />}
              </div>
              <div
                className={`p-3.5 rounded-2xl text-xs leading-relaxed ${
                  msg.sender === 'user'
                    ? 'bg-teal-500 text-white rounded-tr-none'
                    : 'bg-slate-100 dark:bg-slate-800 text-slate-800 dark:text-slate-200 rounded-tl-none border border-slate-200/50 dark:border-slate-700/50 shadow-sm'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.text}</p>
                <span
                  className={`block text-[9px] mt-1 text-right ${
                    msg.sender === 'user' ? 'text-teal-200' : 'text-slate-400 dark:text-slate-500'
                  }`}
                >
                  {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                </span>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="flex gap-3 max-w-[80%]">
              <div className="w-8 h-8 rounded-xl bg-slate-100 dark:bg-slate-800 flex items-center justify-center shrink-0 border border-slate-200/40 dark:border-slate-700/40">
                <Bot className="w-4.5 h-4.5 text-teal-500 animate-pulse" />
              </div>
              <div className="p-3.5 rounded-2xl bg-slate-100 dark:bg-slate-800 rounded-tl-none flex items-center gap-1.5 border border-slate-200/50 dark:border-slate-700/50">
                <Loader2 className="w-3.5 h-3.5 text-teal-500 animate-spin" />
                <span className="text-xs text-slate-400 dark:text-slate-500">AI is composing answer...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <form
          onSubmit={onSubmit}
          className="p-4 border-t border-slate-100 dark:border-slate-800/80 bg-white dark:bg-slate-900 flex gap-3"
        >
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={t.chatPlaceholder}
            className="flex-1 px-4 py-3 rounded-xl border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 text-xs focus:outline-none focus:border-teal-500 focus:ring-1 focus:ring-teal-500 transition-all font-medium"
          />
          <button
            type="submit"
            disabled={!inputValue.trim() || isLoading}
            className="px-5 py-3 rounded-xl bg-teal-500 hover:bg-teal-600 disabled:opacity-40 text-white shadow-md hover:shadow-lg hover:scale-105 transition-all duration-300 font-bold text-xs flex items-center gap-1.5 cursor-pointer"
          >
            <span>{t.chatSendBtn}</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>

      </div>

    </div>
  );
}
