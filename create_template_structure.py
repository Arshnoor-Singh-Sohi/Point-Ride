# create_template_structure.py
# Create the necessary template directories and basic templates

import os

def create_template_structure():
    """Create template directories and basic template files"""
    
    # Create template directories
    template_dirs = [
        'rides/templates',
        'rides/templates/rides'
    ]
    
    for dir_path in template_dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"✅ Created directory: {dir_path}")
    
    # Basic template content to prevent TemplateDoesNotExist errors
    basic_templates = {
        'rides/templates/rides/home_search.html': '''{% extends 'base.html' %}
{% block title %}Find Rides - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Find Your Ride</h1>
    <p>Search for available rides (Template created - functionality coming soon)</p>
    <form method="post">
        {% csrf_token %}
        <div class="mb-3">
            <label>Pickup Location</label>
            <input type="text" name="pickup_location" class="form-control" placeholder="Enter pickup location">
        </div>
        <div class="mb-3">
            <label>Drop-off Location</label>
            <input type="text" name="dropoff_location" class="form-control" placeholder="Enter drop-off location">
        </div>
        <button type="submit" class="btn btn-primary">Search Rides</button>
    </form>
</div>
{% endblock %}''',

        'rides/templates/rides/search_rides.html': '''{% extends 'base.html' %}
{% block title %}Search Results - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Search Results</h1>
    <p>Available rides will be displayed here (Template created - functionality coming soon)</p>
    <a href="{% url 'rides:home_search' %}" class="btn btn-secondary">Back to Search</a>
</div>
{% endblock %}''',

        'rides/templates/rides/create_ride.html': '''{% extends 'base.html' %}
{% block title %}Create Ride - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Create New Ride</h1>
    <p>Create a new ride offering (Template created - functionality coming soon)</p>
    <form method="post">
        {% csrf_token %}
        <div class="mb-3">
            <label>Pickup City</label>
            <select name="pickup_city" class="form-control">
                <option value="">Select pickup city</option>
            </select>
        </div>
        <div class="mb-3">
            <label>Drop-off City</label>
            <select name="dropoff_city" class="form-control">
                <option value="">Select drop-off city</option>
            </select>
        </div>
        <div class="mb-3">
            <label>Price per Seat</label>
            <input type="number" name="price_per_seat" class="form-control" step="0.01">
        </div>
        <button type="submit" class="btn btn-primary">Create Ride</button>
    </form>
    <a href="{% url 'accounts:driver_dashboard' %}" class="btn btn-secondary">Back to Dashboard</a>
</div>
{% endblock %}''',

        'rides/templates/rides/ride_detail.html': '''{% extends 'base.html' %}
{% block title %}Ride Details - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Ride Details</h1>
    <p>Ride details will be displayed here (Template created - functionality coming soon)</p>
    <a href="{% url 'rides:search_rides' %}" class="btn btn-secondary">Back to Search</a>
</div>
{% endblock %}''',

        'rides/templates/rides/booking_detail.html': '''{% extends 'base.html' %}
{% block title %}Booking Details - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Booking Details</h1>
    <p>Booking details will be displayed here (Template created - functionality coming soon)</p>
</div>
{% endblock %}''',

        'rides/templates/rides/route_map.html': '''{% extends 'base.html' %}
{% block title %}Route Map - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>Route Map</h1>
    <p>Interactive route map will be displayed here</p>
    <p>This connects to your teammate's map functionality</p>
    <div id="map-container" style="height: 400px; background: #f8f9fa; border: 1px solid #dee2e6;">
        <div class="d-flex align-items-center justify-content-center h-100">
            <p class="text-muted">Map interface loading...</p>
        </div>
    </div>
</div>
{% endblock %}''',

        'rides/templates/rides/my_rides_traveller.html': '''{% extends 'base.html' %}
{% block title %}My Bookings - pointRide{% endblock %}
{% block content %}
<div class="container py-5">
    <h1>My Bookings</h1>
    <p>Your ride bookings will be displayed here (Template created - functionality coming soon)</p>
    <a href="{% url 'rides:home_search' %}" class="btn btn-primary">Find New Rides</a>
</div>
{% endblock %}'''
    }
    
    # Create template files
    for file_path, content in basic_templates.items():
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Created template: {file_path}")
    
    print("\n🎉 All template files created successfully!")
    print("Templates are basic but functional - no more TemplateDoesNotExist errors!")

if __name__ == "__main__":
    create_template_structure()