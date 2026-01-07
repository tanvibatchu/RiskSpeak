import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { listPortfolios, deletePortfolio, calculateAnalysis } from '../services/api';
import { TrendingUp, Trash2, BarChart3, Loader } from 'lucide-react';

export default function Portfolio() {
    const [portfolios, setPortfolios] = useState([]);
    const [loading, setLoading] = useState(true);
    const [analyzing, setAnalyzing] = useState(null);
    const navigate = useNavigate();
    const location = useLocation();
    
    useEffect(() => {
        loadPortfolios();
    }, []);
    const loadPortfolios = async () => {
        try {
            const data = await listPortfolios();
            setPortfolios(data.portfolios);
        } catch (err) {
            console.error('Failed to load portfolios:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (portfolioId) => {
        if (!confirm('Are you sure you want to delete this portfolio?')) return;

        try {
        await deletePortfolio(portfolioId);
        setPortfolios(portfolios.filter(p => p.portfolio_id !== portfolioId));
        } catch (err) {
        alert('Failed to delete portfolio');
        }
    };

    const handleAnalyze = async (portfolioId) => {
        setAnalyzing(portfolioId);
        try {
        const result = await calculateAnalysis(portfolioId, true);
        navigate(`/analysis/${portfolioId}`, { 
            state: { analysisData: result.analysis } 
        });
        } catch (err) {
        alert('Failed to analyze portfolio: ' + (err.response?.data?.detail || err.message));
        } finally {
        setAnalyzing(null);
        }
    };

    if (loading) {
        return (
        <div className="flex items-center justify-center min-h-screen">
            <Loader className="h-8 w-8 animate-spin text-blue-600" />
        </div>
        );
    }

    return (
        <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">My Portfolios</h1>
            <p className="text-gray-600">Manage and analyze your investment portfolios</p>
        </div>

        {portfolios.length === 0 ? (
            <div className="text-center py-16">
            <TrendingUp className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No portfolios yet
            </h3>
            <p className="text-gray-600 mb-6">
                Create your first portfolio to get started
            </p>
            <button
                onClick={() => navigate('/')}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
            >
                Create Portfolio
            </button>
            </div>
        ) : (
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {portfolios.map((portfolio) => (
                <div
                key={portfolio.portfolio_id}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition p-6"
                >
                <div className="flex justify-between items-start mb-4">
                    <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-1">
                        {portfolio.name}
                    </h3>
                    <p className="text-sm text-gray-500">
                        {portfolio.holdings_count} holdings
                    </p>
                    </div>
                    <button
                    onClick={() => handleDelete(portfolio.portfolio_id)}
                    className="text-red-600 hover:text-red-700 p-2 hover:bg-red-50 rounded"
                    >
                    <Trash2 className="h-5 w-5" />
                    </button>
                </div>

                <div className="mb-4">
                    <span className="inline-block px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
                    {portfolio.source}
                    </span>
                </div>

                <button
                    onClick={() => handleAnalyze(portfolio.portfolio_id)}
                    disabled={analyzing === portfolio.portfolio_id}
                    className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 flex items-center justify-center gap-2"
                >
                    {analyzing === portfolio.portfolio_id ? (
                    <>
                        <Loader className="h-4 w-4 animate-spin" />
                        Analyzing...
                    </>
                    ) : (
                    <>
                        <BarChart3 className="h-4 w-4" />
                        Analyze Risk
                    </>
                    )}
                </button>
                </div>
            ))}
            </div>
        )}
        </div>
    );
    }