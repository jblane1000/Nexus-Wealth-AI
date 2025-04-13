import requests
import logging
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class AIApiClient:
    """
    Client for communicating with the AI Core API
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.timeout = 10  # seconds
    
    def _make_request(self, method, endpoint, data=None, params=None):
        """
        Make a request to the AI Core API
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            data (dict, optional): Request body data
            params (dict, optional): Query parameters
            
        Returns:
            dict: Response data
            
        Raises:
            Exception: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params, timeout=self.timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, timeout=self.timeout)
            elif method == 'PUT':
                response = requests.put(url, json=data, timeout=self.timeout)
            elif method == 'DELETE':
                response = requests.delete(url, json=data, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            # For development/placeholder, return simulated data
            # In production, this should be removed
            if endpoint == '/portfolio' and method == 'GET':
                return self._get_simulated_portfolio_data()
            elif endpoint == '/market' and method == 'GET':
                return self._get_simulated_market_data()
            elif endpoint == '/decisions' and method == 'GET':
                return self._get_simulated_decisions_data()
            else:
                raise Exception(f"Failed to communicate with AI Core: {str(e)}")
    
    def get_portfolio_data(self, user_id):
        """
        Get portfolio data for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Portfolio data
        """
        return self._make_request('GET', '/portfolio', params={'user_id': user_id})
    
    def update_risk_profile(self, user_id, risk_level, risk_score):
        """
        Update a user's risk profile
        
        Args:
            user_id (int): User ID
            risk_level (str): Risk level (Conservative, Moderate, Aggressive)
            risk_score (int): Risk score
            
        Returns:
            dict: Response data
        """
        data = {
            'user_id': user_id,
            'risk_level': risk_level,
            'risk_score': risk_score
        }
        return self._make_request('POST', '/risk_profile', data=data)
    
    def add_goal(self, user_id, goal_id, name, target_amount, target_date, priority):
        """
        Add a new goal
        
        Args:
            user_id (int): User ID
            goal_id (int): Goal ID
            name (str): Goal name
            target_amount (float): Target amount
            target_date (str): Target date (ISO format)
            priority (str): Priority (High, Medium, Low)
            
        Returns:
            dict: Response data
        """
        data = {
            'user_id': user_id,
            'goal_id': goal_id,
            'name': name,
            'target_amount': target_amount,
            'target_date': target_date,
            'priority': priority
        }
        return self._make_request('POST', '/goals', data=data)
    
    def notify_cash_flow(self, user_id, amount, transaction_type):
        """
        Notify about a cash flow (deposit or withdrawal)
        
        Args:
            user_id (int): User ID
            amount (float): Amount
            transaction_type (str): Transaction type (DEPOSIT, WITHDRAWAL)
            
        Returns:
            dict: Response data
        """
        data = {
            'user_id': user_id,
            'amount': amount,
            'transaction_type': transaction_type
        }
        return self._make_request('POST', '/cash_flow', data=data)
    
    def get_market_summary(self):
        """
        Get market summary data
        
        Returns:
            dict: Market summary data
        """
        return self._make_request('GET', '/market')
    
    def get_recent_decisions(self, user_id):
        """
        Get recent AI decisions for a user
        
        Args:
            user_id (int): User ID
            
        Returns:
            dict: Recent decisions data
        """
        return self._make_request('GET', '/decisions', params={'user_id': user_id})
    
    def update_user_settings(self, user_id, trading_enabled):
        """
        Update user settings
        
        Args:
            user_id (int): User ID
            trading_enabled (bool): Whether trading is enabled
            
        Returns:
            dict: Response data
        """
        data = {
            'user_id': user_id,
            'trading_enabled': trading_enabled
        }
        return self._make_request('PUT', '/user/settings', data=data)
    
    # Simulated data methods for development and testing
    # These would be removed in production
    
    def _get_simulated_portfolio_data(self):
        """
        Get simulated portfolio data
        
        Returns:
            dict: Simulated portfolio data
        """
        return {
            'assets': [
                {
                    'symbol': 'AAPL',
                    'name': 'Apple Inc.',
                    'quantity': 10,
                    'price': 152.73,
                    'value': 1527.30,
                    'allocation': 25.45
                },
                {
                    'symbol': 'MSFT',
                    'name': 'Microsoft Corporation',
                    'quantity': 5,
                    'price': 312.82,
                    'value': 1564.10,
                    'allocation': 26.07
                },
                {
                    'symbol': 'VOOG',
                    'name': 'Vanguard S&P 500 Growth ETF',
                    'quantity': 4,
                    'price': 283.45,
                    'value': 1133.80,
                    'allocation': 18.89
                },
                {
                    'symbol': 'BTC',
                    'name': 'Bitcoin',
                    'quantity': 0.015,
                    'price': 60423.17,
                    'value': 906.35,
                    'allocation': 15.10
                }
            ],
            'cash': 865.45,
            'total_value': 6000.00,
            'allocation': {
                'Stocks': 51.52,
                'ETFs': 18.89,
                'Crypto': 15.10,
                'Cash': 14.49
            },
            'performance': {
                'daily': 0.75,
                'weekly': 2.31,
                'monthly': 5.67,
                'yearly': 12.42
            }
        }
    
    def _get_simulated_market_data(self):
        """
        Get simulated market data
        
        Returns:
            dict: Simulated market data
        """
        return {
            'indices': [
                {
                    'name': 'S&P 500',
                    'value': 4536.34,
                    'change': 0.58,
                    'change_percent': 1.21
                },
                {
                    'name': 'Dow Jones',
                    'value': 35492.70,
                    'change': 186.13,
                    'change_percent': 0.51
                },
                {
                    'name': 'NASDAQ',
                    'value': 14138.78,
                    'change': 106.71,
                    'change_percent': 0.76
                },
                {
                    'name': 'TSX Composite',
                    'value': 20795.12,
                    'change': 167.50,
                    'change_percent': 0.81
                }
            ],
            'top_movers': [
                {
                    'symbol': 'XYZ',
                    'name': 'XYZ Corp',
                    'price': 45.67,
                    'change_percent': 8.32
                },
                {
                    'symbol': 'ABC',
                    'name': 'ABC Inc',
                    'price': 78.92,
                    'change_percent': 6.54
                },
                {
                    'symbol': 'DEF',
                    'name': 'DEF Holdings',
                    'price': 112.35,
                    'change_percent': -5.78
                }
            ],
            'crypto': [
                {
                    'symbol': 'BTC',
                    'name': 'Bitcoin',
                    'price': 60423.17,
                    'change_percent': 2.45
                },
                {
                    'symbol': 'ETH',
                    'name': 'Ethereum',
                    'price': 3542.68,
                    'change_percent': 1.87
                }
            ],
            'forex': [
                {
                    'pair': 'USD/CAD',
                    'rate': 1.2743,
                    'change_percent': -0.12
                },
                {
                    'pair': 'EUR/USD',
                    'rate': 1.1324,
                    'change_percent': 0.23
                }
            ]
        }
    
    def _get_simulated_decisions_data(self):
        """
        Get simulated AI decisions data
        
        Returns:
            dict: Simulated decisions data
        """
        now = datetime.utcnow().isoformat()
        yesterday = datetime.utcnow().replace(day=datetime.utcnow().day - 1).isoformat()
        
        return {
            'decisions': [
                {
                    'id': 1,
                    'type': 'ALLOCATION_CHANGE',
                    'description': 'Increased allocation to technology sector based on positive earnings reports and market trend analysis.',
                    'timestamp': now,
                    'actions': [
                        'Purchased 2 MSFT shares at $310.45',
                        'Purchased 3 AAPL shares at $150.25'
                    ]
                },
                {
                    'id': 2,
                    'type': 'RISK_ADJUSTMENT',
                    'description': 'Reduced portfolio volatility in response to increased market uncertainty and your risk profile.',
                    'timestamp': yesterday,
                    'actions': [
                        'Sold 5 XYZ shares at $45.30',
                        'Purchased 2 VOOG shares at $280.15'
                    ]
                }
            ]
        }
