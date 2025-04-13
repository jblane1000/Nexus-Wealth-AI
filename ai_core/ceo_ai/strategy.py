import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class StrategyEngine:
    """
    Strategy Engine for CEO AI
    
    Responsible for:
    - Formulating investment strategies based on user profiles, goals, and risk tolerance
    - Generating target asset allocations
    - Periodically reevaluating strategies based on market conditions and goal progress
    """
    
    def __init__(self):
        """Initialize the Strategy Engine"""
        self.strategies = {}  # Cache of user strategies
        logger.info("Strategy Engine initialized")
    
    def get_target_allocation(self, user_id: int) -> Dict[str, Any]:
        """
        Get target asset allocation for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing target allocation percentages
        """
        # Check if we have a cached strategy
        if user_id in self.strategies:
            return self.strategies[user_id]['allocation']
        
        # If not, generate a new strategy
        self.reevaluate_strategy(user_id)
        return self.strategies[user_id]['allocation']
    
    def reevaluate_strategy(self, user_id: int) -> None:
        """
        Reevaluate investment strategy for a user
        
        Args:
            user_id: User ID
        """
        logger.info(f"Reevaluating strategy for user {user_id}")
        
        # In a real implementation, this would fetch user data from the database
        # For this placeholder, we'll use simulated data
        
        # Simulate fetching user risk profile
        risk_profile = self._get_user_risk_profile(user_id)
        
        # Simulate fetching user goals
        goals = self._get_user_goals(user_id)
        
        # Simulate fetching market conditions
        market_conditions = self._get_market_conditions()
        
        # Generate strategy based on risk profile, goals, and market conditions
        strategy = self._generate_strategy(risk_profile, goals, market_conditions)
        
        # Cache the strategy
        self.strategies[user_id] = {
            'allocation': strategy,
            'generated_at': datetime.now().isoformat(),
            'risk_profile': risk_profile,
            'goals': goals,
            'market_conditions': market_conditions
        }
        
        logger.info(f"Strategy reevaluated for user {user_id}")
    
    def _get_user_risk_profile(self, user_id: int) -> Dict[str, Any]:
        """
        Get user risk profile
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing risk profile data
        """
        # In a real implementation, this would fetch data from the database
        # For this placeholder, we'll return simulated data
        
        # Simulate three risk profiles: Conservative, Moderate, Aggressive
        # Based on user_id modulo 3
        risk_levels = ['Conservative', 'Moderate', 'Aggressive']
        risk_level = risk_levels[user_id % 3]
        
        risk_profile = {
            'risk_level': risk_level,
            'risk_score': 5 + (user_id % 3) * 5,  # 5, 10, or 15
            'investment_horizon': 2 + (user_id % 5),  # 2-6 years
            'loss_tolerance': 5 + (user_id % 3) * 5  # 5%, 10%, or 15%
        }
        
        return risk_profile
    
    def _get_user_goals(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get user financial goals
        
        Args:
            user_id: User ID
            
        Returns:
            List of goal dictionaries
        """
        # In a real implementation, this would fetch data from the database
        # For this placeholder, we'll return simulated data
        
        # Simulate common financial goals
        now = datetime.now()
        goals = [
            {
                'id': 1,
                'name': 'Retirement',
                'target_amount': 500000 + (user_id * 10000),
                'current_amount': 50000 + (user_id * 1000),
                'target_date': (now + timedelta(days=365 * 20)).isoformat(),  # 20 years from now
                'priority': 'High'
            },
            {
                'id': 2,
                'name': 'Home Down Payment',
                'target_amount': 60000 + (user_id * 5000),
                'current_amount': 15000 + (user_id * 500),
                'target_date': (now + timedelta(days=365 * 5)).isoformat(),  # 5 years from now
                'priority': 'Medium'
            },
            {
                'id': 3,
                'name': 'Vacation Fund',
                'target_amount': 10000 + (user_id * 1000),
                'current_amount': 2000 + (user_id * 200),
                'target_date': (now + timedelta(days=365 * 2)).isoformat(),  # 2 years from now
                'priority': 'Low'
            }
        ]
        
        return goals
    
    def _get_market_conditions(self) -> Dict[str, Any]:
        """
        Get current market conditions
        
        Returns:
            Dictionary containing market condition data
        """
        # In a real implementation, this would fetch data from market data APIs
        # For this placeholder, we'll return simulated data
        
        market_conditions = {
            'equity_outlook': 'neutral',  # bullish, neutral, or bearish
            'bond_outlook': 'neutral',
            'crypto_outlook': 'bullish',
            'interest_rates': 'rising',  # rising, stable, or falling
            'inflation': 'high',         # low, moderate, or high
            'volatility': 'moderate',    # low, moderate, or high
            'timestamp': datetime.now().isoformat()
        }
        
        return market_conditions
    
    def _generate_strategy(self, risk_profile: Dict[str, Any], 
                         goals: List[Dict[str, Any]], 
                         market_conditions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate investment strategy based on risk profile, goals, and market conditions
        
        Args:
            risk_profile: Risk profile dictionary
            goals: List of goal dictionaries
            market_conditions: Market conditions dictionary
            
        Returns:
            Dictionary containing strategy and target allocations
        """
        # Base allocations by risk level
        base_allocations = {
            'Conservative': {
                'Equity': 30,
                'Bonds': 50,
                'Cash': 15,
                'Crypto': 5
            },
            'Moderate': {
                'Equity': 50,
                'Bonds': 30,
                'Cash': 10,
                'Crypto': 10
            },
            'Aggressive': {
                'Equity': 70,
                'Bonds': 10,
                'Cash': 5,
                'Crypto': 15
            }
        }
        
        risk_level = risk_profile['risk_level']
        allocation = base_allocations[risk_level].copy()
        
        # Adjust for market conditions
        if market_conditions['equity_outlook'] == 'bullish':
            allocation['Equity'] += 5
            allocation['Bonds'] -= 5
        elif market_conditions['equity_outlook'] == 'bearish':
            allocation['Equity'] -= 5
            allocation['Bonds'] += 5
        
        if market_conditions['crypto_outlook'] == 'bullish':
            allocation['Crypto'] += 5
            allocation['Bonds'] -= 5
        elif market_conditions['crypto_outlook'] == 'bearish':
            allocation['Crypto'] -= 5
            allocation['Bonds'] += 5
        
        # Ensure allocations don't go below 0
        for asset_class in allocation:
            allocation[asset_class] = max(0, allocation[asset_class])
        
        # Adjust for goals
        # Short-term goals need more cash
        short_term_goals = [g for g in goals if 
                           (datetime.fromisoformat(g['target_date']) - datetime.now()).days < 365 * 3]
        
        if short_term_goals:
            short_term_amount = sum(g['target_amount'] - g['current_amount'] for g in short_term_goals)
            # Increase cash allocation for short-term goals
            allocation['Cash'] += 5
            allocation['Equity'] -= 5
        
        # Normalize to ensure sum is 100%
        total = sum(allocation.values())
        for asset_class in allocation:
            allocation[asset_class] = round(allocation[asset_class] * 100 / total, 1)
        
        # Generate specific allocations for each asset class
        equity_allocation = self._generate_equity_allocation(risk_level, market_conditions)
        crypto_allocation = self._generate_crypto_allocation(risk_level, market_conditions)
        
        return {
            'top_level': allocation,
            'Equity': equity_allocation,
            'Crypto': crypto_allocation,
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_equity_allocation(self, risk_level: str, 
                                  market_conditions: Dict[str, Any]) -> Dict[str, float]:
        """
        Generate specific equity allocations
        
        Args:
            risk_level: Risk level (Conservative, Moderate, Aggressive)
            market_conditions: Market conditions dictionary
            
        Returns:
            Dictionary of equity assets and their allocation percentages
        """
        # Base equity allocations by risk level
        base_equity = {
            'Conservative': {
                'Large Cap': 60,
                'Mid Cap': 20,
                'Small Cap': 5,
                'International': 15,
                'Emerging Markets': 0
            },
            'Moderate': {
                'Large Cap': 50,
                'Mid Cap': 20,
                'Small Cap': 10,
                'International': 15,
                'Emerging Markets': 5
            },
            'Aggressive': {
                'Large Cap': 40,
                'Mid Cap': 20,
                'Small Cap': 15,
                'International': 15,
                'Emerging Markets': 10
            }
        }
        
        equity_allocation = base_equity[risk_level].copy()
        
        # Adjust for market conditions
        if market_conditions['volatility'] == 'high':
            # Shift towards large cap in high volatility
            equity_allocation['Large Cap'] += 5
            equity_allocation['Small Cap'] -= 5
        elif market_conditions['volatility'] == 'low':
            # More small cap in low volatility
            equity_allocation['Large Cap'] -= 5
            equity_allocation['Small Cap'] += 5
        
        # Ensure allocations don't go below 0
        for category in equity_allocation:
            equity_allocation[category] = max(0, equity_allocation[category])
        
        # Normalize to ensure sum is 100%
        total = sum(equity_allocation.values())
        for category in equity_allocation:
            equity_allocation[category] = round(equity_allocation[category] * 100 / total, 1)
        
        return equity_allocation
    
    def _generate_crypto_allocation(self, risk_level: str, 
                                  market_conditions: Dict[str, Any]) -> Dict[str, float]:
        """
        Generate specific cryptocurrency allocations
        
        Args:
            risk_level: Risk level (Conservative, Moderate, Aggressive)
            market_conditions: Market conditions dictionary
            
        Returns:
            Dictionary of cryptocurrencies and their allocation percentages
        """
        # Base crypto allocations by risk level
        base_crypto = {
            'Conservative': {
                'Bitcoin': 70,
                'Ethereum': 30,
                'Altcoins': 0
            },
            'Moderate': {
                'Bitcoin': 60,
                'Ethereum': 30,
                'Altcoins': 10
            },
            'Aggressive': {
                'Bitcoin': 50,
                'Ethereum': 30,
                'Altcoins': 20
            }
        }
        
        crypto_allocation = base_crypto[risk_level].copy()
        
        # Adjust for market conditions
        if market_conditions['crypto_outlook'] == 'bullish':
            # More altcoins in bullish market
            crypto_allocation['Bitcoin'] -= 5
            crypto_allocation['Altcoins'] += 5
        elif market_conditions['crypto_outlook'] == 'bearish':
            # More bitcoin in bearish market (less risky)
            crypto_allocation['Bitcoin'] += 5
            crypto_allocation['Altcoins'] -= 5
        
        # Ensure allocations don't go below 0
        for category in crypto_allocation:
            crypto_allocation[category] = max(0, crypto_allocation[category])
        
        # Normalize to ensure sum is 100%
        total = sum(crypto_allocation.values())
        for category in crypto_allocation:
            crypto_allocation[category] = round(crypto_allocation[category] * 100 / total, 1)
        
        return crypto_allocation
