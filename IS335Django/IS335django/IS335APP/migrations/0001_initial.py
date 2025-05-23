# Generated by Django 5.1.7 on 2025-03-14 01:04

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Driver",
            fields=[
                (
                    "id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("license_info", models.CharField(max_length=255)),
                (
                    "contact_details",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("Available", "Available"), ("Busy", "Busy")],
                        max_length=50,
                    ),
                ),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
        ),
        migrations.CreateModel(
            name="Rider",
            fields=[
                (
                    "id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("name", models.CharField(blank=True, max_length=255, null=True)),
                ("contact_details", models.CharField(max_length=255)),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ("password", models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name="SurgeArea",
            fields=[
                (
                    "name",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("multiplier", models.FloatField()),
                (
                    "location",
                    django.contrib.gis.db.models.fields.PolygonField(srid=4326),
                ),
            ],
        ),
        migrations.CreateModel(
            name="VehicleType",
            fields=[
                (
                    "type_id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("fare", models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name="Ride",
            fields=[
                (
                    "id",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                (
                    "pickup_location",
                    django.contrib.gis.db.models.fields.PointField(srid=4326),
                ),
                (
                    "dropoff_location",
                    django.contrib.gis.db.models.fields.PointField(srid=4326),
                ),
                ("start_time", models.DateTimeField(blank=True, null=True)),
                ("end_time", models.DateTimeField(blank=True, null=True)),
                ("distance_traveled", models.FloatField(blank=True, null=True)),
                (
                    "route_taken",
                    django.contrib.gis.db.models.fields.LineStringField(
                        blank=True, null=True, srid=4326
                    ),
                ),
                ("duration", models.FloatField(blank=True, null=True)),
                ("final_price", models.FloatField(blank=True, null=True)),
                (
                    "rides_status",
                    models.CharField(
                        blank=True,
                        choices=[
                            ("searching", "Searching"),
                            ("waiting_for_driver", "Waiting for Driver"),
                            ("on_the_way", "On the Way"),
                            ("completed", "Completed"),
                        ],
                        max_length=50,
                        null=True,
                    ),
                ),
                (
                    "driver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rides",
                        to="IS335APP.driver",
                    ),
                ),
                (
                    "rider",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="rides",
                        to="IS335APP.rider",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Vehicle",
            fields=[
                (
                    "plate_number",
                    models.CharField(max_length=255, primary_key=True, serialize=False),
                ),
                ("make", models.CharField(blank=True, max_length=255, null=True)),
                ("model", models.CharField(blank=True, max_length=255, null=True)),
                ("color", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "driver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="vehicles",
                        to="IS335APP.driver",
                    ),
                ),
                (
                    "vehicle_type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="IS335APP.vehicletype",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Offer",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("Pending", "Pending"),
                            ("Accepted", "Accepted"),
                            ("Rejected", "Rejected"),
                        ],
                        max_length=50,
                    ),
                ),
                (
                    "driver",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="driver_offers",
                        to="IS335APP.driver",
                    ),
                ),
                (
                    "ride",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="offers",
                        to="IS335APP.ride",
                    ),
                ),
            ],
            options={
                "unique_together": {("ride", "driver")},
            },
        ),
    ]
