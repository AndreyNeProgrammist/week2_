from app import db

# Модели данных для PostgreSQL
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(10), unique=True, nullable=False)
    secret = db.Column(db.String(10), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)

class Method(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    caption = db.Column(db.String(30), nullable=False)
    json_params = db.Column(db.JSON, nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    sessions = db.relationship('Session', backref='method', lazy=True)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    method_id = db.Column(db.Integer, db.ForeignKey('method.id'), nullable=False)
    data_in = db.Column(db.String(10000), nullable=False)
    params = db.Column(db.JSON)
    data_out = db.Column(db.String(10000))
    status = db.Column(db.String(20), default='Pending')
