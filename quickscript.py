from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, jsonify
from flask_cors import CORS
from twilio.rest import TwilioRestClient
from flask_apscheduler import APScheduler
import datetime
import dateparser
from flask_login import LoginManager, login_required, login_user
from flask_login import current_user, logout_user
from flask.ext.session import Session

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

app.secret_key = 'A0Zr98j/37X R~XaH!jcN]LDX/,?ET'
app.config['SESSION_TYPE'] = 'filesystem'
sess = Session()
sess.init_app(app)

SCHEDULER_API_ENABLED = True
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

login_manager = LoginManager()
login_manager.init_app(app)

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
    authenticated = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False

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


@login_manager.user_loader
def load_user(user_id):
    return Doctor.query.get(user_id)


class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), index=True)
    phoneNumber = db.Column(db.Integer)
    email = db.Column(db.String(256), index=True)
    address = db.Column(db.String(256), index=True)
    dob = db.Column(db.DateTime, index=True)
    ssn = db.Column(db.String, index=True, unique=True)
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
    dosage = db.Column(db.Integer, index=True)
    # take every x days
    dosagePeriod = db.Column(db.Integer, index=True)
    # number of doses per period
    dosageNumber = db.Column(db.Integer, index=True)
    totalNumDoses = db.Column(db.Integer, index=True)
    expirationDate = db.Column(db.DateTime, index=True)
    datePrescribed = db.Column(db.DateTime, index=True)
    timeOfDay = db.Column(db.String(256), index=True)
    pharmacyFilled = db.Column(db.Boolean, index=True)

    def to_dict(self):
        d = {
            'drugName': self.drugName,
            'dosage': self.dosage,
            'dosagePeriod': self.dosagePeriod,
            'dosageNumber': self.dosageNumber,
            'totalNumDoses': self.totalNumDoses,
            'expirationDate': self.dosage,
            'datePrescribed': self.datePrescribed,
            'timeOfDay': self.timeOfDay,
            'pharmacyFilled': self.pharmacyFilled
        }
        return d


# db.drop_all()

db.create_all()

#############################################################################
# VIEW
#############################################################################


def createDoc(email, password, dob, name="", address="",
              practiceName="", specialty=""):
    doc = Doctor()
    doc.email = email
    doc.password = password
    doc.name = name
    doc.address = address
    doc.dob = dateparser.parse(dob)
    doc.practiceName = practiceName
    doc.specialty = specialty
    db.session.add(doc)
    db.session.commit()
    return doc


@login_required
def createPatient(doctor, name, phoneNumber, dob, email="", address="",
                  ssn=None):
    p = Patient()
    p.name = name
    p.phoneNumber = phoneNumber
    p.email = email
    p.address = address
    p.dob = dateparser.parse(dob)
    p.ssn = ssn
    p.doctor = doctor
    db.session.add(p)
    db.session.commit()
    return p


@login_required
def createPrescription(patient, doctor, datePrescribed,
                       expirationDate,
                       dosage=None, dosagePeriod=None, dosageNumber=None,
                       totalNumDoses=None,
                       timeOfDay='',
                       pharmacyFilled=False, drugName=''):
    p = Prescription()
    p.patient = patient
    p.doctor = doctor
    p.drugName = drugName
    p.dosage = dosage
    p.dosagePeriod = dosagePeriod
    p.dosageNumber = dosageNumber
    p.totalNumDoses = totalNumDoses
    p.expirationDate = dateparser.parse(expirationDate).date()
    p.datePrescribed = dateparser.parse(datePrescribed).date()
    p.timeOfDay = timeOfDay
    p.pharmacyFilled = pharmacyFilled
    db.session.add(p)
    db.session.commit()
    return p


# d = createDoc("a@b.com", "ab", )
# p = createPatient(d, "yes", 234)
# createPrescription(p, d, drugName="Xanax", dosage=1, dosagePeriod=2,
# dosageNumber=7)


@app.route('/loginDoctor', methods=['POST'])
def loginDoc():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']

        doctor = Doctor.query.filter_by(email=email, password=password).first()
        if type(doctor) != Doctor:
            return "Invalid username or password"
        else:
            doctor.authenticated = True
            db.session.add(doctor)
            db.session.commit()
            login_user(doctor, remember=True)

            plist = []
            for p in doctor.patients:
                plist.append(p.to_dict())
            return jsonify({'doctor': doctor.to_dict(), 'patients': plist})


@app.route('/loginDoctor', methods=['POST'])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()


# @app.route('/loginPharmacy', methods=['POST'])
# def loginPharm():
#     if request.method == 'POST':
#         email = request.json['email']
#         password = request.json['password']

#         doctor = Doctor.query.filter_by(email=email, password=password).first()
#         if type(doctor) != Doctor:
#             return "Invalid username or password"

#         plist = []
#         for p in doctor.patients:
#             plist.append(p.to_dict())
#         return jsonify({'doctor': doctor.to_dict(), 'patients': plist})


@app.route('/addPrescriptionView', methods=['POST'])
def addPrescription():
    if request.method == 'POST':
        createPrescription(request.json['patient'], request.json['doctor'],
                           request.json['drugName'],
                           request.json['dosage'],
                           request.json['dosagePeriod'],
                           request.json['dosageNumber'],
                           request.json['totalNumDoses'],
                           request.json['expirationdate'],
                           request.json['datePrescribed'],
                           request.json['timeOfDay'])
        return "Prescription added"


@app.route('/addPatientView', methods=['POST'])
def addPatient():
    print(request.json['ssn'])
    if request.method == 'POST':
        createPatient(request.json['doctor'], request.json['name'],
                      request.json['phoneNumber'], request.json['email'],
                      request.json['address'], request.json['dob'],
                      request.json['ssn'])
        return "Patient added"


@app.route('/addDoctorView', methods=['POST'])
def addDoctor():
    print(request.json['dob'])
    if request.method == 'POST':
        createDoc(request.json['email'], request.json['password'],
                  request.json['name'], request.json['address'],
                  request.json['dob'], request.json['practiceName'],
                  request.json['specialty'])
        return "Doctor added"


#############################################################################
# TWILLIO
#############################################################################


ACCOUNT_SID = "AC196bde1976f17bec537a18d74ddfc9dc"
AUTH_TOKEN = "497c27040c7ef630efe7fb8757ff1c8a"

client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)


class SchedulerConfig(object):
    JOBS = [
        {
            'id': 'sendText',
            'func': 'jobs:checkPrescriptions',
            'args': (),
            'trigger': 'interval',
            'seconds': 60
        }
    ]


def checkPrescriptions():
    MORNING = 8
    NOON = 12
    EVENING = 17

    curDate = datetime.date.today()
    curTime = datetime.datetime.now().hour
    for patient in Patient.query.all():
        phoneNumber = str(patient.phoneNumber)
        drugList = []
        for p in patient.prescriptions:
            if p.totalNumDoses > 0 and (days_between(curDate, p.datePrescribed)
                                        % p.dosagePeriod == 0):
                if "Morning" in p.timeOfDay and curTime == MORNING:
                    drugList.append(p)
                    p.totalNumDoses = p.totalNumDoses - p.dosageNumber
                    db.session.add(p)
                    db.session.commit()
                elif "Noon" in p.timeOfDay and curTime == NOON:
                    drugList.append(p)
                    p.totalNumDoses = p.totalNumDoses - p.dosageNumber
                    db.session.add(p)
                    db.session.commit()
                elif "Evening" in p.timeOfDay and curTime == EVENING:
                    drugList.append(p)
                    p.totalNumDoses = p.totalNumDoses - p.dosageNumber
                    db.session.add(p)
                    db.session.commit()
        sendtext(phoneNumber, drugList)


def sendtext(phoneNumber, drugList):
    text = "Please take these drugs today: \n"
    for drug in drugList:
        text += "{} doses of {}\n".format(drug.dosageNumber, drug.drugName)
    client.sms.messages.create(to=str(phoneNumber),
                               from_="18562194208",
                               body=text)


def days_between(d1, d2):
    d1 = datetime.datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days)
