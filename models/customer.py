from datetime import datetime
from models import db

class Customer(db.Model):
    __tablename__ = 'customer'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=False)
    jurisdiction = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # One customer can have multiple cases
    cases = db.relationship('Case', backref='customer', lazy=True)

    def __repr__(self):
        return f"<Customer {self.name} (ID: {self.id})>"
