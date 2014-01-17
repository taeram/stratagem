from app import app
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager, prompt_bool
from datetime import datetime

db = SQLAlchemy(app)

manager = Manager(usage="Manage the database")

@manager.command
def create():
    """Create the database"""
    db.create_all()

@manager.command
def drop():
    """Empty the database"""
    if prompt_bool("Are you sure you want to drop all tables from the database?"):
        db.drop_all()

@manager.command
def recreate():
    """Recreate the database"""
    drop()
    create()

class Domain(db.Model):
    """
    A domain name
    """
    __tablename__ = 'domain'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, unique=True)

    def __init__(self, name):
        self.name = name

    def toObject(self):
        return {
            "id": self.id,
            "name": self.name
        }

class Address(db.Model):
    """
    An email address
    """
    __tablename__ = 'address'

    id = db.Column(db.Integer, primary_key=True)
    local = db.Column(db.Text)
    domain_id = db.Column(db.Integer, db.ForeignKey('domain.id'))
    domain = db.relationship('Domain')
    total_spam_score = db.Column(db.Float, default=0)
    total_received = db.Column(db.Integer, default=0)
    date_last_received = db.Column(db.DateTime(timezone=False), default=datetime.utcnow)
    created = db.Column(db.DateTime(timezone=False), default=datetime.utcnow)

    def __init__(self, local, domain_id):
        self.local = local
        self.domain_id = domain_id

    def toObject(self):
        return {
            "id": self.id,
            "local": self.local,
            "domain": self.domain.name,
            "created": self.created.strftime('%Y-%m-%d %H:%M:%S'),
            "avg_spam_score": self.total_spam_score / self.total_received,
            "date_last_received": self.date_last_received.strftime('%Y-%m-%d %H:%M:%S'),
            "total_received": self.total_received
        }
