from django.shortcuts import render, redirect
import uuid
from django.db import connection
from . import forms
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import auth
from .models import Rider  
import bcrypt


def main(request):
    return render(request, "app/main.html")


import bcrypt


def register(request):
    if request.method == 'POST':  # Check if the form is submitted
        form = forms.RegistrationForm(request.POST)  # Create form instance with POST data
        if form.is_valid():  # Validate the form
            username = form.cleaned_data.get('username')  # Get the username
            phone_number = form.cleaned_data.get('phone_number')  # Get the phone number
            password = form.cleaned_data.get("password")  # Get the password
            
            # Hash the password before storing
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            user_id = str(uuid.uuid4())  # Generate a unique user ID as string
            
            try:
                # Write data directly to the PostgreSQL database using raw SQL
                with connection.cursor() as cursor:
                    # Insert the data into the rider table with the hashed password
                    cursor.execute(
                        "INSERT INTO rider (id, name, contact_details,location, password) VALUES (%s, %s, %s,%s, %s)",
                        [user_id, username, phone_number,None, hashed_password.decode('utf-8')]
                    )
                    # Debug print to confirm execution
                    print(f"SQL executed: Inserted rider with ID {user_id}")
                
                # Redirect to the main page after successful registration
                return redirect('app:main')
                
            except Exception as e:
                # Handle any database errors with detailed logging
                print(f"Database error: {e}")
                form.add_error(None, f"Registration failed: {e}")
        else:
            # Print form validation errors for debugging
            print(f"Form validation errors: {form.errors}")
    else:
        form = forms.RegistrationForm()  # Create an empty form instance on GET request
    
    return render(request, "app/register.html", {"form": form})



def log_in(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        print(f"Username: {username}, Password: {password}")

        try:
            print(f"Attempting to fetch rider with username: {username}")
            # Fetch the rider by username (assuming 'name' is used for username)
            rider = Rider.objects.get(name=username)
            print(f"Found rider: {rider.name}")

            # Compare the entered password with the stored hashed password using bcrypt
            if bcrypt.checkpw(password.encode('utf-8'), rider.password.encode('utf-8')):
                print("Password is correct!")
                request.session['rider_id'] = rider.id  # Store rider's id in the session
                print(f"Session set for rider_id: {rider.id}")
                return redirect('app:main')  # Redirect to the main page after successful login
            else:
                print("Password is incorrect.")
                messages.error(request, "Invalid username or password.")
        except Rider.DoesNotExist:
            print("Rider not found.")
            messages.error(request, "Invalid username or password.")

    return render(request, 'app/login.html')


def profile(request):
    return render(request,'app/profile.html')

def bookRide(request):
    return render(request, 'app/bookRide.html')

from django.shortcuts import render, redirect
from django.db import connection
from django.utils import timezone
def rideDetails(request):
    ride_details = request.session.get('ride_details', {})

    if not ride_details:
        return render(request, 'error.html', {'message': 'No ride details found.'})
    current_time = timezone.now()
    # Update the ride and driver status when going back to the main menu
    if 'back_to_main' in request.GET:
        ride_id = request.session.get('ride_id')  # Assuming ride_id is stored in session data
        driver_id = request.session.get('driver_id')  # Assuming driver_id is stored in session data
        with connection.cursor() as cursor:
         cursor.execute("""
        UPDATE rides 
        SET rides_status = 'completed', end_time = %s 
        WHERE id = %s;
        
        UPDATE driver 
        SET status = 'Available' 
        WHERE id = %s;
         """, [current_time, ride_id, driver_id])
        # Update the ride status and driver status
        
            
        return redirect('app:main')  # Replace 'main_menu' with the actual view name for your main menu

    return render(request, 'app/rideDetails.html', {'ride_details': ride_details})

# surge/views.py
from django.db import connection
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import SurgeAreaSerializer

def get_surge_areas():
    with connection.cursor() as cursor:
        cursor.execute("SELECT ST_AsGeoJSON(location), multiplier FROM surge_areas;")
        surge_areas = cursor.fetchall()

    surge_areas_list = [
        {"location": row[0], "multiplier": row[1]} for row in surge_areas
    ]
    return surge_areas_list

@api_view(['GET'])
def surge_areas_view(request):
    """
    API endpoint to return surge areas as JSON.
    """
    surge_areas = get_surge_areas()
    serializer = SurgeAreaSerializer(surge_areas, many=True)
    return Response({"surge_areas": serializer.data})

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db import connection
import uuid  # For generating unique ride ID
from datetime import datetime
from django.contrib.gis.geos import Point
import uuid
from datetime import datetime
from django.contrib.gis.geos import Point
from django.contrib.gis.geos import GEOSGeometry
import uuid
from datetime import datetime
import time
import json
from django.contrib import messages
from django.db import connection
from django.shortcuts import redirect, render
from datetime import datetime
import uuid
from django.contrib.gis.geos import Point

def searchDriver(request):
    print("search driver func")
    if request.method == 'POST':
        print(f"POST data: {request.POST}")
        
        # Get logged-in rider's ID
        rider_id = request.session.get('rider_id')
        if not rider_id:
            messages.error(request, "You must be logged in to book a ride.")
            return redirect('app:login')

        try:
            # Process location data
            pickup_location_str = request.POST.get('pickup_location')
            dropoff_location_str = request.POST.get('dropoff_location')
            vehicle_type = request.POST.get('vehicle_type')
            distance = request.POST.get("distance")
            duration = request.POST.get("duration")
            price = request.POST.get("price")
            route_coords_json = request.POST.get("route")

            # Validate required fields
            if not all([pickup_location_str, dropoff_location_str, route_coords_json]):
                messages.error(request, "Missing required ride details")
                return redirect('app:searchDriver')

            # Convert string coordinates to Point objects
            # The input is assumed to be in "lat,lng" order.
            pickup_lat, pickup_lng = map(float, pickup_location_str.split(','))
            dropoff_lat, dropoff_lng = map(float, dropoff_location_str.split(','))

            # Create PostGIS points (Note: Point expects (lng, lat))
            pickup_location = Point(pickup_lng, pickup_lat, srid=4326)
            dropoff_location = Point(dropoff_lng, dropoff_lat, srid=4326)

            # Process route coordinates from JSON.
            # Assume route_coords is a list of [lat, lng] pairs.
            route_coords = json.loads(route_coords_json)
            if len(route_coords) < 2:
                messages.error(request, "Invalid route coordinates")
                return redirect('app:searchDriver')

            # Convert to LineString in WKT format (swapping to lng lat order for WKT)
            linestring_coords = [
                f"{coord[1]} {coord[0]}"  # Swap to lng, lat
                for coord in route_coords
            ]
            linestring_wkt = f"LINESTRING({', '.join(linestring_coords)})"

            # Prepare other ride data
            ride_id = str(uuid.uuid4())
            start_time = datetime.now()
            distance_traveled = float(distance) if distance else 0.0
            final_price = float(price) if price else 0.0
            duration = float(duration) if duration else 0.0
            
            # Database insertion remains unchanged
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO rides (
                        id, driver_id, rider_id, 
                        pickup_location, dropoff_location, 
                        start_time, end_time, 
                        distance_traveled, route_taken, 
                        duration, final_price, rides_status
                    )
                    VALUES (
                        %s, %s, %s,
                        ST_GeomFromText(%s, 4326), ST_GeomFromText(%s, 4326),
                        %s, %s,
                        %s, ST_GeomFromText(%s, 4326),
                        %s, %s, %s
                    )
                    """,
                    [
                        ride_id,          # id
                        None,             # driver_id
                        rider_id,         # rider_id
                        pickup_location.wkt,  # pickup_location (WKT)
                        dropoff_location.wkt, # dropoff_location (WKT)
                        start_time,       # start_time
                        None,             # end_time
                        distance_traveled,# distance_traveled
                        linestring_wkt,   # route_taken (WKT)
                        duration,         # duration
                        final_price,      # final_price
                        "searching"       # rides_status
                    ]
                )
                connection.commit()

            # Store ride ID in session for next page
            request.session["ride_id"] = ride_id
            request.session["vehicle_type"] = vehicle_type
            print(f"here!!!: {start_time} , {distance_traveled} , {final_price} , {duration}")
            return render(request, "app/searchDriver.html", {
                "start_time": start_time,
                "distance_traveled": distance_traveled,
                "final_price": final_price, 
                "duration": duration,
                # Send the pickup and dropoff coordinates separately: 
                "pickup_lat": pickup_location.y,  # y is latitude
                "pickup_lng": pickup_location.x,  # x is longitude
                "dropoff_lat": dropoff_location.y,
                "dropoff_lng": dropoff_location.x,
                # Also send the route coordinates list for frontend use.
                # (Assuming route_coords is a list of [lat, lng] pairs)
                "route_coords": route_coords,
            })

        except ValueError as e:
            print(f"Value error: {e}")
            messages.error(request, "Invalid numerical values in form data")
        except json.JSONDecodeError:
            print("Invalid JSON in route data")
            messages.error(request, "Invalid route data format")
        except Exception as e:
            print(f"Error booking ride: {e}")
            messages.error(request, f"Error creating ride: {str(e)}")
        
        print(f"here22222!!!: {start_time} , {distance_traveled} , {final_price} , {duration}")
        return redirect('app:searchDriver')

    return render(request, 'app/searchDriver.html')



from django.db import connection, transaction
from django.db import connection, transaction
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
from django.db import transaction, connection
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from django.db import transaction, connection
from django.views.decorators.csrf import csrf_exempt

import json
from django.http import JsonResponse
from django.db import transaction, connection
from django.views.decorators.csrf import csrf_exempt

from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json

def parse_coordinates(coord):
    if isinstance(coord, dict):
        # Expecting keys "lat" and "lng"
        return float(coord.get("lat")), float(coord.get("lng"))
    elif isinstance(coord, str):
        # Expecting "lat,lng" format
        parts = coord.split(',')
        return float(parts[0].strip()), float(parts[1].strip())
    else:
        raise ValueError("Invalid coordinate format.")

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.db import connection, transaction
import json

def parse_coordinates(coord):
    if isinstance(coord, dict):
        # Expecting keys "lat" and "lng"
        return float(coord.get("lat")), float(coord.get("lng"))
    elif isinstance(coord, str):
        # Expecting "lat,lng" format
        parts = coord.split(',')
        return float(parts[0].strip()), float(parts[1].strip())
    else:
        raise ValueError("Invalid coordinate format.")

@csrf_exempt
def process_offers(request):
    print("here is process_offers")
    if request.method == 'POST':
        # Retrieve ride_id and vehicle_type from the session
        ride_id = request.session.get('ride_id')
        vehicle_type = request.session.get('vehicle_type')
        if not ride_id or not vehicle_type:
            return JsonResponse({'error': 'Missing ride ID or vehicle type in session.'}, status=400)

        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)

        # Extract required fields from the request data
        required_fields = ['pickup', 'dropoff', 'route', 'distance', 'duration', 'price', 'date']
        if not all(field in data for field in required_fields):
            return JsonResponse({'error': 'Missing required fields.'}, status=400)

        accepted_driver_id = None
        try:
            with transaction.atomic():
                with connection.cursor() as cursor:
                    # Insert available drivers into offer table
                    insert_query = """
                    INSERT INTO offer (ride_id, driver_id, status)
                    SELECT %s, d.id, 'Pending'
                    FROM driver d
                    JOIN rides r ON r.id = %s
                    JOIN vehicle v ON v.driver_id = d.id
                    WHERE d.status = 'Available'
                      AND v.type_id = %s
                      AND ST_DWithin(r.pickup_location::geography, d.location::geography, 50000)
                    GROUP BY d.id, r.pickup_location, d.location
                    ORDER BY ST_Distance(r.pickup_location::geography, d.location::geography) ASC
                    LIMIT 5
                    ON CONFLICT (ride_id, driver_id) DO NOTHING;
                    """
                    cursor.execute(insert_query, [ride_id, ride_id, vehicle_type])
                
                    # Assign a driver randomly
                    assign_query = """
                    WITH random_driver AS (
                        SELECT driver_id FROM offer
                        WHERE ride_id = %s AND status = 'Pending'::offer_status
                        ORDER BY RANDOM() LIMIT 1
                    )
                    UPDATE offer
                    SET status = CASE 
                                    WHEN driver_id = (SELECT driver_id FROM random_driver) THEN 'Accepted'::offer_status
                                    ELSE 'Rejected'::offer_status
                                END
                    WHERE ride_id = %s
                    RETURNING driver_id;
                    """
                    cursor.execute(assign_query, [ride_id, ride_id])
                    accepted = cursor.fetchone()
                    if accepted:
                        accepted_driver_id = accepted[0]
                    else:
                        return JsonResponse({'error': 'No driver accepted.'}, status=500)
                    
                    query = """
                    UPDATE rides 
                    SET rides_status = 'waiting for driver', driver_id = %s
                    WHERE id = %s
                    """
                    cursor.execute(query, (accepted_driver_id, ride_id))

                    # Update driver status
                    update_driver_query = "UPDATE driver SET status = 'Busy' WHERE id = %s;"
                    cursor.execute(update_driver_query, [accepted_driver_id])

                    # Add this query to update the ride_status to 'on the way'
                    update_ride_status_query = """
                    UPDATE rides 
                    SET rides_status = 'on the way'  
                    WHERE id = %s
                    """
                    cursor.execute(update_ride_status_query, (ride_id,))

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        # Retrieve vehicle details
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT type_id, make, model, color, plate_number FROM vehicle WHERE driver_id = %s", [accepted_driver_id])
                vehicle_data = cursor.fetchone()
                if not vehicle_data:
                    return JsonResponse({'error': 'Vehicle details not found.'}, status=500)

                cursor.execute("SELECT name FROM driver WHERE id = %s", [accepted_driver_id])
                driver_row = cursor.fetchone()
                driver_name = driver_row[0] if driver_row else None
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

        # Parse pickup/dropoff coordinates
        try:
            pickup_lat, pickup_lng = parse_coordinates(data['pickup'])
            dropoff_lat, dropoff_lng = parse_coordinates(data['dropoff'])
        except Exception:
            return JsonResponse({'error': 'Invalid coordinate format.'}, status=400)

        # Parse route coordinates
        try:
            route_coords = json.loads(data['route']) if isinstance(data['route'], str) else data['route']
        except Exception:
            route_coords = []
        
        # Store data in session
        request.session['driver_id'] = accepted_driver_id
        request.session['ride_details'] = {
            "start_time": data['date'],
            "distance_traveled": data['distance'],
            "final_price": data['price'],
            "duration": data['duration'],
            "pickup_lat": pickup_lat,
            "pickup_lng": pickup_lng,
            "dropoff_lat": dropoff_lat,
            "dropoff_lng": dropoff_lng,
            "route_coords": route_coords,
            "vehicle_type": vehicle_type,
            "make": vehicle_data[1],
            "model": vehicle_data[2],
            "color": vehicle_data[3],
            "plate_number": vehicle_data[4],
            "driver_name": driver_name,
        }

        return JsonResponse({'message': 'Offer processed successfully', 'redirect_url': '/rideDetails/'})

    return JsonResponse({'error': 'Invalid HTTP method.'}, status=405)

