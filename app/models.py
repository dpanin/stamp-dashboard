import csv
import os
import time
from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import desc
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, reds
from . import login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    """Users table scheme."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), index=True, unique=True)
    role_id = db.Column(db.Integer)

    # Only allow to add password
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Writes hashed password to database."""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Compares password with hashed version in database."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.username


class Document(db.Model):
    """Table scheme with documents status."""

    __tablename__ = 'document'
    id = db.Column(db.Integer, primary_key=True)
    registration_number = db.Column(db.String(15), unique=True)
    date_declaration = db.Column(db.DateTime)
    date_stamp_preparation = db.Column(db.DateTime)
    date_obligation_received = db.Column(db.DateTime)
    date_provision_received = db.Column(db.DateTime)
    date_stamp_received = db.Column(db.DateTime)
    date_report_closed = db.Column(db.DateTime)
    date_last_changed = db.Column(db.DateTime)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'))
    status = db.relationship(
        'Status', backref=db.backref('documents', lazy='dynamic'))

    columns = {
        1: "date_declaration",
        2: "date_stamp_preparation",
        3: "date_obligation_received",
        4: "date_provision_received",
        5: "date_stamp_received",
        6: "date_report_closed"
    }

    @classmethod
    def add(cls, reg_number):
        """Adds registration number to database and Redis queue."""
        dt = datetime.now()
        ts = time.time()
        status = Status.query.filter_by(id=1).first()
        query = Document(
            registration_number=reg_number,
            date_declaration=dt,
            date_last_changed=dt,
            status=status)
        db.session.add(query)
        db.session.commit()
        reds.zadd(1, ts, reg_number)

    @staticmethod
    def format_query(query):
        """Makes datetime more readable and replaces empty cells with '-'."""
        results = []
        for instance in query:
            l = [
                instance.registration_number, instance.date_declaration,
                instance.date_stamp_preparation,
                instance.date_obligation_received,
                instance.date_provision_received, instance.date_stamp_received,
                instance.date_report_closed, instance.status
            ]
            for i in range(len(l)):
                if isinstance(l[i], datetime):
                    l[i] = l[i].strftime('%d.%m.%Y')
                elif l[i] is None:
                    l[i] = "-"
                else:
                    continue
            results.append(l)
        return results

    @classmethod
    def get(cls, lim=10):
        """Returns last 10 entries from 'Documents' table."""
        query = db.session.query(Document).order_by(
            desc(Document.date_last_changed)).limit(lim).all()
        return cls.format_query(query)

    @classmethod
    def get_csv(cls):
        """Exports 'Documents' table to csv file."""
        header = ('Регистрационный номер', 'Дата регистрации',
                  'Дата информирования об изготовлении',
                  'Дата принятия обязательства', 'Дата принятия обеспечения',
                  'График получения', 'Дата закрытия отчета',
                  'Статус заявления')
        contents = Document.get(-1)
        with open('app/report.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(contents)
        basedir = os.path.abspath(os.path.dirname(__file__))
        filedir = os.path.join(basedir, 'report.csv')
        return filedir

    @classmethod
    def search(cls, keyword):
        """Searches entry with the same registration number."""
        query = db.session.query(Document).filter_by(
            registration_number=keyword).all()
        return cls.format_query(query)

    @classmethod
    def update(cls, reg_number, id_number):
        """Changes status, datetime and moves entry to another Redis queue."""
        id_number = int(id_number)
        dtime = datetime.now()
        tstamp = time.time()
        s_id = str(id_number + 1)
        db.session.query(Document).filter_by(
            registration_number=reg_number).update(
            {
                cls.columns[id_number]: dtime,
                "status_id": s_id
            },
            synchronize_session=False)
        db.session.commit()
        reds.zrem(id_number, reg_number)
        reds.zadd(id_number + 1, tstamp, reg_number)

    def __repr__(self):
        return '<Document %r>' % self.registration_number


class Status(db.Model):
    """Status table scheme"""
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), index=True, unique=True)

    def __repr__(self):
        return '<Status %r>' % self.name
