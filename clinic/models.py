from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Doctor(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    room=models.PositiveIntegerField()
    specialty=models.CharField(max_length=200)

    def __str__(self):
        return f"{self.name} — {self.specialty}"

class Patient(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    name=models.CharField(max_length=200)
    age=models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Appointment(models.Model):
    appointment_time=models.DateTimeField()
    doctor=models.ForeignKey(Doctor,on_delete=models.CASCADE,related_name="appointments")
    patient= models.ForeignKey(Patient,on_delete=models.CASCADE,related_name="appointments")

    STATUS_CHOICES=[("Pending","Pending"),("Confirmed","Confirmed")
            ,("Cancelled","Cancelled"),("Completed","Completed")]

    status=models.CharField(max_length=20,choices=STATUS_CHOICES,default="Pending")

    def __str__(self):
        return f"{self.patient.name} → Dr.{self.doctor.name} ({self.appointment_time:%b %d %Y, %I:%M %p})"


