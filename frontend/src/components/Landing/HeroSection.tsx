import { Icon } from '@iconify/react';
import { useNavigate } from 'react-router-dom';
import AppMockup from './AppMockup';

const HeroSection = () => {
  const navigate = useNavigate();

  const handleStartAnalysis = () => {
    navigate('/upload');
  };

  return (
    <section className="overflow-hidden hero-gradient pt-32 pb-20 relative">
      <div className="text-center max-w-4xl z-10 mx-auto px-6 relative">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full border mb-6 animate-fade-in-up bg-slate-100/80 border-slate-200">
          <span className="flex h-2 w-2 rounded-full bg-blue-500"></span>
          <span className="text-xs font-medium text-slate-600">
            Multi-Agent Memo Generation v1.0
          </span>
        </div>

        <h1 className="md:text-7xl leading-[1.1] text-5xl font-semibold text-slate-900 tracking-tighter mb-6">
          Automate your
          <br />
          <span className="text-slate-400">investment memos.</span>
        </h1>

        <p className="md:text-xl leading-relaxed text-lg font-light text-slate-500 max-w-2xl mx-auto mb-10">
          AI-Shark transforms 15-30 hours of manual diligence into structured analysis. Process
          pitch decks, simulate founder Q&A, and generate comprehensive memos instantly.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 items-center justify-center">
          <button
            onClick={handleStartAnalysis}
            className="h-12 px-8 rounded-full text-sm font-medium transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2 bg-blue-600 text-white hover:bg-blue-700"
          >
            Start Analysis
            <Icon icon="lucide:arrow-right" width="16" />
          </button>
        </div>
      </div>

      {/* App UI Mockup */}
      <AppMockup />
    </section>
  );
};

export default HeroSection;
