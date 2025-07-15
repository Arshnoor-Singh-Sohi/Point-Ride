# accounts/urls.py - COMPLETE MATCHING URLs

from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # ===================================
    # REGISTRATION URLS
    # ===================================
    
    # Primary registration URLs
    path('register/traveller/', views.traveller_register, name='traveller_register'),
    path('register/driver/step1/', views.driver_register, name='driver_register'),
    
    # Alternative registration URLs for compatibility
    path('traveller-registration/', views.traveller_register, name='traveller_registration'),
    path('driver-registration/', views.driver_register, name='driver_registration_step1'),
    
    # Legacy compatibility URLs
    path('register/traveller/signup/', views.traveller_register, name='traveller_signup'),
    path('register/driver/signup/', views.driver_register, name='driver_signup'),
    
    # ===================================
    # LOGIN / LOGOUT URLS
    # ===================================
    
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    
    # Alternative login URLs
    path('signin/', views.user_login, name='signin'),
    path('signout/', views.user_logout, name='signout'),
    
    # ===================================
    # DASHBOARD URLS
    # ===================================
    
    path('dashboard/traveller/', views.traveller_dashboard, name='traveller_dashboard'),
    path('dashboard/driver/', views.driver_dashboard, name='driver_dashboard'),
    
    # Alternative dashboard URLs
    path('traveller/dashboard/', views.traveller_dashboard, name='traveller_home'),
    path('driver/dashboard/', views.driver_dashboard, name='driver_home'),
    
    # ===================================
    # PROFILE URLS
    # ===================================
    
    path('profile/', views.profile_view, name='profile'),
    path('profile/view/', views.profile_view, name='profile_view'),
    path('switch-role/', views.switch_role, name='switch_role'),
    
    # ===================================
    # UTILITY URLS
    # ===================================
    
    path('health/', views.health_check, name='health_check'),
    
    # Debug URLs (remove in production)
    path('debug/user-info/', views.debug_user_info, name='debug_user_info'),
    
    # ===================================
    # LEGACY COMPATIBILITY URLS
    # ===================================
    
    # For any old links that might exist
    path('registration/traveller/', views.traveller_register, name='legacy_traveller_registration'),
    path('registration/driver/', views.driver_register, name='legacy_driver_registration'),
    path('accounts/login/', views.user_login, name='legacy_login'),
    path('accounts/logout/', views.user_logout, name='legacy_logout'),
]