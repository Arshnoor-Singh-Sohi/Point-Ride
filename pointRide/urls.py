# pointRide/urls.py

from django.contrib import admin
from django.urls import path, include # Import include
from django.conf import settings # Import settings to access MEDIA_URL/MEDIA_ROOT
from django.conf.urls.static import static # Import static to serve media files

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

    # Add URLs for other apps as they are developed:
    # path('verification/', include('verification.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)