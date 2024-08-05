# FOR A PDF EXPORT
from django.http import HttpResponse
from datetime import datetime
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from .models import FlightSchedule, Reservation
# SEND EMAIL
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def get_flights_data(date):
    flight_schedules = FlightSchedule.objects.filter(departure_date=date).order_by('flight__name', 'flight_number')

    flights_data = []

    for schedule in flight_schedules:
        reservations = Reservation.objects.filter(schedule=schedule, payment_status='approved')
        passengers = []

        for reservation in reservations:
            reservation_passengers = list(reservation.passengers.all())
            if reservation_passengers:
                passengers.extend(reservation_passengers)

        if passengers:
            flights_data.append({
                'schedule': schedule,
                'reservations': reservations,
                'passengers': passengers,
                'adults_count': sum(r.adults for r in reservations),
                'infants_count': sum(r.infants for r in reservations),
                'total_passengers': len(passengers)
            })

    return flights_data


def generate_pdf_by_date_view(request):
    date_str = request.GET.get('date')
    if not date_str:
        return HttpResponse("Date parameter is required.", status=400)

    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return HttpResponse("Invalid date format. Please use YYYY-MM-DD.", status=400)

    flights = get_flights_data(date)
    total_flights = len(flights)
    total_passengers = sum(flight['total_passengers'] for flight in flights)

    context = {
        'date': date_str,
        'flights': flights,
        'total_flights': total_flights,
        'total_passengers': total_passengers,
    }

    html_string = render_to_string('flights/flights_pdf_template.html', context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=flight_report.pdf'

    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html_string.encode("UTF-8")), dest=result)
    if pdf.err:
        return HttpResponse('We had some errors <pre>' + html_string + '</pre>')

    response.write(result.getvalue())
    return response


def send_reservation_email(user, cip_id, status):
    subject = 'وضعیت رزرو شما'

    if status == 'approved':
        html_content = render_to_string('flights/approved_email.html', {
            'user': user,
            'cip_id': cip_id
        })
    elif status == 'pending':
        html_content = render_to_string('flights/pending_email.html', {
            'user': user,
            'cip_id': cip_id
        })
    elif status == 'rejected':
        subject = 'رزور شما رد شد'
        html_content = render_to_string('flights/rejected_email.html', {
            'user': user
        })
    else:
        raise ValueError("Invalid status provided")

    text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, text_content, user.email, [user.email])
    email.attach_alternative(html_content, 'text/html')

    try:
        email.send()
    except Exception as e:
        print(f"Error sending email: {str(e)}")
