import { useState, useEffect, useCallback } from 'react';
import { useParams, useLocation, useNavigate } from 'react-router-dom';
import { getAnalysis, getPortfolioNews } from '../services/api';
import { 
    TrendingUp, TrendingDown, AlertTriangle, CheckCircle, 
    DollarSign, Activity, PieChart, Loader, ArrowLeft, 
    RefreshCw, ExternalLink, Newspaper, ChevronLeft, ChevronRight, X
} from 'lucide-react';
import { PieChart as RechartsPie, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899'];

export default function Analysis() {
    const { portfolioId } = useParams();
    const location = useLocation();
    const navigate = useNavigate();
    const [analysis, setAnalysis] = useState(location.state?.analysisData || null);
    const [loading, setLoading] = useState(!location.state?.analysisData);
    const [newsArticles, setNewsArticles] = useState([]);
    const [loadingNews, setLoadingNews] = useState(false);
    const [currentPage, setCurrentPage] = useState(1);
    const [selectedTicker, setSelectedTicker] = useState('');
    const [tickerSearchValue, setTickerSearchValue] = useState('');
    const [showTickerDropdown, setShowTickerDropdown] = useState(false);
    const ARTICLES_PER_PAGE = 10;

    const loadNews = async () => {
        if (!portfolioId) return;
        setLoadingNews(true);
        try {
            const data = await getPortfolioNews(portfolioId, selectedTicker || null, 100);
            setNewsArticles(data.articles || []);
        } catch (err) {
            console.error('Failed to load news:', err);
            setNewsArticles([]);
        } finally {
            setLoadingNews(false);
        }
    };

    const loadNews = useCallback(async () => {
        if (!portfolioId) return;
        setLoadingNews(true);
        try {
            const data = await getPortfolioNews(portfolioId, selectedTicker || null, 100);
            setNewsArticles(data.articles || []);
        } catch (err) {
            console.error('Failed to load news:', err);
            setNewsArticles([]);
        } finally {
            setLoadingNews(false);
        }
    }, [portfolioId, selectedTicker]);

    useEffect(() => {
        if (!analysis) {
        // If no analysis data passed, would need analysisId to fetch
        // For now, redirect back
        navigate('/portfolio');
        } else if (portfolioId) {
            loadNews();
        }
    }, [portfolioId, analysis, navigate, loadNews]);

    useEffect(() => {
        // Reset to page 1 when ticker filter changes
        if (portfolioId) {
            setCurrentPage(1);
            loadNews();
        }
    }, [selectedTicker, portfolioId, loadNews]);

    // Get unique tickers from portfolio stocks
    const getPortfolioTickers = () => {
        if (!analysis || !analysis.stocks) return [];
        return [...new Set(analysis.stocks.map(stock => stock.info.ticker))].sort();
    };

    // Get filtered and paginated articles
    const getPaginatedArticles = () => {
        const startIndex = (currentPage - 1) * ARTICLES_PER_PAGE;
        const endIndex = startIndex + ARTICLES_PER_PAGE;
        return newsArticles.slice(startIndex, endIndex);
    };

    const totalPages = Math.ceil(newsArticles.length / ARTICLES_PER_PAGE);
    const paginatedArticles = getPaginatedArticles();
    const portfolioTickers = getPortfolioTickers();

    // Filter tickers based on search
    const filteredTickers = portfolioTickers.filter(ticker =>
        ticker.toLowerCase().includes(tickerSearchValue.toLowerCase())
    );

    const handleTickerSelect = (ticker) => {
        setSelectedTicker(ticker);
        setTickerSearchValue('');
        setShowTickerDropdown(false);
    };

    const handleClearTicker = () => {
        setSelectedTicker('');
        setTickerSearchValue('');
        setShowTickerDropdown(false);
        setCurrentPage(1);
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event) => {
            if (showTickerDropdown && !event.target.closest('.ticker-dropdown-container')) {
                setShowTickerDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, [showTickerDropdown]);

    const formatDate = (dateString) => {
        if (!dateString) return '';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', { 
                year: 'numeric', 
                month: 'short', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        } catch {
            return dateString;
        }
    };

    const getSentimentColor = (sentiment) => {
        switch (sentiment) {
            case 'positive':
                return 'text-green-600 bg-green-50';
            case 'negative':
                return 'text-red-600 bg-red-50';
            default:
                return 'text-gray-600 bg-gray-50';
        }
    };

    if (loading || !analysis) {
        return (
        <div className="flex items-center justify-center min-h-screen">
            <Loader className="h-8 w-8 animate-spin text-blue-600" />
        </div>
        );
    }

    const { portfolio_metrics, stocks, sector_allocation, concerns, news_sentiment } = analysis;

    // Prepare sector data for pie chart
    const sectorData = sector_allocation.map(s => ({
        name: s.sector,
        value: s.allocation_pct
    }));

    const getConcernIcon = (level) => {
        switch (level) {
        case 'CRITICAL':
            return <AlertTriangle className="h-5 w-5 text-red-600" />;
        case 'WARNING':
            return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
        case 'WATCH':
            return <CheckCircle className="h-5 w-5 text-blue-600" />;
        default:
            return null;
        }
    };

    const getConcernColor = (level) => {
        switch (level) {
        case 'CRITICAL':
            return 'bg-red-50 border-red-200 text-red-800';
        case 'WARNING':
            return 'bg-yellow-50 border-yellow-200 text-yellow-800';
        case 'WATCH':
            return 'bg-blue-50 border-blue-200 text-blue-800';
        default:
            return 'bg-gray-50 border-gray-200 text-gray-800';
        }
    };

    return (
        <div className="container mx-auto px-4 py-8">
        <button
            onClick={() => navigate('/portfolio')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
            <ArrowLeft className="h-4 w-4" />
            Back to Portfolios
        </button>

        <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
            {analysis.portfolio_name}
            </h1>
            <p className="text-gray-600">Risk Analysis Report</p>
        </div>

        {/* Portfolio Overview */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-2">
                <DollarSign className="h-8 w-8 text-green-600" />
                <div>
                <p className="text-sm text-gray-600">Total Value</p>
                <p className="text-2xl font-bold text-gray-900">
                    ${portfolio_metrics.total_value.toLocaleString()}
                </p>
                </div>
            </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-2">
                <Activity className="h-8 w-8 text-blue-600" />
                <div>
                <p className="text-sm text-gray-600">Portfolio Beta</p>
                <p className="text-2xl font-bold text-gray-900">
                    {portfolio_metrics.portfolio_beta.toFixed(2)}
                </p>
                </div>
            </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="h-8 w-8 text-purple-600" />
                <div>
                <p className="text-sm text-gray-600">Sharpe Ratio</p>
                <p className="text-2xl font-bold text-gray-900">
                    {portfolio_metrics.portfolio_sharpe_ratio.toFixed(2)}
                </p>
                </div>
            </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center gap-3 mb-2">
                {portfolio_metrics.total_unrealized_gain_loss >= 0 ? (
                <TrendingUp className="h-8 w-8 text-green-600" />
                ) : (
                <TrendingDown className="h-8 w-8 text-red-600" />
                )}
                <div>
                <p className="text-sm text-gray-600">Total P/L</p>
                <p className={`text-2xl font-bold ${
                    portfolio_metrics.total_unrealized_gain_loss >= 0 
                    ? 'text-green-600' 
                    : 'text-red-600'
                }`}>
                    {portfolio_metrics.total_unrealized_gain_loss >= 0 ? '+' : ''}
                    {portfolio_metrics.total_unrealized_gain_loss_pct.toFixed(2)}%
                </p>
                </div>
            </div>
            </div>
        </div>

        {/* Concerns */}
        {concerns.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Risk Concerns</h2>
            <div className="space-y-4">
                {concerns.map((concern, index) => (
                <div
                    key={index}
                    className={`border rounded-lg p-4 ${getConcernColor(concern.level)}`}
                >
                    <div className="flex items-start gap-3">
                    {getConcernIcon(concern.level)}
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold">{concern.level}</span>
                        <span className="text-sm">• {concern.category}</span>
                        </div>
                        <h3 className="font-semibold mb-2">{concern.title}</h3>
                        <p className="text-sm">{concern.description}</p>
                        {concern.affected_stocks.length > 0 && (
                        <p className="text-sm mt-2">
                            <strong>Affected:</strong> {concern.affected_stocks.join(', ')}
                        </p>
                        )}
                    </div>
                    </div>
                </div>
                ))}
            </div>
            </div>
        )}

        {/* Sector Allocation */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Sector Allocation</h2>
            <ResponsiveContainer width="100%" height={300}>
                <RechartsPie>
                <Pie
                    data={sectorData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value.toFixed(1)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                >
                    {sectorData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip />
                </RechartsPie>
            </ResponsiveContainer>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">Holdings</h2>
            <div className="space-y-3 max-h-80 overflow-y-auto">
                {stocks.map((stock, index) => (
                <div key={index} className="border-b pb-3">
                    <div className="flex justify-between items-start mb-1">
                    <div>
                        <h3 className="font-semibold text-gray-900">{stock.info.ticker}</h3>
                        <p className="text-sm text-gray-600">{stock.info.sector}</p>
                    </div>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                        stock.metrics.risk_level === 'High Risk' 
                        ? 'bg-red-100 text-red-700'
                        : stock.metrics.risk_level === 'Medium Risk'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-green-100 text-green-700'
                    }`}>
                        {stock.metrics.risk_level}
                    </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-sm">
                    <div>
                        <p className="text-gray-600">Beta</p>
                        <p className="font-medium">{stock.metrics.beta.toFixed(2)}</p>
                    </div>
                    <div>
                        <p className="text-gray-600">Position</p>
                        <p className="font-medium">{stock.metrics.position_size_pct.toFixed(1)}%</p>
                    </div>
                    <div>
                        <p className="text-gray-600">P/L</p>
                        <p className={`font-medium ${
                        stock.metrics.unrealized_gain_loss_pct >= 0 
                            ? 'text-green-600' 
                            : 'text-red-600'
                        }`}>
                        {stock.metrics.unrealized_gain_loss_pct >= 0 ? '+' : ''}
                        {stock.metrics.unrealized_gain_loss_pct.toFixed(2)}%
                        </p>
                    </div>
                    </div>
                </div>
                ))}
            </div>
            </div>
        </div>

        {/* Outlook */}
        <div className="grid md:grid-cols-2 gap-8 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Short-Term Outlook</h2>
            <p className="text-gray-700">{analysis.short_term_outlook}</p>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-bold text-gray-900 mb-3">Long-Term Outlook</h2>
            <p className="text-gray-700">{analysis.long_term_outlook}</p>
            </div>
        </div>

        {/* Portfolio News */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-6">
                <div className="flex items-center gap-3">
                    <Newspaper className="h-6 w-6 text-blue-600" />
                    <h2 className="text-2xl font-bold text-gray-900">Portfolio News</h2>
                    <span className="text-sm text-gray-500">
                        ({newsArticles.length} articles)
                    </span>
                </div>
                <div className="flex items-center gap-3">
                    {/* Ticker Filter Dropdown */}
                    <div className="relative ticker-dropdown-container">
                        <div className="flex items-center gap-2">
                            <label className="text-sm text-gray-600 whitespace-nowrap">Filter by Ticker:</label>
                            <div className="relative">
                                <input
                                    type="text"
                                    value={selectedTicker || tickerSearchValue}
                                    onChange={(e) => {
                                        const value = e.target.value;
                                        setTickerSearchValue(value);
                                        setShowTickerDropdown(true);
                                        if (!value) {
                                            handleClearTicker();
                                        }
                                    }}
                                    onFocus={() => setShowTickerDropdown(true)}
                                    onBlur={() => {
                                        // Delay to allow dropdown click to register
                                        setTimeout(() => setShowTickerDropdown(false), 200);
                                    }}
                                    placeholder="All stocks"
                                    className="px-3 py-2 pr-8 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-32"
                                />
                                {selectedTicker && (
                                    <button
                                        onClick={(e) => {
                                            e.stopPropagation();
                                            handleClearTicker();
                                        }}
                                        className="absolute right-2 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                                    >
                                        <X className="h-4 w-4" />
                                    </button>
                                )}
                            </div>
                        </div>
                        {showTickerDropdown && filteredTickers.length > 0 && (
                            <div 
                                className="absolute z-10 mt-1 w-32 bg-white border border-gray-300 rounded-lg shadow-lg max-h-48 overflow-y-auto"
                                onMouseDown={(e) => e.preventDefault()} // Prevent blur on click
                            >
                                {filteredTickers.map((ticker) => (
                                    <button
                                        key={ticker}
                                        onClick={() => handleTickerSelect(ticker)}
                                        className={`w-full text-left px-3 py-2 hover:bg-blue-50 ${
                                            selectedTicker === ticker ? 'bg-blue-100 font-semibold' : ''
                                        }`}
                                    >
                                        {ticker}
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>
                    <button
                        onClick={loadNews}
                        disabled={loadingNews}
                        className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
                    >
                        <RefreshCw className={`h-4 w-4 ${loadingNews ? 'animate-spin' : ''}`} />
                        {loadingNews ? 'Loading...' : 'Reload News'}
                    </button>
                </div>
            </div>

            {loadingNews && newsArticles.length === 0 ? (
                <div className="flex items-center justify-center py-12">
                    <Loader className="h-8 w-8 animate-spin text-blue-600" />
                </div>
            ) : newsArticles.length === 0 ? (
                <div className="text-center py-12 text-gray-500">
                    <Newspaper className="h-12 w-12 mx-auto mb-4 text-gray-400" />
                    <p>No news articles found{selectedTicker ? ` for ${selectedTicker}` : ''}.</p>
                    <p className="text-sm mt-2">Click "Reload News" to fetch the latest articles.</p>
                </div>
            ) : (
                <>
                    <div className="space-y-4">
                        {paginatedArticles.map((article, index) => (
                        <div
                            key={index}
                            className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 hover:shadow-md transition-all"
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        {article.related_ticker && (
                                            <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-semibold">
                                                {article.related_ticker}
                                            </span>
                                        )}
                                        <span className={`px-2 py-1 rounded text-xs font-medium ${getSentimentColor(article.sentiment)}`}>
                                            {article.sentiment}
                                        </span>
                                        {article.source && (
                                            <span className="text-xs text-gray-500">
                                                • {article.source}
                                            </span>
                                        )}
                                    </div>
                                    <h3 className="text-lg font-semibold text-gray-900 mb-2 hover:text-blue-600">
                                        <a
                                            href={article.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center gap-2 group"
                                        >
                                            {article.title}
                                            <ExternalLink className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                                        </a>
                                    </h3>
                                    {article.description && (
                                        <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                                            {article.description}
                                        </p>
                                    )}
                                    <div className="flex items-center gap-4 text-xs text-gray-500">
                                        {article.published_at && (
                                            <span>{formatDate(article.published_at)}</span>
                                        )}
                                        <a
                                            href={article.url}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="flex items-center gap-1 text-blue-600 hover:text-blue-700 font-medium"
                                        >
                                            Read full article
                                            <ExternalLink className="h-3 w-3" />
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                        ))}
                    </div>

                    {/* Pagination Controls */}
                    {totalPages > 1 && (
                        <div className="flex items-center justify-between mt-6 pt-6 border-t border-gray-200">
                            <div className="text-sm text-gray-600">
                                Showing {((currentPage - 1) * ARTICLES_PER_PAGE) + 1} to {Math.min(currentPage * ARTICLES_PER_PAGE, newsArticles.length)} of {newsArticles.length} articles
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                                    disabled={currentPage === 1}
                                    className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    <ChevronLeft className="h-4 w-4" />
                                    Previous
                                </button>
                                <div className="flex items-center gap-1">
                                    {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                                        let pageNum;
                                        if (totalPages <= 5) {
                                            pageNum = i + 1;
                                        } else if (currentPage <= 3) {
                                            pageNum = i + 1;
                                        } else if (currentPage >= totalPages - 2) {
                                            pageNum = totalPages - 4 + i;
                                        } else {
                                            pageNum = currentPage - 2 + i;
                                        }
                                        return (
                                            <button
                                                key={pageNum}
                                                onClick={() => setCurrentPage(pageNum)}
                                                className={`px-3 py-2 text-sm font-medium rounded-lg transition-colors ${
                                                    currentPage === pageNum
                                                        ? 'bg-blue-600 text-white'
                                                        : 'text-gray-700 bg-white border border-gray-300 hover:bg-gray-50'
                                                }`}
                                            >
                                                {pageNum}
                                            </button>
                                        );
                                    })}
                                </div>
                                <button
                                    onClick={() => setCurrentPage(prev => Math.min(totalPages, prev + 1))}
                                    disabled={currentPage === totalPages}
                                    className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                                >
                                    Next
                                    <ChevronRight className="h-4 w-4" />
                                </button>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
        </div>
    );
    }