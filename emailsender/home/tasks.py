from django.core.mail import send_mail
from celery import shared_task
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from home.models import Subscriber, EmailSummery, Template
from emailsender_core import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db.models import F
import time

@shared_task
def send_email_task(template_id, subscriber_ids, request_data):
    """Celery task to send all emails directly without batching."""
    try:
        template = Template.objects.get(id=template_id)
    except Template.DoesNotExist:
        return "Template does not exist."
    

    subscribers = Subscriber.objects.filter(id__in=subscriber_ids)
    if not subscribers.exists():
        return "No subscribers found."
    

    tracking_server = settings.TRACKING_SERVER
    email_summaries = []
    # mailer_messages = []

    for subscriber in subscribers:
        subscriber_email = subscriber.email or "unknown@example.com"
        try:
            validate_email(subscriber_email)
        except ValidationError:
            email_summaries.append(EmailSummery(
                sended_emails=subscriber_email,
                template_names=template.template_name,
                status='Failed',
                failure_reason='Invalid Email Format',
                subscriber_id=subscriber,
                template_id=template
            ))
            continue

        subject = template.email_subject or "NEET PG Plan A - Special Offer - 6 Months Subscription for 2499/- Only"
        rand = int(time.time())
        email_track = f'<img src="{tracking_server}/track-email/?email={subscriber_email}&subscriber_id={subscriber.id}&template_id={template.id}&subject={subject}&rand={rand}" width="1" height="1" style="display:none;">'
        
        # Generate Unsubscribe URL
        unsubscription = template.unsubscribe_url or settings.UNSUBSCRIPTION_PATH.format(subscriber_email=subscriber_email)
        
        # Prepare context
        context = {
            "subject": subject,
            "template_name": template.template_name,
            "email_body": (template.email_body or "This is a sample email content.") + email_track,
            "button_text": template.button_text or "Default button text",
            "button_color": template.button_color or "#007BFF",
            "button_url": template.button_url or "#",
            "contact_email": template.contact_email or "contact@example.com",
            "unsubscribe_url": unsubscription,
            "privacy_policy_url": template.privacy_policy_url or "https://www.example.com/privacy",
            "logo_url": request_data.get("logo_url"),
            "image_url": request_data.get("image_url"),
            "subscriber": subscriber,
            "tracking_server": tracking_server,
            "template_id": template.id
        }

        # Render HTML content
        html_content = render_to_string("email_template/template1.html", context)

        # Create and send MailerMessage object directly
        send_mail(
            subject,
            strip_tags(html_content),
            settings.DEFAULT_FROM_EMAIL,
            [subscriber_email],
            html_message=html_content
        )

        # Record email summary
        email_summaries.append(EmailSummery(
            sended_emails=subscriber_email,
            template_names=template.template_name,
            status='Queued',
            subscriber_id=subscriber,
            template_id=template,
            failure_reason=" - "
        ))

    # Bulk create email summaries
    EmailSummery.objects.bulk_create(email_summaries)

    # Update template count based on successful sends
    Template.objects.filter(id=template.id).update(count=F('count') + len(email_summaries))

    return f"{len(email_summaries)} emails queued successfully!"


