from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

###############################################################################
# MODEL
###############################################################################


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True, unique=True)
    address = db.Column(db.String(256), index=True, unique=True)
    dob = db.Column(db.DateTime, index=True, unique=True)
    practiceName = db.Column(db.String(256), index=True, unique=True)
    specialty = db.Column(db.String(256), index=True, unique=True)
    email = db.Column(db.String(256), index=True, unique=True)
    password = db.Column(db.String(256), index=True, unique=True)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    address = db.Column(db.String(256), index=True)
    dob = db.Column(db.DateTime, index=True)
    ssn = db.Column(db.Integer, index=True, unique=True)
    doctor = db.relationship('Doctor',
                             backref=db.backref('patients'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))


class Perscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship('Patient',
                              backref=db.backref('perscriptions'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    doctor = db.relationship('Doctor',
                             backref=db.backref('perscriptions'))
    drugName = db.Column(db.String(256), index=True)
    drugManufacturer = db.Column(db.String(256), index=True)
    dosage = db.Column(db.Integer, index=True)
    # take every x days
    dosagePeriod = db.Column(db.Integer, index=True)
    # number of doses per period
    dosageNumber = db.Column(db.Integer, index=True)
    numDays = db.Column(db.Integer, index=True)
    expirationDate = db.Column(db.DateTime, index=True, unique=True)
    datePerscribed = db.Column(db.DateTime, index=True, unique=True)


db.create_all()

##############################################################################
# VIEW
#############################################################################


