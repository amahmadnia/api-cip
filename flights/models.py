from django.db import models
from datetime import date
import random
import string


def generate_short_id(length=4):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))


class Price(models.Model):
    general_price = models.DecimalField(max_digits=10, decimal_places=2)
    infant_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"General: {self.general_price}, Infant: {self.infant_price}"


class Flight(models.Model):
    name = models.CharField(max_length=100)
    price = models.ForeignKey(Price, on_delete=models.CASCADE, related_name='flight')

    def __str__(self):
        return self.name


class FlightSchedule(models.Model):
    FLIGHT_TYPE_CHOICES = [
        ('outbound', 'outbound'),
        ('inbound', 'inbound'),
    ]

    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, related_name='schedules')
    flight_number = models.CharField(max_length=50)
    departure_date = models.DateField()
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    flight_type = models.CharField(max_length=8, choices=FLIGHT_TYPE_CHOICES)

    def __str__(self):
        return f"{self.flight.name} - {self.flight_number}"

    @property
    def formatted_departure_time(self):
        return self.departure_time.strftime('%H:%M')

    @property
    def formatted_arrival_time(self):
        return self.arrival_time.strftime('%H:%M')


class Reservation(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rejected', 'rejected'),
    ]
    cip_id = models.CharField(max_length=4, default=generate_short_id, editable=False, unique=True)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    schedule = models.ForeignKey(FlightSchedule, on_delete=models.CASCADE)
    adults = models.IntegerField()
    infants = models.IntegerField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True)
    payment_status = models.CharField(max_length=8, choices=PAYMENT_STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        prices = self.schedule.flight.price
        if prices:
            self.total_price = (
                    self.adults * prices.general_price +
                    self.infants * prices.infant_price
            )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Reservation for {self.schedule.flight.name} - {self.schedule.flight_number}"


class Passenger(models.Model):
    GENDER_CHOICES = [
        ('Male', 'male'),
        ('Female', 'female')
    ]
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='passengers')
    first_name = models.CharField(max_length=100, blank=False)
    last_name = models.CharField(max_length=100, blank=False)
    gender = models.CharField(choices=GENDER_CHOICES, default='Male', max_length=6)
    birth_date = models.DateField()
    passport_number = models.CharField(max_length=20, blank=False)
    description = models.TextField(blank=True)

    @property
    def age(self):
        today = date.today()
        return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day))

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.passport_number}"
