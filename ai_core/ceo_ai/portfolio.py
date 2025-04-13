import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class PortfolioManager:
    """
    Portfolio Manager for CEO AI
    
    Responsible for:
    - Managing portfolio data for users
    - Tracking asset allocations and positions
    - Handling cash flows (deposits and withdrawals)
    - Recording transactions
    """
    
    def __init__(self):
        """Initialize the Portfolio Manager"""
        # In-memory storage for portfolios (would use database in production)
        self.portfolios = {}
        self.transactions = {}
        logger.info("Portfolio Manager initialized")
    
    def get_portfolio_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get portfolio data for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing portfolio data
        """
        logger.info(f"Getting portfolio data for user {user_id}")
        
        # Check if we have portfolio data for this user
        if user_id not in self.portfolios:
            # Initialize portfolio with default values
            self._initialize_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        
        # Add calculated fields
        portfolio['performance'] = self._calculate_performance(user_id)
        
        return portfolio
    
    def get_portfolio_value(self, user_id: int) -> float:
        """
        Get total portfolio value for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Total portfolio value
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        return self.portfolios[user_id]['total_value']
    
    def get_cash_balance(self, user_id: int) -> float:
        """
        Get cash balance for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Cash balance
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        return self.portfolios[user_id]['cash']
    
    def get_asset_allocation(self, user_id: int) -> Dict[str, Any]:
        """
        Get current asset allocation for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing asset allocation percentages
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        total_value = portfolio['total_value']
        
        # Calculate top-level allocation percentages
        allocation = {
            'top_level': {
                'Equity': 0,
                'Bonds': 0,
                'Cash': 0,
                'Crypto': 0
            },
            'Equity': {},
            'Crypto': {}
        }
        
        # Calculate equity allocation
        equity_value = sum(asset['value'] for asset in portfolio['assets'] 
                          if asset['category'] == 'Equity')
        if equity_value > 0:
            allocation['top_level']['Equity'] = (equity_value / total_value) * 100
            
            # Calculate specific equity allocations
            equity_subcategories = {}
            for asset in portfolio['assets']:
                if asset['category'] == 'Equity':
                    subcategory = asset['subcategory']
                    if subcategory not in equity_subcategories:
                        equity_subcategories[subcategory] = 0
                    equity_subcategories[subcategory] += asset['value']
            
            for subcategory, value in equity_subcategories.items():
                allocation['Equity'][subcategory] = (value / equity_value) * 100
        
        # Calculate crypto allocation
        crypto_value = sum(asset['value'] for asset in portfolio['assets'] 
                          if asset['category'] == 'Crypto')
        if crypto_value > 0:
            allocation['top_level']['Crypto'] = (crypto_value / total_value) * 100
            
            # Calculate specific crypto allocations
            crypto_subcategories = {}
            for asset in portfolio['assets']:
                if asset['category'] == 'Crypto':
                    subcategory = asset['subcategory']
                    if subcategory not in crypto_subcategories:
                        crypto_subcategories[subcategory] = 0
                    crypto_subcategories[subcategory] += asset['value']
            
            for subcategory, value in crypto_subcategories.items():
                allocation['Crypto'][subcategory] = (value / crypto_value) * 100
        
        # Calculate bond allocation
        bond_value = sum(asset['value'] for asset in portfolio['assets'] 
                        if asset['category'] == 'Bonds')
        allocation['top_level']['Bonds'] = (bond_value / total_value) * 100
        
        # Calculate cash allocation
        allocation['top_level']['Cash'] = (portfolio['cash'] / total_value) * 100
        
        # Round percentages to 1 decimal place
        for category in allocation['top_level']:
            allocation['top_level'][category] = round(allocation['top_level'][category], 1)
        
        for category in ['Equity', 'Crypto']:
            for subcategory in allocation[category]:
                allocation[category][subcategory] = round(allocation[category][subcategory], 1)
        
        return allocation
    
    def update_cash_balance(self, user_id: int, amount: float, transaction_type: str) -> None:
        """
        Update cash balance for a user
        
        Args:
            user_id: User ID
            amount: Amount (positive value)
            transaction_type: DEPOSIT or WITHDRAWAL
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        
        if transaction_type == 'DEPOSIT':
            portfolio['cash'] += amount
            portfolio['total_value'] += amount
            logger.info(f"Deposited ${amount} for user {user_id}")
        elif transaction_type == 'WITHDRAWAL':
            if portfolio['cash'] >= amount:
                portfolio['cash'] -= amount
                portfolio['total_value'] -= amount
                logger.info(f"Withdrew ${amount} for user {user_id}")
            else:
                logger.warning(f"Insufficient cash for withdrawal: ${amount} > ${portfolio['cash']}")
                raise ValueError(f"Insufficient cash for withdrawal")
        else:
            logger.error(f"Invalid transaction type: {transaction_type}")
            raise ValueError(f"Invalid transaction type: {transaction_type}")
        
        # Record transaction
        self._record_transaction(user_id, transaction_type, amount, None, None)
    
    def has_sufficient_cash(self, user_id: int, amount: float) -> bool:
        """
        Check if user has sufficient cash
        
        Args:
            user_id: User ID
            amount: Amount to check
            
        Returns:
            True if user has sufficient cash, False otherwise
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        return self.portfolios[user_id]['cash'] >= amount
    
    def needs_rebalancing(self, user_id: int, threshold: float = 5.0) -> bool:
        """
        Check if portfolio needs rebalancing
        
        Args:
            user_id: User ID
            threshold: Percentage threshold for rebalancing
            
        Returns:
            True if portfolio needs rebalancing, False otherwise
        """
        # In a real implementation, this would compare current allocation to target
        # For this placeholder, return True if the portfolio exists (to trigger rebalancing)
        return user_id in self.portfolios
    
    def add_user_goal(self, user_id: int, goal_id: int, name: str, 
                    target_amount: float, target_date, priority: str) -> None:
        """
        Add a new financial goal for a user
        
        Args:
            user_id: User ID
            goal_id: Goal ID
            name: Goal name
            target_amount: Target amount
            target_date: Target date (datetime object)
            priority: Priority (High, Medium, Low)
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        
        # Add goal to portfolio
        if 'goals' not in portfolio:
            portfolio['goals'] = []
        
        goal = {
            'id': goal_id,
            'name': name,
            'target_amount': target_amount,
            'current_amount': 0.0,  # Start at 0
            'target_date': target_date.isoformat(),
            'priority': priority,
            'created_at': datetime.now().isoformat()
        }
        
        portfolio['goals'].append(goal)
        logger.info(f"Added goal {name} for user {user_id}")
    
    def update_user_settings(self, user_id: int, trading_enabled: bool) -> None:
        """
        Update user settings
        
        Args:
            user_id: User ID
            trading_enabled: Whether trading is enabled
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        portfolio['settings'] = {
            'trading_enabled': trading_enabled
        }
        
        logger.info(f"Updated settings for user {user_id}: trading_enabled={trading_enabled}")
    
    def record_trades(self, user_id: int, trades: List[Dict[str, Any]]) -> None:
        """
        Record trades executed by worker AIs
        
        Args:
            user_id: User ID
            trades: List of trade dictionaries
        """
        if user_id not in self.portfolios:
            self._initialize_portfolio(user_id)
        
        portfolio = self.portfolios[user_id]
        
        for trade in trades:
            symbol = trade.get('symbol')
            quantity = trade.get('quantity', 0)
            price = trade.get('price', 0)
            action = trade.get('action', 'BUY')
            asset_name = trade.get('asset_name', symbol)
            category = trade.get('category', 'Equity')
            subcategory = trade.get('subcategory', 'Large Cap')
            
            trade_value = quantity * price
            
            if action == 'BUY':
                # Check if we already have this asset
                existing_asset = next((a for a in portfolio['assets'] if a['symbol'] == symbol), None)
                
                if existing_asset:
                    # Update existing asset
                    avg_price = ((existing_asset['quantity'] * existing_asset['price']) + trade_value) / (existing_asset['quantity'] + quantity)
                    existing_asset['quantity'] += quantity
                    existing_asset['price'] = avg_price
                    existing_asset['value'] = existing_asset['quantity'] * existing_asset['price']
                else:
                    # Add new asset
                    portfolio['assets'].append({
                        'symbol': symbol,
                        'name': asset_name,
                        'category': category,
                        'subcategory': subcategory,
                        'quantity': quantity,
                        'price': price,
                        'value': trade_value
                    })
                
                # Deduct cash
                portfolio['cash'] -= trade_value
                
                # Record transaction
                self._record_transaction(user_id, 'BUY', trade_value, symbol, quantity)
                
                logger.info(f"Recorded BUY trade for user {user_id}: {quantity} {symbol} @ ${price}")
                
            elif action == 'SELL':
                # Find the asset
                existing_asset = next((a for a in portfolio['assets'] if a['symbol'] == symbol), None)
                
                if existing_asset and existing_asset['quantity'] >= quantity:
                    # Update existing asset
                    existing_asset['quantity'] -= quantity
                    existing_asset['value'] = existing_asset['quantity'] * existing_asset['price']
                    
                    # If quantity is 0, remove the asset
                    if existing_asset['quantity'] == 0:
                        portfolio['assets'].remove(existing_asset)
                    
                    # Add cash
                    portfolio['cash'] += trade_value
                    
                    # Record transaction
                    self._record_transaction(user_id, 'SELL', trade_value, symbol, quantity)
                    
                    logger.info(f"Recorded SELL trade for user {user_id}: {quantity} {symbol} @ ${price}")
                else:
                    logger.warning(f"Cannot sell asset {symbol}: asset not found or insufficient quantity")
            
            # Update total portfolio value
            self._update_portfolio_value(user_id)
    
    def _initialize_portfolio(self, user_id: int) -> None:
        """
        Initialize portfolio for a new user
        
        Args:
            user_id: User ID
        """
        # Create a new portfolio with default values
        self.portfolios[user_id] = {
            'user_id': user_id,
            'total_value': 0.0,
            'cash': 0.0,
            'assets': [],
            'goals': [],
            'settings': {
                'trading_enabled': True
            },
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat()
        }
        
        # Initialize transactions list
        self.transactions[user_id] = []
        
        logger.info(f"Initialized portfolio for user {user_id}")
    
    def _update_portfolio_value(self, user_id: int) -> None:
        """
        Update total portfolio value
        
        Args:
            user_id: User ID
        """
        portfolio = self.portfolios[user_id]
        
        # Sum the value of all assets and cash
        asset_value = sum(asset['value'] for asset in portfolio['assets'])
        portfolio['total_value'] = portfolio['cash'] + asset_value
        
        # Update last_updated timestamp
        portfolio['last_updated'] = datetime.now().isoformat()
    
    def _record_transaction(self, user_id: int, transaction_type: str, 
                          amount: float, symbol: Optional[str], quantity: Optional[float]) -> None:
        """
        Record a transaction
        
        Args:
            user_id: User ID
            transaction_type: Transaction type (DEPOSIT, WITHDRAWAL, BUY, SELL)
            amount: Transaction amount
            symbol: Asset symbol (for BUY/SELL)
            quantity: Asset quantity (for BUY/SELL)
        """
        if user_id not in self.transactions:
            self.transactions[user_id] = []
        
        transaction = {
            'id': len(self.transactions[user_id]) + 1,
            'type': transaction_type,
            'amount': amount,
            'date': datetime.now().isoformat()
        }
        
        if transaction_type == 'DEPOSIT':
            transaction['description'] = f"Deposit of ${amount:.2f}"
        elif transaction_type == 'WITHDRAWAL':
            transaction['description'] = f"Withdrawal of ${amount:.2f}"
        elif transaction_type in ['BUY', 'SELL']:
            transaction['asset_symbol'] = symbol
            transaction['quantity'] = quantity
            transaction['description'] = f"{transaction_type} {quantity} {symbol} for ${amount:.2f}"
        
        self.transactions[user_id].append(transaction)
        logger.info(f"Recorded transaction: {transaction}")
    
    def _calculate_performance(self, user_id: int) -> Dict[str, float]:
        """
        Calculate portfolio performance metrics
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing performance metrics
        """
        # In a real implementation, this would calculate actual performance metrics
        # For this placeholder, return simulated data
        return {
            'daily': 0.75,
            'weekly': 2.31,
            'monthly': 5.67,
            'yearly': 12.42
        }
