from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    province = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(20), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    notifications_enabled = db.Column(db.Boolean, default=True)
    email_notifications = db.Column(db.Boolean, default=True)
    trading_enabled = db.Column(db.Boolean, default=True)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    portfolio = db.relationship('Portfolio', backref='user', uselist=False)
    goals = db.relationship('Goal', backref='user')
    risk_profile = db.relationship('RiskProfile', backref='user', uselist=False)
    transactions = db.relationship('Transaction', backref='user')
    
    def __repr__(self):
        return f'<User {self.email}>'

class Portfolio(db.Model):
    __tablename__ = 'portfolios'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_value = db.Column(db.Float, default=0.0)
    cash_balance = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Portfolio assets would typically be managed by the AI Core
    
    def __repr__(self):
        return f'<Portfolio {self.id} - User {self.user_id}>'

class Goal(db.Model):
    __tablename__ = 'goals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Goal {self.name} - {self.target_amount}>'
    
    @property
    def progress_percentage(self):
        if self.target_amount == 0:
            return 0
        return min(100, (self.current_amount / self.target_amount) * 100)

class RiskProfile(db.Model):
    __tablename__ = 'risk_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    investment_experience = db.Column(db.String(20), nullable=False)  # 1-5 scale
    investment_horizon = db.Column(db.String(20), nullable=False)     # 1-5 scale
    risk_tolerance = db.Column(db.String(20), nullable=False)         # 1-5 scale
    income_stability = db.Column(db.String(20), nullable=False)       # 1-5 scale
    emergency_funds = db.Column(db.String(20), nullable=False)        # 1-5 scale
    risk_score = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)  # Conservative, Moderate, Aggressive
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<RiskProfile {self.user_id} - {self.risk_level}>'

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # DEPOSIT, WITHDRAWAL, BUY, SELL
    amount = db.Column(db.Float, nullable=False)
    asset_symbol = db.Column(db.String(20), nullable=True)
    asset_name = db.Column(db.String(100), nullable=True)
    quantity = db.Column(db.Float, nullable=True)
    price = db.Column(db.Float, nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(200), nullable=True)
    
    def __repr__(self):
        return f'<Transaction {self.id} - {self.type} - {self.amount}>'
