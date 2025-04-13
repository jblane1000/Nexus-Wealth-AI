import logging
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Module imports
from ceo_ai.strategy import StrategyEngine
from ceo_ai.portfolio import PortfolioManager
from ceo_ai.risk import RiskAnalyzer
from ceo_ai.market import MarketAnalyzer
from ceo_ai.decision import DecisionEngine

logger = logging.getLogger(__name__)

class CEOAgent:
    """
    CEO AI Agent - Central decision engine for Nexus Wealth AI
    
    Responsibilities:
    - Interpret user inputs (goals, risk, constraints)
    - Formulate master investment strategy
    - Monitor markets and portfolio
    - Make high-level strategic decisions
    - Delegate tasks to Worker AIs
    - Ensure portfolio alignment with goals
    """
    
    def __init__(self, rag_system, mcu_server):
        """
        Initialize the CEO AI Agent
        
        Args:
            rag_system: RAG System instance for information retrieval
            mcu_server: MCU Server instance for worker communication
        """
        self.rag_system = rag_system
        self.mcu_server = mcu_server
        
        # Initialize sub-components
        self.strategy_engine = StrategyEngine()
        self.portfolio_manager = PortfolioManager()
        self.risk_analyzer = RiskAnalyzer()
        self.market_analyzer = MarketAnalyzer(rag_system)
        self.decision_engine = DecisionEngine(
            strategy_engine=self.strategy_engine,
            portfolio_manager=self.portfolio_manager,
            risk_analyzer=self.risk_analyzer,
            market_analyzer=self.market_analyzer
        )
        
        # State tracking
        self.user_profiles = {}  # Cache of user profiles
        self.active_tasks = {}   # Track tasks delegated to workers
        
        logger.info("CEO AI Agent initialized")
    
    def get_portfolio_data(self, user_id: int) -> Dict[str, Any]:
        """
        Get portfolio data for a user
        
        Args:
            user_id: User ID
            
        Returns:
            Dict containing portfolio data
        """
        logger.info(f"Getting portfolio data for user {user_id}")
        return self.portfolio_manager.get_portfolio_data(user_id)
    
    def get_market_summary(self) -> Dict[str, Any]:
        """
        Get market summary data
        
        Returns:
            Dict containing market summary data
        """
        logger.info("Getting market summary")
        return self.market_analyzer.get_market_summary()
    
    def get_recent_decisions(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Get recent AI decisions for a user
        
        Args:
            user_id: User ID
            
        Returns:
            List of decision objects
        """
        logger.info(f"Getting recent decisions for user {user_id}")
        return self.decision_engine.get_recent_decisions(user_id)
    
    def update_risk_profile(self, user_id: int, risk_level: str, risk_score: int) -> None:
        """
        Update a user's risk profile
        
        Args:
            user_id: User ID
            risk_level: Risk level (Conservative, Moderate, Aggressive)
            risk_score: Risk score
        """
        logger.info(f"Updating risk profile for user {user_id}: {risk_level} ({risk_score})")
        
        # Update risk profile in database
        self.risk_analyzer.update_user_risk_profile(user_id, risk_level, risk_score)
        
        # Update user profile cache
        if user_id in self.user_profiles:
            self.user_profiles[user_id]['risk_level'] = risk_level
            self.user_profiles[user_id]['risk_score'] = risk_score
        
        # Reevaluate portfolio strategy based on new risk profile
        self.strategy_engine.reevaluate_strategy(user_id)
        
        # Delegate portfolio rebalancing if needed
        if self.portfolio_manager.needs_rebalancing(user_id):
            self._delegate_portfolio_rebalancing(user_id)
    
    def add_goal(self, user_id: int, goal_id: int, name: str, 
                target_amount: float, target_date: str, priority: str) -> None:
        """
        Add a new financial goal for a user
        
        Args:
            user_id: User ID
            goal_id: Goal ID
            name: Goal name
            target_amount: Target amount
            target_date: Target date (ISO format)
            priority: Priority (High, Medium, Low)
        """
        logger.info(f"Adding goal for user {user_id}: {name}, ${target_amount}, {target_date}")
        
        # Convert target_date string to datetime
        try:
            target_date_obj = datetime.fromisoformat(target_date)
        except ValueError:
            logger.error(f"Invalid date format: {target_date}")
            raise ValueError(f"Invalid date format: {target_date}")
        
        # Add goal to database
        self.portfolio_manager.add_user_goal(
            user_id, goal_id, name, target_amount, target_date_obj, priority
        )
        
        # Reevaluate portfolio strategy based on new goal
        self.strategy_engine.reevaluate_strategy(user_id)
        
        # Delegate portfolio rebalancing if needed
        if self.portfolio_manager.needs_rebalancing(user_id):
            self._delegate_portfolio_rebalancing(user_id)
    
    def process_cash_flow(self, user_id: int, amount: float, transaction_type: str) -> None:
        """
        Process a deposit or withdrawal
        
        Args:
            user_id: User ID
            amount: Amount (positive for deposit, negative for withdrawal)
            transaction_type: DEPOSIT or WITHDRAWAL
        """
        logger.info(f"Processing {transaction_type} of ${amount} for user {user_id}")
        
        # Update portfolio with cash flow
        self.portfolio_manager.update_cash_balance(user_id, amount, transaction_type)
        
        # For deposits, delegate investment of new funds
        if transaction_type == 'DEPOSIT' and amount > 0:
            self._delegate_cash_investment(user_id, amount)
        
        # For withdrawals, delegate liquidation of assets if needed
        elif transaction_type == 'WITHDRAWAL' and amount > 0:
            if not self.portfolio_manager.has_sufficient_cash(user_id, amount):
                self._delegate_asset_liquidation(user_id, amount)
    
    def update_user_settings(self, user_id: int, trading_enabled: bool) -> None:
        """
        Update user settings
        
        Args:
            user_id: User ID
            trading_enabled: Whether trading is enabled
        """
        logger.info(f"Updating settings for user {user_id}: trading_enabled={trading_enabled}")
        
        # Update settings in database
        self.portfolio_manager.update_user_settings(user_id, trading_enabled)
        
        # Update user profile cache
        if user_id in self.user_profiles:
            self.user_profiles[user_id]['trading_enabled'] = trading_enabled
        
        # If trading disabled, cancel any pending trades
        if not trading_enabled:
            self._cancel_pending_trades(user_id)
    
    def _delegate_portfolio_rebalancing(self, user_id: int) -> None:
        """
        Delegate portfolio rebalancing to appropriate worker AIs
        
        Args:
            user_id: User ID
        """
        logger.info(f"Delegating portfolio rebalancing for user {user_id}")
        
        # Get current portfolio allocation
        current_allocation = self.portfolio_manager.get_asset_allocation(user_id)
        
        # Get target allocation based on strategy
        target_allocation = self.strategy_engine.get_target_allocation(user_id)
        
        # Determine which assets need adjustment
        adjustments = self._calculate_allocation_adjustments(current_allocation, target_allocation)
        
        # Delegate tasks to appropriate worker AIs
        for asset_class, adjustment in adjustments.items():
            if abs(adjustment) < 0.01:  # Skip negligible adjustments
                continue
                
            if asset_class == 'Equity':
                self._delegate_to_equity_worker(user_id, adjustment, target_allocation.get('Equity', {}))
            elif asset_class == 'Crypto':
                self._delegate_to_crypto_worker(user_id, adjustment, target_allocation.get('Crypto', {}))
            
            # Log decision
            self.decision_engine.log_decision(
                user_id=user_id,
                decision_type='ALLOCATION_CHANGE',
                description=f"Adjusted {asset_class} allocation by {adjustment:.2f}%",
                data={
                    'asset_class': asset_class,
                    'adjustment': adjustment,
                    'reason': 'Portfolio rebalancing'
                }
            )
    
    def _delegate_cash_investment(self, user_id: int, amount: float) -> None:
        """
        Delegate investment of cash to appropriate worker AIs
        
        Args:
            user_id: User ID
            amount: Amount to invest
        """
        logger.info(f"Delegating investment of ${amount} for user {user_id}")
        
        # Get target allocation based on strategy
        target_allocation = self.strategy_engine.get_target_allocation(user_id)
        
        # Calculate amount to allocate to each asset class
        allocations = {}
        for asset_class, percentage in target_allocation.get('top_level', {}).items():
            if asset_class != 'Cash':  # Skip cash allocation
                allocations[asset_class] = amount * (percentage / 100)
        
        # Delegate tasks to appropriate worker AIs
        for asset_class, alloc_amount in allocations.items():
            if alloc_amount < 10:  # Skip tiny allocations
                continue
                
            if asset_class == 'Equity':
                self._delegate_to_equity_worker(
                    user_id, 
                    alloc_amount, 
                    target_allocation.get('Equity', {})
                )
            elif asset_class == 'Crypto':
                self._delegate_to_crypto_worker(
                    user_id, 
                    alloc_amount, 
                    target_allocation.get('Crypto', {})
                )
            
            # Log decision
            self.decision_engine.log_decision(
                user_id=user_id,
                decision_type='CASH_INVESTMENT',
                description=f"Allocated ${alloc_amount:.2f} to {asset_class}",
                data={
                    'asset_class': asset_class,
                    'amount': alloc_amount,
                    'reason': 'New deposit investment'
                }
            )
    
    def _delegate_asset_liquidation(self, user_id: int, amount: float) -> None:
        """
        Delegate liquidation of assets to appropriate worker AIs
        
        Args:
            user_id: User ID
            amount: Amount needed
        """
        logger.info(f"Delegating liquidation of assets worth ${amount} for user {user_id}")
        
        # Get current portfolio allocation
        current_allocation = self.portfolio_manager.get_asset_allocation(user_id)
        
        # Get target allocation based on strategy
        target_allocation = self.strategy_engine.get_target_allocation(user_id)
        
        # Calculate how much to liquidate from each asset class
        # while maintaining target allocation as closely as possible
        liquidation_plan = self._calculate_liquidation_plan(
            user_id, amount, current_allocation, target_allocation
        )
        
        # Delegate tasks to appropriate worker AIs
        for asset_class, liquidation_amount in liquidation_plan.items():
            if liquidation_amount < 10:  # Skip tiny liquidations
                continue
                
            if asset_class == 'Equity':
                self._delegate_to_equity_worker(
                    user_id, 
                    -liquidation_amount,  # Negative amount indicates selling
                    current_allocation.get('Equity', {})
                )
            elif asset_class == 'Crypto':
                self._delegate_to_crypto_worker(
                    user_id, 
                    -liquidation_amount,  # Negative amount indicates selling
                    current_allocation.get('Crypto', {})
                )
            
            # Log decision
            self.decision_engine.log_decision(
                user_id=user_id,
                decision_type='ASSET_LIQUIDATION',
                description=f"Liquidated ${liquidation_amount:.2f} of {asset_class}",
                data={
                    'asset_class': asset_class,
                    'amount': liquidation_amount,
                    'reason': 'Withdrawal request'
                }
            )
    
    def _delegate_to_equity_worker(self, user_id: int, amount: float, allocation: Dict[str, float]) -> None:
        """
        Delegate a task to the Equity Worker AI
        
        Args:
            user_id: User ID
            amount: Amount to invest (positive) or liquidate (negative)
            allocation: Asset allocation dictionary for equities
        """
        task_id = f"equity_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        task_data = {
            'task_id': task_id,
            'user_id': user_id,
            'amount': amount,
            'allocation': allocation,
            'action': 'BUY' if amount > 0 else 'SELL',
            'timestamp': datetime.now().isoformat()
        }
        
        # Send task to Equity Worker via MCU
        self.mcu_server.send_task_to_worker('equity_trader', task_data)
        
        # Track active task
        self.active_tasks[task_id] = {
            'worker_type': 'equity_trader',
            'user_id': user_id,
            'status': 'PENDING',
            'created_at': datetime.now().isoformat(),
            'data': task_data
        }
        
        logger.info(f"Delegated task {task_id} to Equity Worker: {'invest' if amount > 0 else 'liquidate'} ${abs(amount)}")
    
    def _delegate_to_crypto_worker(self, user_id: int, amount: float, allocation: Dict[str, float]) -> None:
        """
        Delegate a task to the Crypto Worker AI
        
        Args:
            user_id: User ID
            amount: Amount to invest (positive) or liquidate (negative)
            allocation: Asset allocation dictionary for cryptocurrencies
        """
        task_id = f"crypto_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        task_data = {
            'task_id': task_id,
            'user_id': user_id,
            'amount': amount,
            'allocation': allocation,
            'action': 'BUY' if amount > 0 else 'SELL',
            'timestamp': datetime.now().isoformat()
        }
        
        # Send task to Crypto Worker via MCU
        self.mcu_server.send_task_to_worker('crypto_trader', task_data)
        
        # Track active task
        self.active_tasks[task_id] = {
            'worker_type': 'crypto_trader',
            'user_id': user_id,
            'status': 'PENDING',
            'created_at': datetime.now().isoformat(),
            'data': task_data
        }
        
        logger.info(f"Delegated task {task_id} to Crypto Worker: {'invest' if amount > 0 else 'liquidate'} ${abs(amount)}")
    
    def _cancel_pending_trades(self, user_id: int) -> None:
        """
        Cancel any pending trades for a user
        
        Args:
            user_id: User ID
        """
        # Find active tasks for this user
        user_tasks = [task_id for task_id, task in self.active_tasks.items() 
                     if task['user_id'] == user_id and task['status'] == 'PENDING']
        
        # Cancel each task
        for task_id in user_tasks:
            task = self.active_tasks[task_id]
            worker_type = task['worker_type']
            
            # Send cancel request to worker
            cancel_msg = {
                'task_id': task_id,
                'action': 'CANCEL',
                'reason': 'Trading disabled by user',
                'timestamp': datetime.now().isoformat()
            }
            
            self.mcu_server.send_task_to_worker(worker_type, cancel_msg)
            
            # Update task status
            self.active_tasks[task_id]['status'] = 'CANCELLED'
            
            logger.info(f"Cancelled task {task_id} for user {user_id}")
    
    def _calculate_allocation_adjustments(self, current: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate allocation adjustments needed to reach target allocation
        
        Args:
            current: Current allocation dictionary
            target: Target allocation dictionary
            
        Returns:
            Dictionary of asset classes and their adjustment percentages
        """
        adjustments = {}
        
        # Compare top-level allocations
        current_top = current.get('top_level', {})
        target_top = target.get('top_level', {})
        
        for asset_class in set(list(current_top.keys()) + list(target_top.keys())):
            current_pct = current_top.get(asset_class, 0)
            target_pct = target_top.get(asset_class, 0)
            
            adjustment = target_pct - current_pct
            if abs(adjustment) >= 0.5:  # Only adjust if difference is significant
                adjustments[asset_class] = adjustment
        
        return adjustments
    
    def _calculate_liquidation_plan(self, user_id: int, amount: float, 
                                  current: Dict[str, Any], target: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate optimal liquidation plan to maintain target allocation
        
        Args:
            user_id: User ID
            amount: Amount needed
            current: Current allocation dictionary
            target: Target allocation dictionary
            
        Returns:
            Dictionary of asset classes and amounts to liquidate
        """
        liquidation_plan = {}
        portfolio_value = self.portfolio_manager.get_portfolio_value(user_id)
        
        # First, use available cash
        cash_available = self.portfolio_manager.get_cash_balance(user_id)
        amount_needed = amount
        
        if cash_available > 0:
            cash_to_use = min(cash_available, amount_needed)
            amount_needed -= cash_to_use
            liquidation_plan['Cash'] = cash_to_use
        
        if amount_needed <= 0:
            return liquidation_plan
        
        # Calculate how far each asset class is from its target
        deviation = {}
        current_top = current.get('top_level', {})
        target_top = target.get('top_level', {})
        
        for asset_class in current_top:
            if asset_class == 'Cash':
                continue
                
            current_pct = current_top.get(asset_class, 0)
            target_pct = target_top.get(asset_class, 0)
            
            # Positive deviation means overweight compared to target
            deviation[asset_class] = current_pct - target_pct
        
        # Sort asset classes by deviation (descending)
        sorted_assets = sorted(deviation.items(), key=lambda x: x[1], reverse=True)
        
        # Liquidate from overweight assets first
        remaining_amount = amount_needed
        for asset_class, dev in sorted_assets:
            if dev <= 0 and any(d > 0 for _, d in sorted_assets):
                continue  # Skip underweight assets if there are overweight ones
                
            # Calculate maximum amount we can take from this asset class
            asset_value = (current_top.get(asset_class, 0) / 100) * portfolio_value
            
            # If it's overweight, we can take more
            if dev > 0:
                max_liquidation = (dev / 100) * portfolio_value
                liquidation_amount = min(max_liquidation, remaining_amount)
            else:
                # If all assets are underweight, liquidate proportionally
                liquidation_amount = (asset_value / portfolio_value) * remaining_amount
            
            if liquidation_amount > 0:
                liquidation_plan[asset_class] = liquidation_amount
                remaining_amount -= liquidation_amount
                
                if remaining_amount <= 0:
                    break
        
        return liquidation_plan
    
    def handle_worker_response(self, response: Dict[str, Any]) -> None:
        """
        Handle a response from a Worker AI
        
        Args:
            response: Response data from worker
        """
        task_id = response.get('task_id')
        status = response.get('status')
        
        if not task_id or task_id not in self.active_tasks:
            logger.warning(f"Received response for unknown task: {task_id}")
            return
        
        logger.info(f"Received worker response for task {task_id}: {status}")
        
        # Update task status
        self.active_tasks[task_id]['status'] = status
        self.active_tasks[task_id]['completed_at'] = datetime.now().isoformat()
        self.active_tasks[task_id]['response'] = response
        
        # Process response based on task type and status
        task = self.active_tasks[task_id]
        user_id = task['data']['user_id']
        
        if status == 'COMPLETED':
            # Update portfolio with executed trades
            if 'trades' in response:
                self.portfolio_manager.record_trades(user_id, response['trades'])
                
                # Log decision outcome
                self.decision_engine.update_decision_outcome(
                    task_id=task_id,
                    outcome='SUCCESS',
                    details=response
                )
        
        elif status == 'FAILED':
            # Log decision outcome
            self.decision_engine.update_decision_outcome(
                task_id=task_id,
                outcome='FAILED',
                details=response
            )
            
            # Notify risk system
            if 'error' in response:
                self.risk_analyzer.log_execution_failure(
                    user_id=user_id,
                    worker_type=task['worker_type'],
                    error=response['error']
                )
        
        # Clean up old tasks periodically
        self._cleanup_completed_tasks()
    
    def _cleanup_completed_tasks(self) -> None:
        """Clean up completed tasks older than 24 hours"""
        current_time = datetime.now()
        to_remove = []
        
        for task_id, task in self.active_tasks.items():
            if task['status'] in ['COMPLETED', 'FAILED', 'CANCELLED']:
                completed_at = datetime.fromisoformat(task.get('completed_at', ''))
                if (current_time - completed_at).total_seconds() > 86400:  # 24 hours
                    to_remove.append(task_id)
        
        for task_id in to_remove:
            del self.active_tasks[task_id]
