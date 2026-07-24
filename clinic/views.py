from django.urls import reverse_lazy
from django.views.generic import CreateView,DetailView,TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Appointment,Doctor,Patient
from .forms import AppointmentForm,SignUpForm
from django.shortcuts import redirect
from datetime import datetime,timedelta
from django.utils import timezone
from .serializers import DoctorSerializer,AppointmentSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated,AllowAny

class AppointmentViewSet(viewsets.ModelViewSet):
    serializer_class=AppointmentSerializer
    permission_classes=[IsAuthenticated]
    http_method_names = ['get', 'patch', 'head']  # no post,put,delete

    def get_queryset(self): #overrides queryset=Appointment.objects.all() and uses basename in urls
        user=self.request.user
        if hasattr(user,'patient'):
            return user.patient.appointments.all()
        elif hasattr(user,'doctor'):
            return user.doctor.appointments.all()
        return Appointment.objects.none()

class DoctorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset=Doctor.objects.all()
    serializer_class=DoctorSerializer
    permission_classes=[AllowAny]

class SignUpView(CreateView):
    form_class=SignUpForm
    template_name='registration/signup.html'
    success_url=reverse_lazy('login')

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')
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

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user,"doctor"):
            return redirect("doc_home")
        return super().dispatch(request, *args, **kwargs)

class BookAppointmentView(LoginRequiredMixin,TemplateView):
    template_name='clinic/book_app.html'

    def get_context_data(self,**kwargs):
        context=super().get_context_data(**kwargs)
        context['doctors']=Doctor.objects.all()
        doctor_id=self.request.GET.get('doctor')
        date_str=self.request.GET.get('date')
        context['selected_doctor_id']=doctor_id

        if doctor_id and date_str:
            doctor=Doctor.objects.get(pk=doctor_id)
            selected_date=datetime.strptime(date_str,'%Y-%m-%d').date()
            context['slots']=get_available_slots(doctor,selected_date)
            context['selected_date']=date_str
        return context

class AppointmentCreateView(LoginRequiredMixin, CreateView):
    model = Appointment
    template_name = 'clinic/create_app.html'
    form_class = AppointmentForm
    success_url = reverse_lazy('home')

    def get_initial(self):
        initial = super().get_initial()
        doctor_id = self.request.GET.get('doctor')
        time_str = self.request.GET.get('time')
        if doctor_id:
            initial['doctor'] = doctor_id
        if time_str:
            initial['appointment_time'] = time_str
        return initial

    def form_valid(self, form):
        patient = Patient.objects.get(user=self.request.user)
        form.instance.patient = patient
        return super().form_valid(form)
    
class PatientAppointmentDetailView(LoginRequiredMixin,DetailView):
    model=Appointment
    template_name='clinic/patient_app_detail.html'
    context_object_name='appointment'

    def get_queryset(self):
        return Appointment.objects.filter(patient__user=self.request.user)

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

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user,"patient"):
            return redirect("patient_home")
        return super().dispatch(request, *args, **kwargs)
    
class DocAppointmentDetailView(LoginRequiredMixin,DetailView):
    model=Appointment
    template_name='clinic/doc_app_detail.html'
    context_object_name='appointment'

    def get_queryset(self):
        return Appointment.objects.filter(doctor__user=self.request.user)
    
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

def get_available_slots(doctor,date):
    slots=[]
    start= datetime.combine(date,datetime.min.time()).replace(hour=9)
    end= datetime.combine(date,datetime.min.time()).replace(hour=17)

    while start<end:
        slots.append(timezone.make_aware(start))
        start+= timedelta(minutes=30)

    booked_time=doctor.appointments.filter(appointment_time__date=date
                    ).values_list('appointment_time',flat=True) #returns list otherwise would return list of tuples w/o flat=True
    
    available=[s for s in slots if s not in booked_time and s> timezone.now()]
    return available
