import React, { useState } from 'react';
import { Icon } from '@iconify/react';
import { useAppDispatch, useAppSelector } from '../store/hooks';
import {
  updatePhaseStatus,
  updateAgentWeights,
  applyWeightTemplate,
  setSimulationMode,
  removeDocument,
} from '../store/slices/analysisSlice';

export const AnalysisPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const { companyName, metadata, documents, agentWeights, simulationMode, phases } = useAppSelector(
    (state) => state.analysis
  );

  const [sliderValues, setSliderValues] = useState(agentWeights);

  const handleRunAnalysis = () => {
    // TODO: Connect to backend - POST /api/analysis/run-agents
    dispatch(updatePhaseStatus({ phaseId: 'phase3', status: 'running', progressMessage: 'Analyzing with AI agents...' }));
    setTimeout(() => {
      dispatch(updatePhaseStatus({ phaseId: 'phase3', status: 'completed', progressMessage: 'Analysis complete', result: {} }));
    }, 3000);
  };

  const handleGenerateSimulation = () => {
    // TODO: Connect to backend - POST /api/analysis/generate-simulation
    dispatch(updatePhaseStatus({ phaseId: 'phase4', status: 'running', progressMessage: 'Generating founder responses...' }));
    setTimeout(() => {
      dispatch(updatePhaseStatus({ phaseId: 'phase4', status: 'completed', progressMessage: 'Simulation complete', result: {} }));
    }, 2500);
  };

  const handleGenerateMemo = () => {
    // TODO: Connect to backend - POST /api/analysis/generate-memo
    dispatch(updatePhaseStatus({ phaseId: 'phase5', status: 'running', progressMessage: 'Generating investment memo...' }));
    setTimeout(() => {
      dispatch(updatePhaseStatus({ phaseId: 'phase5', status: 'completed', progressMessage: 'Memo generated', result: {} }));
    }, 4000);
  };

  const handleWeightChange = (agent: keyof typeof agentWeights, value: number) => {
    setSliderValues({
      ...sliderValues,
      [agent]: { ...sliderValues[agent], weight: value },
    });
  };

  const handleApplyWeights = () => {
    dispatch(updateAgentWeights(sliderValues));
  };

  const autoBalanceWeights = () => {
    const total = Object.values(sliderValues).reduce((sum, w) => sum + w.weight, 0);
    const balanced = Object.entries(sliderValues).reduce(
      (acc, [key, config]) => ({
        ...acc,
        [key]: { ...config, weight: Math.round((config.weight / total) * 100) },
      }),
      {} as typeof sliderValues
    );
    setSliderValues(balanced);
    dispatch(updateAgentWeights(balanced));
  };

  const getTotalWeight = () => {
    return Object.values(sliderValues).reduce((sum, w) => sum + w.weight, 0);
  };

  const getPhaseIndicatorClass = (status: string) => {
    switch (status) {
      case 'completed':
        return 'border-green-200 bg-green-50 text-green-600';
      case 'running':
        return 'border-blue-200 bg-blue-50 text-blue-600 ring-4 ring-white';
      case 'failed':
        return 'border-red-200 bg-red-50 text-red-600';
      default:
        return 'border-slate-200 bg-white text-slate-500';
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'completed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-green-50 text-green-700 border border-green-100">
            <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
            Completed
          </span>
        );
      case 'running':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-blue-50 text-blue-600 border border-blue-200">
            <Icon icon="lucide:loader-2" width={12} className="animate-spin" />
            Processing
          </span>
        );
      case 'failed':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[10px] font-medium bg-red-50 text-red-700 border border-red-100">
            <Icon icon="lucide:alert-circle" width={12} />
            Failed
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 antialiased selection:bg-blue-100 selection:text-blue-900">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/85 backdrop-blur-sm border-b border-slate-200">
        <div className="flex h-14 max-w-7xl mx-auto px-6 items-center justify-between">
          <div className="flex items-center gap-1 group cursor-pointer">
            <a href="/" className="flex items-center gap-2">
              <Icon icon="lucide:zap" width={20} className="text-blue-600" />
              <span className="text-sm font-medium tracking-tight text-slate-900">AI-Shark</span>
            </a>
            <span className="mx-2 text-slate-300">/</span>
            <span className="text-sm text-slate-500">New Analysis</span>
          </div>

          <div className="flex items-center gap-4">
            <button className="text-slate-500 hover:text-slate-900 transition-colors">
              <Icon icon="lucide:bell" width={18} />
            </button>
            <div className="flex text-xs font-medium text-blue-700 bg-blue-100 w-8 h-8 border-blue-200 border rounded-full items-center justify-center">
              JD
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="pt-24 max-w-3xl mx-auto px-6">
        <header className="mb-10">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900 mb-2">
            Deal Analysis Pipeline
          </h1>
          <p className="text-sm text-slate-500">
            Configure agents and simulate founder interviews to generate your investment memo.
          </p>
        </header>

        <div className="flex flex-col gap-8 relative">
          {/* PHASE 1: Pitch Deck Processing */}
          <div className="relative z-10">
            <div className="phase-connector"></div>

            <div className="flex gap-6">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ${getPhaseIndicatorClass(phases.phase1.status)}`}>
                {phases.phase1.status === 'completed' ? (
                  <Icon icon="lucide:check" width={20} />
                ) : (
                  '01'
                )}
              </div>

              <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">1. Pitch Deck Processing</h2>
                    <p className="text-xs text-slate-500 mt-0.5">Primary source of truth for the analysis.</p>
                  </div>
                  {getStatusBadge(phases.phase1.status)}
                </div>

                <div className="p-5">
                  <div className="flex items-center justify-between p-3 rounded-lg border border-slate-200 bg-white shadow-sm mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-red-50 text-red-500 flex items-center justify-center border border-red-100">
                        <Icon icon="lucide:file-text" width={20} />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-slate-900">{documents.pitchDeckPath}</div>
                        <div className="text-xs text-slate-400">4.2 MB • Processed just now</div>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 text-slate-400 hover:text-blue-600 transition-colors">
                        <Icon icon="lucide:eye" width={16} />
                      </button>
                      <button className="p-2 text-slate-400 hover:text-blue-600 transition-colors">
                        <Icon icon="lucide:download" width={16} />
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                        Company
                      </div>
                      <div className="text-xs font-semibold text-slate-700">{metadata?.company_name}</div>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                        Round
                      </div>
                      <div className="text-xs font-semibold text-slate-700">{metadata?.round}</div>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">Ask</div>
                      <div className="text-xs font-semibold text-slate-700">{metadata?.ask}</div>
                    </div>
                    <div className="p-3 bg-slate-50 rounded-lg border border-slate-100">
                      <div className="text-[10px] uppercase tracking-wider text-slate-400 font-medium mb-1">
                        Sector
                      </div>
                      <div className="text-xs font-semibold text-slate-700">{metadata?.sector}</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* PHASE 2: Additional Documents */}
          <div className="relative z-10">
            <div className="phase-connector"></div>

            <div className="flex gap-6">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass('pending')}`}>
                02
              </div>

              <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">2. Additional Documents</h2>
                    <p className="text-xs text-slate-500 mt-0.5">Financials, technical papers, or legal docs.</p>
                  </div>
                </div>

                <div className="p-5">
                  <div className="border-2 border-dashed border-slate-200 rounded-xl p-8 text-center hover:bg-slate-50 hover:border-blue-400 transition-all cursor-pointer group">
                    <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-3 group-hover:scale-110 transition-transform">
                      <Icon icon="lucide:upload-cloud" width={20} />
                    </div>
                    <p className="text-sm font-medium text-slate-900">Click to upload or drag and drop</p>
                    <p className="text-xs text-slate-500 mt-1">Supports PDF, XLSX, DOCX (Max 50MB)</p>
                  </div>

                  {documents.additionalDocs.length > 0 && (
                    <div className="mt-4 space-y-2">
                      {documents.additionalDocs.map((doc, index) => (
                        <div
                          key={index}
                          className="flex items-center justify-between p-2 rounded-lg border border-slate-100 bg-slate-50/50"
                        >
                          <div className="flex items-center gap-3">
                            <Icon icon="lucide:file-spreadsheet" className="text-emerald-600 ml-2" width={16} />
                            <span className="text-xs font-medium text-slate-600">{doc}</span>
                          </div>
                          <button
                            onClick={() => dispatch(removeDocument(doc))}
                            className="text-slate-400 hover:text-red-500 px-2"
                          >
                            <Icon icon="lucide:x" width={14} />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="mt-4 flex justify-end">
                    <button className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-lg hover:bg-slate-50 hover:border-slate-300 transition-all shadow-sm">
                      Process Documents
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* PHASE 3: Multi-Agent Analysis */}
          <div className="relative z-10">
            <div className="phase-connector"></div>

            <div className="flex gap-6">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(phases.phase3.status)}`}>
                {phases.phase3.status === 'completed' ? <Icon icon="lucide:check" width={20} /> : '03'}
              </div>

              <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">3. Multi-Agent Analysis</h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Specialized LLM agents analyze documents independently.
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    {phases.phase1.status === 'completed' ? (
                      <>
                        <span className="text-[10px] font-medium text-slate-400">Requires Step 1</span>
                        <Icon icon="lucide:check-circle-2" className="text-green-500" width={14} />
                      </>
                    ) : (
                      <span className="text-[10px] font-medium text-red-500">Locked</span>
                    )}
                  </div>
                </div>

                <div className="p-5">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
                    <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-blue-200 hover:shadow-sm transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="p-2 rounded-lg bg-blue-50 text-blue-600">
                          <Icon icon="lucide:trending-up" width={18} />
                        </div>
                        <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                      </div>
                      <h3 className="text-xs font-semibold text-slate-900">Market Agent</h3>
                      <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                        Analyzes TAM, SAM, CAGR and competitive landscape density.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-purple-200 hover:shadow-sm transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="p-2 rounded-lg bg-purple-50 text-purple-600">
                          <Icon icon="lucide:cpu" width={18} />
                        </div>
                        <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                      </div>
                      <h3 className="text-xs font-semibold text-slate-900">Technical Agent</h3>
                      <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                        Evaluates architecture stack, IP defensibility, and roadmap feasibility.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-orange-200 hover:shadow-sm transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="p-2 rounded-lg bg-orange-50 text-orange-600">
                          <Icon icon="lucide:shield-alert" width={18} />
                        </div>
                        <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                      </div>
                      <h3 className="text-xs font-semibold text-slate-900">Risk Agent</h3>
                      <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                        Identifies regulatory hurdles, execution risks, and cap table issues.
                      </p>
                    </div>

                    <div className="p-4 rounded-xl border border-slate-200 bg-white hover:border-emerald-200 hover:shadow-sm transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="p-2 rounded-lg bg-emerald-50 text-emerald-600">
                          <Icon icon="lucide:briefcase" width={18} />
                        </div>
                        <div className="w-2 h-2 rounded-full bg-slate-200"></div>
                      </div>
                      <h3 className="text-xs font-semibold text-slate-900">Business Agent</h3>
                      <p className="text-[10px] text-slate-500 mt-1 leading-relaxed">
                        Audits unit economics, GTM strategy, and financial projections.
                      </p>
                    </div>
                  </div>

                  <button
                    onClick={handleRunAnalysis}
                    disabled={phases.phase1.status !== 'completed' || phases.phase3.status === 'running'}
                    className="w-full py-2.5 bg-slate-900 hover:bg-slate-800 text-white rounded-lg text-xs font-medium transition-all flex items-center justify-center gap-2 shadow-lg shadow-slate-900/10 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {phases.phase3.status === 'running' ? (
                      <>
                        <Icon icon="lucide:loader-2" width={14} className="animate-spin" />
                        Running Analysis...
                      </>
                    ) : (
                      <>
                        <Icon icon="lucide:play" width={14} />
                        Run Multi-Agent Analysis
                      </>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* PHASE 4: Founder Simulation */}
          <div className="relative z-10">
            <div className="phase-connector"></div>

            <div className="flex gap-6">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(phases.phase4.status)}`}>
                {phases.phase4.status === 'completed' ? <Icon icon="lucide:check" width={20} /> : '04'}
              </div>

              <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">4. Founder Simulation</h2>
                    <p className="text-xs text-slate-500 mt-0.5">Simulate Q&A to answer standard DD questions.</p>
                  </div>
                  {getStatusBadge(phases.phase4.status)}
                </div>

                <div className="p-5">
                  <div className="flex bg-slate-100/50 p-1 rounded-lg border border-slate-100 mb-6 w-full sm:w-fit">
                    <label className="flex-1 sm:flex-none cursor-pointer">
                      <input
                        type="radio"
                        name="sim_mode"
                        value="context"
                        checked={simulationMode === 'context'}
                        onChange={() => dispatch(setSimulationMode('context'))}
                        className="hidden custom-radio"
                      />
                      <div className="px-4 py-1.5 rounded-md text-xs font-medium text-slate-500 transition-all flex items-center gap-2 border border-transparent">
                        <div className="w-2 h-2 rounded-full border border-slate-400 radio-dot bg-transparent"></div>
                        Context Simulation
                      </div>
                    </label>
                    <label className="flex-1 sm:flex-none cursor-pointer">
                      <input
                        type="radio"
                        name="sim_mode"
                        value="direct-qa"
                        checked={simulationMode === 'direct-qa'}
                        onChange={() => dispatch(setSimulationMode('direct-qa'))}
                        className="hidden custom-radio"
                      />
                      <div className="px-4 py-1.5 rounded-md text-xs font-medium text-slate-500 transition-all flex items-center gap-2 border border-transparent">
                        <div className="w-2 h-2 rounded-full border border-slate-400 radio-dot bg-transparent"></div>
                        Direct Q&A Upload
                      </div>
                    </label>
                  </div>

                  <div className="bg-blue-50/50 border border-blue-100 rounded-lg p-4 mb-4">
                    <div className="flex gap-3">
                      <div className="mt-0.5 text-blue-500">
                        <Icon icon="lucide:info" width={16} />
                      </div>
                      <div>
                        <h4 className="text-xs font-semibold text-blue-900">Context Mode Active</h4>
                        <p className="text-[11px] leading-relaxed text-blue-700/80 mt-1">
                          The system will use the Pitch Deck and processed documents to infer answers to a standard
                          50-question VC Due Diligence Questionnaire.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="border border-slate-200 rounded-lg p-4 bg-white mb-6">
                    <div className="flex justify-between items-center mb-3">
                      <label className="text-xs font-medium text-slate-700">
                        Upload Emails / Transcripts (Optional)
                      </label>
                      <span className="text-[10px] text-slate-400">Enriches the founder persona</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <button className="px-3 py-1.5 border border-slate-200 hover:border-blue-400 hover:text-blue-600 rounded-md text-xs text-slate-500 bg-slate-50 transition-colors flex items-center gap-2">
                        <Icon icon="lucide:plus" width={14} />
                        Add Files
                      </button>
                      <span className="text-[10px] text-slate-400 italic">No files selected</span>
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      onClick={handleGenerateSimulation}
                      disabled={phases.phase3.status !== 'completed' || phases.phase4.status === 'running'}
                      className="px-4 py-2 bg-white border border-slate-200 text-slate-700 text-xs font-medium rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {phases.phase4.status === 'running' ? (
                        <>
                          <Icon icon="lucide:loader-2" width={12} className="animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          <Icon icon="lucide:sparkles" width={12} />
                          Generate Q&A Responses
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* PHASE 5: Final Investment Memo */}
          <div className="relative z-10">
            <div className="flex gap-6">
              <div className={`flex-shrink-0 w-12 h-12 rounded-full border flex items-center justify-center font-medium text-sm z-10 shadow-sm ring-4 ring-white ${getPhaseIndicatorClass(phases.phase5.status)}`}>
                {phases.phase5.status === 'completed' ? <Icon icon="lucide:check" width={20} /> : '05'}
              </div>

              <div className="bg-white border border-slate-200 rounded-xl w-full overflow-hidden shadow-sm">
                <div className="p-5 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
                  <div>
                    <h2 className="text-sm font-semibold text-slate-900">5. Final Investment Memo</h2>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Synthesize findings and generate the final PDF/Doc.
                    </p>
                  </div>
                  {getStatusBadge(phases.phase5.status)}
                </div>

                <div className="p-6">
                  <div className="flex gap-4 mb-8 pb-6 border-b border-slate-100">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <div
                        className={`w-1.5 h-1.5 rounded-full ${
                          phases.phase3.status === 'completed' ? 'bg-green-500' : 'bg-slate-300'
                        }`}
                      ></div>
                      Analysis Phase
                    </div>
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                      <div
                        className={`w-1.5 h-1.5 rounded-full ${
                          phases.phase4.status === 'completed' ? 'bg-green-500' : 'bg-slate-300'
                        }`}
                      ></div>
                      Founder Simulation
                    </div>
                  </div>

                  <div className="mb-6">
                    <div className="flex justify-between items-end mb-4">
                      <label className="text-xs font-semibold text-slate-900 uppercase tracking-wider">
                        Analysis Weighting
                      </label>
                      <div className="flex gap-2">
                        <button
                          onClick={() => dispatch(applyWeightTemplate('balanced'))}
                          className="px-2 py-1 rounded text-[10px] font-medium bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors"
                        >
                          Balanced
                        </button>
                        <button
                          onClick={() => dispatch(applyWeightTemplate('tech-focused'))}
                          className="px-2 py-1 rounded text-[10px] font-medium border border-slate-200 text-slate-500 hover:border-blue-300 hover:text-blue-600 transition-colors"
                        >
                          Tech-Focused
                        </button>
                        <button
                          onClick={() => dispatch(applyWeightTemplate('market-focused'))}
                          className="px-2 py-1 rounded text-[10px] font-medium border border-slate-200 text-slate-500 hover:border-blue-300 hover:text-blue-600 transition-colors"
                        >
                          Market-Focused
                        </button>
                      </div>
                    </div>

                    <div className="space-y-5 bg-slate-50 p-5 rounded-xl border border-slate-100">
                      <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                        <span className="text-xs font-medium text-slate-700">Market</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={sliderValues.market.weight}
                          onChange={(e) => handleWeightChange('market', parseInt(e.target.value))}
                        />
                        <span className="text-xs font-mono text-slate-500 text-right">
                          {sliderValues.market.weight}%
                        </span>
                      </div>

                      <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                        <span className="text-xs font-medium text-slate-700">Product/Tech</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={sliderValues.tech.weight}
                          onChange={(e) => handleWeightChange('tech', parseInt(e.target.value))}
                        />
                        <span className="text-xs font-mono text-slate-500 text-right">
                          {sliderValues.tech.weight}%
                        </span>
                      </div>

                      <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                        <span className="text-xs font-medium text-slate-700">Business</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={sliderValues.business.weight}
                          onChange={(e) => handleWeightChange('business', parseInt(e.target.value))}
                        />
                        <span className="text-xs font-mono text-slate-500 text-right">
                          {sliderValues.business.weight}%
                        </span>
                      </div>

                      <div className="grid grid-cols-[100px_1fr_40px] gap-4 items-center">
                        <span className="text-xs font-medium text-slate-700">Risk</span>
                        <input
                          type="range"
                          min="0"
                          max="100"
                          value={sliderValues.risk.weight}
                          onChange={(e) => handleWeightChange('risk', parseInt(e.target.value))}
                        />
                        <span className="text-xs font-mono text-slate-500 text-right">
                          {sliderValues.risk.weight}%
                        </span>
                      </div>

                      <div className="pt-3 border-t border-slate-200 mt-2 flex justify-between items-center">
                        <button
                          onClick={autoBalanceWeights}
                          className="text-[10px] text-blue-600 font-medium hover:underline flex items-center gap-1"
                        >
                          <Icon icon="lucide:wand-2" width={12} />
                          Auto-Balance
                        </button>
                        <div className="flex items-center gap-2">
                          <span className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">
                            Total
                          </span>
                          <span
                            className={`text-xs font-bold px-2 py-0.5 rounded border shadow-sm ${
                              getTotalWeight() === 100
                                ? 'text-slate-900 bg-white border-slate-200'
                                : 'text-orange-900 bg-orange-50 border-orange-200'
                            }`}
                          >
                            {getTotalWeight()}%
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center justify-between mt-8 pt-6 border-t border-slate-100">
                    <div className="flex items-center gap-2">
                      <div className="h-8 w-8 rounded-lg border border-slate-200 flex items-center justify-center text-slate-400 bg-slate-50">
                        <Icon icon="lucide:file-text" width={16} />
                      </div>
                      <div className="flex flex-col">
                        <span className="text-[10px] font-medium text-slate-500 uppercase">Output Format</span>
                        <span className="text-xs font-medium text-slate-900">PDF & Markdown</span>
                      </div>
                    </div>
                    <button
                      onClick={handleGenerateMemo}
                      disabled={
                        phases.phase3.status !== 'completed' ||
                        getTotalWeight() !== 100 ||
                        phases.phase5.status === 'running'
                      }
                      className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-full text-sm font-medium transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {phases.phase5.status === 'running' ? (
                        <>
                          <Icon icon="lucide:loader-2" width={16} className="animate-spin" />
                          Generating...
                        </>
                      ) : (
                        <>
                          Generate Final Memo
                          <Icon icon="lucide:arrow-right" width={16} />
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-20 border-t border-slate-200 py-8 bg-white">
        <div className="max-w-7xl mx-auto px-6 flex justify-between items-center text-xs text-slate-400">
          <div>© 2024 AI-Shark Inc.</div>
          <div className="flex gap-4">
            <a href="#" className="hover:text-slate-600">
              Privacy
            </a>
            <a href="#" className="hover:text-slate-600">
              Help Center
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};
