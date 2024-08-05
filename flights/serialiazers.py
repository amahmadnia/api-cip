from rest_framework import serializers
from accounts.serializers import CustomUserSerializer
from .models import *


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = ('id', 'name')


class FlightScheduleSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()

    class Meta:
        model = FlightSchedule
        fields = ('id', 'flight', 'flight_number', 'departure_time', 'arrival_time',
                  'flight_type')


class PassengerSerializer(serializers.ModelSerializer):
    age = serializers.ReadOnlyField()

    class Meta:
        model = Passenger
        fields = ['first_name', 'last_name', 'passport_number', 'birth_date', 'age', 'gender', 'description']


class ReservationSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True)

    class Meta:
        model = Reservation
        fields = ['cip_id', 'schedule', 'adults', 'infants', 'date_updated', 'total_price',
                  'payment_status', 'user', 'passengers']
        read_only_fields = ['cip_id', 'date_created', 'date_updated', 'total_price', 'user']

    def create(self, validated_data):
        passengers_data = validated_data.pop('passengers')
        reservation = Reservation.objects.create(**validated_data)
        for passenger_data in passengers_data:
            Passenger.objects.create(reservation=reservation, **passenger_data)
        return reservation


class ReservationManageSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Reservation
        fields = ['id', 'cip_id', 'user', 'adults', 'infants', 'total_price']


class PriceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Price
        fields = ['general_price', 'infant_price']
