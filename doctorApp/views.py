from django.http import HttpResponse
from django.http import JsonResponse
import django.models as model
import json


def index(request):
    if request.method == "POST":
        data = json.loads(request.body)
        loginEmail = data["email"]
        loginPassword = data["password"]
        docObject = model.Doctor.objects.get(email=loginEmail,
                                             password=loginPassword)

        doctor = docObject.__dict__.pop("patients")
        patients = []

        for p in docObject.patients.all():
            perscriptionList = []
            for q in p.perscriptions.all():
                perscriptionList.append(q.__dict__)
            p.perscriptions = perscriptionList
            patients.append(p.__dict__)

        responseData = {"doctor": doctor, "patients":patients}
        responseData = json.dumps(responseData)
        
