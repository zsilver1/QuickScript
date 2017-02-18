from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)


###############################################################################
# MODEL
###############################################################################


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    address = db.Column(db.String(256), index=True)
    dob = db.Column(db.DateTime, index=True, unique=True)
    practiceName = db.Column(db.String(256), index=True)
    specialty = db.Column(db.String(256), index=True)
    email = db.Column(db.String(256), index=True, unique=True)
    password = db.Column(db.String(256), index=True)

    def to_dict(self):
        d = {
            'name': self.name,
            'address': self.address,
            'dob': self.dob,
            'practiceName': self.practiceName,
            'specialty': self.specialty,
            'email': self.email,
            'password': self.password,
        }
        return d


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    phoneNumber = db.Column(db.Integer)
    email = db.Column(db.String(256), index=True)
    address = db.Column(db.String(256), index=True)
    dob = db.Column(db.DateTime, index=True)
    ssn = db.Column(db.Integer, index=True, unique=True)
    doctor = db.relationship('Doctor',
                             backref=db.backref('patients'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))

    def to_dict(self):
        d = {
            'name': self.name,
            'address': self.address,
            'dob': self.dob,
            'ssn': self.ssn,
            'email': self.email,
            'phoneNumber': self.phoneNumber,
            'perscriptions': [p.to_dict() for p in self.perscriptions]
        }
        return d


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
    expirationDate = db.Column(db.DateTime, index=True)
    datePerscribed = db.Column(db.DateTime, index=True)
    timeOfDay = db.Column(db.String(256), index=True)

    def to_dict(self):
        d = {
            'drugName': self.drugName,
            'drugManufacturer': self.drugManufacturer,
            'dosage': self.dosage,
            'dosagePeriod': self.dosagePeriod,
            'dosageNumber': self.dosageNumber,
            'numDays': self.numDays,
            'expirationDate': self.dosage,
            'datePerscribed': self.dosagePeriod,
            'timeOfDay': self.dosageNumber,
        }
        return d


# remove me
db.drop_all()


db.create_all()

##############################################################################
# VIEW
#############################################################################


def addDoc(email, password, name="", address="",
           dob=None, practiceName="", specialty=""):
    doc = Doctor()
    doc.email = email
    doc.password = password
    doc.name = name
    doc.address = address
    doc.dob = dob
    doc.practiceName = practiceName
    doc.specialty = specialty
    db.session.add(doc)
    db.session.commit()
    return doc


def addPatient(doctor, name, phoneNumber, email="", address="",
               dob=None, ssn=None):
    p = Patient()
    p.name = name
    p.phoneNumber = phoneNumber
    p.email = email
    p.address = address
    p.dob = dob
    p.ssn = ssn
    p.doctor = doctor
    db.session.add(p)
    db.session.commit()
    return p


def addPerscription(patient, doctor, drugName='', drugManufacturer='',
                    dosage=None, dosagePeriod=None, dosageNumber=None,
                    numDays=None, expirationDate=None, datePerscribed=None,
                    timeOfDay=''):
    p = Perscription()
    p.patient = patient
    p.doctor = doctor
    p.drugName = drugName
    p.drugManufacturer = drugManufacturer
    p.dosage = dosage
    p.dosagePeriod = dosagePeriod
    p.dosageNumber = dosageNumber
    p.numDays = numDays
    p.expirationDate = expirationDate
    p.datePerscribed = datePerscribed
    p.timeOfDay = timeOfDay
    db.session.add(p)
    db.session.commit()
    return p


d = addDoc("hello@email.com", "password")
p = addPatient(d, "yes", 234)
addPerscription(p, d)
# addDoc("hellothere@email.com", "password")

@app.route('/login', methods=['GET', 'POST'])
def login():
    # REMOVE ME
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # HANDLE ERRORS
        doctor = Doctor.query.filter_by(email=email, password=password).first()

        plist = []
        for p in doctor.patients:
            plist.append(p.to_dict())
        return jsonify({'doctor': doctor.to_dict(), 'patients': plist})
