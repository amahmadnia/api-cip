from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_registration_email(user):
    subject = 'به سایت ثبت رزرو های cip کویت خوش آمدید'
    html_content = render_to_string('accounts/registration_email.html', {'user': user})

    # text_content = strip_tags(html_content)
    email = EmailMultiAlternatives(subject, html_content, user.email, [user.email])
    email.attach_alternative(html_content, 'text/html')

    try:
        email.send()
    except Exception as e:
        print(e)
