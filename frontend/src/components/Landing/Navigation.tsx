import { Icon } from '@iconify/react';
import { useNavigate } from 'react-router-dom';

const Navigation = () => {
  const navigate = useNavigate();

  const handleUploadClick = () => {
    navigate('/upload');
  };

  const handleContactClick = (e: React.MouseEvent<HTMLAnchorElement>) => {
    e.preventDefault();
    const contactSection = document.getElementById('contact');
    if (contactSection) {
      contactSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <nav className="fixed top-0 w-full z-50 glass-nav border-b border-white/20">
      <div className="flex h-14 max-w-7xl mx-auto px-6 items-center justify-between">
        <div className="flex items-center gap-1 group cursor-pointer">
          <Icon
            icon="lucide:zap"
            width="20"
            className="group-hover:text-blue-600 transition-colors text-slate-900"
          />
          <span className="text-sm font-medium tracking-tight">AI-Shark</span>
        </div>

        <div className="hidden md:flex items-center gap-8 text-xs font-normal text-slate-500">
          <a href="#" className="transition-colors hover:text-slate-900">
            Platform
          </a>
          <a href="#" className="transition-colors hover:text-slate-900">
            Agents
          </a>
          <a
            href="#contact"
            onClick={handleContactClick}
            className="transition-colors hover:text-slate-900"
          >
            Contact
          </a>
        </div>

        <button
          onClick={handleUploadClick}
          className="transition-all hover:scale-105 hover:bg-slate-800 text-xs font-medium text-white bg-slate-900 rounded-full pt-1.5 px-4 pb-1.5"
        >
          Upload Deck
        </button>
      </div>
    </nav>
  );
};

export default Navigation;
