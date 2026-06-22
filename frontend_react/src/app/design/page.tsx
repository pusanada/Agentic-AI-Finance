'use client';

import React, { useState } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/store/translations';
import ProgressCard from '@/components/ProgressCard';
import ThemeToggle from '@/components/ThemeToggle';
import LangToggle from '@/components/LangToggle';
import { 
  Bot, User, Send, X, MessageSquare, Sparkles, 
  ChevronRight, CheckCircle2, Lock, Activity, ShieldCheck, Sun, Moon 
} from 'lucide-react';

export default function DesignSystemPage() {
  const { language } = useAppStore();
  const t = translations[language];

  // Dummy states for design previews
  const [card1Expanded, setCard1Expanded] = useState(true);
  const [card2Expanded, setCard2Expanded] = useState(false);

  return (
    <div className="space-y-6 animate-slide-up pb-12">
      
      {/* Title */}
      <div className="text-center md:text-left">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-800 dark:text-white flex items-center justify-center md:justify-start gap-2">
          <ShieldCheck className="w-8 h-8 text-teal-500" />
          <span>{t.navDesign} (Consistency Panel)</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-2xl">
          Side-by-side visual reference for PR presentations showcasing UI typography, HSL palettes, toggle components, progress indicator states, and chat helper panels in both themes.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        
        {/* ================= LIGHT MODE SYSTEM ================= */}
        <div className="bg-slate-50 border border-slate-200 rounded-3xl p-6 sm:p-8 shadow-md text-slate-900 space-y-8">
          <div className="flex items-center justify-between border-b border-slate-200 pb-3">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-500 flex items-center gap-1.5">
              <Sun className="w-4 h-4 text-yellow-500 fill-yellow-500" /> Light Mode Specification
            </span>
            <span className="text-[10px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">#FFFFFF / #F8FAFC</span>
          </div>

          {/* 1. Language Toggle Showcase */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">1. Language Toggle (TH/EN)</h3>
            <div className="flex items-center gap-4">
              <LangToggle />
              <span className="text-xs text-slate-500 italic">Global state linked pill selection</span>
            </div>
          </div>

          {/* 2. Theme Toggle Showcase */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">2. Theme Toggle (Sun/Moon)</h3>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <span className="text-xs text-slate-500 italic">Supports anti-flash rendering script</span>
            </div>
          </div>

          {/* 3. Progress Cards Showcase */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">3. AI Logic Progress Cards</h3>
            <div className="space-y-3 max-w-md">
              <ProgressCard
                phase={1}
                title="Complete State (Checked & Highlighted)"
                description="This card indicates a completed workflow step with green highlight"
                status="complete"
                steps={[{ label: 'Sample check mark step', isCompleted: true }]}
              />
              <ProgressCard
                phase={2}
                title="Processing State (Pulsing Indicator)"
                description="This card represents an active process in execution"
                status="processing"
                steps={[{ label: 'Sample active check', isCompleted: false }]}
              />
              <ProgressCard
                phase={3}
                title="Locked State (Security Boundary)"
                description="This card is disabled until preceding pipelines finish"
                status="locked"
              />
            </div>
          </div>

          {/* 4. Open Chat window Mock */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">4. Chat Assistant Window Preview</h3>
            <div className="w-full max-w-sm rounded-2xl bg-white border border-slate-200 shadow-lg overflow-hidden flex flex-col h-[320px]">
              <div className="px-4 py-2.5 bg-gradient-to-r from-teal-600 to-emerald-600 text-white flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-teal-200" />
                  <span className="text-xs font-bold">Tax AI Q&A Widget</span>
                </div>
                <X className="w-3.5 h-3.5 opacity-80" />
              </div>
              <div className="flex-1 p-3 bg-slate-50 space-y-2.5 overflow-y-auto">
                <div className="flex gap-2 max-w-[85%]">
                  <div className="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center shrink-0">
                    <Bot className="w-3 h-3 text-teal-500" />
                  </div>
                  <div className="p-2.5 bg-slate-100 rounded-2xl rounded-tl-none text-[11px] leading-relaxed text-slate-800">
                    How can I assist you with ThaiESG deductions today?
                  </div>
                </div>
                <div className="flex gap-2 max-w-[85%] ml-auto flex-row-reverse">
                  <div className="w-6 h-6 rounded-full bg-teal-500 text-white flex items-center justify-center shrink-0">
                    <User className="w-3 h-3" />
                  </div>
                  <div className="p-2.5 bg-teal-500 text-white rounded-2xl rounded-tr-none text-[11px] leading-relaxed">
                    What is the maximum holding period?
                  </div>
                </div>
              </div>
              <div className="p-2 border-t border-slate-200 bg-white flex gap-2">
                <div className="flex-1 px-3 py-1 bg-slate-100 text-[10px] rounded-full text-slate-400">
                  Type your tax questions here...
                </div>
                <div className="w-6 h-6 rounded-full bg-teal-500 text-white flex items-center justify-center">
                  <Send className="w-3 h-3" />
                </div>
              </div>
            </div>
          </div>

          {/* 5. Typography Scale */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-wider">5. Typography & Data Scale</h3>
            <div className="space-y-2 border border-slate-200 p-4 rounded-2xl bg-white">
              <div>
                <span className="text-[10px] text-slate-400 block">Dashboard Title</span>
                <span className="text-2xl font-extrabold text-slate-900">Tax OCR & Investment Quota</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 block">Financial Stats Data Point</span>
                <span className="text-xl font-bold font-mono text-teal-600">฿300,000.00 THB</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-400 block">Label Caption</span>
                <span className="text-xs text-slate-500">Calculated according to 30% of income rule.</span>
              </div>
            </div>
          </div>

        </div>

        {/* ================= DARK MODE SYSTEM ================= */}
        <div className="bg-slate-950 border border-slate-800 rounded-3xl p-6 sm:p-8 shadow-xl text-slate-100 space-y-8">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <span className="text-xs font-bold uppercase tracking-widest text-slate-400 flex items-center gap-1.5">
              <Moon className="w-4 h-4 text-emerald-400 fill-emerald-400" /> Dark Mode Specification
            </span>
            <span className="text-[10px] bg-slate-900 text-slate-400 px-2 py-0.5 rounded font-mono">#0B0F19 / #0F1628</span>
          </div>

          {/* 1. Language Toggle Showcase */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">1. Language Toggle (TH/EN)</h3>
            <div className="flex items-center gap-4">
              <LangToggle />
              <span className="text-xs text-slate-400 italic">Dark Theme contrast aligned</span>
            </div>
          </div>

          {/* 2. Theme Toggle Showcase */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">2. Theme Toggle (Sun/Moon)</h3>
            <div className="flex items-center gap-4">
              <ThemeToggle />
              <span className="text-xs text-slate-400 italic">Moon icon activated when class is "dark"</span>
            </div>
          </div>

          {/* 3. Progress Cards Showcase */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">3. AI Logic Progress Cards</h3>
            <div className="space-y-3 max-w-md">
              <ProgressCard
                phase={1}
                title="Complete State (Checked & Highlighted)"
                description="This card indicates a completed workflow step with green highlight"
                status="complete"
                steps={[{ label: 'Sample check mark step', isCompleted: true }]}
              />
              <ProgressCard
                phase={2}
                title="Processing State (Pulsing Indicator)"
                description="This card represents an active process in execution"
                status="processing"
                steps={[{ label: 'Sample active check', isCompleted: false }]}
              />
              <ProgressCard
                phase={3}
                title="Locked State (Security Boundary)"
                description="This card is disabled until preceding pipelines finish"
                status="locked"
              />
            </div>
          </div>

          {/* 4. Open Chat window Mock */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">4. Chat Assistant Window Preview</h3>
            <div className="w-full max-w-sm rounded-2xl bg-slate-900 border border-slate-800 shadow-2xl overflow-hidden flex flex-col h-[320px]">
              <div className="px-4 py-2.5 bg-slate-800 text-white flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bot className="w-4 h-4 text-emerald-400" />
                  <span className="text-xs font-bold">Tax AI Q&A Widget</span>
                </div>
                <X className="w-3.5 h-3.5 opacity-80 text-slate-400" />
              </div>
              <div className="flex-1 p-3 bg-slate-950 space-y-2.5 overflow-y-auto">
                <div className="flex gap-2 max-w-[85%]">
                  <div className="w-6 h-6 rounded-full bg-slate-800 flex items-center justify-center shrink-0">
                    <Bot className="w-3 h-3 text-emerald-400" />
                  </div>
                  <div className="p-2.5 bg-slate-800 rounded-2xl rounded-tl-none text-[11px] leading-relaxed text-slate-200">
                    How can I assist you with ThaiESG deductions today?
                  </div>
                </div>
                <div className="flex gap-2 max-w-[85%] ml-auto flex-row-reverse">
                  <div className="w-6 h-6 rounded-full bg-teal-500 text-white flex items-center justify-center shrink-0">
                    <User className="w-3 h-3" />
                  </div>
                  <div className="p-2.5 bg-teal-500 text-white rounded-2xl rounded-tr-none text-[11px] leading-relaxed">
                    What is the maximum holding period?
                  </div>
                </div>
              </div>
              <div className="p-2 border-t border-slate-800 bg-slate-900 flex gap-2">
                <div className="flex-1 px-3 py-1 bg-slate-800 text-[10px] rounded-full text-slate-500">
                  Type your tax questions here...
                </div>
                <div className="w-6 h-6 rounded-full bg-teal-500 text-white flex items-center justify-center">
                  <Send className="w-3 h-3" />
                </div>
              </div>
            </div>
          </div>

          {/* 5. Typography Scale */}
          <div className="space-y-3">
            <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider">5. Typography & Data Scale</h3>
            <div className="space-y-2 border border-slate-800 p-4 rounded-2xl bg-slate-900">
              <div>
                <span className="text-[10px] text-slate-500 block">Dashboard Title</span>
                <span className="text-2xl font-extrabold text-white">Portfolio Allocator & Compliance</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">Financial Stats Data Point</span>
                <span className="text-xl font-bold font-mono text-emerald-400">฿300,000.00 THB</span>
              </div>
              <div>
                <span className="text-[10px] text-slate-500 block">Label Caption</span>
                <span className="text-xs text-slate-400">Calculated according to 30% of income rule.</span>
              </div>
            </div>
          </div>

        </div>

      </div>

      {/* Palette swatches */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-3xl p-6 shadow-sm">
        <h3 className="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider mb-4">
          6. Color Palette Swatches (PR Presentational Scale)
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-4">
          
          <div className="space-y-2">
            <div className="h-12 rounded-xl bg-teal-500 shadow-inner"></div>
            <div className="text-[10px] font-bold text-slate-800 dark:text-slate-300">Professional Teal</div>
            <div className="text-[9px] font-mono text-slate-400">#14b8a6 (Primary Light)</div>
          </div>
          
          <div className="space-y-2">
            <div className="h-12 rounded-xl bg-emerald-500 shadow-inner"></div>
            <div className="text-[10px] font-bold text-slate-800 dark:text-slate-300">Emerald Accent</div>
            <div className="text-[9px] font-mono text-slate-400">#10b981 (Primary Dark)</div>
          </div>

          <div className="space-y-2">
            <div className="h-12 rounded-xl bg-blue-500 shadow-inner"></div>
            <div className="text-[10px] font-bold text-slate-800 dark:text-slate-300">Sapphire Accent</div>
            <div className="text-[9px] font-mono text-slate-400">#3b82f6 (Trust/Safety)</div>
          </div>

          <div className="space-y-2">
            <div className="h-12 rounded-xl bg-slate-900 border border-slate-700 shadow-inner"></div>
            <div className="text-[10px] font-bold text-slate-800 dark:text-slate-300">Dark Slate</div>
            <div className="text-[9px] font-mono text-slate-400">#0f172a (Slate Dark)</div>
          </div>

          <div className="space-y-2">
            <div className="h-12 rounded-xl bg-slate-50 border border-slate-200 shadow-inner"></div>
            <div className="text-[10px] font-bold text-slate-800 dark:text-slate-300">Airy Light Gray</div>
            <div className="text-[9px] font-mono text-slate-400">#f8fafc (Slate Light)</div>
          </div>

          <div className="space-y-2">
            <div className="h-12 rounded-xl bg-slate-950 shadow-inner"></div>
            <div className="text-[10px] font-bold text-slate-800 dark:text-slate-300">Cinematic Black</div>
            <div className="text-[9px] font-mono text-slate-400">#0b0f19 (Background Dark)</div>
          </div>

        </div>
      </div>

    </div>
  );
}
