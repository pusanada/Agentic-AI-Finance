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
  ExternalLink,
  X
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

  const goalLabelMap: Record<string, string> = {
    Growth: language === 'TH' ? 'Growth (เติบโตสูง)' : 'Growth',
    Dividend: language === 'TH' ? 'Dividend (ปันผล)' : 'Dividend',
    Balanced: language === 'TH' ? 'Balanced (สมดุล)' : 'Balanced',
  };

  const riskLabelMap: Record<string, string> = {
    Conservative: language === 'TH' ? 'Conservative (เสี่ยงต่ำ)' : 'Conservative',
    Moderate: language === 'TH' ? 'Moderate (ปานกลาง)' : 'Moderate',
    Aggressive: language === 'TH' ? 'Aggressive (เสี่ยงสูง)' : 'Aggressive',
  };

  const parseHighRiskReason = (reason: string) => {
    const lower = reason.toLowerCase();
    if (lower.includes("contains stock ea") && (lower.includes("greenwashing") || lower.includes("conflict"))) {
      return { type: "critical", text: "EA — Data Conflict (Greenwashing)" };
    }
    if (lower.includes("contains stock ea") && lower.includes("cgr score")) {
      return { type: "critical", text: "EA — CGR Score < 90" };
    }
    if (lower.includes("contains stock ea") && (lower.includes("sec") || lower.includes("penalty") || lower.includes("penalties"))) {
      return { type: "critical", text: "EA — SEC Penalties" };
    }
    if (lower.includes("contains stock ptt") && (lower.includes("greenwashing") || lower.includes("conflict"))) {
      return { type: "warning", text: "PTT — Conflict Signal" };
    }
    if (lower.includes("contains stock ptt") && lower.includes("cgr score")) {
      return { type: "warning", text: "PTT — CGR Score < 90 (2 จุด)" };
    }
    if (lower.includes("contains stock ptt") && lower.includes("disclosure")) {
      return { type: "warning", text: "PTT — Disclosure Mismatch" };
    }
    if (lower.includes("ocr")) {
      return { type: "warning", text: "OCR — Confidence Low" };
    }
    if (lower.includes("compliance")) {
      return { type: "critical", text: "Compliance Guard Violation" };
    }
    // Fallback
    const clean = reason.replace(/\s*\([+-][\d.]+%\)/g, '').trim();
    return { type: "warning", text: clean };
  };

  // Parameters inputs (prefilled from OCR if available)
  const [income, setIncome] = useState<number | ''>(ocrResult?.assessable_income ?? 1200000.0);
  const [alreadyPurchased, setAlreadyPurchased] = useState<number | ''>(ocrResult?.already_purchased ?? 0.0);
  const [goal, setGoal] = useState<'Growth' | 'Dividend' | 'Balanced'>('Growth');
  const [riskProfile, setRiskProfile] = useState<'Conservative' | 'Moderate' | 'Aggressive'>('Moderate');
  const [userInstructions, setUserInstructions] = useState<string>('');
  
  // Pipeline simulation states for visual engagement
  const [pipelinePhase, setPipelinePhase] = useState<number>(0);
  const [expandedFundCode, setExpandedFundCode] = useState<string | null>(null);
  const [explainScore, setExplainScore] = useState<boolean>(false);
  const [showConfirmModal, setShowConfirmModal] = useState<boolean>(false);

  // Sync inputs with OCRResult if it updates
  useEffect(() => {
    if (ocrResult) {
      setIncome(ocrResult.assessable_income ?? '');
      setAlreadyPurchased(ocrResult.already_purchased ?? '');
    }
  }, [ocrResult]);

  // Lock body scroll when confirmation overlay is open
  useEffect(() => {
    if (showConfirmModal) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [showConfirmModal]);

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
          assessable_income: income === '' ? 0 : income,
          already_purchased: alreadyPurchased === '' ? 0 : alreadyPurchased,
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
    <>
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
                    onChange={(e) => {
                      const val = e.target.value;
                      setIncome(val === '' ? '' : Number(val));
                    }}
                    className="w-full px-3.5 py-2 text-xs rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white focus:outline-none focus:border-emerald-400 transition-all font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{t.alreadyPurchasedLabel}</label>
                  <input
                    type="number"
                    value={alreadyPurchased}
                    onChange={(e) => {
                      const val = e.target.value;
                      setAlreadyPurchased(val === '' ? '' : Number(val));
                    }}
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
              <div className={`transition-all duration-300 ${
                explainScore 
                  ? 'flex flex-col gap-4' 
                  : 'grid grid-cols-1 md:grid-cols-2 gap-4'
              }`}>
                
                {explainScore ? (
                  /* Compliance Guard Mini Card / Badge when AUQ is expanded */
                  <div className={`rounded-xl p-3 border shadow-sm flex items-center justify-between transition-all duration-300 ${
                    portfolioResult.compliance.is_compliant 
                      ? 'border-emerald-500/20 bg-emerald-950/5 dark:bg-emerald-950/10' 
                      : 'border-red-500/20 bg-red-950/5 dark:bg-red-950/10'
                  }`}>
                    <div className="flex items-center gap-2">
                      <div className={`p-1.5 rounded-lg ${
                        portfolioResult.compliance.is_compliant ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                      }`}>
                        {portfolioResult.compliance.is_compliant ? <ShieldCheck className="w-4 h-4" /> : <ShieldAlert className="w-4 h-4" />}
                      </div>
                      <span className="text-xs font-semibold text-slate-500 dark:text-slate-400">{t.complianceStatus}:</span>
                      <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        portfolioResult.compliance.is_compliant ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'
                      }`}>
                        {portfolioResult.compliance.is_compliant ? t.complianceCompliant : t.complianceViolated}
                      </span>
                    </div>
                    {portfolioResult.compliance.violations.length > 0 && (
                      <span className="text-[10px] font-semibold text-red-500 dark:text-red-400 bg-red-500/10 px-2 py-0.5 rounded-md">
                        {portfolioResult.compliance.violations.length} {language === 'TH' ? 'ข้อผิดพลาด' : 'Violations'}
                      </span>
                    )}
                  </div>
                ) : (
                  /* Full Compliance Guard Shield Card when AUQ is collapsed */
                  <div className={`rounded-2xl p-5 border shadow-lg flex items-start gap-4 transition-all duration-300 ${
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
                )}

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

                    {/* Glass Box Explain Score Toggle Button */}
                    <button 
                      type="button"
                      onClick={() => setExplainScore(!explainScore)}
                      className="mt-3 text-[11px] font-semibold text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 transition-colors inline-flex items-center gap-1 cursor-pointer focus:outline-none"
                    >
                      <span>{explainScore ? '▲ ซ่อนวิธีคำนวณ' : '▼ ดูวิธีคำนวณ (Explain Score)'}</span>
                    </button>

                    {/* Glass Box Score Breakdown Dropdown */}
                    {explainScore && (
                      <div className="mt-3 p-4 rounded-xl border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/40 space-y-3 transition-all duration-300">
                        <div className="text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-800/80 pb-2">
                          <span>🔍 Breakdown</span>
                        </div>
                        
                        <div className="font-mono text-xs space-y-2">
                          {/* Starting Score */}
                          <div className="flex justify-between items-center text-slate-600 dark:text-slate-300">
                            <span className="text-slate-500 dark:text-slate-400 text-[11px]">Starting Score</span>
                            <span className="font-bold text-slate-900 dark:text-white">100%</span>
                          </div>

                          {/* Dynamic Reasons */}
                          <div className="space-y-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
                            {portfolioResult.auq.reasons.map((reason, idx) => {
                              const parsed = (() => {
                                const match = reason.match(/\(([+-][\d.]+)%\)/);
                                if (match) {
                                  const val = match[1];
                                  const cleanText = reason.replace(/\s*\([+-][\d.]+%\)/g, '').trim();
                                  const parsedVal = parseFloat(val);
                                  const sign = parsedVal > 0 ? '+' : '';
                                  
                                  // Apply short/concise mappings
                                  let displayText = cleanText;
                                  const lowerText = cleanText.toLowerCase();
                                  
                                  if (lowerText.includes("ocr")) {
                                    displayText = "OCR Confidence";
                                  } else if (lowerText.includes("investor risk profile") || lowerText.includes("kyc")) {
                                    displayText = "Kyc Incomplete";
                                  } else if (lowerText.includes("compliance checks failed") || lowerText.includes("violations detected")) {
                                    displayText = "Compliance Failed";
                                  } else if (lowerText.includes("custom allocation instructions") || lowerText.includes("custom instructions")) {
                                    displayText = "Custom Instructions";
                                  } else if (lowerText.includes("contains stock ptt") && lowerText.includes("conflicting disclosures")) {
                                    // Count occurrences of PTT greenwashing conflict before this index
                                    let pttCountBefore = 0;
                                    for (let i = 0; i < idx; i++) {
                                      const prevReason = portfolioResult.auq.reasons[i].toLowerCase();
                                      if (prevReason.includes("contains stock ptt") && prevReason.includes("conflicting disclosures")) {
                                        pttCountBefore++;
                                      }
                                    }
                                    displayText = pttCountBefore === 0 ? "PTT Conflict" : "PTT Disclosure";
                                  } else if (lowerText.includes("contains stock ea") && lowerText.includes("conflicting disclosures")) {
                                    displayText = "EA Controversy";
                                  } else if (lowerText.includes("contains stock ea") && lowerText.includes("cgr score")) {
                                    displayText = "CGR Below Threshold";
                                  } else if (lowerText.includes("contains stock ea") && lowerText.includes("sec")) {
                                    displayText = "SEC Warning";
                                  } else {
                                    // General fallback ticker parsing
                                    const tickerMatch = cleanText.match(/stock ([A-Z0-9]+)/i);
                                    const ticker = tickerMatch ? tickerMatch[1] : "";
                                    if (lowerText.includes("greenwashing") || lowerText.includes("conflict")) {
                                      displayText = ticker ? `${ticker} Conflict` : "Greenwashing Conflict";
                                    } else if (lowerText.includes("cgr score")) {
                                      displayText = ticker ? `${ticker} CGR Low` : "CGR Score Violation";
                                    } else if (lowerText.includes("sec")) {
                                      displayText = ticker ? `${ticker} SEC Warning` : "SEC Warning";
                                    }
                                  }

                                  return { 
                                    percentage: parsedVal === 0 ? '0%' : `${sign}${parsedVal}%`, 
                                    text: displayText 
                                  };
                                }
                                return { percentage: '0%', text: reason };
                              })();
                              
                              const isNegative = parsed.percentage.startsWith('-');
                              const colorClass = isNegative ? 'text-red-500 dark:text-red-400 font-bold' : 'text-slate-400 dark:text-slate-500';

                              return (
                                <div key={idx} className="flex justify-between items-start gap-3 leading-normal">
                                  <span className="text-slate-500 dark:text-slate-400 text-[11px] flex-1">{parsed.text}</span>
                                  <span className={`text-right shrink-0 ${colorClass}`}>{parsed.percentage}</span>
                                </div>
                              );
                            })}
                          </div>

                          {/* Final Score */}
                          <div className="flex justify-between items-center text-slate-900 dark:text-white pt-1">
                            <span className="font-bold">Final Score</span>
                            <span className="font-extrabold text-emerald-500 dark:text-emerald-400 text-sm">{portfolioResult.auq.confidence_score}%</span>
                          </div>
                        </div>
                        
                        {/* Recommendation */}
                        <div className="text-[10px] bg-blue-500/5 border border-blue-500/10 p-2.5 rounded-lg text-slate-600 dark:text-slate-400 leading-normal font-sans">
                          <div className="font-bold text-blue-500 dark:text-blue-400 mb-0.5">
                            {language === 'TH' ? 'คำแนะนำระบบ:' : 'Recommendation:'}
                          </div>
                          <div>
                            {portfolioResult.auq.requires_override 
                              ? (language === 'TH' ? 'ต้องการความเห็นชอบจากผู้เชี่ยวชาญ (Human Review Required)' : 'Human Review Required')
                              : (language === 'TH' ? 'ผ่านเกณฑ์ตรวจสอบอัตโนมัติ (Auto-Approved)' : 'Auto-Approved')
                            }
                          </div>
                        </div>
                      </div>
                    )}
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
                  <div className={`w-2.5 h-2.5 rounded-full animate-ping shrink-0 mt-1 ${
                    portfolioResult.compliance.is_compliant 
                      ? 'bg-emerald-500' 
                      : 'bg-amber-500'
                  }`}></div>
                  <span className="text-xs text-slate-700 dark:text-slate-300 font-semibold leading-relaxed break-words">
                    {portfolioResult.compliance.is_compliant 
                      ? (language === 'TH' 
                          ? 'ตรวจสอบสัดส่วนการลงทุนผ่านเกณฑ์ทั้งหมด ระบบพร้อมดำเนินการจัดส่งคำสั่งซื้อ' 
                          : 'Validation checks passed. Ready to lock quota and execute portfolio trades.')
                      : (language === 'TH'
                          ? 'พบการละเมิดเกณฑ์ตรวจสอบ (Compliance Violation) ระบบล็อกการจัดส่งคำสั่งซื้อชั่วคราว กรุณาส่งต่อข้อมูลให้ CFA พิจารณา'
                          : 'Compliance violations detected. Execution blocked. Please escalate to a CFA analyst.')
                    }
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
                    disabled={!portfolioResult.compliance.is_compliant}
                    onClick={() => setShowConfirmModal(true)}
                    className={`flex-1 sm:flex-none inline-flex items-center justify-center gap-1.5 px-4.5 py-2.5 text-white font-bold text-xs rounded-xl shadow-md transition-all duration-300 ${
                      portfolioResult.compliance.is_compliant
                        ? 'bg-blue-600 hover:bg-blue-700 hover:shadow-lg hover:scale-[1.01] cursor-pointer'
                        : 'bg-slate-200 dark:bg-slate-800 text-slate-400 dark:text-slate-600 cursor-not-allowed opacity-50 border border-slate-300 dark:border-slate-700'
                    }`}
                  >
                    <ShieldCheck className={`w-3.5 h-3.5 ${
                      portfolioResult.compliance.is_compliant 
                        ? 'text-blue-200' 
                        : 'text-slate-400 dark:text-slate-600'
                    }`} />
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

      {showConfirmModal && portfolioResult && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/75 backdrop-blur-md p-4 animate-in fade-in duration-200">
          <div className="bg-slate-900 border border-slate-800 rounded-3xl p-6 max-w-md w-full shadow-2xl animate-in zoom-in-95 duration-200 text-white relative flex flex-col max-h-[90vh] overflow-hidden">
            <button 
              onClick={() => setShowConfirmModal(false)}
              className="absolute top-4 right-4 text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              <X className="w-5 h-5" />
            </button>

            {portfolioResult.auq.uncertainty_rating === 'HIGH' ? (
              /* SPECIAL CASE: AUQ = HIGH (คำเตือน: พอร์ตนี้มีความเสี่ยงสูงมาก) */
              <>
                {/* Header */}
                <div className="flex items-center gap-2 mb-4 border-b border-red-950 pb-3 shrink-0">
                  <span className="text-xl shrink-0">🛑</span>
                  <h3 className="text-base font-extrabold text-red-400 uppercase tracking-wide">
                    {language === 'TH' ? 'คำเตือน: พอร์ตนี้มีความเสี่ยงสูงมาก' : 'Warning: High Risk Portfolio'}
                  </h3>
                </div>

                {/* Scrollable Details */}
                <div className="overflow-y-auto flex-1 pr-1 space-y-4 mb-4">
                  <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                    <span>⚠️</span>
                    <span>AUQ Confidence:</span>
                    <span className="font-mono text-red-500 font-extrabold">{portfolioResult.auq.confidence_score}% (HIGH)</span>
                  </div>

                  {/* Warning list Box */}
                  <div className="bg-red-950/20 border border-red-900/30 rounded-2xl p-4.5 text-xs">
                    <h4 className="font-bold text-slate-400 mb-2.5 uppercase tracking-wide">
                      {language === 'TH' ? 'ระบบตรวจพบ:' : 'System Detected:'}
                    </h4>
                    
                    <div className="space-y-2 font-mono text-[11px] leading-relaxed">
                      {portfolioResult.auq.reasons
                        .filter(r => !r.toLowerCase().includes("verified") && !r.toLowerCase().includes("+0%"))
                        .map((reason, idx) => {
                          const parsed = parseHighRiskReason(reason);
                          const bullet = parsed.type === "critical" ? "🔴" : "🟡";
                          return (
                            <div key={idx} className="flex items-start gap-2">
                              <span className="shrink-0 mt-0.5">{bullet}</span>
                              <span className="text-slate-200">{parsed.text}</span>
                            </div>
                          );
                        })}
                    </div>
                  </div>

                  {/* Locked text */}
                  <div className="text-center font-bold text-red-400 text-xs py-2 flex items-center justify-center gap-1.5 animate-pulse">
                    <span>❌</span>
                    <span>{language === 'TH' ? 'ไม่สามารถยืนยันได้ด้วยตนเอง' : 'Cannot self-confirm execution'}</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-2 shrink-0">
                  <button
                    onClick={() => {
                      setShowConfirmModal(false);
                      alert(language === 'TH' ? 'ส่งต่อข้อมูลพอร์ตการลงทุนนี้ให้ CFA ผู้เชี่ยวชาญตรวจสอบความสอดคล้องเรียบร้อยแล้ว' : 'Portfolio construction escalated to CFA analyst.');
                    }}
                    className="w-full py-3 bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-xs rounded-xl shadow-md transition-all duration-200 text-center hover:scale-[1.01] cursor-pointer flex items-center justify-center gap-1.5 border border-slate-700"
                  >
                    <span>📩</span>
                    <span>{language === 'TH' ? 'ส่งให้ผู้เชี่ยวชาญตรวจสอบ' : 'Escalate to Expert for Review'}</span>
                  </button>
                  <button
                    onClick={() => setShowConfirmModal(false)}
                    className="w-full py-3 bg-red-650 hover:bg-red-750 text-white font-bold text-xs rounded-xl shadow-md transition-all duration-200 text-center hover:scale-[1.01] cursor-pointer flex items-center justify-center gap-1.5"
                  >
                    <span>❌</span>
                    <span>{language === 'TH' ? 'ยกเลิก' : 'Cancel'}</span>
                  </button>
                </div>
              </>
            ) : (
              /* NORMAL CASE: BEFORE PORTFOLIO CONFIRMATION (ยืนยันการจัดพอร์ตและสั่งซื้อ) */
              <>
                {/* Header */}
                <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3 shrink-0">
                  <span className="text-xl shrink-0">⚠️</span>
                  <h3 className="text-base font-extrabold text-slate-100 uppercase tracking-wide">
                    {language === 'TH' ? 'ยืนยันการจัดพอร์ตและสั่งซื้อ ThaiESG' : 'Confirm Portfolio & Buy ThaiESG'}
                  </h3>
                </div>

                {/* Scrollable Content */}
                <div className="overflow-y-auto flex-1 pr-1 space-y-4 mb-4">
                  {/* Sub Container: สรุปพอร์ตการลงทุน */}
                  <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-4.5 space-y-4">
                    <div>
                      <h4 className="text-xs font-bold text-slate-400 mb-2 flex items-center gap-1.5 uppercase">
                        <span>📊</span> {language === 'TH' ? 'สรุปพอร์ตการลงทุน' : 'Portfolio Summary'}
                      </h4>
                      <div className="space-y-1.5 text-xs">
                        <div className="flex justify-between">
                          <span className="text-slate-500">{language === 'TH' ? 'เป้าหมาย:' : 'Goal:'}</span>
                          <span className="font-semibold text-slate-200">{goalLabelMap[goal] || goal}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-slate-500">{language === 'TH' ? 'ระดับความเสี่ยง:' : 'Risk Profile:'}</span>
                          <span className="font-semibold text-slate-200">{riskLabelMap[riskProfile] || riskProfile}</span>
                        </div>
                        <div className="flex justify-between items-baseline pt-0.5 border-t border-slate-900 mt-1">
                          <span className="text-slate-500">{language === 'TH' ? 'เงินลงทุนรวม:' : 'Total Investment:'}</span>
                          <span className="font-bold font-mono text-emerald-400 text-sm">
                            ฿{portfolioResult.portfolio.total_allocated.toLocaleString('en-US', { maximumFractionDigits: 0 })} {language === 'TH' ? 'บาท' : 'THB'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Fund list nested box */}
                    <div className="border border-slate-800/80 rounded-xl overflow-hidden bg-slate-900/50 text-[11px]">
                      <div className="grid grid-cols-12 bg-slate-950/80 px-3 py-1.5 font-bold text-slate-500 border-b border-slate-800/60 uppercase">
                        <div className="col-span-6">{language === 'TH' ? 'กองทุน' : 'Fund'}</div>
                        <div className="col-span-3 text-center">{language === 'TH' ? 'สัดส่วน' : 'Weight'}</div>
                        <div className="col-span-3 text-right">{language === 'TH' ? 'จำนวน' : 'Amount'}</div>
                      </div>
                      <div className="divide-y divide-slate-900">
                        {portfolioResult.portfolio.allocations.map((item) => (
                          <div key={item.fund_code} className="grid grid-cols-12 px-3 py-2 text-slate-300 font-mono items-center">
                            <div className="col-span-6 font-sans font-bold text-slate-200 flex items-center gap-1.5">
                              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
                              {item.fund_code}
                            </div>
                            <div className="col-span-3 text-center font-bold">{(item.weight * 100).toFixed(0)}%</div>
                            <div className="col-span-3 text-right text-emerald-400 font-bold">
                              ฿{item.amount.toLocaleString('en-US', { maximumFractionDigits: 0 })}
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Safety check summary */}
                  <div className="bg-slate-950/70 border border-slate-800 rounded-2xl p-4.5">
                    <h4 className="text-xs font-bold text-slate-400 mb-2 flex items-center gap-1.5 uppercase">
                      <span>🛡️</span> {language === 'TH' ? 'การตรวจสอบความปลอดภัย' : 'Safety & Compliance Check'}
                    </h4>
                    <div className="space-y-1.5 text-xs font-semibold">
                      <div className="flex items-center gap-2">
                        <span>{portfolioResult.compliance.is_compliant ? '✅' : '❌'}</span>
                        <span className="text-slate-400">{language === 'TH' ? 'Compliance Guard:' : 'Compliance Guard:'}</span>
                        <span className={portfolioResult.compliance.is_compliant ? 'text-emerald-400' : 'text-red-400'}>
                          {portfolioResult.compliance.is_compliant ? (language === 'TH' ? 'ผ่าน' : 'Passed') : (language === 'TH' ? 'ไม่ผ่าน' : 'Violated')}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span>✅</span>
                        <span className="text-slate-400">{language === 'TH' ? 'วงเงิน ThaiESG คงเหลือ:' : 'Remaining ThaiESG Quota:'}</span>
                        <span className="text-slate-200 font-mono">
                          ฿{portfolioResult.quota.remaining_quota.toLocaleString('en-US', { maximumFractionDigits: 0 })} {language === 'TH' ? 'บาท' : 'THB'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span>✅</span>
                        <span className="text-slate-400">{language === 'TH' ? 'ระยะเวลาถือครอง:' : 'Holding Period:'}</span>
                        <span className="text-slate-200">
                          5 {language === 'TH' ? 'ปี (ตามเกณฑ์)' : 'Years (Compliant)'}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span>⚠️</span>
                        <span className="text-slate-400">AUQ Confidence:</span>
                        <span className={`font-mono ${
                          portfolioResult.auq.confidence_score >= 80 ? 'text-emerald-400 font-bold' : portfolioResult.auq.confidence_score >= 70 ? 'text-yellow-400 font-bold' : 'text-red-400 font-bold'
                        }`}>
                          {portfolioResult.auq.confidence_score}% ({portfolioResult.auq.uncertainty_rating})
                        </span>
                      </div>
                      {portfolioResult.auq.requires_override && (
                        <div className="flex items-center gap-2 text-yellow-500 text-[11px] pt-1.5 font-bold pl-1 animate-pulse">
                          <span>📌</span>
                          <span>{language === 'TH' ? 'ต้องได้รับความเห็นชอบจากผู้เชี่ยวชาญก่อน' : 'Analyst override approval required'}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-3 shrink-0">
                  <button
                    onClick={() => {
                      setShowConfirmModal(false);
                      alert(language === 'TH' ? 'ดำเนินการจัดส่งคำสั่งซื้อสำเร็จ!' : 'Order executed successfully!');
                    }}
                    className="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs rounded-xl shadow-md transition-all duration-200 text-center hover:scale-[1.02] cursor-pointer flex items-center justify-center gap-1.5 border border-emerald-500/20"
                  >
                    <span>✅</span>
                    <span>{language === 'TH' ? 'ยืนยัน' : 'Confirm'}</span>
                  </button>
                  <button
                    onClick={() => setShowConfirmModal(false)}
                    className="flex-1 py-3 bg-red-600 hover:bg-red-700 text-white font-bold text-xs rounded-xl shadow-md transition-all duration-200 text-center hover:scale-[1.02] cursor-pointer flex items-center justify-center gap-1.5 border border-red-500/20"
                  >
                    <span>❌</span>
                    <span>{language === 'TH' ? 'ยกเลิก' : 'Cancel'}</span>
                  </button>
                </div>

                {/* Disclaimer */}
                <div className="text-[10px] text-slate-400 leading-normal pl-1 flex items-start gap-1">
                  <span className="text-[12px] shrink-0 mt-0.5">💡</span>
                  <p>
                    {language === 'TH' 
                      ? 'การยืนยันนี้ถือว่าท่านรับทราบความเสี่ยงและเงื่อนไขการลงทุนตามที่ระบบแสดงไว้ข้างต้น' 
                      : 'By confirming, you acknowledge the investment risks and compliance constraints displayed above.'}
                  </p>
                </div>
              </>
            )}

          </div>
        </div>
      )}
    </>
  );
}
