from datetime import datetime
from models import db

class Chunk(db.Model):
    __tablename__ = 'chunk'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('case.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(50), nullable=True)
    chunk_index = db.Column(db.Integer, nullable=False)
    page = db.Column(db.Integer, nullable=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'case_id': self.case_id,
            'document_id': self.document_id,
            'filename': self.filename,
            'document_type': self.document_type,
            'chunk_index': self.chunk_index,
            'page': self.page,
            'text': self.text,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def __repr__(self):
        return f"<Chunk doc={self.document_id} idx={self.chunk_index} page={self.page}>"
