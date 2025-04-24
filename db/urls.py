from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('client/<int:client_id>/', views.client_detail, name='client_detail'),
    path('import-excel/', views.import_excel, name='import_excel'),
    path('preview-gsheet/', views.preview_gsheet, name='preview_gsheet'),
    path('import-gsheet/', views.import_gsheet, name='import_gsheet'),
    path('delete-all-data/', views.delete_all_data, name='delete_all_data'),
    path('building/<int:building_id>/', views.building_detail, name='building_detail'),
    path('admin-view/', views.admin_view, name='admin_view'),  # New URL for admin view
    path('building/update-bins/<int:building_id>/', views.building_update_bins, name='building_update_bins'),
    path('process-all-buildings/', views.process_all_buildings, name='process_all_buildings'),  
    path('update-tracking/', views.update_tracking, name='update_tracking'),  # New URL pattern
]
