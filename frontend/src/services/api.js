import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Portfolio APIs
export const uploadCSV = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await axios.post(`${API_BASE_URL}/api/portfolio/upload`, formData);
    return response.data;
};

export const createPortfolioManual = async (portfolio) => {
    const response = await api.post('/api/portfolio/manual', portfolio);
    return response.data;
};

export const getPortfolio = async (portfolioId) => {
    const response = await api.get(`/api/portfolio/${portfolioId}`);
    return response.data;
};

export const listPortfolios = async () => {
    const response = await api.get('/api/portfolio/');
    return response.data;
};

export const deletePortfolio = async (portfolioId) => {
    const response = await api.delete(`/api/portfolio/${portfolioId}`);
    return response.data;
};

// Analysis APIs
export const calculateAnalysis = async (portfolioId, includeNews = true) => {
    const response = await api.post(
        `/api/analysis/calculate/${portfolioId}`,
        null,
        { params: { include_news: includeNews } }
    );
    return response.data;
};

export const getAnalysis = async (analysisId) => {
    const response = await api.get(`/api/analysis/${analysisId}`);
    return response.data;
};

export const getPortfolioNews = async (portfolioId, ticker = null, limit = 100) => {
    const params = { limit };
    if (ticker) {
        params.ticker = ticker;
    }
    const response = await api.get(`/api/analysis/portfolio/${portfolioId}/news`, {
        params
    });
    return response.data;
};

// Broker APIs
export const connectWealthsimple = async (credentials) => {
    const response = await api.post('/api/brokers/wealthsimple/connect', credentials);
    return response.data;
};

export const connectQuestrade = async (credentials) => {
    const response = await api.post('/api/brokers/questrade/connect', credentials);
    return response.data;
};

export const connectIBKR = async (credentials) => {
    const response = await api.post('/api/brokers/ibkr/connect', credentials);
    return response.data;
};

export const getSupportedBrokers = async () => {
    const response = await api.get('/api/brokers/supported');
    return response.data;
};

export default api;