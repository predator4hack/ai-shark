import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Provider } from 'react-redux';

import { store } from './store';
import { PitchDeckPage } from './pages/PitchDeckPage';
import { NotFoundPage } from './pages/NotFoundPage';
import { AnalysisPage } from './pages/AnalysisPage';
import LandingPage from './pages/LandingPage';

function App() {
  return (
    <Provider store={store}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/upload" element={<PitchDeckPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </Provider>
  );
}

export default App;
