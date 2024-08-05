from rest_framework import generics, status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError
from .serialiazers import *
from datetime import datetime
from .utils import generate_pdf_by_date_view, send_reservation_email


class FlightListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer


class FlightScheduleListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FlightScheduleSerializer

    def get_queryset(self):
        flight_id = self.request.query_params.get('flight_id')
        date_str = self.request.query_params.get('date')

        if not flight_id:
            raise ValidationError({'flight_id': 'Flight ID is required.'})
        try:
            flight_id = int(flight_id)
        except ValueError:
            raise ValidationError({'flight_id': 'Flight ID must be an integer.'})

        if not date_str:
            raise ValidationError({'date': 'Date is required.'})
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError({'date': 'Date must be in YYYY-MM-DD format.'})

        return FlightSchedule.objects.filter(flight_id=flight_id, departure_date=date)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FlightScheduleDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FlightScheduleSerializer

    def get_object(self):
        flight_id = self.request.query_params.get('flight_id')
        if not flight_id:
            raise NotFound({'flight_id': 'Flight ID is required.'})
        try:
            flight_id = int(flight_id)
        except ValueError:
            raise NotFound({'flight_id': 'Flight id must be an integer'})

        try:
            return FlightSchedule.objects.get(id=flight_id)
        except FlightSchedule.DoesNotExist:
            raise NotFound({'flight_id': 'Flight schedule not found for the given flight ID'})

    def get(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)


class ReservationCreateView(generics.CreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer

    def create(self, request, *args, **kwargs):
        user = request.user
        schedule_id = self.request.data.get('schedule')
        adults = self.request.data.get('adults')
        infants = self.request.data.get('infants')
        payment_status = self.request.data.get('status')
        passengers = self.request.data.get('passengers', [])

        if not schedule_id:
            return Response({'schedule': 'Schedule ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            schedule = FlightSchedule.objects.get(id=schedule_id)
        except FlightSchedule.DoesNotExist:
            raise NotFound('Flight schedule not found')

        reservation = Reservation.objects.create(
            user=user,
            schedule=schedule,
            adults=adults,
            infants=infants,
            payment_status=payment_status,
        )

        passenger_serializer = PassengerSerializer(data=passengers, many=True)
        if passenger_serializer.is_valid():
            passenger_serializer.save(reservation=reservation)
        else:
            reservation.delete()
            return Response(passenger_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        reservation_serializer = self.get_serializer(reservation)
        send_reservation_email(user, reservation.cip_id, payment_status)
        return Response(reservation_serializer.data, status=status.HTTP_201_CREATED)

class ReservationView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ReservationSerializer
    
    def get_queryset(self):
        date_str = self.request.query_params.get('date')
        if not date_str:
            raise ValidationError({'date': 'Date is required.'})
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            raise ValidationError({'date': 'Date must be in YYYY-MM-DD format.'})
        return Reservation.objects.filter(user=self.request.user, date_created__date=date)
    
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        except ValidationError as e:
            return Response(e.detail, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PriceView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = PriceSerializer
    queryset = Price.objects.all()


class ReservationPendingListView(generics.ListAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = ReservationManageSerializer
    queryset = Reservation.objects.filter(payment_status='pending')


class ApproveReservationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        if reservation.payment_status == 'approved':
            return Response({'status': 'Reservation already approved'}, status=status.HTTP_400_BAD_REQUEST)

        reservation.payment_status = 'approved'
        reservation.save()
        send_reservation_email(reservation.user, reservation.cip_id, reservation.payment_status)
        return Response({'status': 'Reservation approved'}, status=status.HTTP_200_OK)


class RejectReservationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, reservation_id):
        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return Response({'error': 'Reservation not found'}, status=status.HTTP_404_NOT_FOUND)

        reservation.payment_status = 'rejected'
        send_reservation_email(reservation.user, cip_id=None, status=reservation.payment_status)
        reservation.delete()
        return Response({'status': 'Reservation rejected and deleted'}, status=status.HTTP_200_OK)


def ExportByDateView(request):
    return generate_pdf_by_date_view(request)
