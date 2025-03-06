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


def mail_send(request, selected_template, subscribers):
    """Optimized mail sending with django-mail-queue."""

    if not subscribers.exists():
        messages.error(request, "No subscribers found.")
        return redirect('home:send_email')

    tracking_server = settings.TRACKING_SERVER
    email_summaries = []
    mailer_messages = []

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

        subject = selected_template.email_subject or "No Subject"
        rand = int(time.time())
        email_track = f'<img src="{tracking_server}/track-email/?email={subscriber_email}&subscriber_id={subscriber.id}&template_id={selected_template.id}&subject={subject}&rand={rand}" width="1" height="1" style="display:none;">'
        
        # Generate Unsubscribe URL
        unsubscription = selected_template.unsubscribe_url or settings.UNSUBSCRIPTION_PATH.format(subscriber_email=subscriber_email)
        
        # print("Logo URL:", request.build_absolute_uri(selected_template.logo.url) if selected_template.logo else "No Logo Found")
        # print("Image URL:", request.build_absolute_uri(selected_template.image.url) if selected_template.image else "No Image Found")


        # Prepare context
        context = {
            "subject": subject,
            "template_name": selected_template.template_name,
            "email_body": (selected_template.email_body or "This is a sample email content.") + email_track,
            "button_text": selected_template.button_text or "Click Here",
            "button_color": selected_template.button_color or "#007BFF",
            "button_url": selected_template.button_url or "#",
            "contact_email": selected_template.contact_email or "abhishek@medicoapps.org",
            "unsubscribe_url": unsubscription,
            "privacy_policy_url": selected_template.privacy_policy_url or "https://www.medicos.app/termsandprivacy",

            "logo_url": request.build_absolute_uri(selected_template.logo.url).replace("http://127.0.0.1:8000", "http://email.arolus.com") if selected_template.logo else "https://www.medicoapps.org/static/images/logoo.png",

            "image_url": request.build_absolute_uri(selected_template.image.url).replace("http://127.0.0.1:8000", "http://email.arolus.com") if selected_template.image else "https://www.medicoapps.org/static/images/Medical-Apps.jpg",


            # "logo_url": "http://email.arolus.com" + selected_template.logo.url if selected_template.logo else "https://www.medicoapps.org/static/images/logoo.png",
            # "image_url": "http://email.arolus.com" + selected_template.image.url if selected_template.image else "https://www.medicoapps.org/static/images/Medical-Apps.jpg",

            # "logo_url":selected_template.logo,
            # "image_url": selected_template.image,

            "subscriber": subscriber,
            "tracking_server": tracking_server,
            "template_id": selected_template.id
        }


        # print("Generated Logo URL:", selected_template.logo.url)
        # print("Generated Image URL:", selected_template.image.url)

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

    # Bulk create MailerMessage objects
    MailerMessage.objects.bulk_create(mailer_messages)

    # Bulk create email summaries
    EmailSummery.objects.bulk_create(email_summaries)

    # Update template count based on successful sends
    Template.objects.filter(id=selected_template.id).update(count=F('count') + len(email_summaries))

    messages.success(request, f"{len(email_summaries)} emails queued for sending.")
    return redirect("home:email_sent_summary")
