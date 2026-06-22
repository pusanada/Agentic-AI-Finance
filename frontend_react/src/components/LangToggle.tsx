'use client';

import React from 'react';
import { useAppStore } from '@/store/useAppStore';

export default function LangToggle() {
  const { language, setLanguage } = useAppStore();

  return (
    <div className="flex items-center p-1 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 shadow-sm">
      <button
        onClick={() => setLanguage('TH')}
        className={`px-3 py-1 rounded-full text-xs font-semibold tracking-wider transition-all duration-300 ${
          language === 'TH'
            ? 'bg-teal-500 text-white shadow-sm'
            : 'text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
        }`}
      >
        TH
      </button>
      <button
        onClick={() => setLanguage('EN')}
        className={`px-3 py-1 rounded-full text-xs font-semibold tracking-wider transition-all duration-300 ${
          language === 'EN'
            ? 'bg-teal-500 text-white shadow-sm'
            : 'text-slate-500 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white'
        }`}
      >
        EN
      </button>
    </div>
  );
}
