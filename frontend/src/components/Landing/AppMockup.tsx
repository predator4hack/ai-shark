import { Icon } from '@iconify/react';

const AppMockup = () => {
  return (
    <div className="mt-20 max-w-6xl mx-auto px-4 md:px-8">
      <div className="relative rounded-t-3xl border backdrop-blur-xl p-2 md:p-4 ui-shadow overflow-hidden border-slate-200 bg-white/50">
        {/* Window Controls */}
        <div className="absolute top-4 left-6 flex gap-2">
          <div className="w-3 h-3 rounded-full bg-slate-200"></div>
          <div className="w-3 h-3 rounded-full bg-slate-200"></div>
          <div className="w-3 h-3 rounded-full bg-slate-200"></div>
        </div>

        {/* Main App Interface */}
        <div className="mt-8 rounded-xl border overflow-hidden flex flex-col md:flex-row h-[500px] md:h-[600px] bg-white border-slate-100">
          {/* Sidebar */}
          <div className="w-full md:w-64 border-r p-4 flex-col gap-6 hidden md:flex bg-slate-50 border-slate-100">
            <div className="flex flex-col gap-1">
              <div className="text-[10px] font-semibold uppercase tracking-widest mb-2 text-slate-400">
                Analysis
              </div>
              <div className="flex items-center gap-3 px-3 py-2 rounded-lg border shadow-sm bg-white border-slate-200">
                <Icon icon="lucide:file-text" className="text-blue-600" width="16" />
                <span className="text-xs font-medium text-slate-800">Current Memo</span>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-slate-500 transition-colors hover:text-slate-900">
                <Icon icon="lucide:layers" width="16" />
                <span className="text-xs font-medium">Documents</span>
              </div>
              <div className="flex items-center gap-3 px-3 py-2 text-slate-500 transition-colors hover:text-slate-900">
                <Icon icon="lucide:messages-square" width="16" />
                <span className="text-xs font-medium">Founder Q&A</span>
              </div>
            </div>

            <div className="flex flex-col gap-1">
              <div className="text-[10px] font-semibold uppercase tracking-widest mb-2 text-slate-400">
                Recent Decks
              </div>
              <div className="flex items-center justify-between px-3 py-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500"></div>
                  <span className="text-xs font-medium text-slate-600">Nebula_Seed.pdf</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">Done</span>
              </div>
              <div className="flex items-center justify-between px-3 py-2">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
                  <span className="text-xs font-medium text-slate-600">FlowStack_A.pptx</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400">45%</span>
              </div>
            </div>
          </div>

          {/* Dashboard Content */}
          <div className="flex-1 md:p-8 overflow-y-auto pt-6 px-6 pb-6">
            <div className="flex justify-between items-end mb-8">
              <div>
                <h2 className="text-xl font-semibold tracking-tight text-slate-900">
                  Investment Memo Generation
                </h2>
                <p className="text-xs text-slate-500 mt-1">
                  Multi-agent synthesis for Nebula Robotics Series A.
                </p>
              </div>
              <div className="flex gap-2">
                <button className="p-2 rounded-lg border text-slate-500 border-slate-200 hover:bg-slate-50 flex items-center gap-2 px-3">
                  <span className="text-xs font-medium">Export PDF</span>
                  <Icon icon="lucide:download" width="14" />
                </button>
              </div>
            </div>

            {/* Grid Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
              <div className="p-4 rounded-xl border shadow-sm hover:shadow-md transition-shadow border-slate-100 bg-white">
                <div className="flex justify-between items-start mb-2">
                  <div className="p-2 rounded-md bg-blue-50 text-blue-600">
                    <Icon icon="lucide:brain-circuit" width="18" />
                  </div>
                  <span className="text-xs font-medium px-2 py-0.5 rounded-full text-blue-600 bg-blue-50">
                    Tech-Focused
                  </span>
                </div>
                <div className="text-2xl font-semibold tracking-tight text-slate-900">92/100</div>
                <div className="text-xs mt-1 text-slate-400">Weighted Score</div>
              </div>
              <div className="p-4 rounded-xl border shadow-sm hover:shadow-md transition-shadow border-slate-100 bg-white">
                <div className="flex justify-between items-start mb-2">
                  <div className="p-2 rounded-md bg-purple-50 text-purple-600">
                    <Icon icon="lucide:files" width="18" />
                  </div>
                </div>
                <div className="text-2xl font-semibold tracking-tight text-slate-900">14</div>
                <div className="text-xs mt-1 text-slate-400">Sources Processed</div>
              </div>
              <div className="p-4 rounded-xl border shadow-sm hover:shadow-md transition-shadow border-slate-100 bg-white">
                <div className="flex justify-between items-start mb-2">
                  <div className="p-2 rounded-md bg-orange-50 text-orange-600">
                    <Icon icon="lucide:flag" width="18" />
                  </div>
                </div>
                <div className="text-2xl font-semibold tracking-tight text-slate-900">3</div>
                <div className="text-xs mt-1 text-slate-400">Major Risk Factors</div>
              </div>
            </div>

            {/* Agent Analysis View */}
            <div className="flex flex-col overflow-hidden bg-white h-full border-slate-100 border rounded-xl shadow-sm">
              <div className="pt-6 px-6 pb-6">
                <div className="flex items-center justify-between mb-8">
                  <div>
                    <h3 className="text-sm font-semibold text-slate-900">
                      Agent Analysis Breakdown
                    </h3>
                    <p className="text-xs text-slate-500 mt-1">
                      Multi-dimensional scoring assessment
                    </p>
                  </div>
                  <div className="flex gap-2 text-[10px] font-medium uppercase tracking-wider">
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-emerald-50 text-emerald-700 border border-emerald-100/50">
                      <div className="w-1.5 h-1.5 rounded-full bg-emerald-500"></div> Strong
                    </div>
                    <div className="flex items-center gap-1.5 px-2 py-1 rounded-md bg-yellow-50 text-yellow-700 border border-yellow-100/50">
                      <div className="w-1.5 h-1.5 rounded-full bg-yellow-500"></div> Neutral
                    </div>
                  </div>
                </div>

                {/* Vertical Bars Chart */}
                <div className="flex gap-3 h-48 px-2 items-end justify-between">
                  {/* Business Agent */}
                  <AgentBar
                    label="Business"
                    percentage={88}
                    tooltip="Model & Revenue"
                    icon="lucide:briefcase"
                    color="emerald"
                  />

                  {/* Market Agent */}
                  <AgentBar
                    label="Market"
                    percentage={76}
                    tooltip="TAM & Comp"
                    icon="lucide:target"
                    color="yellow"
                  />

                  {/* Technical Agent */}
                  <AgentBar
                    label="Tech"
                    percentage={95}
                    tooltip="IP & Stack"
                    icon="lucide:cpu"
                    color="emerald"
                  />

                  {/* Risk Agent */}
                  <AgentBar
                    label="Risk"
                    percentage={92}
                    tooltip="Regulatory"
                    icon="lucide:shield-check"
                    color="emerald"
                  />
                </div>
              </div>

              {/* Insight Footer */}
              <div className="bg-slate-50/50 border-t border-slate-100 p-5 mt-auto backdrop-blur-sm">
                <div className="flex gap-3 items-start">
                  <div className="shrink-0 mt-0.5 p-1 rounded-md bg-blue-50 text-blue-600 border border-blue-100">
                    <Icon icon="lucide:sparkles" width="12" />
                  </div>
                  <div>
                    <p className="text-[10px] font-bold uppercase tracking-wider text-slate-400 mb-1">
                      Generated Insight
                    </p>
                    <p className="text-xs leading-relaxed text-slate-600 font-medium">
                      "While the <span className="text-slate-900">technical stack</span> and IP
                      portfolio are exceptionally strong, the Go-to-Market strategy relies heavily on
                      enterprise partnerships that have yet to materialize in signed LOIs."
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

interface AgentBarProps {
  label: string;
  percentage: number;
  tooltip: string;
  icon: string;
  color: 'emerald' | 'yellow';
}

const AgentBar = ({ label, percentage, tooltip, icon, color }: AgentBarProps) => {
  const colorClasses = {
    emerald: {
      bar: 'bg-emerald-500 group-hover:bg-emerald-400',
      ring: 'ring-slate-100 group-hover:ring-emerald-100',
      icon: 'group-hover:text-emerald-600 group-hover:bg-emerald-50',
      text: 'group-hover:text-emerald-600',
    },
    yellow: {
      bar: 'bg-yellow-500 group-hover:bg-yellow-400',
      ring: 'ring-slate-100 group-hover:ring-yellow-100',
      icon: 'group-hover:text-yellow-600 group-hover:bg-yellow-50',
      text: 'group-hover:text-yellow-600',
    },
  };

  const classes = colorClasses[color];

  return (
    <div className="flex flex-col items-center gap-3 w-full group cursor-default">
      <div className="opacity-0 translate-y-2 group-hover:opacity-100 group-hover:translate-y-0 transition-all duration-300 absolute -mt-8 bg-slate-900 text-white text-[10px] font-medium px-2 py-1 rounded">
        {tooltip}
      </div>
      <span className={`text-xs font-bold text-slate-700 transition-colors ${classes.text}`}>
        {percentage}%
      </span>
      <div
        className={`w-full max-w-[56px] h-full bg-slate-50 rounded-lg relative overflow-hidden ring-1 ${classes.ring} transition-all`}
      >
        <div
          className={`absolute bottom-0 w-full ${classes.bar} rounded-b-lg rounded-t-sm transition-all duration-700 ease-out`}
          style={{ height: `${percentage}%` }}
        >
          <div className="absolute inset-0 bg-gradient-to-t from-black/10 to-transparent opacity-50"></div>
          <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNCIgaGVpZ2h0PSI0IiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciPjxjaXJjbGUgY3g9IjIiIGN5PSIyIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwgMjU1LCAyNTUsIDAuMikiLz48L3N2Zz4=')] opacity-20"></div>
        </div>
      </div>
      <div className="flex flex-col items-center gap-1.5 mt-1">
        <div
          className={`p-1.5 rounded-md bg-slate-50 text-slate-400 ${classes.icon} transition-colors duration-300`}
        >
          <Icon icon={icon} width="14" />
        </div>
        <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wide group-hover:text-slate-900 transition-colors">
          {label}
        </span>
      </div>
    </div>
  );
};

export default AppMockup;
