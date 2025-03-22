from datetime import datetime
from flask_login import UserMixin
from app import db, login
from werkzeug.security import generate_password_hash, check_password_hash
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')
    files = db.relationship('FinancialFile', backref='owner', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class FinancialFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_type = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    analyses = db.relationship('Analysis', back_populates='file', lazy='dynamic')

class Analysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('financial_file.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_type = db.Column(db.String(50))
    results = db.Column(db.JSON)
    
    file = db.relationship('FinancialFile', back_populates='analyses')
    user = db.relationship('User', backref='user_analyses')
    
    def __repr__(self):
        return f'<Analysis {self.id} {self.analysis_type}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
