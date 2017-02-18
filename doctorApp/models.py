from django.db import models


class Doctor(models.Model):
    name = models.CharField(max_length=256)
    address = models.CharField(max_length=256)
    dob = models.DateTimeField()
    practiceName = models.CharField(max_length=256)
    specialty = models.CharField(max_length=256)
    email = models.CharField(max_length=256)
    password = models.CharField(max_length=256)
    patients = models.ManyToManyField(Patient)


class Patient(models.Model):
    address = models.CharField(max_length=256)
    name = models.CharField(max_length=256)
    ssn = models.IntegerField(default=0)
    dob = models.DateTimeField()
    doctor = models.ManyToManyField(Doctor)


class Drug(models.Model):
    drugName = models.CharField(max_length=256)
    manufacturer = models.CharField(max_length=256)


class Perscription(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor,on_delete=models.CASCADE)
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    dosage = models.IntegerField(default=0)

    # take every x days
    dosagePeriod = models.IntegerField(default=0)
    # number of doses
    dosageNumber = models.IntegerField(default=0)
    # number of days
    numDays = models.IntegerField(default=0)

    expirationDate = models.DateTimeField()
    datePerscribed = models.DateTimeField()
