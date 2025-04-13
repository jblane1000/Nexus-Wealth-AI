import os
from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

from models import db, User, Portfolio, Transaction, Goal, RiskProfile
from forms import LoginForm, RegisterForm, GoalForm, RiskProfileForm
from config import Config
from api_client import AIApiClient

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Initialize API client
ai_api_client = AIApiClient(base_url=os.environ.get('AI_CORE_URL', 'http://ai_core:5000'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))
        flash('Invalid email or password')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Simple KYC placeholder - would be more robust in production
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            full_name=form.full_name.data,
            email=form.email.data,
            password_hash=hashed_password,
            date_of_birth=form.date_of_birth.data,
            address=form.address.data,
            city=form.city.data,
            province=form.province.data,
            postal_code=form.postal_code.data,
            country=form.country.data
        )
        db.session.add(user)
        db.session.commit()
        
        # Create empty portfolio for new user
        portfolio = Portfolio(user_id=user.id, total_value=0.0, cash_balance=0.0)
        db.session.add(portfolio)
        db.session.commit()
        
        flash('Registration successful! Please complete your risk profile.')
        login_user(user)
        return redirect(url_for('risk_profile'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's portfolio and goals
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    risk_profile = RiskProfile.query.filter_by(user_id=current_user.id).first()
    
    # Get recent transactions
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(Transaction.date.desc()).limit(10).all()
    
    # Get portfolio data from AI Core
    try:
        portfolio_data = ai_api_client.get_portfolio_data(current_user.id)
    except Exception as e:
        logger.error(f"Error getting portfolio data: {str(e)}")
        portfolio_data = {
            'assets': [],
            'allocation': {},
            'performance': {
                'daily': 0,
                'weekly': 0,
                'monthly': 0,
                'yearly': 0
            }
        }
    
    return render_template(
        'dashboard.html',
        portfolio=portfolio,
        goals=goals,
        risk_profile=risk_profile,
        transactions=transactions,
        portfolio_data=portfolio_data
    )

@app.route('/risk_profile', methods=['GET', 'POST'])
@login_required
def risk_profile():
    # Check if user already has a risk profile
    existing_profile = RiskProfile.query.filter_by(user_id=current_user.id).first()
    
    form = RiskProfileForm()
    if form.validate_on_submit():
        # Calculate risk score based on form answers (simplified)
        risk_score = sum([
            int(form.investment_experience.data),
            int(form.investment_horizon.data),
            int(form.risk_tolerance.data),
            int(form.income_stability.data),
            int(form.emergency_funds.data)
        ])
        
        # Determine risk level based on score
        if risk_score <= 7:
            risk_level = 'Conservative'
        elif risk_score <= 14:
            risk_level = 'Moderate'
        else:
            risk_level = 'Aggressive'
        
        if existing_profile:
            # Update existing profile
            existing_profile.investment_experience = form.investment_experience.data
            existing_profile.investment_horizon = form.investment_horizon.data
            existing_profile.risk_tolerance = form.risk_tolerance.data
            existing_profile.income_stability = form.income_stability.data
            existing_profile.emergency_funds = form.emergency_funds.data
            existing_profile.risk_score = risk_score
            existing_profile.risk_level = risk_level
        else:
            # Create new profile
            profile = RiskProfile(
                user_id=current_user.id,
                investment_experience=form.investment_experience.data,
                investment_horizon=form.investment_horizon.data,
                risk_tolerance=form.risk_tolerance.data,
                income_stability=form.income_stability.data,
                emergency_funds=form.emergency_funds.data,
                risk_score=risk_score,
                risk_level=risk_level
            )
            db.session.add(profile)
        
        db.session.commit()
        
        # Notify AI Core about risk profile update
        try:
            ai_api_client.update_risk_profile(current_user.id, risk_level, risk_score)
        except Exception as e:
            logger.error(f"Error updating risk profile with AI Core: {str(e)}")
        
        flash('Risk profile updated successfully!')
        return redirect(url_for('goals'))
    
    # Populate form with existing data if available
    if existing_profile and request.method == 'GET':
        form.investment_experience.data = existing_profile.investment_experience
        form.investment_horizon.data = existing_profile.investment_horizon
        form.risk_tolerance.data = existing_profile.risk_tolerance
        form.income_stability.data = existing_profile.income_stability
        form.emergency_funds.data = existing_profile.emergency_funds
    
    return render_template('risk_profile.html', form=form)

@app.route('/goals', methods=['GET', 'POST'])
@login_required
def goals():
    form = GoalForm()
    if form.validate_on_submit():
        goal = Goal(
            user_id=current_user.id,
            name=form.name.data,
            target_amount=form.target_amount.data,
            current_amount=0.0,
            target_date=form.target_date.data,
            priority=form.priority.data
        )
        db.session.add(goal)
        db.session.commit()
        
        # Notify AI Core about new goal
        try:
            ai_api_client.add_goal(
                user_id=current_user.id,
                goal_id=goal.id,
                name=goal.name,
                target_amount=goal.target_amount,
                target_date=goal.target_date.isoformat(),
                priority=goal.priority
            )
        except Exception as e:
            logger.error(f"Error notifying AI Core about new goal: {str(e)}")
        
        flash('Goal added successfully!')
        return redirect(url_for('dashboard'))
    
    # Get existing goals
    goals = Goal.query.filter_by(user_id=current_user.id).all()
    
    return render_template('goals.html', form=form, goals=goals)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Deposit amount must be greater than zero')
            return redirect(url_for('deposit'))
        
        portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
        portfolio.cash_balance += amount
        portfolio.total_value += amount
        
        # Record transaction
        transaction = Transaction(
            user_id=current_user.id,
            type='DEPOSIT',
            amount=amount,
            date=datetime.utcnow(),
            description=f'Deposit of ${amount:.2f}'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Notify AI Core about deposit
        try:
            ai_api_client.notify_cash_flow(
                user_id=current_user.id,
                amount=amount,
                transaction_type='DEPOSIT'
            )
        except Exception as e:
            logger.error(f"Error notifying AI Core about deposit: {str(e)}")
        
        flash(f'Successfully deposited ${amount:.2f}')
        return redirect(url_for('dashboard'))
    
    return render_template('deposit.html')

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    if request.method == 'POST':
        amount = float(request.form.get('amount', 0))
        if amount <= 0:
            flash('Withdrawal amount must be greater than zero')
            return redirect(url_for('withdraw'))
        
        portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
        if amount > portfolio.cash_balance:
            flash('Insufficient funds for withdrawal')
            return redirect(url_for('withdraw'))
        
        portfolio.cash_balance -= amount
        portfolio.total_value -= amount
        
        # Record transaction
        transaction = Transaction(
            user_id=current_user.id,
            type='WITHDRAWAL',
            amount=amount,
            date=datetime.utcnow(),
            description=f'Withdrawal of ${amount:.2f}'
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        # Notify AI Core about withdrawal
        try:
            ai_api_client.notify_cash_flow(
                user_id=current_user.id,
                amount=-amount,  # Negative amount for withdrawal
                transaction_type='WITHDRAWAL'
            )
        except Exception as e:
            logger.error(f"Error notifying AI Core about withdrawal: {str(e)}")
        
        flash(f'Successfully withdrew ${amount:.2f}')
        return redirect(url_for('dashboard'))
    
    # Get available balance
    portfolio = Portfolio.query.filter_by(user_id=current_user.id).first()
    
    return render_template('withdraw.html', available_balance=portfolio.cash_balance)

@app.route('/transactions')
@login_required
def transactions():
    # Get transaction history with pagination
    page = request.args.get('page', 1, type=int)
    transactions = Transaction.query.filter_by(user_id=current_user.id).order_by(
        Transaction.date.desc()
    ).paginate(page=page, per_page=20)
    
    return render_template('transactions.html', transactions=transactions)

@app.route('/api/portfolio')
@login_required
def api_portfolio():
    """API endpoint for frontend to get portfolio data"""
    try:
        portfolio_data = ai_api_client.get_portfolio_data(current_user.id)
        return jsonify(portfolio_data)
    except Exception as e:
        logger.error(f"Error getting portfolio data: {str(e)}")
        return jsonify({'error': 'Failed to get portfolio data'}), 500

@app.route('/api/market_summary')
@login_required
def api_market_summary():
    """API endpoint for frontend to get market summary data"""
    try:
        market_data = ai_api_client.get_market_summary()
        return jsonify(market_data)
    except Exception as e:
        logger.error(f"Error getting market data: {str(e)}")
        return jsonify({'error': 'Failed to get market data'}), 500

@app.route('/api/decisions')
@login_required
def api_decisions():
    """API endpoint for frontend to get recent AI decisions"""
    try:
        decisions = ai_api_client.get_recent_decisions(current_user.id)
        return jsonify(decisions)
    except Exception as e:
        logger.error(f"Error getting AI decisions: {str(e)}")
        return jsonify({'error': 'Failed to get AI decisions'}), 500

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        # Update notification preferences
        notifications_enabled = 'notifications_enabled' in request.form
        email_notifications = 'email_notifications' in request.form
        trading_enabled = 'trading_enabled' in request.form
        
        current_user.notifications_enabled = notifications_enabled
        current_user.email_notifications = email_notifications
        current_user.trading_enabled = trading_enabled
        
        db.session.commit()
        
        # Notify AI Core about settings update
        try:
            ai_api_client.update_user_settings(
                user_id=current_user.id,
                trading_enabled=trading_enabled
            )
        except Exception as e:
            logger.error(f"Error updating settings with AI Core: {str(e)}")
        
        flash('Settings updated successfully!')
        return redirect(url_for('settings'))
    
    return render_template('settings.html', user=current_user)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=Config.DEBUG)
