from django.urls import path
from . import views

urlpatterns = [
    path('ping/', views.ping, name='ping'),
    path('prescription/analyze/', views.analyze_prescription, name='analyze_prescription'),
]
