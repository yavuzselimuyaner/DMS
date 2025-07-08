from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False, unique=True)
    data = db.Column(db.LargeBinary, nullable=False)
    mimetype = db.Column(db.String(128), nullable=False)
    uploaded_by = db.Column(db.String(64), nullable=False)
    explanation = db.Column(db.Text)
    deleted_by = db.Column(db.String(64))
    upload_time = db.Column(db.DateTime, server_default=func.now())
