# surge/serializers.py
from rest_framework import serializers

class SurgeAreaSerializer(serializers.Serializer):
    location = serializers.CharField()  # GeoJSON location
    multiplier = serializers.FloatField()  # Multiplier


class SurgeAreaSerializer_explore(serializers.Serializer):
    location = serializers.CharField()  # GeoJSON location
    multiplier = serializers.FloatField()  # Multiplier
    name = serializers.CharField()
