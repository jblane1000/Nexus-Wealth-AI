import logging
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """
    Risk Analyzer for CEO AI
    
    Responsible for:
    - Analyzing portfolio risk metrics
    - Evaluating user risk tolerance
    - Monitoring for risky positions or market conditions
    - Generating risk alerts and recommendations
    """
    
    def __init__(self):
        """Initialize the Risk Analyzer"""
        # Cache of risk analyses
        self.risk_analyses = {}
        # Constants for VaR calculations
        self.confidence_level = 0.95  # 95% confidence level for VaR
        logger.info("Risk Analyzer initialized")
    
    def analyze_portfolio_risk(self, user_id: int, portfolio_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze risk metrics for a portfolio
        
        Args:
            user_id: User ID
            portfolio_data: Portfolio data dictionary
            
        Returns:
            Dictionary containing risk metrics
        """
        logger.info(f"Analyzing portfolio risk for user {user_id}")
        
        # Extract portfolio assets
        assets = portfolio_data.get('assets', [])
        total_value = portfolio_data.get('total_value', 0)
        
        if total_value == 0:
            logger.warning(f"Portfolio for user {user_id} has zero value")
            return self._get_default_risk_metrics()
        
        # Calculate risk metrics
        volatility = self._calculate_portfolio_volatility(assets)
        var = self._calculate_value_at_risk(total_value, volatility)
        sharpe_ratio = self._calculate_sharpe_ratio(portfolio_data)
        beta = self._calculate_portfolio_beta(assets)
        risk_concentration = self._calculate_risk_concentration(assets, total_value)
        drawdown = self._calculate_max_drawdown(user_id, total_value)
        
        # Generate risk score (1-100, lower is less risky)
        risk_score = self._calculate_risk_score(
            volatility, var, sharpe_ratio, beta, risk_concentration
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Assemble risk analysis
        risk_analysis = {
            'timestamp': datetime.now().isoformat(),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'metrics': {
                'volatility': volatility,
                'value_at_risk': var,
                'sharpe_ratio': sharpe_ratio,
                'beta': beta,
                'risk_concentration': risk_concentration,
                'max_drawdown': drawdown
            },
            'alerts': [],
            'recommendations': []
        }
        
        # Generate alerts and recommendations
        self._generate_alerts_and_recommendations(risk_analysis, portfolio_data)
        
        # Cache the analysis
        self.risk_analyses[user_id] = risk_analysis
        
        logger.info(f"Risk analysis completed for user {user_id}: score={risk_score}, level={risk_level}")
        return risk_analysis
    
    def is_within_risk_tolerance(self, user_id: int, 
                               risk_tolerance: Dict[str, Any], 
                               portfolio_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if portfolio is within user's risk tolerance
        
        Args:
            user_id: User ID
            risk_tolerance: Risk tolerance dictionary
            portfolio_data: Portfolio data dictionary
            
        Returns:
            Tuple of (is_within_tolerance, [list of issues])
        """
        # Analyze portfolio risk if not already analyzed
        if user_id not in self.risk_analyses:
            self.analyze_portfolio_risk(user_id, portfolio_data)
        
        risk_analysis = self.risk_analyses[user_id]
        issues = []
        
        # Check if risk score exceeds tolerance
        max_risk_score = risk_tolerance.get('max_risk_score', 80)
        if risk_analysis['risk_score'] > max_risk_score:
            issues.append(f"Risk score ({risk_analysis['risk_score']}) exceeds maximum tolerance ({max_risk_score})")
        
        # Check value at risk
        max_var_pct = risk_tolerance.get('max_var_pct', 15)
        var_pct = risk_analysis['metrics']['value_at_risk'] / portfolio_data['total_value'] * 100
        if var_pct > max_var_pct:
            issues.append(f"Value at Risk ({var_pct:.1f}%) exceeds maximum tolerance ({max_var_pct}%)")
        
        # Check concentration risk
        max_concentration = risk_tolerance.get('max_concentration', 25)
        if risk_analysis['metrics']['risk_concentration'] > max_concentration:
            issues.append(f"Concentration risk ({risk_analysis['metrics']['risk_concentration']:.1f}%) " +
                         f"exceeds maximum tolerance ({max_concentration}%)")
        
        # Within tolerance if no issues found
        is_within_tolerance = len(issues) == 0
        
        logger.info(f"Risk tolerance check for user {user_id}: {is_within_tolerance}")
        if not is_within_tolerance:
            logger.info(f"Risk tolerance issues: {issues}")
        
        return is_within_tolerance, issues
    
    def get_risk_level(self, user_id: int) -> str:
        """
        Get current risk level for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Risk level string (Low, Moderate, High, Very High, Extreme)
        """
        if user_id in self.risk_analyses:
            return self.risk_analyses[user_id]['risk_level']
        else:
            logger.warning(f"No risk analysis available for user {user_id}")
            return "Unknown"
    
    def should_adjust_strategy(self, user_id: int, market_conditions: Dict[str, Any]) -> bool:
        """
        Determine if strategy should be adjusted based on risk
        
        Args:
            user_id: User ID
            market_conditions: Market conditions dictionary
            
        Returns:
            True if strategy should be adjusted, False otherwise
        """
        if user_id not in self.risk_analyses:
            logger.warning(f"No risk analysis available for user {user_id}")
            return False
        
        risk_level = self.risk_analyses[user_id]['risk_level']
        volatility = market_conditions.get('volatility', 'moderate')
        
        # Adjust strategy if risk level is high and market volatility is high
        if risk_level in ['High', 'Very High', 'Extreme'] and volatility == 'high':
            logger.info(f"Recommending strategy adjustment for user {user_id} " +
                       f"due to high risk ({risk_level}) and market volatility ({volatility})")
            return True
        
        return False
    
    def identify_risky_assets(self, user_id: int, 
                            portfolio_data: Dict[str, Any], 
                            threshold: float = 15.0) -> List[Dict[str, Any]]:
        """
        Identify assets that are too risky based on volatility
        
        Args:
            user_id: User ID
            portfolio_data: Portfolio data dictionary
            threshold: Volatility threshold percentage
            
        Returns:
            List of risky assets
        """
        risky_assets = []
        
        for asset in portfolio_data.get('assets', []):
            # In a real implementation, this would fetch actual volatility data
            # For this placeholder, we'll simulate volatility based on asset category
            asset_volatility = self._get_simulated_asset_volatility(asset)
            
            if asset_volatility > threshold:
                risky_assets.append({
                    'symbol': asset['symbol'],
                    'name': asset['name'],
                    'volatility': asset_volatility,
                    'value': asset['value'],
                    'allocation_pct': (asset['value'] / portfolio_data['total_value']) * 100
                })
        
        if risky_assets:
            logger.info(f"Identified {len(risky_assets)} risky assets for user {user_id}")
        
        return risky_assets
    
    def _calculate_portfolio_volatility(self, assets: List[Dict[str, Any]]) -> float:
        """
        Calculate portfolio volatility
        
        Args:
            assets: List of asset dictionaries
            
        Returns:
            Annualized volatility percentage
        """
        # In a real implementation, this would use historical return data
        # and compute the standard deviation, considering covariance between assets
        # For this placeholder, we'll simulate a realistic volatility value
        
        if not assets:
            return 0.0
        
        # Simulate volatility based on asset composition
        total_value = sum(asset['value'] for asset in assets)
        weighted_volatility = 0.0
        
        if total_value == 0:
            return 0.0
        
        for asset in assets:
            # Simulate asset volatility based on its category
            asset_volatility = self._get_simulated_asset_volatility(asset)
            weight = asset['value'] / total_value
            weighted_volatility += weight * asset_volatility
        
        # Add a small random factor for variation
        import random
        variation = random.uniform(0.9, 1.1)
        
        return weighted_volatility * variation
    
    def _get_simulated_asset_volatility(self, asset: Dict[str, Any]) -> float:
        """
        Get simulated volatility for an asset based on category
        
        Args:
            asset: Asset dictionary
            
        Returns:
            Annualized volatility percentage
        """
        category = asset.get('category', 'Equity')
        subcategory = asset.get('subcategory', '')
        
        # Base volatility by category
        base_volatility = {
            'Cash': 0.5,
            'Bonds': 5.0,
            'Equity': 15.0,
            'Crypto': 40.0
        }.get(category, 10.0)
        
        # Adjust for subcategory
        if category == 'Equity':
            subcategory_multiplier = {
                'Large Cap': 0.8,
                'Mid Cap': 1.0,
                'Small Cap': 1.3,
                'International': 1.1,
                'Emerging Markets': 1.5
            }.get(subcategory, 1.0)
            base_volatility *= subcategory_multiplier
        
        if category == 'Crypto':
            subcategory_multiplier = {
                'Bitcoin': 0.9,
                'Ethereum': 1.1,
                'Altcoins': 1.5
            }.get(subcategory, 1.0)
            base_volatility *= subcategory_multiplier
        
        # Add a small random factor for variation
        import random
        variation = random.uniform(0.9, 1.1)
        
        return base_volatility * variation
    
    def _calculate_value_at_risk(self, portfolio_value: float, volatility: float) -> float:
        """
        Calculate Value at Risk (VaR)
        
        Args:
            portfolio_value: Total portfolio value
            volatility: Annualized volatility percentage
            
        Returns:
            Value at Risk amount
        """
        # Convert volatility to daily (assuming 252 trading days)
        daily_volatility = volatility / math.sqrt(252)
        
        # Calculate VaR for specified confidence level
        import scipy.stats as stats
        z_score = stats.norm.ppf(self.confidence_level)
        
        # Simplified VaR calculation
        var = portfolio_value * (daily_volatility / 100) * z_score
        
        return abs(var)  # VaR is always positive
    
    def _calculate_sharpe_ratio(self, portfolio_data: Dict[str, Any]) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            portfolio_data: Portfolio data dictionary
            
        Returns:
            Sharpe Ratio
        """
        # In a real implementation, this would use actual returns data
        # For this placeholder, return a simulated value
        
        # Simulate portfolio returns based on composition
        assets = portfolio_data.get('assets', [])
        
        if not assets:
            return 0.0
        
        # Simulate expected return based on asset composition
        total_value = sum(asset['value'] for asset in assets)
        expected_return = 0.0
        
        if total_value == 0:
            return 0.0
        
        for asset in assets:
            category = asset.get('category', 'Equity')
            # Simulate asset expected return
            asset_return = {
                'Cash': 1.0,
                'Bonds': 3.0,
                'Equity': 8.0,
                'Crypto': 15.0
            }.get(category, 5.0)
            
            weight = asset['value'] / total_value
            expected_return += weight * asset_return
        
        # Risk-free rate (treasury yield)
        risk_free_rate = 2.0  # Assuming 2% yield
        
        # Calculate volatility
        volatility = self._calculate_portfolio_volatility(assets)
        
        # Calculate Sharpe ratio
        if volatility == 0:
            return 0.0
        
        sharpe_ratio = (expected_return - risk_free_rate) / volatility
        
        return sharpe_ratio
    
    def _calculate_portfolio_beta(self, assets: List[Dict[str, Any]]) -> float:
        """
        Calculate portfolio beta (market sensitivity)
        
        Args:
            assets: List of asset dictionaries
            
        Returns:
            Portfolio beta
        """
        # In a real implementation, this would use regression of returns
        # against market index returns
        # For this placeholder, return a simulated value
        
        if not assets:
            return 1.0
        
        total_value = sum(asset['value'] for asset in assets)
        weighted_beta = 0.0
        
        if total_value == 0:
            return 1.0
        
        for asset in assets:
            category = asset.get('category', 'Equity')
            subcategory = asset.get('subcategory', '')
            
            # Simulate asset beta
            asset_beta = 1.0  # Market neutral by default
            
            if category == 'Equity':
                asset_beta = {
                    'Large Cap': 0.95,
                    'Mid Cap': 1.05,
                    'Small Cap': 1.15,
                    'International': 0.9,
                    'Emerging Markets': 1.2
                }.get(subcategory, 1.0)
            elif category == 'Bonds':
                asset_beta = 0.2
            elif category == 'Cash':
                asset_beta = 0.0
            elif category == 'Crypto':
                asset_beta = 1.5  # Crypto often has low correlation with market
            
            weight = asset['value'] / total_value
            weighted_beta += weight * asset_beta
        
        return weighted_beta
    
    def _calculate_risk_concentration(self, assets: List[Dict[str, Any]], total_value: float) -> float:
        """
        Calculate risk concentration (percentage in single largest position)
        
        Args:
            assets: List of asset dictionaries
            total_value: Total portfolio value
            
        Returns:
            Concentration percentage
        """
        if not assets or total_value == 0:
            return 0.0
        
        # Find largest position
        largest_position = max(assets, key=lambda a: a['value'], default={'value': 0})
        
        # Calculate percentage of portfolio in largest position
        concentration = (largest_position['value'] / total_value) * 100
        
        return concentration
    
    def _calculate_max_drawdown(self, user_id: int, current_value: float) -> float:
        """
        Calculate maximum drawdown
        
        Args:
            user_id: User ID
            current_value: Current portfolio value
            
        Returns:
            Maximum drawdown percentage
        """
        # In a real implementation, this would use historical portfolio values
        # For this placeholder, return a simulated value
        
        # Simulate a random drawdown between 5% and 15%
        import random
        max_drawdown = random.uniform(5.0, 15.0)
        
        return max_drawdown
    
    def _calculate_risk_score(self, volatility: float, var: float, 
                            sharpe_ratio: float, beta: float, 
                            risk_concentration: float) -> int:
        """
        Calculate overall risk score
        
        Args:
            volatility: Portfolio volatility
            var: Value at Risk
            sharpe_ratio: Sharpe Ratio
            beta: Portfolio beta
            risk_concentration: Risk concentration
            
        Returns:
            Risk score (1-100)
        """
        # Normalize inputs to 0-100 scale
        vol_score = min(100, volatility * 3)  # Volatility of 33% = max score
        var_score = min(100, var / 1000 * 50)  # VaR of $2000 = max score for $10000 portfolio
        
        # Sharpe ratio: higher is better, so inverse the score
        sharpe_score = max(0, 100 - sharpe_ratio * 40)  # Sharpe of 2.5 = 0 score (very good)
        
        # Beta: 1.0 is neutral, higher is more risky
        beta_score = min(100, max(0, (beta - 0.5) * 75))  # Beta of 1.8 = max score
        
        # Concentration: higher is more risky
        conc_score = min(100, risk_concentration * 2)  # Concentration of 50% = max score
        
        # Weight the factors (adjust weights as needed)
        weights = {
            'volatility': 0.35,
            'var': 0.15,
            'sharpe': 0.20,
            'beta': 0.15,
            'concentration': 0.15
        }
        
        # Calculate weighted average
        risk_score = (
            vol_score * weights['volatility'] +
            var_score * weights['var'] +
            sharpe_score * weights['sharpe'] +
            beta_score * weights['beta'] +
            conc_score * weights['concentration']
        )
        
        # Round to nearest integer
        return round(risk_score)
    
    def _determine_risk_level(self, risk_score: int) -> str:
        """
        Determine risk level from risk score
        
        Args:
            risk_score: Risk score (1-100)
            
        Returns:
            Risk level string
        """
        if risk_score < 20:
            return "Very Low"
        elif risk_score < 40:
            return "Low"
        elif risk_score < 60:
            return "Moderate"
        elif risk_score < 80:
            return "High"
        else:
            return "Very High"
    
    def _generate_alerts_and_recommendations(self, risk_analysis: Dict[str, Any],
                                           portfolio_data: Dict[str, Any]) -> None:
        """
        Generate risk alerts and recommendations
        
        Args:
            risk_analysis: Risk analysis dictionary (will be modified)
            portfolio_data: Portfolio data dictionary
        """
        metrics = risk_analysis['metrics']
        alerts = risk_analysis['alerts']
        recommendations = risk_analysis['recommendations']
        
        # Check volatility
        if metrics['volatility'] > 20:
            alerts.append({
                'type': 'HIGH_VOLATILITY',
                'severity': 'WARNING',
                'message': f"Portfolio volatility is high at {metrics['volatility']:.1f}%"
            })
            recommendations.append({
                'action': 'REDUCE_VOLATILITY',
                'message': "Consider reducing exposure to volatile assets"
            })
        
        # Check value at risk
        total_value = portfolio_data.get('total_value', 0)
        if total_value > 0:
            var_pct = (metrics['value_at_risk'] / total_value) * 100
            if var_pct > 5:
                alerts.append({
                    'type': 'HIGH_VAR',
                    'severity': 'WARNING',
                    'message': f"Value at Risk is {var_pct:.1f}% of portfolio value"
                })
                recommendations.append({
                    'action': 'HEDGING',
                    'message': "Consider hedging strategies to reduce downside risk"
                })
        
        # Check concentration risk
        if metrics['risk_concentration'] > 20:
            alerts.append({
                'type': 'HIGH_CONCENTRATION',
                'severity': 'WARNING',
                'message': f"Portfolio concentration is high at {metrics['risk_concentration']:.1f}%"
            })
            recommendations.append({
                'action': 'DIVERSIFY',
                'message': "Diversify holdings to reduce concentration risk"
            })
        
        # Check beta
        if metrics['beta'] > 1.3:
            alerts.append({
                'type': 'HIGH_BETA',
                'severity': 'INFO',
                'message': f"Portfolio beta is high at {metrics['beta']:.2f}"
            })
            recommendations.append({
                'action': 'REDUCE_BETA',
                'message': "Consider reducing market exposure during volatile periods"
            })
    
    def _get_default_risk_metrics(self) -> Dict[str, Any]:
        """
        Get default risk metrics for an empty portfolio
        
        Returns:
            Dictionary of default risk metrics
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'risk_score': 0,
            'risk_level': 'None',
            'metrics': {
                'volatility': 0.0,
                'value_at_risk': 0.0,
                'sharpe_ratio': 0.0,
                'beta': 0.0,
                'risk_concentration': 0.0,
                'max_drawdown': 0.0
            },
            'alerts': [],
            'recommendations': [
                {
                    'action': 'INITIAL_INVESTMENT',
                    'message': "Make your first investment to begin portfolio analysis"
                }
            ]
        }
