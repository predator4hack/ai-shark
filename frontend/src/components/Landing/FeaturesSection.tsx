import { Icon } from '@iconify/react';

const FeaturesSection = () => {
  return (
    <section className="bg-slate-50 pt-24 pb-24">
      <div className="max-w-7xl mx-auto px-6">
        <div className="mb-16 text-center">
          <h2 className="text-3xl md:text-5xl font-semibold tracking-tighter mb-4 text-slate-900">
            The 30-hour workflow,
            <br />
            <span className="text-slate-400">automated.</span>
          </h2>
          <p className="text-slate-500 max-w-xl mx-auto">
            Our multi-agent system reads, reasons, and writes like a senior analyst, but at machine
            speed.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 auto-rows-[400px]">
          {/* Card 1: Large Span - Multi-Agent Architecture */}
          <div className="md:col-span-2 rounded-[32px] p-8 md:p-12 relative overflow-hidden group shadow-sm hover:shadow-xl transition-all duration-500 border bg-white border-slate-100">
            <div className="relative z-10 max-w-md">
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center mb-6 bg-blue-50 text-blue-600">
                <Icon icon="lucide:bot" width="24" />
              </div>
              <h3 className="text-2xl font-semibold tracking-tight mb-3 text-slate-900">
                Multi-Agent Architecture
              </h3>
              <p className="text-slate-500 leading-relaxed">
                We deploy specialized agents for every dimension of the deal. The{' '}
                <strong>Market Agent</strong> validates TAM/SAM, the <strong>Technical Agent</strong>{' '}
                audits the stack, and the <strong>Risk Agent</strong> stress-tests assumptions—all in
                parallel.
              </p>
            </div>
            <div className="absolute right-0 bottom-0 w-1/2 h-full opacity-50 group-hover:opacity-100 transition-opacity duration-700">
              <div className="absolute bottom-12 right-12 w-64 h-64 bg-gradient-to-tr rounded-full blur-3xl from-blue-100 to-indigo-100"></div>
              <div className="absolute bottom-16 right-16 w-32 h-32 bg-gradient-to-tr rounded-full blur-2xl from-purple-100 to-white"></div>
            </div>
          </div>

          {/* Card 2: Vertical - Founder Simulation */}
          <div className="rounded-[32px] p-8 md:p-12 relative overflow-hidden shadow-2xl flex flex-col justify-between bg-black text-white">
            <div>
              <Icon icon="lucide:message-circle" width="24" className="mb-6 text-white/50" />
              <h3 className="text-2xl font-semibold tracking-tight mb-3">Founder Simulation</h3>
              <p className="text-sm leading-relaxed text-white/60">
                Don't wait for a call. AI-Shark simulates founder responses to standard due
                diligence questionnaires using uploaded data context.
              </p>
            </div>

            <div className="mt-8 backdrop-blur-md rounded-xl p-4 border bg-white/10 border-white/10">
              <div className="flex gap-3 mb-3">
                <div className="w-6 h-6 shrink-0 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                  <Icon icon="lucide:help-circle" width="12" />
                </div>
                <span className="text-xs text-white/80">"How does your CAC scale?"</span>
              </div>
              <div className="flex gap-3">
                <div className="w-6 h-6 shrink-0 rounded-full bg-green-500/20 flex items-center justify-center text-green-400">
                  <Icon icon="lucide:bot" width="12" />
                </div>
                <span className="text-xs text-white/60">
                  "Based on our Series A deck, CAC reduces by 20% via network effects..."
                </span>
              </div>
            </div>
          </div>

          {/* Card 3: Contextual Parsing */}
          <div className="rounded-[32px] p-8 md:p-12 relative overflow-hidden shadow-sm hover:shadow-xl transition-all duration-500 border flex flex-col bg-white border-slate-100">
            <h3 className="text-2xl font-semibold tracking-tight mb-3 text-slate-900">
              Contextual Parsing
            </h3>
            <p className="text-slate-500 text-sm mb-8">
              We handle PDFs, PPTX, transcripts, and emails to build a complete graph of the
              company.
            </p>

            <div className="mt-auto relative h-40 w-full">
              <div className="absolute inset-x-4 bottom-4 rounded-xl shadow-lg border p-4 flex items-center gap-4 bg-white border-slate-100">
                <div className="w-10 h-10 rounded-lg flex items-center justify-center bg-red-50 text-red-500">
                  <Icon icon="lucide:file-type" width="20" />
                </div>
                <div className="flex-1">
                  <div className="h-2 w-2/3 rounded-full mb-2 bg-slate-200"></div>
                  <div className="text-[10px] text-slate-400">Metadata Extracted</div>
                </div>
                <div className="w-6 h-6 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                  <Icon icon="lucide:check" width="12" />
                </div>
              </div>
              <div className="absolute inset-x-8 bottom-0 translate-y-2 scale-95 rounded-xl shadow border p-4 opacity-50 -z-10 bg-white border-slate-100"></div>
            </div>
          </div>

          {/* Card 4: Large Span Gradient - Investment Memo Export */}
          <div className="md:col-span-2 bg-gradient-to-br rounded-[32px] p-8 md:p-12 relative overflow-hidden shadow-xl from-blue-600 to-indigo-700 text-white">
            <div className="relative z-10 grid grid-cols-1 md:grid-cols-2 gap-8 items-center h-full">
              <div>
                <h3 className="text-2xl font-semibold tracking-tight mb-3">
                  Investment Memo Export
                </h3>
                <p className="leading-relaxed text-blue-100">
                  Configurable templates allow you to weight analysis towards "Market-Focused",
                  "Tech-Focused", or "Balanced" perspectives before exporting to DOCX or Markdown.
                </p>
                <div className="flex gap-2 mt-6">
                  <span className="px-3 py-1 rounded-full text-xs bg-white/20 border border-white/20">
                    DOCX
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs bg-white/20 border border-white/20">
                    PDF
                  </span>
                  <span className="px-3 py-1 rounded-full text-xs bg-white/20 border border-white/20">
                    Markdown
                  </span>
                </div>
              </div>
              <div className="relative h-full min-h-[200px] flex items-center justify-center">
                <div className="w-40 h-52 bg-white rounded-lg shadow-2xl rotate-3 transform transition-transform hover:rotate-6 flex flex-col p-4">
                  <div className="w-1/2 h-2 bg-slate-200 rounded mb-4"></div>
                  <div className="w-full h-1 bg-slate-100 rounded mb-2"></div>
                  <div className="w-full h-1 bg-slate-100 rounded mb-2"></div>
                  <div className="w-3/4 h-1 bg-slate-100 rounded mb-6"></div>
                  <div className="w-full h-20 bg-blue-50 rounded mb-2 border border-blue-100"></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default FeaturesSection;
