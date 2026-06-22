'use client';

import React, { useState } from 'react';
import { ChevronDown, ChevronUp, CheckCircle2, Lock, Activity, ShieldCheck, ExternalLink } from 'lucide-react';

export interface ProgressStep {
  label: string;
  isCompleted: boolean;
  sourceName?: string;
  sourceLink?: string;
}

interface ProgressCardProps {
  phase: number;
  title: string;
  description: string;
  status: 'complete' | 'processing' | 'locked';
  steps?: ProgressStep[];
  defaultExpanded?: boolean;
}

export default function ProgressCard({
  phase,
  title,
  description,
  status,
  steps = [],
  defaultExpanded = false,
}: ProgressCardProps) {
  const [expanded, setExpanded] = useState(defaultExpanded);

  const getStatusStyles = () => {
    switch (status) {
      case 'complete':
        return {
          border: 'border-emerald-500/30 dark:border-emerald-500/20 bg-emerald-50/30 dark:bg-emerald-950/10',
          badge: 'bg-emerald-500/10 text-emerald-600 dark:text-emerald-400',
          iconColor: 'text-emerald-500',
          textMuted: 'text-slate-500 dark:text-slate-400',
        };
      case 'processing':
        return {
          border: 'border-blue-500/40 dark:border-blue-500/20 bg-blue-50/20 dark:bg-blue-950/10 animate-pulse-slow',
          badge: 'bg-blue-500/10 text-blue-600 dark:text-blue-400',
          iconColor: 'text-blue-500',
          textMuted: 'text-slate-500 dark:text-slate-400',
        };
      case 'locked':
      default:
        return {
          border: 'border-slate-200 dark:border-slate-800 bg-slate-50/30 dark:bg-slate-900/20 opacity-60',
          badge: 'bg-slate-200/50 dark:bg-slate-800 text-slate-500 dark:text-slate-400',
          iconColor: 'text-slate-400 dark:text-slate-600',
          textMuted: 'text-slate-400 dark:text-slate-500',
        };
    }
  };

  const styles = getStatusStyles();

  return (
    <div
      className={`rounded-xl border transition-all duration-300 shadow-sm ${styles.border} overflow-hidden`}
    >
      {/* Header */}
      <button
        onClick={() => status !== 'locked' && setExpanded(!expanded)}
        disabled={status === 'locked'}
        className={`w-full text-left p-4 flex items-start justify-between gap-3 focus:outline-none ${
          status === 'locked' ? 'cursor-not-allowed' : 'cursor-pointer hover:bg-slate-100/50 dark:hover:bg-slate-800/10'
        }`}
      >
        <div className="flex gap-3">
          {/* Status Indicator Icon */}
          <div className="mt-0.5">
            {status === 'complete' && (
              <CheckCircle2 className={`w-5 h-5 ${styles.iconColor}`} />
            )}
            {status === 'processing' && (
              <div className="relative flex h-5 w-5 items-center justify-center">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-blue-400 opacity-75"></span>
                <Activity className={`relative w-4 h-4 ${styles.iconColor}`} />
              </div>
            )}
            {status === 'locked' && (
              <Lock className={`w-4 h-4 mt-0.5 ${styles.iconColor}`} />
            )}
          </div>

          <div>
            <div className="flex items-center gap-2">
              <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${styles.badge}`}>
                PHASE {phase}
              </span>
            </div>
            <h4 className="text-sm font-semibold text-slate-800 dark:text-slate-200 mt-1">
              {title}
            </h4>
            <p className={`text-xs mt-0.5 leading-relaxed ${styles.textMuted}`}>
              {description}
            </p>
          </div>
        </div>

        {status !== 'locked' && (
          <div className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 p-1">
            {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </div>
        )}
      </button>

      {/* Expanded Content (Sub-steps/Logs) */}
      {expanded && status !== 'locked' && (
        <div className="px-4 pb-4 pt-1 border-t border-slate-100 dark:border-slate-800/60 bg-slate-50/50 dark:bg-slate-900/10">
          <div className="space-y-2 mt-2 pl-8 border-l border-slate-200 dark:border-slate-700">
            {steps.length > 0 ? (
              steps.map((step, idx) => (
                <div key={idx} className="flex items-center gap-2 text-xs">
                  {step.isCompleted ? (
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 fill-emerald-100 dark:fill-transparent shrink-0" />
                  ) : (
                    <div className="w-3.5 h-3.5 rounded-full border-2 border-slate-300 dark:border-slate-600 shrink-0" />
                  )}
                  <span className={step.isCompleted ? 'text-slate-700 dark:text-slate-300 font-medium' : 'text-slate-500 dark:text-slate-500'}>
                    {step.label}
                  </span>
                  {step.sourceName && (
                    step.sourceLink ? (
                      <a
                        href={step.sourceLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-1 px-1.5 py-0.5 text-[9px] font-bold text-blue-700 bg-blue-50 dark:text-blue-300 dark:bg-blue-950/40 rounded hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors shrink-0"
                      >
                        {step.sourceName}
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    ) : (
                      <span className="text-[10px] bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 px-1.5 py-0.5 rounded font-mono">
                        {step.sourceName}
                      </span>
                    )
                  )}
                </div>
              ))
            ) : (
              <div className="text-xs text-slate-400 dark:text-slate-500 italic">
                Ready for orchestrator feedback.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
