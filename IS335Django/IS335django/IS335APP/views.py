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

def rideDetails(request):
    return render(request , 'app/rideDetails.html')

# def log_out(request):
#     auth.logout(request)

#     return redirect("log_in")

