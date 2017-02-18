from django.http import HttpResponse
from django.http import JsonResponse
import django.models as model
import json


def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loginEmail = data["email"]
        loginPassword = data["password"]
        doctorPatient = model.DoctorPatient.objects.get(
            doctor.email=loginEmail, doctor.password=loginPassword)

        doctor = doctorPatient.doctor
        patient = doctorPatient.patient
        notes = doctorPatient.notes

        doctorData = {}
        patientData = {}
        for item in doc.__dict__.items():
            doctorData[item[0]] = item[1]

        for item in 
