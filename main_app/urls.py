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
     path('signup/', views.signup, name='signup'),
     path('login/', views.user_login, name='login'),
     path('community/', views.community, name='community'),
     path('contact/', views.contact, name='contact'),
     path('about/', views.about, name='about'),
     path('account/', views.account, name='account'),
     path('cart/', views.cart, name='cart'),
     path('logout/', views.user_logout, name='logout'),
     path('share_data/', views.share_data, name='share_data'),
     path('add_data/', views.add_data, name='add_data'),
     path('update_data/', views.update_data, name='update_data'),
     path('delete_data/', views.update_data, name='delete_data'),
     path('get_listing_details/', views.get_listing_details, name='get_listing_details'),
     path('find_data/<int:product_id>/<str:username>/', views.prod_info, name='prod_info'),
     path('rating/', views.rating, name='rating'),
     path('generate_payment_link/', views.generate_payment_link, name='generate_payment_link'),
     path('payment_success/', views.payment_success, name='payment_success'),
     path('purchased_items/', views.purchased_items, name='purchased_items'),
     path('successful_payment/', views.successful_payment, name='successful_payment'),
 
]