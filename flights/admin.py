from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin


def format_price(value):
    return "{:,.0f}".format(value)


@admin.register(Price)
class PriceAdmin(admin.ModelAdmin):
    list_display = ('formatted_general_price', 'formatted_infant_price')
    search_fields = ('formatted_general_price', 'formatted_infant_price')
    ordering = ('general_price',)

    def formatted_general_price(self, obj):
        return format_price(obj.general_price)

    formatted_general_price.short_description = 'General Price'
    formatted_general_price.admin_order_field = 'general_price'

    def formatted_infant_price(self, obj):
        return format_price(obj.infant_price)

    formatted_infant_price.short_description = 'Infant Price'
    formatted_infant_price.admin_order_field = 'infant_price'


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = ('name', 'formatted_price')
    search_fields = ('name',)
    raw_id_fields = ('price',)
    autocomplete_fields = ('price',)

    def formatted_price(self, obj):
        return format_price(obj.price.general_price)

    formatted_price.short_description = 'Price'
    formatted_price.admin_order_field = 'price__general_price'


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 1


@admin.register(Reservation)
class ReservationAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id', 'cip_id', 'user', 'schedule', 'adults', 'infants', 'total_price', 'payment_status', 'date_created')
    search_fields = ('user__username', 'schedule__flight__name', 'schedule__flight_number')
    list_filter = ('user', 'schedule', 'adults', 'infants', 'payment_status')
    inlines = [PassengerInline]


@admin.register(FlightSchedule)
class FlightScheduleAdmin(admin.ModelAdmin):
    list_display = ('flight', 'flight_number', 'departure_time', 'departure_date', 'arrival_time', 'flight_type')
    search_fields = ('flight__name', 'flight_number')
    list_filter = ('flight_type', 'departure_time', 'arrival_time', 'departure_date')
