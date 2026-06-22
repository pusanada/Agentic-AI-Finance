'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAppStore } from '@/store/useAppStore';
import { translations } from '@/store/translations';
import { UploadCloud, FileText, CheckCircle2, AlertCircle, ArrowRight, Calculator, FileCheck, Coins } from 'lucide-react';

export default function TaxOcrDashboard() {
  const router = useRouter();
  const {
    language,
    theme,
    setTheme,
    ocrCompleted,
    ocrResult,
    setOcrResult,
    isUploading,
    setIsUploading,
  } = useAppStore();

  const t = translations[language];

  // Internal states
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [manualIncome, setManualIncome] = useState<number>(0);
  const [manualPurchased, setManualPurchased] = useState<number>(0);

  // Sync manual inputs when OCR finishes
  useEffect(() => {
    if (ocrResult) {
      setManualIncome(ocrResult.assessable_income);
      setManualPurchased(ocrResult.already_purchased);
    }
  }, [ocrResult]);

  // Calculations
  const calculatedMaxQuota = Math.min(manualIncome * 0.3, 300000);
  const calculatedRemaining = Math.max(0, calculatedMaxQuota - manualPurchased);
  const quotaPercentage = manualIncome > 0 ? (calculatedMaxQuota / manualIncome) * 100 : 0;
  const remainingPercentage = calculatedMaxQuota > 0 ? (calculatedRemaining / calculatedMaxQuota) * 100 : 0;

  // Handler for file upload
  const handleFileUpload = async (file: File) => {
    if (!file) return;
    setIsUploading(true);
    setErrorMsg(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://127.0.0.1:8080/api/v1/tax/ocr', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to process document. Please check the file format.');
      }

      const data = await response.json();
      setOcrResult({
        assessable_income: data.assessable_income,
        withholding_tax: data.withholding_tax,
        other_deductions: data.existing_deductions,
        confidence: data.confidence,
        document_type: data.document_type,
        already_purchased: data.already_purchased,
      });
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.message || t.ocrFail);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileUpload(e.target.files[0]);
    }
  };

  // Upload specific demo test file triggers
  const triggerDemoFile = (type: 'no_esg' | 'with_esg') => {
    const filename = type === 'no_esg' ? 'mock_tax_no_esg.pdf' : 'mock_tax_with_esg.pdf';
    // Generate a small dummy file to upload
    const dummyBlob = new Blob(['%PDF-1.5 dummy content for mock parsing'], { type: 'application/pdf' });
    const dummyFile = new File([dummyBlob], filename, { type: 'application/pdf' });
    handleFileUpload(dummyFile);
  };

  // SVG Donut slice helper
  const size = 180;
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  
  // Slices: Used (Purchased) vs Remaining
  const usedRatio = calculatedMaxQuota > 0 ? manualPurchased / calculatedMaxQuota : 0;
  const usedDash = circumference * Math.min(1, usedRatio);
  const remainingDash = circumference * (1 - Math.min(1, usedRatio));

  return (
    <div className="space-y-6 animate-slide-up">
      {/* Title */}
      <div className="text-center md:text-left">
        <h1 className="text-3xl font-extrabold tracking-tight text-slate-800 dark:text-slate-100 flex items-center justify-center md:justify-start gap-2">
          <Coins className="w-8 h-8 text-teal-500" />
          <span>{t.page1Title}</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-2 max-w-2xl">
          {language === 'TH' 
            ? 'วิเคราะห์ข้อมูลเงินได้สะสมและภาษีหัก ณ ที่จ่าย เพื่อคำนวณวงเงินสูงสุดที่สามารถลงทุนลดหย่อนภาษีในกองทุนรวมไทยเพื่อความยั่งยืน (ThaiESG) ได้อย่างถูกต้องตามเกณฑ์สรรพากรปี 2569' 
            : 'Analyze assessable income and withholding tax from your documents to compute the exact eligible deduction space for Thailand ESG (ThaiESG) funds.'}
        </p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        
        {/* Left Side: Upload Zone & Demo selectors */}
        <div className="col-span-12 lg:col-span-6 space-y-6">
          <div 
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`relative rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-300 bg-white dark:bg-slate-900 shadow-sm flex flex-col items-center justify-center min-h-[300px] ${
              dragActive 
                ? 'border-teal-500 bg-teal-50/20 dark:bg-teal-950/10 scale-[1.01]' 
                : 'border-slate-300 dark:border-slate-800 hover:border-teal-400'
            }`}
          >
            <input 
              type="file" 
              id="file-upload-input" 
              className="hidden" 
              accept="image/*,.pdf"
              onChange={handleFileInputChange}
            />

            {isUploading ? (
              <div className="space-y-4">
                <div className="relative w-16 h-16 mx-auto flex items-center justify-center">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal-400 opacity-75"></span>
                  <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-teal-500"></div>
                </div>
                <div>
                  <h3 className="font-semibold text-slate-800 dark:text-slate-200">{t.processingOcr}</h3>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">Typhoon-Vision is extracting tax columns...</p>
                </div>
              </div>
            ) : ocrCompleted && ocrResult ? (
              <div className="space-y-4">
                <div className="w-16 h-16 rounded-full bg-teal-50 dark:bg-teal-950/30 flex items-center justify-center mx-auto shadow-inner">
                  <CheckCircle2 className="w-8 h-8 text-teal-500" />
                </div>
                <div>
                  <h3 className="font-bold text-teal-600 dark:text-teal-400">{t.ocrSuccess}</h3>
                  <div className="inline-flex items-center gap-1 bg-slate-105 dark:bg-slate-800 text-[10px] text-slate-500 dark:text-slate-400 px-2 py-0.5 rounded-full font-mono mt-1">
                    <FileCheck className="w-3 h-3 text-teal-500" />
                    {ocrResult.document_type} (Conf: {(ocrResult.confidence * 100).toFixed(0)}%)
                  </div>
                </div>
                <label 
                  htmlFor="file-upload-input"
                  className="inline-block text-xs font-semibold px-4 py-2 rounded-full border border-teal-500 hover:bg-teal-50 dark:hover:bg-slate-800 text-teal-600 dark:text-teal-400 cursor-pointer transition-colors shadow-sm"
                >
                  {language === 'TH' ? 'อัปโหลดไฟล์ใหม่' : 'Upload New File'}
                </label>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="w-16 h-16 rounded-full bg-slate-50 dark:bg-slate-800 flex items-center justify-center mx-auto text-slate-400 group-hover:text-teal-500 transition-colors shadow-inner">
                  <UploadCloud className="w-8 h-8 text-teal-500" />
                </div>
                <div>
                  <h3 className="font-bold text-slate-800 dark:text-slate-200 text-sm">{t.uploadTitle}</h3>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{t.uploadSubtitle}</p>
                </div>
                
                <label 
                  htmlFor="file-upload-input"
                  className="inline-block text-xs font-bold px-5 py-2.5 rounded-full bg-teal-500 hover:bg-teal-600 text-white shadow-md cursor-pointer transition-all duration-300 hover:scale-105"
                >
                  {t.uploadButton}
                </label>
              </div>
            )}

            {errorMsg && (
              <div className="absolute bottom-4 left-4 right-4 flex items-center gap-2 bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400 text-xs p-3 rounded-lg border border-red-100 dark:border-red-900/30">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{errorMsg}</span>
              </div>
            )}
          </div>

          {/* Quick Demo files */}
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-5 shadow-sm border border-slate-200/60 dark:border-slate-800/60">
            <h3 className="text-xs font-bold text-slate-800 dark:text-slate-200 uppercase tracking-wider mb-3">
              {t.demoFilesTitle}
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <button
                onClick={() => triggerDemoFile('no_esg')}
                disabled={isUploading}
                className="flex items-center gap-2 p-3 text-left rounded-xl bg-slate-50 hover:bg-teal-50/50 dark:bg-slate-800 dark:hover:bg-slate-700/60 border border-slate-200 dark:border-slate-700/60 transition-all text-xs font-medium focus:outline-none disabled:opacity-50"
              >
                <FileText className="w-4 h-4 text-slate-500 dark:text-slate-400 shrink-0" />
                <div>
                  <div className="text-slate-700 dark:text-slate-300">{t.demoFile1}</div>
                  <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">Mock No Existing ESG</div>
                </div>
              </button>
              
              <button
                onClick={() => triggerDemoFile('with_esg')}
                disabled={isUploading}
                className="flex items-center gap-2 p-3 text-left rounded-xl bg-slate-50 hover:bg-teal-50/50 dark:bg-slate-800 dark:hover:bg-slate-700/60 border border-slate-200 dark:border-slate-700/60 transition-all text-xs font-medium focus:outline-none disabled:opacity-50"
              >
                <FileText className="w-4 h-4 text-teal-500 shrink-0" />
                <div>
                  <div className="text-slate-700 dark:text-slate-300">{t.demoFile2}</div>
                  <div className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">Mock With 100k ESG</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Right Side: Computed Quotas & Donut Chart */}
        <div className="col-span-12 lg:col-span-6 space-y-6">
          <div className="bg-white dark:bg-slate-900 rounded-2xl p-6 shadow-sm border border-slate-200/60 dark:border-slate-800/60 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-800 dark:text-white flex items-center gap-2">
                <Calculator className="w-5 h-5 text-teal-500" />
                {t.calculatedQuotas}
              </h2>
              {manualIncome > 0 && (
                <span className="text-[10px] font-bold bg-teal-500/10 text-teal-600 dark:text-teal-400 px-2.5 py-1 rounded-full uppercase tracking-wider">
                  Calculated
                </span>
              )}
            </div>

            {/* Live inputs for overrides */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">
                  {language === 'TH' ? 'รายได้ประเมิน (แก้ไขได้)' : 'Assessable Income (Editable)'}
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={manualIncome || ''}
                    onChange={(e) => setManualIncome(Number(e.target.value))}
                    placeholder="0"
                    className="w-full pl-3 pr-10 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-none focus:border-teal-500 transition-all font-mono"
                  />
                  <span className="absolute right-3 top-2.5 text-xs text-slate-400 font-medium">THB</span>
                </div>
              </div>
              <div>
                <label className="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">
                  {language === 'TH' ? 'ซื้อแล้วปีนี้ (แก้ไขได้)' : 'Already Purchased (Editable)'}
                </label>
                <div className="relative">
                  <input
                    type="number"
                    value={manualPurchased || ''}
                    onChange={(e) => setManualPurchased(Number(e.target.value))}
                    placeholder="0"
                    className="w-full pl-3 pr-10 py-2 text-sm rounded-lg border border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-800 text-slate-800 dark:text-slate-100 focus:outline-none focus:border-teal-500 transition-all font-mono"
                  />
                  <span className="absolute right-3 top-2.5 text-xs text-slate-400 font-medium">THB</span>
                </div>
              </div>
            </div>

            {/* Calculations Breakdown grid */}
            <div className="grid grid-cols-2 gap-4">
              {/* Total Income */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/50 dark:border-slate-800">
                <div className="text-xs text-slate-500 dark:text-slate-400">{t.totalIncome}</div>
                <div className="text-lg font-bold text-slate-800 dark:text-white mt-1 font-mono">
                  ฿{manualIncome.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>
              {/* Deductions */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/50 dark:border-slate-800">
                <div className="text-xs text-slate-500 dark:text-slate-400">{t.purchasedLimit}</div>
                <div className="text-lg font-bold text-teal-600 dark:text-teal-400 mt-1 font-mono">
                  ฿{manualPurchased.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>
              {/* Max Quota */}
              <div className="bg-slate-50 dark:bg-slate-950 p-4 rounded-xl border border-slate-200/50 dark:border-slate-800">
                <div className="text-xs text-slate-500 dark:text-slate-400">{t.maxQuota}</div>
                <div className="text-lg font-bold text-slate-800 dark:text-white mt-1 font-mono">
                  ฿{calculatedMaxQuota.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>
              {/* Remaining Quota */}
              <div className="bg-teal-50/50 dark:bg-teal-950/15 p-4 rounded-xl border border-teal-200/40 dark:border-teal-900/30">
                <div className="text-xs text-teal-600 dark:text-teal-400 font-semibold">{t.remainingQuota}</div>
                <div className="text-xl font-extrabold text-teal-500 dark:text-teal-400 mt-1 font-mono">
                  ฿{calculatedRemaining.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                </div>
              </div>
            </div>

            {/* Donut Chart container */}
            <div className="flex flex-col sm:flex-row items-center justify-around gap-6 py-4 bg-slate-50/40 dark:bg-slate-950/5 rounded-2xl border border-slate-200/30 dark:border-slate-800/20">
              {/* Donut SVG */}
              <div className="relative" style={{ width: size, height: size }}>
                <svg width={size} height={size} className="transform -rotate-90">
                  {/* Background Circle */}
                  <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    stroke="#e2e8f0"
                    strokeWidth={strokeWidth}
                    fill="transparent"
                    className="dark:stroke-slate-800"
                  />
                  {/* Used (Already Purchased) Slice */}
                  {manualPurchased > 0 && calculatedMaxQuota > 0 && (
                    <circle
                      cx={size / 2}
                      cy={size / 2}
                      r={radius}
                      stroke="#0d9488" // teal-600
                      strokeWidth={strokeWidth}
                      strokeDasharray={circumference}
                      strokeDashoffset={0}
                      fill="transparent"
                    />
                  )}
                  {/* Remaining Slice */}
                  {calculatedRemaining > 0 && calculatedMaxQuota > 0 && (
                    <circle
                      cx={size / 2}
                      cy={size / 2}
                      r={radius}
                      stroke="#2dd4bf" // teal-400
                      strokeWidth={strokeWidth}
                      strokeDasharray={circumference}
                      strokeDashoffset={usedDash}
                      fill="transparent"
                      strokeLinecap="round"
                    />
                  )}
                </svg>
                {/* Centered statistics */}
                <div className="absolute inset-0 flex flex-col items-center justify-center text-center p-2 pointer-events-none">
                  <span className="text-[10px] uppercase font-bold text-slate-400 dark:text-slate-500">
                    {t.remainingLabel}
                  </span>
                  <span className="text-lg font-extrabold text-teal-600 dark:text-teal-400 font-mono mt-0.5">
                    {remainingPercentage.toFixed(0)}%
                  </span>
                  <span className="text-[9px] text-slate-400 font-mono mt-0.5">
                    ฿{Math.round(calculatedRemaining / 1000)}k left
                  </span>
                </div>
              </div>

              {/* Legends list */}
              <div className="space-y-3">
                <h4 className="text-xs font-bold text-slate-700 dark:text-slate-300">{t.esgQuotaChart}</h4>
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-3 h-3 rounded-sm bg-teal-400 shrink-0"></span>
                    <span className="text-slate-600 dark:text-slate-400">
                      {t.remainingLabel}: <strong>฿{calculatedRemaining.toLocaleString()}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs">
                    <span className="w-3 h-3 rounded-sm bg-teal-600 shrink-0"></span>
                    <span className="text-slate-600 dark:text-slate-400">
                      {t.purchasedLimit}: <strong>฿{manualPurchased.toLocaleString()}</strong>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs opacity-50">
                    <span className="w-3 h-3 rounded-sm bg-slate-300 dark:bg-slate-700 shrink-0"></span>
                    <span className="text-slate-500 dark:text-slate-400">
                      {t.maxQuota}: <strong>฿{calculatedMaxQuota.toLocaleString()}</strong>
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <p className="text-[10px] text-slate-400 dark:text-slate-500 text-center leading-relaxed">
              * {t.customQuotaNote}
            </p>

            {/* Bottom Proceed Action Button */}
            <button
              onClick={() => {
                // Save inputs to useAppStore before proceeding
                setOcrResult({
                  assessable_income: manualIncome,
                  already_purchased: manualPurchased,
                  withholding_tax: ocrResult?.withholding_tax || 0.0,
                  other_deductions: ocrResult?.other_deductions || 0.0,
                  confidence: ocrResult?.confidence || 1.0,
                  document_type: ocrResult?.document_type || 'Manual Override Input',
                });
                router.push('/portfolio');
              }}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-600 hover:from-teal-600 hover:to-emerald-700 text-white font-bold text-sm shadow-md hover:shadow-xl hover:scale-[1.01] transition-all duration-300 flex items-center justify-center gap-2 group cursor-pointer"
            >
              <span>{t.proceedToPortfolio}</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}
