from django.http import HttpResponse
from django.http import JsonResponse
from django.models import Doctor
import json


def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loginEmail = data["email"]
        loginPassword = data["password"]
        doc = Doctor.objects.get(email=loginEmail, password=loginPassword)
        # HANDLE ERRORS

        doctorData = {}
        patientData = {}
        for item in doc.__dict__.items():
            doctorData[item[0]] = item[1]
            
        
