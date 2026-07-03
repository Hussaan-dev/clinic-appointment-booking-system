from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView,DetailView,TemplateView,UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment,Doctor,Patient
from .forms import AppointmentForm
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import redirect

class SignUpView(CreateView):
    form_class=UserCreationForm
    template_name='registration/signup.html'
    success_url=reverse_lazy('login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('home')
    if hasattr(request.user,"patient"):
        return redirect('patient_home')
    if hasattr(request.user,"doctor"):
        return redirect("doc_home")
    else:
        return redirect("create_patient")

class PatientCreateView(LoginRequiredMixin,CreateView):
    model=Patient
    template_name='clinic/create_patient.html'
    fields=['name','age']
    success_url=reverse_lazy('home')

    def form_valid(self,form):
        form.instance.user=self.request.user
        return super().form_valid(form)
    
    def dispatch(self,request,*args,**kwargs) :
        if hasattr(request.user,"patient"):
            return redirect('patient_home')
        if hasattr(request.user,"doctor"):
            return redirect('doc_home')
        return super().dispatch(request, *args, **kwargs)

class PatientHomeView(LoginRequiredMixin,TemplateView):
    template_name="clinic/patient_home.html"

    def get_context_data(self,**kwargs):
        context= super().get_context_data(**kwargs)

        appointments=Appointment.objects.filter(patient__user=self.request.user)
        context["pending_appointments"] = appointments.filter(status="Pending").order_by('appointment_time')
        context["confirmed_appointments"] = appointments.filter(status="Confirmed").order_by('appointment_time')
        context["completed_appointments"] = appointments.filter(status="Completed").order_by('-appointment_time')
        context["cancelled_appointments"] = appointments.filter(status="Cancelled").order_by('-appointment_time')
        return context


class AppointmentCreateView(LoginRequiredMixin,CreateView):
    model=Appointment
    template_name='clinic/create_app.html'
    form_class=AppointmentForm
    success_url=reverse_lazy('home')

    def form_valid(self, form):
        patient=Patient.objects.get(user=self.request.user)
        form.instance.patient=patient
        return super().form_valid(form)
    
class PatientAppointmentDetailView(LoginRequiredMixin,DetailView):
    model=Appointment
    template_name='clinic/patient_app_detail.html'
    context_object_name='appointment'

class DocHomeView(LoginRequiredMixin,TemplateView):
    template_name="clinic/doc_home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        appointments = Appointment.objects.filter(doctor__user=self.request.user)
        context["pending_appointments"] = appointments.filter(status="Pending").order_by('appointment_time')
        context["confirmed_appointments"] = appointments.filter(status="Confirmed").order_by('appointment_time')
        context["completed_appointments"] = appointments.filter(status="Completed").order_by('-appointment_time')
        context["cancelled_appointments"] = appointments.filter(status="Cancelled").order_by('-appointment_time')
        return context
    
class DocAppointmentDetailView(LoginRequiredMixin,DetailView):
    model=Appointment
    template_name='clinic/doc_app_detail.html'
    context_object_name='appointment'
    
def mark_confirmed(request,pk):
    if request.method=='POST':
        appointment=Appointment.objects.get(pk=pk,doctor__user=request.user)
        appointment.status='Confirmed'
        appointment.save()
    return redirect('doc_appointment_detail',pk=pk)

def mark_completed(request,pk):
    if request.method == 'POST':
        appointment=Appointment.objects.get(pk=pk,doctor__user=request.user)
        appointment.status="Completed"
        appointment.save()
        return redirect("doc_appointment_detail",pk=pk)

def mark_cancelled(request,pk):
    if request.method == 'POST':
        appointment=Appointment.objects.get(pk=pk,doctor__user=request.user)
        appointment.status="Cancelled"
        appointment.save()
        return redirect("doc_appointment_detail",pk=pk)

def patient_cancel(request,pk):
    if request.method == 'POST':
        appointment=Appointment.objects.get(pk=pk,patient__user=request.user)
        appointment.status="Cancelled"
        appointment.save()
        return redirect("patient_appointment_detail",pk=pk)