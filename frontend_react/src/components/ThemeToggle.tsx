'use client';

import React from 'react';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/store/translations';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, toggleTheme, language } = useAppStore();
  const t = translations[language];

  return (
    <button
      onClick={toggleTheme}
      className="relative flex items-center justify-between p-2 rounded-full bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 transition-all duration-300 shadow-sm border border-slate-200 dark:border-slate-700 group focus:outline-none"
      aria-label={theme === 'light' ? t.themeDark : t.themeLight}
      title={theme === 'light' ? t.themeDark : t.themeLight}
    >
      <div className="relative w-12 h-6 flex items-center rounded-full bg-slate-300 dark:bg-slate-600 transition-colors duration-300 p-0.5">
        {/* Knob */}
        <div
          className={`absolute w-5 h-5 rounded-full bg-white dark:bg-slate-900 shadow-md transform transition-transform duration-300 flex items-center justify-center ${
            theme === 'dark' ? 'translate-x-6' : 'translate-x-0'
          }`}
        >
          {theme === 'dark' ? (
            <Moon className="w-3.5 h-3.5 text-emerald-400 fill-emerald-400" />
          ) : (
            <Sun className="w-3.5 h-3.5 text-yellow-500 fill-yellow-500" />
          )}
        </div>
      </div>
    </button>
  );
}
