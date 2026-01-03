import Navigation from '../components/Landing/Navigation';
import HeroSection from '../components/Landing/HeroSection';
import FeaturesSection from '../components/Landing/FeaturesSection';
import PipelineSection from '../components/Landing/PipelineSection';
import ContactSection from '../components/Landing/ContactSection';
import Footer from '../components/Landing/Footer';

const LandingPage = () => {
  return (
    <div className="antialiased selection:bg-blue-100 selection:text-blue-900 text-slate-900">
      <Navigation />
      <HeroSection />
      <FeaturesSection />
      <PipelineSection />
      <ContactSection />
      <Footer />
    </div>
  );
};

export default LandingPage;
