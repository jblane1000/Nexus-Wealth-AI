from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, FloatField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from datetime import date, timedelta

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegisterForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    province = StringField('Province/State', validators=[DataRequired()])
    postal_code = StringField('Postal Code', validators=[DataRequired()])
    country = StringField('Country', validators=[DataRequired()])
    agree_terms = BooleanField('I agree to the Terms and Conditions', validators=[DataRequired()])
    submit = SubmitField('Register')
    
    def validate_date_of_birth(self, field):
        today = date.today()
        age = today.year - field.data.year - ((today.month, today.day) < (field.data.month, field.data.day))
        if age < 18:
            raise ValidationError('You must be at least 18 years old to register')

class RiskProfileForm(FlaskForm):
    investment_experience = SelectField(
        'How would you rate your investment experience?',
        choices=[
            ('1', 'No experience'),
            ('2', 'Beginner'),
            ('3', 'Some experience'),
            ('4', 'Experienced'),
            ('5', 'Very experienced')
        ],
        validators=[DataRequired()]
    )
    
    investment_horizon = SelectField(
        'What is your investment time horizon?',
        choices=[
            ('1', 'Less than 1 year'),
            ('2', '1-3 years'),
            ('3', '3-5 years'),
            ('4', '5-10 years'),
            ('5', 'More than 10 years')
        ],
        validators=[DataRequired()]
    )
    
    risk_tolerance = SelectField(
        'How would you react if your portfolio lost 20% of its value in a month?',
        choices=[
            ('1', 'Sell everything immediately'),
            ('2', 'Sell some investments'),
            ('3', 'Do nothing'),
            ('4', 'Buy a little more'),
            ('5', 'Buy significantly more')
        ],
        validators=[DataRequired()]
    )
    
    income_stability = SelectField(
        'How stable is your income?',
        choices=[
            ('1', 'Very unstable'),
            ('2', 'Somewhat unstable'),
            ('3', 'Moderate stability'),
            ('4', 'Stable'),
            ('5', 'Very stable')
        ],
        validators=[DataRequired()]
    )
    
    emergency_funds = SelectField(
        'How many months of expenses do you have saved in an emergency fund?',
        choices=[
            ('1', 'None'),
            ('2', 'Less than 3 months'),
            ('3', '3-6 months'),
            ('4', '6-12 months'),
            ('5', 'More than 12 months')
        ],
        validators=[DataRequired()]
    )
    
    submit = SubmitField('Submit Risk Profile')

class GoalForm(FlaskForm):
    name = StringField('Goal Name', validators=[DataRequired()])
    target_amount = FloatField('Target Amount ($)', validators=[
        DataRequired(),
        NumberRange(min=100, message='Target amount must be at least $100')
    ])
    target_date = DateField('Target Date', validators=[DataRequired()])
    priority = SelectField(
        'Priority',
        choices=[
            ('High', 'High'),
            ('Medium', 'Medium'),
            ('Low', 'Low')
        ],
        validators=[DataRequired()]
    )
    description = TextAreaField('Description (Optional)')
    submit = SubmitField('Add Goal')
    
    def validate_target_date(self, field):
        min_date = date.today() + timedelta(days=30)
        if field.data < min_date:
            raise ValidationError('Target date must be at least 30 days in the future')
