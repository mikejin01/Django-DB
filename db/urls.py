from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('compliance/<int:building_id>/', views.building_compliance_detail, name='building_compliance_detail'),
    path('client/<int:client_id>/', views.client_detail, name='client_detail'),
    path('import-excel/', views.import_excel, name='import_excel'),
]
