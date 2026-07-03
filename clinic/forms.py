from .models import Appointment
from django import forms

class AppointmentForm(forms.ModelForm):
    class Meta:
        model=Appointment
        fields=['doctor','appointment_time']
        widgets= {
            'appointment_time': forms.DateTimeInput(
                attrs={'type':'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            )
        }