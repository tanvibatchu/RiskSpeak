import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadCSV, createPortfolioManual } from '../services/api';
import { Upload, Plus, FileText } from 'lucide-react';

export default function Home() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showManual, setShowManual] = useState(false);
    const [manualHoldings, setManualHoldings] = useState([
        { ticker: '', quantity: '', purchase_price: '' }
    ]);
    const navigate = useNavigate();

    const handleFileUpload = async (e) => {
        e.preventDefault();
        if (!file) return;

        setLoading(true);
        setError('');

        try {
        const result = await uploadCSV(file);
        navigate('/portfolio', { state: { portfolioId: result.portfolio_id } });
        } catch (err) {
        setError(err.response?.data?.detail || 'Failed to upload file');
        } finally {
        setLoading(false);
        }
    };

    const handleManualSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
        const validHoldings = manualHoldings.filter(
            h => h.ticker && h.quantity && h.purchase_price
        );

        if (validHoldings.length === 0) {
            setError('Please add at least one holding');
            setLoading(false);
            return;
        }

        const portfolio = {
            portfolio_name: 'Manual Portfolio',
            holdings: validHoldings.map(h => ({
            ticker: h.ticker.toUpperCase(),
            quantity: parseFloat(h.quantity),
            purchase_price: parseFloat(h.purchase_price)
            }))
        };

        const result = await createPortfolioManual(portfolio);
        navigate('/portfolio', { state: { portfolioId: result.portfolio_id } });
        } catch (err) {
        setError(err.response?.data?.detail || 'Failed to create portfolio');
        } finally {
        setLoading(false);
        }
    };

    const addHolding = () => {
        setManualHoldings([...manualHoldings, { ticker: '', quantity: '', purchase_price: '' }]);
    };

    const removeHolding = (index) => {
        setManualHoldings(manualHoldings.filter((_, i) => i !== index));
    };

    const updateHolding = (index, field, value) => {
        const updated = [...manualHoldings];
        updated[index][field] = value;
        setManualHoldings(updated);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="container mx-auto px-4 py-16">
            <div className="text-center mb-12">
            <h1 className="text-5xl font-bold text-gray-900 mb-4">
                Risk<span className="text-blue-600">Speak</span>
            </h1>
            <p className="text-xl text-gray-600">
                Comprehensive Portfolio Risk Analysis
            </p>
            </div>

            <div className="max-w-4xl mx-auto">
            <div className="bg-white rounded-lg shadow-xl p-8">
                <div className="flex gap-4 mb-8 border-b">
                <button
                    onClick={() => setShowManual(false)}
                    className={`pb-4 px-4 font-semibold ${
                    !showManual
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-500'
                    }`}
                >
                    <Upload className="inline mr-2 h-5 w-5" />
                    Upload CSV
                </button>
                <button
                    onClick={() => setShowManual(true)}
                    className={`pb-4 px-4 font-semibold ${
                    showManual
                        ? 'border-b-2 border-blue-600 text-blue-600'
                        : 'text-gray-500'
                    }`}
                >
                    <Plus className="inline mr-2 h-5 w-5" />
                    Manual Entry
                </button>
                </div>

                {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    {error}
                </div>
                )}

                {!showManual ? (
                <form onSubmit={handleFileUpload}>
                    <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                        Upload Portfolio CSV
                    </label>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center hover:border-blue-500 transition">
                        <FileText className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                        <input
                        type="file"
                        accept=".csv"
                        onChange={(e) => setFile(e.target.files[0])}
                        className="hidden"
                        id="file-upload"
                        />
                        <label
                        htmlFor="file-upload"
                        className="cursor-pointer text-blue-600 hover:text-blue-700 font-medium"
                        >
                        Choose CSV file
                        </label>
                        {file && (
                        <p className="mt-2 text-sm text-gray-600">
                            Selected: {file.name}
                        </p>
                        )}
                        <p className="mt-2 text-xs text-gray-500">
                        Format: Ticker, Quantity, Purchase_Price
                        </p>
                    </div>
                    </div>
                    <button
                    type="submit"
                    disabled={!file || loading}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                    >
                    {loading ? 'Uploading...' : 'Analyze Portfolio'}
                    </button>
                </form>
                ) : (
                <form onSubmit={handleManualSubmit}>
                    <div className="space-y-4 mb-6">
                    {manualHoldings.map((holding, index) => (
                        <div key={index} className="flex gap-2">
                        <input
                            type="text"
                            placeholder="Ticker (e.g., AAPL)"
                            value={holding.ticker}
                            onChange={(e) => updateHolding(index, 'ticker', e.target.value)}
                            className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        />
                        <input
                            type="number"
                            placeholder="Quantity"
                            value={holding.quantity}
                            onChange={(e) => updateHolding(index, 'quantity', e.target.value)}
                            className="w-32 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        />
                        <input
                            type="number"
                            step="0.01"
                            placeholder="Price"
                            value={holding.purchase_price}
                            onChange={(e) => updateHolding(index, 'purchase_price', e.target.value)}
                            className="w-32 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                        />
                        {manualHoldings.length > 1 && (
                            <button
                            type="button"
                            onClick={() => removeHolding(index)}
                            className="px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg"
                            >
                            ×
                            </button>
                        )}
                        </div>
                    ))}
                    </div>
                    <button
                    type="button"
                    onClick={addHolding}
                    className="w-full mb-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-blue-500 hover:text-blue-600 transition"
                    >
                    + Add Another Stock
                    </button>
                    <button
                    type="submit"
                    disabled={loading}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
                    >
                    {loading ? 'Creating...' : 'Create Portfolio'}
                    </button>
                </form>
                )}
            </div>

            <div className="mt-8 text-center">
                <button
                onClick={() => navigate('/brokers')}
                className="text-blue-600 hover:text-blue-700 font-medium"
                >
                Or connect your broker account →
                </button>
            </div>
            </div>
        </div>
        </div>
    );
    }