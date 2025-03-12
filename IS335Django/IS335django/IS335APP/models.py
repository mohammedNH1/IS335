from django.db import models

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
    latitude = models.FloatField(null=True, blank=True)  # Replace PointField
    longitude = models.FloatField(null=True, blank=True)  # Replace PointField

class Offer(models.Model):
    OFFER_STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected')
    ]
    
    status = models.CharField(max_length=50, choices=OFFER_STATUS_CHOICES)
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="offers")
    ride = models.ForeignKey('Rides', on_delete=models.CASCADE, related_name="offers")

    class Meta:
        unique_together = ('ride', 'driver')  # Use the ForeignKey fields here

class Rider(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    contact_details = models.CharField(max_length=255)
    password = models.CharField(max_length=255, default="")
    latitude = models.FloatField(null=True, blank=True)  # Replace PointField
    longitude = models.FloatField(null=True, blank=True)  # Replace PointField

class Rides(models.Model):
    RIDE_STATUS_CHOICES = [
        ('searching', 'searching'),
        ('waiting for driver', 'waiting for driver'),
        ('on the way', 'on the way'),
        ('completed', 'completed')
    ]
    
    id = models.CharField(max_length=255, primary_key=True)
    pickup_latitude = models.FloatField(null=True, blank=True)  # Replace PointField
    pickup_longitude = models.FloatField(null=True, blank=True)  # Replace PointField
    dropoff_latitude = models.FloatField(null=True, blank=True)  # Replace PointField
    dropoff_longitude = models.FloatField(null=True, blank=True)  # Replace PointField
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    distance_traveled = models.FloatField(null=True, blank=True)
    route_taken = models.TextField(null=True, blank=True)  # Replace GeometryField
    duration = models.FloatField(null=True, blank=True)
    final_price = models.FloatField(null=True, blank=True)
    rides_status = models.CharField(max_length=50, choices=RIDE_STATUS_CHOICES, null=True, blank=True)
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    rider = models.ForeignKey(Rider, on_delete=models.CASCADE, null=True, blank=True)

class SurgeArea(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    multiplier = models.FloatField()
    area_boundaries = models.TextField(null=True, blank=True)  # Replace GeometryField

class VehicleType(models.Model):
    type_id = models.CharField(max_length=255, primary_key=True)
    fare = models.FloatField()

class Vehicle(models.Model):
    type_id = models.CharField(max_length=255)
    make = models.CharField(max_length=255, null=True, blank=True)
    model = models.CharField(max_length=255, null=True, blank=True)
    color = models.CharField(max_length=255, null=True, blank=True)
    plate_number = models.CharField(max_length=255, primary_key=True)
    
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.CASCADE)
