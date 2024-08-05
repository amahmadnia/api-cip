from django.urls import path
from . import views

urlpatterns = [
    path('flights/', views.FlightListView.as_view(), name='flight_list'),
    path('flight-schedules-list/', views.FlightScheduleListView.as_view(), name='flight-schedules-list'),
    path('flight-schedules-detail/', views.FlightScheduleDetailView.as_view(), name='flight-schedules-detail'),
    path('reservations/', views.ReservationCreateView.as_view(), name='reservation-create'),
    path('reserved-flights/', views.ReservationView.as_view(), name="reserved-flight"),
    path('price/', views.PriceView.as_view(), name='price'),

    path('reservations/pending/', views.ReservationPendingListView.as_view(), name='pending-reservations'),
    path('reservations/<int:reservation_id>/approve/', views.ApproveReservationView.as_view(),
         name='approve-reservation'),
    path('reservations/<int:reservation_id>/reject/', views.RejectReservationView.as_view(), name='reject-reservation'),

    path('export-pdf/8ba32987-d682-4d49-b054-ac3372fabec6/', views.ExportByDateView, name='export_pdf'),
]
