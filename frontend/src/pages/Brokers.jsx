import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
    getSupportedBrokers, 
    connectWealthsimple, 
    connectQuestrade, 
    connectIBKR 
} from '../services/api';
import { Building2, CheckCircle, Loader, ArrowLeft } from 'lucide-react';

export default function Brokers() {
    const [brokers, setBrokers] = useState([]);
    const [selectedBroker, setSelectedBroker] = useState(null);
    const [loading, setLoading] = useState(false);
    const [credentials, setCredentials] = useState({});
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        loadBrokers();
    }, []);

    const loadBrokers = async () => {
        try {
        const data = await getSupportedBrokers();
        setBrokers(data.brokers);
        } catch (err) {
        console.error('Failed to load brokers:', err);
        }
    };

    const handleConnect = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
        let result;
        switch (selectedBroker) {
            case 'wealthsimple':
            result = await connectWealthsimple(credentials);
            break;
            case 'questrade':
            result = await connectQuestrade(credentials);
            break;
            case 'ibkr':
            result = await connectIBKR(credentials);
            break;
            default:
            throw new Error('Invalid broker');
        }

        if (result.portfolio_id) {
            navigate('/portfolio', { state: { portfolioId: result.portfolio_id } });
        } else {
            setError(result.message || 'Connected but no holdings found');
        }
        } catch (err) {
        setError(err.response?.data?.detail || 'Failed to connect to broker');
        } finally {
        setLoading(false);
        }
    };

    const renderForm = () => {
        if (!selectedBroker) return null;

        const broker = brokers.find(b => b.id === selectedBroker);

        return (
        <div className="mt-6">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
            <p className="text-sm text-blue-800">
                <strong>Note:</strong> {broker.note}
            </p>
            </div>

            <form onSubmit={handleConnect} className="space-y-4">
            {selectedBroker === 'wealthsimple' && (
                <>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                    </label>
                    <input
                    type="email"
                    required
                    value={credentials.email || ''}
                    onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                    placeholder="your@email.com"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password
                    </label>
                    <input
                    type="password"
                    required
                    value={credentials.password || ''}
                    onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                    placeholder="••••••••"
                    />
                </div>
                </>
            )}

            {selectedBroker === 'questrade' && (
                <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                    Refresh Token
                </label>
                <input
                    type="text"
                    required
                    value={credentials.refresh_token || ''}
                    onChange={(e) => setCredentials({ ...credentials, refresh_token: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                    placeholder="Your Questrade refresh token"
                />
                <p className="text-xs text-gray-500 mt-1">
                    Get your refresh token from{' '}
                    <a 
                    href="https://login.questrade.com/APIAccess/UserApps.aspx" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                    >
                    Questrade API portal
                    </a>
                </p>
                </div>
            )}

            {selectedBroker === 'ibkr' && (
                <>
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
                    <p className="text-sm text-yellow-800">
                    <strong>Requirements:</strong> TWS or IB Gateway must be running on your local machine.
                    </p>
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                    Client ID
                    </label>
                    <input
                    type="text"
                    required
                    value={credentials.client_id || ''}
                    onChange={(e) => setCredentials({ ...credentials, client_id: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                    placeholder="Your IBKR client ID"
                    />
                </div>
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                    Client Secret
                    </label>
                    <input
                    type="password"
                    required
                    value={credentials.client_secret || ''}
                    onChange={(e) => setCredentials({ ...credentials, client_secret: e.target.value })}
                    className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-black"
                    placeholder="Your IBKR client secret"
                    />
                </div>
                </>
            )}

            {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                {error}
                </div>
            )}

            <div className="flex gap-3">
                <button
                type="button"
                onClick={() => {
                    setSelectedBroker(null);
                    setCredentials({});
                    setError('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-black"
                >
                Cancel
                </button>
                <button
                type="submit"
                disabled={loading}
                className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                {loading ? (
                    <>
                    <Loader className="h-4 w-4 animate-spin" />
                    Connecting...
                    </>
                ) : (
                    'Connect'
                )}
                </button>
            </div>
            </form>
        </div>
        );
    };

    return (
        <div className="container mx-auto px-4 py-8">
        <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-6"
        >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
        </button>

        <div className="max-w-4xl mx-auto">
            <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Connect Your Broker</h1>
            <p className="text-gray-600">
                Import your portfolio directly from your brokerage account
            </p>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
            {brokers.map((broker) => (
                <div
                key={broker.id}
                className={`bg-white rounded-lg shadow-md hover:shadow-lg transition p-6 cursor-pointer border-2 ${
                    selectedBroker === broker.id
                    ? 'border-blue-600'
                    : 'border-transparent'
                }`}
                onClick={() => setSelectedBroker(broker.id)}
                >
                <div className="flex items-start justify-between mb-4">
                    <Building2 className="h-10 w-10 text-blue-600" />
                    {selectedBroker === broker.id && (
                    <CheckCircle className="h-6 w-6 text-blue-600" />
                    )}
                </div>
                
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {broker.name}
                </h3>
                
                <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                    <span className="text-gray-600">Region:</span>
                    <span className="font-medium">{broker.region}</span>
                    </div>
                    <div className="flex items-center gap-2">
                    <span className="text-gray-600">Status:</span>
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-700">
                        {broker.status}
                    </span>
                    </div>
                </div>
                </div>
            ))}
            </div>

            {selectedBroker && (
            <div className="mt-8 bg-white rounded-lg shadow-md p-6">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                Connect to {brokers.find(b => b.id === selectedBroker)?.name}
                </h2>
                {renderForm()}
            </div>
            )}
        </div>
        </div>
    );
    }