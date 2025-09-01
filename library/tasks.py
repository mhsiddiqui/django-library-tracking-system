import logging
import smtplib
from collections import defaultdict

from celery import shared_task
from django.utils import timezone

from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass


@shared_task
def check_overdue_loans():
    overdue_loans = Loan.objects.filter(
        due_date__lte=timezone.now().date(), is_returned=False
    ).select_related('book', 'member', 'member__user')

    # Group user loans
    user_overdue_books = defaultdict(list)
    for loan in overdue_loans:
        user_overdue_books[loan.member.user.email].append(loan)

    # Send each user email with all overdue books
    for email, loans in user_overdue_books.items():
        try:
            books = ', '.join([loan.book.title for loan in loans])
            username = loans[0].member.user.username
            send_mail(
                subject='Book Loaned Successfully',
                message=f'Hello {username},\n\nYour due date for book(s) "{books}" has passed.'
                        f'\nPlease return it as soon as possible.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except smtplib.SMTPException:
            logger.error('There was an error while sending email', exc_info=True)
        except ImproperlyConfigured:
            logger.error('SMTP is not properly configured', exc_info=True)
        except Exception as ex:
            logger.error(f'There was an error while sending email to {email}', exc_info=True)
