# pointRide/urls.py

from django.contrib import admin
from django.urls import path, include # Import include
from django.conf import settings # Import settings to access MEDIA_URL/MEDIA_ROOT
from django.conf.urls.static import static # Import static to serve media files
from django.contrib.auth import views as auth_views

# Import the home view from the accounts app
from accounts.views import home
from rides.views import route_map  # Import the specific view for maps

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include accounts app URLs under the 'accounts/' path
    path('accounts/', include('accounts.urls')),
    
    # Include rides app URLs under the 'rides/' path
    path('rides/', include('rides.urls')),
    
    # Map route for your teammate's map work (specific endpoint)
    path('accounts/maps/', route_map, name='accounts_maps'),  # This connects to your teammate's work

    # Set the home view for the root URL
    path('', home, name='home'), # This uses the 'home' view from accounts.views

    # ===================================
    # FORGOT PASSWORD URLS
    # ===================================
    
    path('forgot-password/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset.html'
    ), name='password_reset'),
    path('forgot-password/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete')

    # Add URLs for other apps as they are developed:
    # path('verification/', include('verification.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
