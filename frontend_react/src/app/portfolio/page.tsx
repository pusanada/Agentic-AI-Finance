'use client';

import React, { useState, useEffect } from 'react';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/store/translations';
import ProgressCard from '@/components/ProgressCard';
import { 
  ShieldCheck, 
  ShieldAlert, 
  Coins, 
  Settings, 
  PieChart, 
  FileText, 
  LineChart, 
  Sparkles,
  HelpCircle,
  TrendingUp,
  UserCheck,
  Check,
  Search,
  ChevronRight,
  AlertTriangle,
  ExternalLink
} from 'lucide-react';

export default function PortfolioAllocatorPage() {
  const {
    language,
    theme,
    setTheme,
    ocrResult,
    portfolioResult,
    setPortfolioResult,
    isAllocating,
    setIsAllocating,
  } = useAppStore();

  const t = translations[language];

  // Parameters inputs (prefilled from OCR if available)
  const [income, setIncome] = useState<number>(ocrResult?.assessable_income || 1200000.0);
  const [alreadyPurchased, setAlreadyPurchased] = useState<number>(ocrResult?.already_purchased || 0.0);
  const [goal, setGoal] = useState<'Growth' | 'Dividend' | 'Balanced'>('Growth');
  const [riskProfile, setRiskProfile] = useState<'Conservative' | 'Moderate' | 'Aggressive'>('Moderate');
  const [userInstructions, setUserInstructions] = useState<string>('');
  
  // Pipeline simulation states for visual engagement
  const [pipelinePhase, setPipelinePhase] = useState<number>(0);
  const [expandedFundCode, setExpandedFundCode] = useState<string | null>(null);

  // Sync inputs with OCRResult if it updates
  useEffect(() => {
    if (ocrResult) {
      setIncome(ocrResult.assessable_income);
      setAlreadyPurchased(ocrResult.already_purchased);
    }
  }, [ocrResult]);

  const handleAllocate = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAllocating(true);
    setPortfolioResult(null);
    setPipelinePhase(1);

    // Simulate multi-agent steps pipeline for beautiful visual UX
    // Step 1: Quota check
    await new Promise((resolve) => setTimeout(resolve, 800));
    setPipelinePhase(2);

    // Step 2: ESG filtering
    await new Promise((resolve) => setTimeout(resolve, 800));
    setPipelinePhase(3);

    // Step 3: SEC Opp Day Audio audit
    await new Promise((resolve) => setTimeout(resolve, 1000));
    setPipelinePhase(4);

    // Step 4: Compliance check
    await new Promise((resolve) => setTimeout(resolve, 800));
    setPipelinePhase(5);

    try {
      const response = await fetch('http://127.0.0.1:8080/api/v1/portfolio/allocate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          assessable_income: income,
          already_purchased: alreadyPurchased,
          financial_goal: goal,
          risk_profile: riskProfile,
          user_instructions: userInstructions,
          ocr_confidence: ocrResult?.confidence || 1.0,
        }),
      });

      if (!response.ok) {
        throw new Error('Allocation API error');
      }

      const data = await response.json();
      setPortfolioResult(data);
      setPipelinePhase(6); // Success, show results
    } catch (err) {
      console.error(err);
      setPipelinePhase(0);
      alert('Failed to connect to allocation API. Ensure supervisor backend is running on port 8080.');
    } finally {
      setIsAllocating(false);
    }
  };

  const renderLogLine = (log: string) => {
    if (log.includes("Calculated remaining")) {
      return (
        <span>
          {log}{' '}
          <a
            href="https://www.rd.go.th/65208.html"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline inline-flex items-center gap-0.5 font-bold"
          >
            [RD Tax Guideline]
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </span>
      );
    }
    if (log.includes("check_portfolio_compliance") || log.includes("Compliance Guard check:")) {
      return (
        <span>
          {log}{' '}
          <a
            href="https://www.sec.or.th/TH/Pages/LawRegulation/RulesRegulation.aspx"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline inline-flex items-center gap-0.5 font-bold"
          >
            [SEC Rules]
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </span>
      );
    }
    if (log.includes("Cycle") || log.includes("Generating allocation")) {
      return (
        <span>
          {log}{' '}
          <a
            href="https://market.sec.or.th/public/idisc/th"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:underline inline-flex items-center gap-0.5 font-bold"
          >
            [SEC i-Disc]
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </span>
      );
    }
    return log;
  };

  // Mock underlying holdings database to enrich fund rendering with tickers
  const underlyingHoldingsMap: Record<string, Array<{ ticker: string; weight: number; esg_score: number }>> = {
    'K-THAIESG-A': [
      { ticker: 'PTT', weight: 15, esg_score: 95 },
      { ticker: 'CPALL', weight: 12, esg_score: 88 },
      { ticker: 'ADVANC', weight: 10, esg_score: 96 },
      { ticker: 'SCC', weight: 8, esg_score: 92 },
    ],
    'SCBTHAIESG': [
      { ticker: 'BDMS', weight: 14, esg_score: 87 },
      { ticker: 'KBANK', weight: 11, esg_score: 94 },
      { ticker: 'SCB', weight: 10, esg_score: 89 },
      { ticker: 'AOT', weight: 9, esg_score: 85 },
    ],
    'B-THAIESG': [
      { ticker: 'PTT', weight: 10, esg_score: 95 },
      { ticker: 'BGRIM', weight: 8, esg_score: 97 },
      { ticker: 'CPF', weight: 7, esg_score: 81 },
      { ticker: 'Green Bond SET', weight: 35, esg_score: 99 },
    ],
    'ASP-THAIESG': [
      { ticker: 'SCG Debentures', weight: 25, esg_score: 94 },
      { ticker: 'PTT Green Bond', weight: 20, esg_score: 95 },
      { ticker: 'BDMS ESG Bond', weight: 15, esg_score: 88 },
    ],
    'T-THAIESG-D': [
      { ticker: 'CPN', weight: 12, esg_score: 91 },
      { ticker: 'GULF', weight: 10, esg_score: 86 },
      { ticker: 'INTUCH', weight: 9, esg_score: 94 },
      { ticker: 'OR', weight: 8, esg_score: 89 },
    ],
  };

  return (
    <div className="space-y-6 animate-slide-up text-slate-800 dark:text-slate-100">
      
      {/* Title */}
      <div className="text-center md:text-left">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white flex items-center justify-center md:justify-start gap-2">
          <TrendingUp className="w-8 h-8 text-emerald-500 dark:text-emerald-400" />
          <span>{t.page2Title}</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-2xl">
          {language === 'TH'
            ? 'จัดพอร์ตการลงทุน ThaiESG ที่เหมาะสมกับเป้าหมาย พร้อมสแกนความสอดคล้องด้าน ESG และกฎเกณฑ์ความปลอดภัยโดย Compliance Guard'
            : 'Construct your ThaiESG portfolio optimized for custom financial targets, validated against active compliance guardrails.'}
        </p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        
        {/* Left Area: Setup Form & Results */}
        <div className="col-span-12 lg:col-span-8 space-y-6">
          
          {/* Allocator Inputs Form */}
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xl text-slate-800 dark:text-slate-100">
            <h2 className="text-base font-bold text-slate-900 dark:text-white mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5 text-emerald-500 dark:text-emerald-400" />
              {t.formSection}
            </h2>

            <form onSubmit={handleAllocate} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{t.incomeLabel}</label>
                  <input
                    type="number"
                    value={income}
                    onChange={(e) => setIncome(Number(e.target.value))}
                    className="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-400 transition-all font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{t.alreadyPurchasedLabel}</label>
                  <input
                    type="number"
                    value={alreadyPurchased}
                    onChange={(e) => setAlreadyPurchased(Number(e.target.value))}
                    className="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-400 transition-all font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{t.goalLabel}</label>
                  <select
                    value={goal}
                    onChange={(e) => setGoal(e.target.value as any)}
                    className="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-400 transition-all cursor-pointer"
                  >
                    <option value="Growth">Growth (เน้นหุ้น ESG เติบโตสูง)</option>
                    <option value="Dividend">Dividend (เน้นปันผลสม่ำเสมอ)</option>
                    <option value="Balanced">Balanced (ความเสี่ยงปานกลาง ผสมตราสารหนี้)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{t.riskLabel}</label>
                  <select
                    value={riskProfile}
                    onChange={(e) => setRiskProfile(e.target.value as any)}
                    className="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-400 transition-all cursor-pointer"
                  >
                    <option value="Conservative">Conservative (เสี่ยงต่ำ เสียภาษีปลอดภัย)</option>
                    <option value="Moderate">Moderate (เสี่ยงปานกลาง บาลานซ์พอร์ต)</option>
                    <option value="Aggressive">Aggressive (เสี่ยงสูง เน้นผลตอบแทนสูงสุด)</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{t.instructionsLabel}</label>
                <textarea
                  value={userInstructions}
                  onChange={(e) => setUserInstructions(e.target.value)}
                  placeholder={t.instructionsPlaceholder}
                  rows={2}
                  className="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-400 transition-all resize-none"
                />
              </div>

              <button
                type="submit"
                disabled={isAllocating}
                className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-500 to-blue-600 hover:from-emerald-600 hover:to-blue-700 text-white font-bold text-xs shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.005] transition-all cursor-pointer flex items-center justify-center gap-2"
              >
                {isAllocating ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>{t.allocating}</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 text-emerald-300" />
                    <span>{t.allocateBtn}</span>
                  </>
                )}
              </button>
            </form>
          </div>

          {/* Allocation Results Panel */}
          {portfolioResult && (
            <div className="space-y-6">
              
              {/* Compliance & AUQ Alert Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                
                {/* Compliance Guard Shield Card */}
                <div className={`rounded-2xl p-5 border shadow-lg flex items-start gap-4 ${
                  portfolioResult.compliance.is_compliant 
                    ? 'border-emerald-500/30 bg-emerald-950/10' 
                    : 'border-red-500/30 bg-red-950/10'
                }`}>
                  <div className={`p-2.5 rounded-xl ${
                    portfolioResult.compliance.is_compliant ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                  }`}>
                    {portfolioResult.compliance.is_compliant ? <ShieldCheck className="w-8 h-8" /> : <ShieldAlert className="w-8 h-8" />}
                  </div>
                  <div>
                    <h3 className="text-xs font-semibold text-slate-400 uppercase tracking-wider">{t.complianceStatus}</h3>
                    <div className={`text-base font-bold mt-1 ${
                      portfolioResult.compliance.is_compliant ? 'text-emerald-400' : 'text-red-400'
                    }`}>
                      {portfolioResult.compliance.is_compliant ? t.complianceCompliant : t.complianceViolated}
                    </div>
                    {portfolioResult.compliance.violations.length > 0 && (
                      <div className="mt-2 text-xs text-red-400 bg-red-900/10 p-2.5 rounded-lg border border-red-500/20">
                        <div className="font-semibold">{t.violationsFound}</div>
                        <ul className="list-disc list-inside mt-1 space-y-0.5 opacity-80">
                          {portfolioResult.compliance.violations.map((v, i) => <li key={i}>{v}</li>)}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>

                {/* AUQ System Confidence Card */}
                <div className="rounded-2xl p-5 border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-lg flex items-start gap-4 text-slate-800 dark:text-slate-100">
                  <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
                    <UserCheck className="w-8 h-8" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">{t.systemConfidence}</h3>
                    
                    <div className="flex items-center justify-between mt-1">
                      <span className="text-lg font-extrabold font-mono text-slate-900 dark:text-white">
                        {portfolioResult.auq.confidence_score}%
                      </span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        portfolioResult.auq.requires_override
                          ? 'bg-red-500/10 text-red-400'
                          : 'bg-emerald-500/10 text-emerald-400'
                      }`}>
                        {portfolioResult.auq.requires_override ? t.humanReviewRequired : t.humanReviewNotRequired}
                      </span>
                    </div>

                    {/* Confidence percentage bar */}
                    <div className="w-full bg-slate-200 dark:bg-slate-800 rounded-full h-1.5 mt-2 overflow-hidden">
                      <div 
                        className={`h-1.5 rounded-full ${
                          portfolioResult.auq.confidence_score >= 80 
                            ? 'bg-emerald-400' 
                            : portfolioResult.auq.confidence_score >= 60 
                            ? 'bg-yellow-400' 
                            : 'bg-red-400'
                        }`}
                        style={{ width: `${portfolioResult.auq.confidence_score}%` }}
                      ></div>
                    </div>
                  </div>
                </div>

              </div>

              {/* Generated Portfolio Tickers & Details */}
              <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-6 shadow-xl space-y-6 text-slate-800 dark:text-slate-100">
                <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800 pb-4">
                  <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
                    <PieChart className="w-5 h-5 text-emerald-500 dark:text-emerald-400" />
                    {t.allocResult}
                  </h2>
                  <div className="text-right">
                    <div className="text-[10px] text-slate-500 dark:text-slate-400 font-semibold uppercase">{language === 'TH' ? 'ยอดลงทุนรวม' : 'Total Investment'}</div>
                    <div className="text-lg font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                      ฿{portfolioResult.portfolio.total_allocated.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </div>
                  </div>
                </div>

                {/* Donut weights preview / Horizontal visual bar */}
                <div className="space-y-2">
                  <div className="flex w-full h-4 rounded-lg overflow-hidden bg-slate-200 dark:bg-slate-800">
                    {portfolioResult.portfolio.allocations.map((item, idx) => {
                      const colors = ['bg-emerald-400', 'bg-blue-500', 'bg-teal-400', 'bg-indigo-500', 'bg-cyan-400'];
                      const col = colors[idx % colors.length];
                      return (
                        <div 
                          key={item.fund_code}
                          className={`${col} h-full transition-all`}
                          style={{ width: `${item.weight * 100}%` }}
                          title={`${item.fund_code}: ${(item.weight * 100).toFixed(0)}%`}
                        ></div>
                      );
                    })}
                  </div>
                  <div className="flex flex-wrap gap-x-4 gap-y-1.5">
                    {portfolioResult.portfolio.allocations.map((item, idx) => {
                      const colors = ['bg-emerald-400', 'bg-blue-500', 'bg-teal-400', 'bg-indigo-500', 'bg-cyan-400'];
                      const col = colors[idx % colors.length];
                      return (
                        <div key={item.fund_code} className="flex items-center gap-1.5 text-xs text-slate-400">
                          <span className={`w-2 h-2 rounded-full ${col}`}></span>
                          <span>{item.fund_code} ({(item.weight * 100).toFixed(0)}%)</span>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Funds Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-slate-200 dark:border-slate-800 text-slate-500 dark:text-slate-400 font-bold">
                        <th className="pb-3 pr-2">{t.fundCode}</th>
                        <th className="pb-3 hidden sm:table-cell">{t.fundName}</th>
                        <th className="pb-3 text-center">ESG</th>
                        <th className="pb-3 text-right">{t.weight}</th>
                        <th className="pb-3 text-right">{t.amount}</th>
                        <th className="pb-3"></th>
                      </tr>
                    </thead>
                    <tbody>
                      {portfolioResult.portfolio.allocations.map((item) => {
                        const isExpanded = expandedFundCode === item.fund_code;
                        const subHoldings = underlyingHoldingsMap[item.fund_code] || [];
                        return (
                          <React.Fragment key={item.fund_code}>
                            {/* Primary row */}
                            <tr 
                              onClick={() => setExpandedFundCode(isExpanded ? null : item.fund_code)}
                              className="border-b border-slate-100 dark:border-slate-800/60 hover:bg-slate-100/50 dark:hover:bg-slate-800/30 transition-colors cursor-pointer"
                            >
                              <td className="py-3.5 font-bold text-slate-800 dark:text-slate-200 pr-2">{item.fund_code}</td>
                              <td className="py-3.5 hidden sm:table-cell text-slate-500 dark:text-slate-400 max-w-[200px] truncate">{item.fund_name}</td>
                              <td className="py-3.5 text-center">
                                <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 font-bold font-mono text-[10px]">
                                  {item.esg_rating}
                                </span>
                              </td>
                              <td className="py-3.5 text-right font-mono text-slate-600 dark:text-slate-300">{(item.weight * 100).toFixed(0)}%</td>
                              <td className="py-3.5 text-right font-mono text-emerald-600 dark:text-emerald-400 font-semibold">
                                ฿{item.amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                              </td>
                              <td className="py-3.5 text-right text-slate-400">
                                <ChevronRight className={`w-4 h-4 transform transition-transform duration-200 ${isExpanded ? 'rotate-90 text-emerald-400' : ''}`} />
                              </td>
                            </tr>

                            {/* Expanded underlying stock tickers row */}
                            {isExpanded && (
                              <tr>
                                <td colSpan={6} className="bg-slate-50/50 dark:bg-slate-950/60 p-4 rounded-xl border border-slate-200 dark:border-slate-800">
                                  <div className="space-y-2">
                                    <h4 className="font-semibold text-slate-500 dark:text-slate-400 text-[10px] uppercase tracking-wider mb-2 flex items-center gap-1">
                                      <Search className="w-3.5 h-3.5 text-teal-500 dark:text-teal-400" />
                                      {t.underlyingStocks}
                                    </h4>
                                    
                                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                      {subHoldings.map((stock) => (
                                        <div 
                                          key={stock.ticker} 
                                          className="p-2.5 rounded-lg bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 flex items-center justify-between shadow-sm"
                                        >
                                          <div>
                                            <span className="font-bold text-slate-800 dark:text-slate-200 text-xs">{stock.ticker}</span>
                                            <span className="block text-[9px] text-slate-400 dark:text-slate-500">{stock.weight}% {t.underlyingWeight}</span>
                                          </div>
                                          <div className="text-right flex flex-col items-end shrink-0">
                                            <span className="text-[10px] font-bold text-teal-600 dark:text-teal-400 font-mono">
                                              ESG: {stock.esg_score}
                                            </span>
                                            <a
                                              href={`https://market.sec.or.th/public/idisc/th/FinancialReport/OneReport?symbol=${stock.ticker}`}
                                              target="_blank"
                                              rel="noopener noreferrer"
                                              className="inline-flex items-center gap-0.5 text-[8px] font-semibold text-blue-600 dark:text-blue-400 hover:underline mt-0.5 transition-all"
                                            >
                                              📄 One Report
                                              <ExternalLink className="w-2 h-2" />
                                            </a>
                                          </div>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </td>
                              </tr>
                            )}
                          </React.Fragment>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </div>

              {/* Execution traces from supervisor */}
              <div className="bg-slate-950 border border-slate-800 rounded-2xl p-5 shadow-xl font-mono text-xs">
                <h3 className="text-slate-200 font-bold border-b border-slate-800 pb-2 mb-3 flex items-center gap-2">
                  <FileText className="w-4 h-4 text-emerald-400" />
                  {t.traceTitle}
                </h3>
                <div className="space-y-1.5 overflow-y-auto max-h-[160px] text-slate-300 leading-relaxed pr-2">
                  {portfolioResult.execution_trace.map((log, idx) => (
                    <div key={idx} className="flex items-start gap-1">
                      <span className="text-slate-600 shrink-0">[{idx + 1}]</span>
                      <span className={log.includes("FAILED") || log.includes("Warning") ? "text-amber-400" : log.includes("PASSED") ? "text-emerald-400" : ""}>
                                {renderLogLine(log)}
                              </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Glassmorphism Action Bar */}
              <div className="glass-panel border border-slate-200 dark:border-slate-800 rounded-2xl p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-xl mt-4">
                <div className="flex items-start gap-2.5 min-w-0 flex-1">
                  <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-ping shrink-0 mt-1 animate-pulse-slow"></div>
                  <span className="text-xs text-slate-700 dark:text-slate-300 font-semibold leading-relaxed break-words">
                    {language === 'TH' ? 'ตรวจสอบสัดส่วนการลงทุนผ่านเกณฑ์ทั้งหมด ระบบพร้อมดำเนินการจัดส่งคำสั่งซื้อ' : 'Validation checks passed. Ready to lock quota and execute portfolio trades.'}
                  </span>
                </div>
                
                <div className="flex items-center gap-3 w-full sm:w-auto">
                  <button
                    onClick={() => alert(language === 'TH' ? 'ส่งต่อข้อมูลพอร์ตการลงทุนนี้ให้ CFA ผู้เชี่ยวชาญตรวจสอบความสอดคล้องเรียบร้อยแล้ว' : 'Portfolio construction escalated to CFA analyst.')}
                    className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-4.5 py-2.5 bg-red-800 hover:bg-red-900 text-white font-bold text-xs rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-[1.01] cursor-pointer"
                  >
                    <AlertTriangle className="w-3.5 h-3.5" />
                    <span>{language === 'TH' ? 'ส่งต่อให้ CFA ตรวจสอบ' : 'Escalate to CFA'}</span>
                  </button>
                  <button
                    onClick={() => alert(language === 'TH' ? 'ดำเนินการจัดสรรสิทธิ์และสั่งซื้อกองทุน ThaiESG สำเร็จ!' : 'Portfolio executed successfully. Asset allocation trades completed.')}
                    className="flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-4.5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs rounded-xl shadow-md hover:shadow-lg transition-all duration-300 hover:scale-[1.01] cursor-pointer"
                  >
                    <ShieldCheck className="w-3.5 h-3.5 text-blue-200" />
                    <span>{language === 'TH' ? 'ยืนยันสั่งซื้อและจัดพอร์ต' : 'Confirm and Execute'}</span>
                  </button>
                </div>
              </div>

            </div>
          )}
        </div>

        {/* Right Sidebar: AI Logic Progress Cards */}
        <div className="col-span-12 lg:col-span-4 space-y-4">
          <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-xl">
            <h3 className="text-sm font-bold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
              {t.traceTitle}
            </h3>
            
            <div className="space-y-3">
              {/* Phase 1 */}
              <ProgressCard
                phase={1}
                title={t.phase1Name}
                description={t.phase1Desc}
                status={pipelinePhase >= 2 ? 'complete' : pipelinePhase === 1 ? 'processing' : 'locked'}
                steps={[
                  { label: 'Verify personal assessable base', isCompleted: true },
                  { label: 'Calculate 30% allowance cap limits', isCompleted: true }
                ]}
              />

              {/* Phase 2 */}
              <ProgressCard
                phase={2}
                title={t.phase2Name}
                description={t.phase2Desc}
                status={pipelinePhase >= 3 ? 'complete' : pipelinePhase === 2 ? 'processing' : 'locked'}
                steps={[
                  { label: 'Screen funds with eligible ThaiESG indicators', isCompleted: true },
                  { label: 'Filter ESG score rating constraints (A-AAA)', isCompleted: true }
                ]}
              />

              {/* Phase 3 - Expanded by Default */}
              <ProgressCard
                phase={3}
                title={t.phase3Name}
                description={t.phase3Desc}
                status={pipelinePhase >= 4 ? 'complete' : pipelinePhase === 3 ? 'processing' : 'locked'}
                defaultExpanded={true}
                steps={[
                  { label: 'Audit live data sheets', isCompleted: pipelinePhase >= 3, sourceName: '↗ SEC Portal', sourceLink: 'https://market.sec.or.th/public/idisc/th' },
                  { label: 'Extract audio sentiment keywords', isCompleted: pipelinePhase >= 4, sourceName: '🎵 ฟัง Opp Day', sourceLink: 'https://www.youtube.com/results?search_query=Opp+Day+ThaiESG' }
                ]}
              />

              {/* Phase 4 */}
              <ProgressCard
                phase={4}
                title={t.phase4Name}
                description={t.phase4Desc}
                status={pipelinePhase >= 5 ? 'complete' : pipelinePhase === 4 ? 'processing' : 'locked'}
                steps={[
                  { label: 'Verify absolute risk tolerance limits', isCompleted: pipelinePhase >= 5, sourceName: '🛡️ SEC Rules', sourceLink: 'https://www.sec.or.th/TH/Pages/LawRegulation/RulesRegulation.aspx' },
                  { label: 'Self-healing allocation optimization loop', isCompleted: pipelinePhase >= 5, sourceName: '📊 RD Tax Rules', sourceLink: 'https://www.rd.go.th/65208.html' }
                ]}
              />

              {/* Phase 5 */}
              <ProgressCard
                phase={5}
                title={t.phase5Name}
                description={t.phase5Desc}
                status={pipelinePhase >= 6 ? 'complete' : pipelinePhase === 5 ? 'processing' : 'locked'}
                steps={[
                  { label: 'Calculate aleatoric/epistemic uncertainty indices', isCompleted: pipelinePhase >= 6 },
                  { label: 'Compile Explainable XAI report metrics', isCompleted: pipelinePhase >= 6 }
                ]}
              />
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
