from rest_framework import serializers
from .models import Doctor,Appointment

class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Doctor
        fields=['id','name','room','specialty'] #removed user

class AppointmentSerializer(serializers.ModelSerializer):
    class Meta:
        model=Appointment
        fields=['id','patient','doctor','appointment_time','status']
        read_only_fields= ['patient', 'status']