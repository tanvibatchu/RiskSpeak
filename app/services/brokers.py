from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from app.models import StockHolding
from app.config import settings

class BaseBroker(ABC):
    """Base class for broker integrations"""
    
    @abstractmethod
    def authenticate(self, auth_data: Dict) -> bool:
        """Authenticate with broker API"""
        pass
    
    @abstractmethod
    def fetch_holdings(self) -> List[StockHolding]:
        """Fetch user's holdings from broker"""
        pass
    
    @abstractmethod
    def get_account_info(self) -> Dict:
        """Get account information"""
        pass


class WealthsimpleBroker(BaseBroker):
    """Wealthsimple Trade API integration"""
    
    def __init__(self):
        self.client_id = settings.WEALTHSIMPLE_CLIENT_ID
        self.client_secret = settings.WEALTHSIMPLE_CLIENT_SECRET
        self.access_token = None
        self.base_url = "https://trade-service.wealthsimple.com"
    
    def authenticate(self, auth_data: Dict) -> bool:
        """
        Authenticate with Wealthsimple
        Note: Wealthsimple doesn't have an official public API yet
        This is a placeholder for when they release one or using unofficial API
        """
        email = auth_data.get('email')
        password = auth_data.get('password')
        
        print(f"Authenticating Wealthsimple user: {email}")
        
        return True
    
    def fetch_holdings(self) -> List[StockHolding]:
        """Fetch holdings from Wealthsimple"""
        if not self.access_token:
            raise Exception("Not authenticated")
        
        holdings = []
        
        return holdings
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        return {
            "broker": "wealthsimple",
            "account_type": "TFSA",
            "account_number": "XXXXX"
        }


class QuestradeBroker(BaseBroker):
    """Questrade API integration"""
    
    def __init__(self):
        self.client_id = settings.QUESTRADE_CLIENT_ID
        self.refresh_token = settings.QUESTRADE_REFRESH_TOKEN
        self.access_token = None
        self.api_server = None
    
    def authenticate(self, auth_data: Dict) -> bool:
        """
        Authenticate with Questrade using refresh token
        Questrade has official API documentation
        """
        import requests
        
        refresh_token = auth_data.get('refresh_token', self.refresh_token)
        
        try:
            url = "https://login.questrade.com/oauth2/token"
            params = {
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token
            }
            
            response = requests.post(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.access_token = data['access_token']
            self.api_server = data['api_server']
            self.refresh_token = data['refresh_token']
            
            return True
            
        except Exception as e:
            print(f"Questrade authentication error: {e}")
            return False
    
    def fetch_holdings(self) -> List[StockHolding]:
        """Fetch holdings from Questrade"""
        import requests
        
        if not self.access_token or not self.api_server:
            raise Exception("Not authenticated")
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            accounts_url = f"{self.api_server}v1/accounts"
            accounts_response = requests.get(accounts_url, headers=headers)
            accounts_response.raise_for_status()
            accounts = accounts_response.json()['accounts']
            
            account_id = accounts[0]['number']
            positions_url = f"{self.api_server}v1/accounts/{account_id}/positions"
            positions_response = requests.get(positions_url, headers=headers)
            positions_response.raise_for_status()
            positions = positions_response.json()['positions']
            
            holdings = []
            for position in positions:
                if position['currentMarketValue'] > 0:
                    holdings.append(StockHolding(
                        ticker=position['symbol'],
                        quantity=position['openQuantity'],
                        purchase_price=position['averageEntryPrice']
                    ))
            
            return holdings
            
        except Exception as e:
            print(f"Error fetching Questrade holdings: {e}")
            return []
    
    def get_account_info(self) -> Dict:
        """Get Questrade account information"""
        import requests
        
        if not self.access_token or not self.api_server:
            return {}
        
        try:
            headers = {'Authorization': f'Bearer {self.access_token}'}
            url = f"{self.api_server}v1/accounts"
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            accounts = response.json()['accounts']
            
            return {
                "broker": "questrade",
                "accounts": [
                    {
                        "type": acc['type'],
                        "number": acc['number'],
                        "status": acc['status']
                    }
                    for acc in accounts
                ]
            }
        except Exception as e:
            print(f"Error fetching Questrade account info: {e}")
            return {}


class InteractiveBrokersBroker(BaseBroker):
    """Interactive Brokers API integration"""
    
    def __init__(self):
        self.client_id = settings.IBKR_CLIENT_ID
        self.client_secret = settings.IBKR_CLIENT_SECRET
        self.access_token = None
    
    def authenticate(self, auth_data: Dict) -> bool:
        """
        Authenticate with Interactive Brokers
        IBKR requires TWS or IB Gateway to be running
        """
        print("IBKR authentication - requires TWS/Gateway setup")
        return True
    
    def fetch_holdings(self) -> List[StockHolding]:
        """Fetch holdings from Interactive Brokers"""
        return []
    
    def get_account_info(self) -> Dict:
        """Get IBKR account information"""
        return {
            "broker": "interactive_brokers",
            "note": "Requires TWS/IB Gateway"
        }


class BrokerFactory:
    """Factory to create broker instances"""
    
    @staticmethod
    def create_broker(broker_name: str) -> BaseBroker:
        """Create broker instance by name"""
        brokers = {
            'wealthsimple': WealthsimpleBroker,
            'questrade': QuestradeBroker,
            'ibkr': InteractiveBrokersBroker,
            'interactive_brokers': InteractiveBrokersBroker
        }
        
        broker_class = brokers.get(broker_name.lower())
        if not broker_class:
            raise ValueError(f"Unsupported broker: {broker_name}")
        
        return broker_class()