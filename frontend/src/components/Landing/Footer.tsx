import { Icon } from '@iconify/react';

const Footer = () => {
  return (
    <footer className="bg-slate-50 border-slate-200 border-t pt-20 pb-12">
      <div className="max-w-7xl mx-auto px-6">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-10 mb-16">
          <div className="col-span-2">
            <div className="flex items-center gap-1 mb-6">
              <Icon icon="lucide:zap" width="20" className="text-slate-900" />
              <span className="text-sm font-medium tracking-tight">AI-Shark</span>
            </div>
            <p className="text-sm text-slate-500 max-w-xs leading-relaxed">
              Intelligent document analysis for the modern venture capital firm.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-4 text-slate-900">
              Product
            </h4>
            <ul className="space-y-3 text-sm text-slate-500">
              <li>
                <a href="#" className="hover:text-slate-900">
                  Agents
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-slate-900">
                  Workflow
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-slate-900">
                  Security
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-4 text-slate-900">
              Company
            </h4>
            <ul className="space-y-3 text-sm text-slate-500">
              <li>
                <a href="#" className="hover:text-slate-900">
                  About
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-slate-900">
                  Blog
                </a>
              </li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-semibold uppercase tracking-wider mb-4 text-slate-900">
              Legal
            </h4>
            <ul className="space-y-3 text-sm text-slate-500">
              <li>
                <a href="#" className="hover:text-slate-900">
                  Privacy
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-slate-900">
                  Terms
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t text-xs border-slate-200 text-slate-400">
          <div>© 2024 AI-Shark Inc. All rights reserved.</div>
          <div className="flex gap-6 mt-4 md:mt-0">
            <a href="#" className="hover:text-slate-900">
              <Icon icon="lucide:twitter" width="16" />
            </a>
            <a href="#" className="hover:text-slate-900">
              <Icon icon="lucide:linkedin" width="16" />
            </a>
            <a href="#" className="hover:text-slate-900">
              <Icon icon="lucide:github" width="16" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
