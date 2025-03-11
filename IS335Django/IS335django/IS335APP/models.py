# models.py
from django.db import models
from django.contrib.gis.db import models as gis_models  # for geography and geometry fields

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
    location = gis_models.PointField()  # for geography data type

class Offer(models.Model):
    OFFER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected','Rejected')
    ]
    
    ride_id = models.CharField(max_length=255)
    driver_id = models.CharField(max_length=255)
    status = models.CharField(max_length=50, choices=OFFER_STATUS_CHOICES)
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="offers")
    ride = models.ForeignKey('Rides', on_delete=models.CASCADE, related_name="offers")

    class Meta:
        unique_together = ('ride_id', 'driver_id')

class Rider(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    contact_details = models.CharField(max_length=255)
    location = gis_models.PointField()  # for geography data type

class Rides(models.Model):
    RIDE_STATUS_CHOICES = [
        ('searching', 'searching'),
        (' waiting for drive', ' waiting for drive'),
        ('on the way','on the way'),
         ('completed','completed')
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    driver_id = models.CharField(max_length=255)
    pickup_location = gis_models.PointField()  # for geography data type
    dropoff_location = gis_models.PointField()  # for geography data type
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    distance_traveled = models.FloatField(null=True, blank=True)
    route_taken = gis_models.GeometryField(null=True, blank=True)  # for geometry data type
    duration = models.FloatField(null=True, blank=True)
    final_price = models.FloatField(null=True, blank=True)
    rides_status = models.CharField(max_length=50, choices=RIDE_STATUS_CHOICES, null=True, blank=True)
    rider_id = models.CharField(max_length=255, null=True, blank=True)
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, null=True, blank=True)

class SurgeArea(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    multiplier = models.FloatField()
    location = gis_models.GeometryField()  # for geometry data type

class VehicleType(models.Model):
    type_id = models.CharField(max_length=255, primary_key=True)
    fare = models.FloatField()

class Vehicle(models.Model):
    driver_id = models.CharField(max_length=255)
    type_id = models.CharField(max_length=255)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    plate_number = models.CharField(max_length=255, primary_key=True)
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
