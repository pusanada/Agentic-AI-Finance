'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/store/translations';
import ThemeToggle from './ThemeToggle';
import LangToggle from './LangToggle';
import { ShieldCheck, BarChart3, MessageSquare, Paintbrush, Layers } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const { language } = useAppStore();
  const t = translations[language];

  React.useEffect(() => {
    try {
      const theme = localStorage.getItem('app-theme') || 'dark';
      useAppStore.getState().setTheme(theme as 'light' | 'dark');
    } catch (e) {}
  }, []);

  const links = [
    { href: '/', label: t.navHome, icon: BarChart3 },
    { href: '/portfolio', label: t.navPortfolio, icon: Layers },
    { href: '/chat', label: t.navChat, icon: MessageSquare },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-slate-200/80 dark:border-slate-800/80 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md transition-all duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-teal-500 to-emerald-500 flex items-center justify-center shadow-md shadow-teal-500/10 group-hover:scale-105 transition-transform">
            <ShieldCheck className="w-6 h-6 text-white" />
          </div>
          <div>
            <span className="font-bold text-base tracking-tight text-slate-800 dark:text-white block">
              ThaiESG
            </span>
            <span className="text-[10px] text-teal-600 dark:text-teal-400 font-medium tracking-wider uppercase block -mt-1">
              Compliance Guard
            </span>
          </div>
        </Link>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center gap-1">
          {links.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all duration-300 ${
                  isActive
                    ? 'bg-teal-50/80 dark:bg-teal-950/20 text-teal-600 dark:text-teal-400'
                    : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800/50'
                }`}
              >
                <Icon className="w-4 h-4 shrink-0" />
                {link.label}
              </Link>
            );
          })}
          
          {/* Design System Link */}
          <Link
            href="/design"
            className={`flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold tracking-wide transition-all duration-300 ${
              pathname === '/design'
                ? 'bg-teal-50/80 dark:bg-teal-950/20 text-teal-600 dark:text-teal-400'
                : 'text-slate-600 hover:text-slate-900 dark:text-slate-400 dark:hover:text-white hover:bg-slate-50 dark:hover:bg-slate-800/50'
            }`}
          >
            <Paintbrush className="w-4 h-4 shrink-0" />
            {t.navDesign}
          </Link>
        </nav>

        {/* Right Settings controls */}
        <div className="flex items-center gap-3">
          <LangToggle />
          <ThemeToggle />
        </div>
      </div>
    </header>
  );
}
