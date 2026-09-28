from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from models.customer import Customer
from models.case import Case
from models.document import Document
from models.message import Message
from models.chunk import Chunk

__all__ = ['db', 'Customer', 'Case', 'Document', 'Message', 'Chunk']
