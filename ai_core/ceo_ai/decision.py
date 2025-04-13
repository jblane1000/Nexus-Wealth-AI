import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import other CEO AI components
from .strategy import StrategyEngine
from .portfolio import PortfolioManager
from .risk import RiskAnalyzer
from .market import MarketAnalyzer

logger = logging.getLogger(__name__)

class DecisionEngine:
    """
    Decision Engine for CEO AI
    
    Responsible for:
    - Evaluating investment opportunities based on strategy, risk, and market analysis
    - Optimizing portfolio allocation
    - Generating trade recommendations or decisions
    - Considering user goals and constraints
    """
    
    def __init__(self, strategy_engine: StrategyEngine, 
                 portfolio_manager: PortfolioManager, 
                 risk_analyzer: RiskAnalyzer, 
                 market_analyzer: MarketAnalyzer):
        """Initialize the Decision Engine
        
        Args:
            strategy_engine: Instance of StrategyEngine
            portfolio_manager: Instance of PortfolioManager
            risk_analyzer: Instance of RiskAnalyzer
            market_analyzer: Instance of MarketAnalyzer
        """
        self.strategy_engine = strategy_engine
        self.portfolio_manager = portfolio_manager
        self.risk_analyzer = risk_analyzer
        self.market_analyzer = market_analyzer
        logger.info("Decision Engine initialized")

    def evaluate_investment_opportunities(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Evaluate potential investment opportunities for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of potential investment opportunities with scores
        """
        logger.info(f"Evaluating investment opportunities for user {user_id}")
        
        # Get necessary data
        target_allocation = self.strategy_engine.get_target_allocation(user_id)
        market_summary = self.market_analyzer.get_market_summary()
        # portfolio_data = self.portfolio_manager.get_portfolio_data(user_id)
        # risk_analysis = self.risk_analyzer.analyze_portfolio_risk(user_id, portfolio_data)

        # In a real implementation, this would involve complex analysis:
        # - Screen assets based on strategy criteria
        # - Analyze fundamentals and technicals
        # - Score opportunities based on potential return, risk, and fit
        
        # For this placeholder, simulate some opportunities based on market outlook
        opportunities = []
        
        # Example: If tech sector is strong, suggest a tech ETF
        if market_summary.get('sectors', {}).get('Technology') == 'strong':
            opportunities.append({
                'type': 'Equity',
                'asset': 'QQQ', # Example Tech ETF
                'rationale': 'Strong outlook for the technology sector.',
                'score': 75, # Score out of 100
                'risk_level': 'Moderate'
            })
            
        # Example: If crypto outlook is bullish, suggest Bitcoin
        if market_summary.get('crypto', {}).get('overall_sentiment') == 'positive':
             opportunities.append({
                'type': 'Crypto',
                'asset': 'BTC',
                'rationale': 'Positive sentiment and bullish outlook for Bitcoin.',
                'score': 80,
                'risk_level': 'High'
            })

        # Example: If interest rates are rising, consider inflation-protected bonds
        if market_summary.get('interest_rates') == 'rising':
             opportunities.append({
                'type': 'Bonds',
                'asset': 'TIP', # Example TIPS ETF
                'rationale': 'Potential hedge against inflation in a rising rate environment.',
                'score': 65,
                'risk_level': 'Low'
            })

        logger.info(f"Generated {len(opportunities)} potential opportunities for user {user_id}")
        return opportunities

    def generate_rebalancing_trades(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Generate trades needed to rebalance the portfolio towards the target allocation
        
        Args:
            user_id: User ID
            
        Returns:
            List of trade orders (buy/sell instructions)
        """
        logger.info(f"Generating rebalancing trades for user {user_id}")
        
        # Get current and target allocations
        current_allocation = self.portfolio_manager.get_asset_allocation(user_id)
        target_allocation = self.strategy_engine.get_target_allocation(user_id)
        portfolio_value = self.portfolio_manager.get_portfolio_value(user_id)
        
        if portfolio_value == 0: 
            logger.warning(f"Cannot generate trades for user {user_id} with zero portfolio value.")
            return []
            
        trades = []
        tolerance = 5.0 # Rebalancing tolerance percentage (e.g., 5% deviation)

        # Calculate target values for each top-level asset class
        target_values = {}
        for asset_class, percentage in target_allocation.get('top_level', {}).items():
            target_values[asset_class] = portfolio_value * (percentage / 100.0)
            
        # Calculate current values for each top-level asset class
        current_values = {}
        current_top_level = current_allocation.get('top_level', {})
        for asset_class, percentage in current_top_level.items():
             current_values[asset_class] = portfolio_value * (percentage / 100.0)
             
        # Determine adjustments needed for top-level classes
        adjustments = {}
        for asset_class in target_values:
            current_val = current_values.get(asset_class, 0.0)
            target_val = target_values.get(asset_class, 0.0)
            diff = target_val - current_val
            
            # Check if difference exceeds tolerance band
            if abs(diff / portfolio_value * 100) > tolerance:
                adjustments[asset_class] = diff

        # Generate trades based on adjustments
        # This is a simplified approach. A real system would be more sophisticated, 
        # considering specific assets within classes, transaction costs, taxes, etc.
        
        # Prioritize sells first to generate cash, then buys
        for asset_class, amount in sorted(adjustments.items(), key=lambda item: item[1]):
            if amount < 0: # Need to sell
                trades.append({
                    'action': 'SELL',
                    'asset_class': asset_class,
                    'amount': abs(amount),
                    'rationale': f"Rebalancing: Reducing overweight {asset_class} allocation."
                })
                logger.debug(f"Trade SELL {asset_class}: ${abs(amount):.2f}")
                
        for asset_class, amount in sorted(adjustments.items(), key=lambda item: item[1], reverse=True):
             if amount > 0: # Need to buy
                trades.append({
                    'action': 'BUY',
                    'asset_class': asset_class,
                    'amount': amount,
                    'rationale': f"Rebalancing: Increasing underweight {asset_class} allocation."
                })
                logger.debug(f"Trade BUY {asset_class}: ${amount:.2f}")

        # TODO: Convert class-level trades into specific asset trades (e.g., buy SPY for Equity)
        # This requires mapping asset classes to specific instruments based on the detailed strategy.

        logger.info(f"Generated {len(trades)} rebalancing trade instructions for user {user_id}")
        return trades

    def make_tactical_decision(self, user_id: int, opportunity: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make a decision on a specific tactical investment opportunity
        
        Args:
            user_id: User ID
            opportunity: Opportunity dictionary from evaluate_investment_opportunities
            
        Returns:
            A trade decision/recommendation, or None if no action is taken
        """
        logger.info(f"Making tactical decision for user {user_id} on opportunity: {opportunity.get('asset')}")
        
        # Get portfolio and risk context
        portfolio_data = self.portfolio_manager.get_portfolio_data(user_id)
        risk_analysis = self.risk_analyzer.analyze_portfolio_risk(user_id, portfolio_data)
        # risk_tolerance = self.strategy_engine._get_user_risk_profile(user_id) # Need access to user risk profile
        
        # Basic checks (placeholders)
        # 1. Is the opportunity's risk level acceptable?
        # opportunity_risk = opportunity.get('risk_level', 'Moderate')
        # if not self._is_risk_level_acceptable(opportunity_risk, risk_tolerance):
        #    logger.warning(f"Opportunity risk ({opportunity_risk}) exceeds user tolerance.")
        #    return None
            
        # 2. Is the overall portfolio risk too high?
        if risk_analysis['risk_score'] > 70: # Example threshold
            logger.warning(f"Overall portfolio risk ({risk_analysis['risk_score']}) is high, avoiding new tactical trades.")
            return None

        # 3. Do we have enough cash?
        # Determine trade size (e.g., 1-5% of portfolio value)
        trade_size_pct = 2.0 
        trade_amount = portfolio_data['total_value'] * (trade_size_pct / 100.0)
        if not self.portfolio_manager.has_sufficient_cash(user_id, trade_amount):
             logger.warning(f"Insufficient cash (${portfolio_data['cash']:.2f}) for tactical trade of ${trade_amount:.2f}.")
             return None

        # If checks pass, generate a trade recommendation
        decision = {
            'action': 'BUY',
            'asset': opportunity.get('asset'),
            'asset_type': opportunity.get('type'),
            'amount': trade_amount,
            'rationale': f"Tactical allocation based on opportunity score ({opportunity.get('score')}) and rationale: {opportunity.get('rationale')}",
            'decision_type': 'TACTICAL'
        }
        
        logger.info(f"Recommended tactical BUY decision for user {user_id}: {decision}")
        return decision
        
    # Placeholder for risk level check - needs user risk profile access
    # def _is_risk_level_acceptable(self, opportunity_risk: str, user_risk_tolerance: Dict[str, Any]) -> bool:
    #     risk_map = {'Low': 1, 'Moderate': 2, 'High': 3, 'Very High': 4}
    #     user_tolerance_level = user_risk_tolerance.get('risk_level', 'Moderate') # e.g., 'Conservative', 'Moderate', 'Aggressive'
    #     # Map user tolerance to a max acceptable risk number
    #     max_acceptable = {'Conservative': 2, 'Moderate': 3, 'Aggressive': 4}.get(user_tolerance_level, 2)
    #     return risk_map.get(opportunity_risk, 2) <= max_acceptable
