from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets
import string

db = SQLAlchemy()

def generate_reference_no():
    """Generate a unique 8-character alphanumeric reference number"""
    alphabet = string.ascii_uppercase + string.digits
    return 'ASHV-' + ''.join(secrets.choice(alphabet) for i in range(8))

class Letter(db.Model):
    __tablename__ = 'letters'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_no = db.Column(db.String(20), unique=True, nullable=False, default=generate_reference_no)
    date = db.Column(db.String(50), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    to_address = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # pending, verified, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to roll numbers
    roll_numbers = db.relationship('RollNumber', backref='letter', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Letter {self.reference_no}>'

class RollNumber(db.Model):
    __tablename__ = 'roll_numbers'
    
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), nullable=False)
    letter_id = db.Column(db.Integer, db.ForeignKey('letters.id'), nullable=False)
    
    def __repr__(self):
        return f'<RollNumber {self.roll_no}>'
