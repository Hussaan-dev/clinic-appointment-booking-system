"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from clinic import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/',auth_views.LoginView.as_view(),name='login'),
    path('logout/',auth_views.LogoutView.as_view(),name='logout'),
    path('signup/',views.SignUpView.as_view(),name='signup'),
    path('',views.home,name='home'),
    path('patient/home/',views.PatientHomeView.as_view(),name='patient_home'),
    path('book-appointment/',views.AppointmentCreateView.as_view(),name='create_appointment'),
    path('patient/appointment/<int:pk>/',views.PatientAppointmentDetailView.as_view(),name='patient_appointment_detail'),
    path('patient/register/',views.PatientCreateView.as_view(),name='create_patient'),
    path('doctor/home/',views.DocHomeView.as_view(),name='doc_home'),
    path('doctor/appointment/<int:pk>/',views.DocAppointmentDetailView.as_view(),name='doc_appointment_detail'),
    path('doctor/appointment/<int:pk>/mark_confirmed/',views.mark_confirmed,name='mark_confirmed'),
    path('doctor/appointment/<int:pk>/mark_completed/',views.mark_completed,name='mark_completed'),
    path('doctor/appointment/<int:pk>/mark_cancelled/',views.mark_cancelled,name='mark_cancelled'),
    path('patient/appointment/<int:pk>/mark_cancelled/',views.patient_cancel,name='patient_cancel'),
]
