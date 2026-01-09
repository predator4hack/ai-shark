import { Icon } from '@iconify/react';

const PipelineSection = () => {
  return (
    <section className="overflow-hidden text-white bg-[#050505] pt-32 pb-32 relative">
      <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent to-transparent via-white/20"></div>

      <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
        <div>
          <div className="text-blue-500 font-mono text-xs mb-6 tracking-widest uppercase">
            The Pipeline
          </div>
          <h2 className="text-4xl md:text-6xl font-semibold tracking-tighter mb-6 leading-tight">
            From raw upload to
            <span className="text-white/40"> final verdict.</span>
          </h2>
          <p className="text-lg mb-8 font-light max-w-md text-white/60">
            A sophisticated multi-phase pipeline that ensures no detail in the data room goes
            unnoticed.
          </p>

          <ul className="space-y-8 relative">
            {/* Line connecting dots */}
            <div className="absolute top-2 bottom-2 left-2 w-px bg-white/10"></div>

            <li className="flex items-start gap-6 relative">
              <div className="mt-1 w-4 h-4 rounded-full bg-blue-600 border-4 border-[#050505] relative z-10 shrink-0"></div>
              <div>
                <h4 className="text-sm font-medium text-white">1. Deck Ingestion</h4>
                <p className="text-xs mt-1 text-white/50">
                  OCR and extraction from PDF/PPTX, creating structured context.
                </p>
              </div>
            </li>
            <li className="flex items-start gap-6 relative">
              <div className="mt-1 w-4 h-4 rounded-full bg-slate-700 border-4 border-[#050505] relative z-10 shrink-0"></div>
              <div>
                <h4 className="text-sm font-medium text-white">2. Multi-Agent Reasoning</h4>
                <p className="text-xs mt-1 text-white/50">
                  Business, Market, Tech, and Risk agents analyze independently.
                </p>
              </div>
            </li>
            <li className="flex items-start gap-6 relative">
              <div className="mt-1 w-4 h-4 rounded-full bg-slate-700 border-4 border-[#050505] relative z-10 shrink-0"></div>
              <div>
                <h4 className="text-sm font-medium text-white">3. Synthesis & Scoring</h4>
                <p className="text-xs mt-1 text-white/50">
                  Aggregating findings into a cohesive narrative with weighted scoring.
                </p>
              </div>
            </li>
          </ul>
        </div>

        {/* Visualization abstraction */}
        <div className="relative">
          <div className="absolute -inset-4 bg-blue-500/20 blur-3xl rounded-full"></div>
          <div className="relative rounded-2xl border p-1 backdrop-blur-sm bg-white/5 border-white/10">
            <div className="rounded-xl overflow-hidden relative h-[400px] flex items-center justify-center bg-black">
              {/* Grid lines */}
              <div
                className="absolute inset-0"
                style={{
                  backgroundImage:
                    'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)',
                  backgroundSize: '40px 40px',
                }}
              ></div>

              {/* Center Hub */}
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-16 h-16 rounded-full border border-blue-500/50 flex items-center justify-center bg-blue-500/10 z-20 shadow-[0_0_30px_rgba(59,130,246,0.3)]">
                <Icon icon="lucide:cpu" className="text-blue-500" />
              </div>

              {/* Orbiting Nodes */}
              <div className="absolute top-1/4 left-1/4 p-2 rounded border border-white/10 bg-white/5 text-[10px] text-white/70">
                Risk Agent
              </div>
              <div className="absolute bottom-1/4 right-1/4 p-2 rounded border border-white/10 bg-white/5 text-[10px] text-white/70">
                Market Agent
              </div>
              <div className="absolute top-1/4 right-1/4 p-2 rounded border border-white/10 bg-white/5 text-[10px] text-white/70">
                Tech Agent
              </div>

              {/* Connecting lines (SVG) */}
              <svg className="absolute inset-0 w-full h-full pointer-events-none">
                <line
                  x1="50%"
                  y1="50%"
                  x2="25%"
                  y2="25%"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="1"
                ></line>
                <line
                  x1="50%"
                  y1="50%"
                  x2="75%"
                  y2="75%"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="1"
                ></line>
                <line
                  x1="50%"
                  y1="50%"
                  x2="75%"
                  y2="25%"
                  stroke="rgba(255,255,255,0.1)"
                  strokeWidth="1"
                ></line>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default PipelineSection;
