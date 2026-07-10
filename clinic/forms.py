from .models import Appointment
from django import forms
from django.utils import timezone

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
    def clean_appointment_time(self):
        appointment_time = self.cleaned_data['appointment_time']
        if appointment_time < timezone.now():
            raise forms.ValidationError("You can't book an appointment in the past")
        return appointment_time