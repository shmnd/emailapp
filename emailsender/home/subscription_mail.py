from mailqueue.models import MailerMessage
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from home.models import Subscriber, EmailSummery, Template
from django.contrib import messages
from django.shortcuts import redirect
from django.template.loader import render_to_string
from emailsender_core import settings
from django.utils.html import strip_tags
from django.db.models import F
import time
from django.core.management import call_command
from threading import Thread

def send_emails_in_background():
    call_command('send_queued_messages')

def mail_send(request, selected_template, subscribers):
    """Optimized mail sending in batches without Celery."""
    if not subscribers.exists():
        messages.error(request, "No subscribers found.")
        return redirect('home:send_email')

    tracking_server = settings.TRACKING_SERVER
    email_summaries = []
    mailer_messages = []
    batch_size = 100  # Define batch size
    batch_count = 0

    for subscriber in subscribers:
        subscriber_email = subscriber.email or "unknown@example.com"
        try:
            validate_email(subscriber_email)
        except ValidationError:
            email_summaries.append(EmailSummery(
                sended_emails=subscriber_email,
                template_names=selected_template.template_name,
                status='Failed',
                failure_reason='Invalid Email Format',
                subscriber_id=subscriber,
                template_id=selected_template
            ))
            continue

        subject = selected_template.email_subject or "NEET PG Plan A - Special Offer - 6 Months Subscription for 2499/- Only"
        rand = int(time.time())
        email_track = f'<img src="{tracking_server}/track-email/?email={subscriber_email}&subscriber_id={subscriber.id}&template_id={selected_template.id}&subject={subject}&rand={rand}" width="1" height="1" style="display:none;">'
        
        # Generate Unsubscribe URL
        unsubscription = selected_template.unsubscribe_url or settings.UNSUBSCRIPTION_PATH.format(subscriber_email=subscriber_email)
        
        # Prepare context
        context = {
            "subject": subject,
            "template_name": selected_template.template_name,
            "email_body": (selected_template.email_body or "This is a sample email content.") + email_track,
            "button_text": selected_template.button_text or "We are giving away NEET PG 2024 Book Worth 999/- For Free to any one who is willing to spend 10 Minutes talking to me . In the cal l will be taking about what are the biggest challenges you are facing in your studies , specifically NEET PG Preparation so that we can understand and help our students better.",
            "button_color": selected_template.button_color or "#007BFF",
            "button_url": selected_template.button_url or "#",
            "contact_email": selected_template.contact_email or "abhishek@medicoapps.org",
            "unsubscribe_url": unsubscription,
            "privacy_policy_url": selected_template.privacy_policy_url or "https://www.medicos.app/termsandprivacy",
            "logo_url": request.build_absolute_uri(selected_template.logo.url).replace("http://", "https://"), 
            "image_url": request.build_absolute_uri(selected_template.image.url).replace("http://", "https://"),
            "subscriber": subscriber,
            "tracking_server": tracking_server,
            "template_id": selected_template.id
        }

        # Render HTML content
        html_content = render_to_string("email_template/template1.html", context)

        # Create MailerMessage object
        message = MailerMessage(
            subject=subject,
            to_address=subscriber_email,
            from_address=settings.DEFAULT_FROM_EMAIL,
            content=strip_tags(html_content),
            html_content=html_content
        )
        mailer_messages.append(message)

        # Record email summary
        email_summaries.append(EmailSummery(
            sended_emails=subscriber_email,
            template_names=selected_template.template_name,
            status='Queued',
            subscriber_id=subscriber,
            template_id=selected_template,
            failure_reason=" - "
        ))

        # Send emails in batches to save memory
        if len(mailer_messages) >= batch_size:
            MailerMessage.objects.bulk_create(mailer_messages)
            mailer_messages = []
            batch_count += 1

    # Insert any remaining emails
    if mailer_messages:
        MailerMessage.objects.bulk_create(mailer_messages)

    # Bulk create email summaries
    EmailSummery.objects.bulk_create(email_summaries)

    # Update template count based on successful sends
    Template.objects.filter(id=selected_template.id).update(count=F('count') + len(email_summaries))

    # Run email sending command in a background thread
    thread = Thread(target=send_emails_in_background)
    thread.start()

    messages.success(request, f"{len(email_summaries)} emails queued for sending in {batch_count + 1} batches.")
    return redirect("home:email_sent_summary")
