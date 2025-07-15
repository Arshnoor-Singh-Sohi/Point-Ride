# pointRide/urls.py

from django.contrib import admin
from django.urls import path, include # Import include
from django.conf import settings # Import settings to access MEDIA_URL/MEDIA_ROOT
from django.conf.urls.static import static # Import static to serve media files

# Import the home view from the accounts app
from accounts.views import home

urlpatterns = [
    path('admin/', admin.site.urls),

    # Include accounts app URLs under the 'accounts/' path
    path('accounts/', include('accounts.urls')),

    # Set the home view for the root URL
    path('', home, name='home'), # This uses the 'home' view from accounts.views

    # Add URLs for other apps as they are developed:
    # path('rides/', include('rides.urls')),
    # path('verification/', include('verification.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

