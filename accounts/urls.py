# accounts/urls.py

from django.urls import path
from . import views  # Import views from the current app

app_name = 'accounts'  # Namespace for this app's URLs

urlpatterns = [
    # URL for traveller registration
    path('register/traveller/', views.TravellerRegistrationView.as_view(), name='traveller_registration'),

    # URL for driver registration - Step 1
    path('register/driver/step1/', views.DriverRegistrationStep1View.as_view(), name='driver_registration_step1'),

    # URL for user login
    path('login/', views.CustomLoginView.as_view(), name='login'),

    # URL for user logout
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    path('register/traveller/', views.traveller_register, name='traveller_register'),

    path('dashboard/traveller/', views.traveller_dashboard, name='traveller_dashboard'),

    path('dashboard/driver/', views.driver_dashboard, name='driver_dashboard'),

]
