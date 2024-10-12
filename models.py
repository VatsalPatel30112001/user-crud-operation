import uuid 
from flask import Flask
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Table, ForeignKey, DateTime, Boolean

from database import db

class Manager(db.Model):
    __tablename__ = 'managers'
    
    manager_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    
    users = relationship('User', backref='manager', lazy=True)

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    manager_id = Column(String(36), ForeignKey('managers.manager_id'), nullable=True)
    full_name = Column(String(100), nullable=False)
    mob_num = Column(String(10), nullable=False)
    pan_num = Column(String(10), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    def update(self):
        self.updated_at = datetime.utcnow()
        db.session.commit() 