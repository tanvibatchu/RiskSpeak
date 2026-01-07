import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Home from './pages/home';
import Portfolio from './pages/portfolio';
import Analysis from './pages/analysis';
import Brokers from './pages/brokers';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-white shadow-sm border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <a href="/" className="text-2xl font-bold text-black">
                Risk<span className="text-blue-600">Speak</span>
              </a>
              <div className="flex gap-6">
                <a href="/" className="text-gray-600 hover:text-gray-900">
                  Home
                </a>
                <a href="/portfolio" className="text-gray-600 hover:text-gray-900">
                  Portfolios
                </a>
                <a href="/brokers" className="text-gray-600 hover:text-gray-900">
                  Brokers
                </a>
              </div>
            </div>
          </div>
        </nav>

        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/portfolio" element={<Portfolio />} />
          <Route path="/analysis/:portfolioId" element={<Analysis />} />
          <Route path="/brokers" element={<Brokers />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;