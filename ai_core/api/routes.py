import logging
from flask import Blueprint, request, jsonify
from flask_restful import Api, Resource

logger = logging.getLogger(__name__)

def register_routes(app, ceo_agent, rag_system, mcu_server):
    """Register API routes with the Flask application
    
    Args:
        app: Flask application
        ceo_agent: CEO AI Agent instance
        rag_system: RAG System instance
        mcu_server: MCU Server instance
    """
    # Create API blueprint
    api_bp = Blueprint('api', __name__)
    api = Api(api_bp)
    
    # Portfolio endpoints
    class PortfolioResource(Resource):
        def get(self):
            """Get portfolio data for a user"""
            user_id = request.args.get('user_id')
            if not user_id:
                return {"error": "user_id is required"}, 400
            
            try:
                portfolio_data = ceo_agent.get_portfolio_data(int(user_id))
                return portfolio_data
            except Exception as e:
                logger.error(f"Error getting portfolio data: {str(e)}")
                return {"error": "Failed to get portfolio data"}, 500
    
    # Market data endpoints
    class MarketResource(Resource):
        def get(self):
            """Get market summary data"""
            try:
                market_data = ceo_agent.get_market_summary()
                return market_data
            except Exception as e:
                logger.error(f"Error getting market data: {str(e)}")
                return {"error": "Failed to get market data"}, 500
    
    # Decision endpoints
    class DecisionsResource(Resource):
        def get(self):
            """Get recent AI decisions for a user"""
            user_id = request.args.get('user_id')
            if not user_id:
                return {"error": "user_id is required"}, 400
            
            try:
                decisions = ceo_agent.get_recent_decisions(int(user_id))
                return {"decisions": decisions}
            except Exception as e:
                logger.error(f"Error getting decisions: {str(e)}")
                return {"error": "Failed to get decisions"}, 500
    
    # Risk profile endpoints
    class RiskProfileResource(Resource):
        def post(self):
            """Update user risk profile"""
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            required_fields = ['user_id', 'risk_level', 'risk_score']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            try:
                ceo_agent.update_risk_profile(
                    user_id=data['user_id'],
                    risk_level=data['risk_level'],
                    risk_score=data['risk_score']
                )
                return {"status": "success"}, 200
            except Exception as e:
                logger.error(f"Error updating risk profile: {str(e)}")
                return {"error": "Failed to update risk profile"}, 500
    
    # Goal endpoints
    class GoalsResource(Resource):
        def post(self):
            """Add a new goal"""
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            required_fields = ['user_id', 'goal_id', 'name', 'target_amount', 'target_date', 'priority']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            try:
                ceo_agent.add_goal(
                    user_id=data['user_id'],
                    goal_id=data['goal_id'],
                    name=data['name'],
                    target_amount=data['target_amount'],
                    target_date=data['target_date'],
                    priority=data['priority']
                )
                return {"status": "success"}, 201
            except Exception as e:
                logger.error(f"Error adding goal: {str(e)}")
                return {"error": "Failed to add goal"}, 500
    
    # Cash flow endpoints
    class CashFlowResource(Resource):
        def post(self):
            """Process deposit or withdrawal"""
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            required_fields = ['user_id', 'amount', 'transaction_type']
            for field in required_fields:
                if field not in data:
                    return {"error": f"Missing required field: {field}"}, 400
            
            try:
                ceo_agent.process_cash_flow(
                    user_id=data['user_id'],
                    amount=data['amount'],
                    transaction_type=data['transaction_type']
                )
                return {"status": "success"}, 200
            except Exception as e:
                logger.error(f"Error processing cash flow: {str(e)}")
                return {"error": "Failed to process cash flow"}, 500
    
    # User settings endpoints
    class UserSettingsResource(Resource):
        def put(self):
            """Update user settings"""
            data = request.get_json()
            if not data:
                return {"error": "No data provided"}, 400
            
            if 'user_id' not in data:
                return {"error": "Missing required field: user_id"}, 400
            
            try:
                ceo_agent.update_user_settings(
                    user_id=data['user_id'],
                    trading_enabled=data.get('trading_enabled', True)
                )
                return {"status": "success"}, 200
            except Exception as e:
                logger.error(f"Error updating user settings: {str(e)}")
                return {"error": "Failed to update user settings"}, 500
    
    # MCU status endpoint
    class MCUStatusResource(Resource):
        def get(self):
            """Get status of worker AIs"""
            try:
                worker_status = mcu_server.get_worker_status()
                return {"workers": worker_status}
            except Exception as e:
                logger.error(f"Error getting worker status: {str(e)}")
                return {"error": "Failed to get worker status"}, 500
    
    # RAG query endpoint
    class RAGQueryResource(Resource):
        def post(self):
            """Query the RAG system"""
            data = request.get_json()
            if not data or 'query' not in data:
                return {"error": "Missing query parameter"}, 400
            
            try:
                results = rag_system.query(
                    query=data['query'],
                    filters=data.get('filters', {}),
                    limit=data.get('limit', 5)
                )
                return {"results": results}
            except Exception as e:
                logger.error(f"Error querying RAG system: {str(e)}")
                return {"error": "Failed to query RAG system"}, 500
    
    # Register resources with API
    api.add_resource(PortfolioResource, '/portfolio')
    api.add_resource(MarketResource, '/market')
    api.add_resource(DecisionsResource, '/decisions')
    api.add_resource(RiskProfileResource, '/risk_profile')
    api.add_resource(GoalsResource, '/goals')
    api.add_resource(CashFlowResource, '/cash_flow')
    api.add_resource(UserSettingsResource, '/user/settings')
    api.add_resource(MCUStatusResource, '/mcu/status')
    api.add_resource(RAGQueryResource, '/rag/query')
    
    # Register blueprint with app
    app.register_blueprint(api_bp, url_prefix='/api/v1')
