import random
from datetime import datetime
from models import db

class Case(db.Model):
    __tablename__ = 'case'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.String(20), unique=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    consultancy_type = db.Column(db.String(100), nullable=False)
    problem_description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # A case has multiple documents and messages
    documents = db.relationship('Document', backref='case', lazy=True, cascade='all, delete-orphan')
    messages = db.relationship('Message', backref='case', lazy=True, cascade='all, delete-orphan')

    @staticmethod
    def generate_case_id():
        """Generates a readable case ID format such as CASE-10231."""
        random_digits = random.randint(10000, 99999)
        return f"CASE-{random_digits}"

    def __repr__(self):
        return f"<Case {self.case_id}>"
