from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from . import login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), index=True, unique=True)

    # Хеширование паролей
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % (self.username)


class Table(db.Model):
    __tablename__ = 'table'
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(15))
    date_declaration = db.Column(db.Date)
    date_stamp_preparation = db.Column(db.Date)
    data_obligation_received = db.Column(db.Date)
    date_provision_received = db.Column(db.Date)
    datr_stamp_received = db.Column(db.Date)
    date_report_closed = db.Column(db.Date)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))

    def __repr__(self):
        return '<Table %r>' % (self.registration_number)


class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(64), index=True, unique=True)
