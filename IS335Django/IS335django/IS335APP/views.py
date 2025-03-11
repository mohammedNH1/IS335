
from django.shortcuts import render, redirect
import uuid
from django.db import connection
from . import forms
from django.http import HttpResponse 
# def register(request):
#     return HttpResponse("teeet")


def main(request):
    return render(request, "app/main.html")



def register(request):
    if request.method == 'POST':  # Check if the form is submitted
        form = forms.RegistrationForm(request.POST)  # Create form instance with POST data
        if form.is_valid():  # Validate the form
            name = form.cleaned_data.get('username')  # Get the username
            contact_details = form.cleaned_data.get('phone_number')  # Get the phone number
            password = form.cleaned_data.get("password")  # Get the password
            user_id = uuid.uuid4()  # Generate a unique user ID

            try:
                # Write data directly to the PostgreSQL database using raw SQL
                with connection.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO your_table_name (id, username, contact_details, password, location) VALUES (%s, %s, %s, %s, NULL)",
                        [user_id, name, contact_details, password]
                    )
                # Redirect to the main menu after successful registration
                return redirect('main_menu')  # Redirect to the main menu page
            except Exception as e:
                # Handle any database errors (you can log the error or show an error message)
                print(f"Error inserting into the database: {e}")
                form.add_error(None, "There was an error with the registration. Please try again.")
        else:
            # If form is invalid, it will be redisplayed with errors
            print("Form is not valid")
    else:
        form = forms.RegistrationForm()  # Create an empty form instance on GET request

    return render(request, "app/register.html", {"form": form})




