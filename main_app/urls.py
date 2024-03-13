from django.urls import path
from main_app import views
from django.contrib import admin

#Django Admin Customization
admin.site.site_header = "Pairit Admin Panel"
admin.site.site_title = "Pairit"
admin.site.index_title = "Admin Panel"

urlpatterns = [
     path('', views.home, name='home'),
     path('find_data/', views.find_data, name='find_data'),
]