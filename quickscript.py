from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)
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
            'prescriptions': [p.to_dict() for p in self.prescriptions]
        }
        return d


class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'))
    patient = db.relationship('Patient',
                              backref=db.backref('prescriptions'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    doctor = db.relationship('Doctor',
                             backref=db.backref('prescriptions'))
    drugName = db.Column(db.String(256), index=True)
    drugManufacturer = db.Column(db.String(256), index=True)
    dosage = db.Column(db.Integer, index=True)
    # take every x days
    dosagePeriod = db.Column(db.Integer, index=True)
    # number of doses per period
    dosageNumber = db.Column(db.Integer, index=True)
    numDays = db.Column(db.Integer, index=True)
    expirationDate = db.Column(db.DateTime, index=True)
    datePrescribed = db.Column(db.DateTime, index=True)
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
            'datePrescribed': self.datePrescribed,
            'timeOfDay': self.dosageNumber,
        }
        return d


# remove me
db.drop_all()


db.create_all()

##############################################################################
# VIEW
#############################################################################


def createDoc(email, password, name="", address="",
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


def createPatient(doctor, name, phoneNumber, email="", address="",
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


def createPrescription(patient, doctor, drugName='', drugManufacturer='',
                       dosage=None, dosagePeriod=None, dosageNumber=None,
                       numDays=None, expirationDate=None, datePrescribed=None,
                       timeOfDay=''):
    p = Prescription()
    p.patient = patient
    p.doctor = doctor
    p.drugName = drugName
    p.drugManufacturer = drugManufacturer
    p.dosage = dosage
    p.dosagePeriod = dosagePeriod
    p.dosageNumber = dosageNumber
    p.numDays = numDays
    p.expirationDate = expirationDate
    p.datePrescribed = datePrescribed
    p.timeOfDay = timeOfDay
    db.session.add(p)
    db.session.commit()
    return p


d = createDoc("hello@email.com", "password")
p = createPatient(d, "yes", 234)
createPrescription(p, d)


@app.route('/login', methods=['POST'])
def login():
    # REMOVE ME
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        # HANDLE ERRORS
        doctor = Doctor.query.filter_by(email=email, password=password).first()

        plist = []
        for p in doctor.patients:
            plist.append(p.to_dict())
        return jsonify({'doctor': doctor.to_dict(), 'patients': plist})


@app.route('/addPrescriptionView', methods=['POST'])
def addPrescription():
    if request.method == 'POST':
        p = request.get_json()
    return str(p)


@app.route('/addPatientView', methods=['POST'])
def addPatient():
    pass


@app.route('/addDoctorView', methods=['POST'])
def addDoctor():
    if request.method == 'POST':
        createDoc(request.form['email'], request.form['password'])
    return "yes"
