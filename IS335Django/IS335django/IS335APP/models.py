from django.db import models
from django.contrib.gis.db import models as gis_models  # for geography and geometry fields
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
import hashlib

# Enum-like status fields can be represented as choices in Django

class Driver(models.Model):
    DRIVER_STATUS_CHOICES = [
        ('Available', 'Available'),
        ('Busy', 'Busy'),
    ]

    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    license_info = models.CharField(max_length=255)
    contact_details = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=50, choices=DRIVER_STATUS_CHOICES)
    location = gis_models.PointField(srid=4326)  # Use SRID 4326 for WGS84 coordinate system

    def __str__(self):
        return self.name

class Rider(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    contact_details = models.CharField(max_length=255)
    #location = gis_models.PointField(srid=4326)  # Use SRID 4326 for WGS84 coordinate system
    password = models.CharField(max_length=255)

    class Meta:
        db_table = 'rider'
    def __str__(self):
        return self.name if self.name else f"Rider {self.id}"
    def set_password(self, password):
        """
        Hashes the password and stores it in the database.
        """
        self.password = hashlib.sha256(password.encode('utf-8')).hexdigest()

    def check_password(self, password):
        """
        Checks if the given password matches the stored hash.
        """
        return hashlib.sha256(password.encode('utf-8')).hexdigest() == self.password


class Ride(models.Model):
    RIDE_STATUS_CHOICES = [
        ('searching', 'Searching'),
        ('waiting_for_driver', 'Waiting for Driver'),
        ('on_the_way', 'On the Way'),
        ('completed', 'Completed'),
    ]

    id = models.CharField(max_length=255, primary_key=True)
    pickup_location = gis_models.PointField(srid=4326)  # Use SRID 4326 for WGS84 coordinate system
    dropoff_location = gis_models.PointField(srid=4326)  # Use SRID 4326 for WGS84 coordinate system
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    distance_traveled = models.FloatField(null=True, blank=True)
    route_taken = gis_models.LineStringField(srid=4326, null=True, blank=True)  # Use LineString for routes
    duration = models.FloatField(null=True, blank=True)
    final_price = models.FloatField(null=True, blank=True)
    rides_status = models.CharField(max_length=50, choices=RIDE_STATUS_CHOICES, null=True, blank=True)

    # ForeignKeys
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='rides')  # Use related_name for reverse lookup
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, null=True, blank=True, related_name='rides')

    def __str__(self):
        return f"Ride {self.id} by Driver {self.driver.id}"

    class Meta():
        db_table = 'rides'


class Offer(models.Model):
    OFFER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    ride = models.ForeignKey(Ride, on_delete=models.CASCADE, related_name="offers")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="driver_offers")
    status = models.CharField(max_length=50, choices=OFFER_STATUS_CHOICES)

    class Meta:
        unique_together = ('ride', 'driver')

    def __str__(self):
        return f"Offer for Ride {self.ride.id} by Driver {self.driver.id}"


class SurgeArea(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    multiplier = models.FloatField()
    location = gis_models.PolygonField(srid=4326)  # Use Polygon for surge areas

    def __str__(self):
        return self.name


class VehicleType(models.Model):
    type_id = models.CharField(max_length=255, primary_key=True)
    fare = models.FloatField()

    def __str__(self):
        return f"{self.type_id} (Fare: {self.fare})"


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=255, primary_key=True)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)

    # Foreign Keys
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.make} {self.model} ({self.plate_number})"
