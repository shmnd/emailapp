from django.shortcuts import redirect
from concurrent.futures import ThreadPoolExecutor
from emailsender_core import settings
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from home.models import Subscriber, EmailSummery, Template
from django.db.models import F
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import time
import smtplib

try:
    server = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    server.starttls()
    server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    server.quit()
except Exception as e:
    print(f"SMTP connection failed: {e}")





def send_email_task(subscriber, selected_template, tracking_server, logo_cid, image_cid):
    """Send email and prepare EmailSummery instance for bulk creation."""
    subscriber_email = subscriber.email or "unknown@example.com"
    try:
        validate_email(subscriber_email)
    except ValidationError:
        return EmailSummery(
            sended_emails=subscriber_email,
            template_names=selected_template.template_name,
            status='Failed',
            failure_reason='Invalid Email Format',
            subscriber_id=subscriber,
            template_id=selected_template
        )

    subject = selected_template.email_subject or "No Subject"
    rand = int(time.time())
    email_track = f'<img src="{tracking_server}/track-email/?email={subscriber_email}&subscriber_id={subscriber.id}&template_id={selected_template.id}&subject={subject}&rand={rand}" width="1" height="1" style="display:none;">'
    unsubscription = settings.UNSUBSCRIPTION_PATH.format(subscriber_email=subscriber_email)
    context = {
        "subject": subject,
        "template_name": selected_template.template_name,
        "email_body": (selected_template.email_body or "This is a sample email content.") + email_track,
        "button_text": selected_template.button_text or "Click Here",
        "button_color": selected_template.button_color or "#007BFF",
        "button_url": selected_template.button_url or "#",
        "contact_email": selected_template.contact_email or "abhishek@medicoapps.org",
        "unsubscribe_url": selected_template.unsubscribe_url or unsubscription,
        "privacy_policy_url": selected_template.privacy_policy_url or "#",
        "logo_url": f"cid:{logo_cid}",
        "image_url": f"cid:{image_cid}",
        "subscriber": subscriber,
        "tracking_server": tracking_server,
        "template_id": selected_template.id
    }

    html_content = render_to_string("email_template/template1.html", context)
    plain_text_content = strip_tags(html_content)


    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[subscriber_email],
    )
    email.attach_alternative(html_content, "text/html")

    if selected_template.logo:
        try:
            with open(selected_template.logo.path, "rb") as img:
                mime_img = MIMEImage(img.read(), _subtype="jpeg")
                mime_img.add_header("Content-ID", f"<{logo_cid}>")
                mime_img.add_header("Content-Disposition", "inline", filename="logo.jpg")
                email.attach(mime_img)
        except Exception as e:
            print(f"Error attaching logo: {e}")

    if selected_template.image:
        try:
            with open(selected_template.image.path, "rb") as img:
                mime_img = MIMEImage(img.read(), _subtype="jpeg")
                mime_img.add_header("Content-ID", f"<{image_cid}>")
                mime_img.add_header("Content-Disposition", "inline", filename="banner.jpg")
                email.attach(mime_img)
        except Exception as e:
            print(f"Error attaching banner: {e}")

    try:
        email.send()
        return EmailSummery(
            sended_emails=subscriber_email,
            template_names=selected_template.template_name,
            status='Sent',
            subscriber_id=subscriber,
            template_id=selected_template,
            failure_reason = " - "
        )
    except Exception as e:
        print(f'Failed due to :{e}')
        return EmailSummery(
            sended_emails=subscriber_email,
            template_names=selected_template.template_name,
            status='Failed',
            failure_reason=e,
            subscriber_id=subscriber,
            template_id=selected_template
        )


def mail_send(request, selected_template, selected_tags):
    """Optimized mail sending with bulk create and concurrent execution."""
    subscribers = Subscriber.objects.filter(tags__id__in=selected_tags).distinct() if selected_tags else Subscriber.objects.filter(is_unsubscribed=False)

    if not subscribers.exists():
        messages.error(request, "No subscribers found.")
        return redirect('home:send_email')

    tracking_server = settings.TRACKING_SERVER
    logo_cid, image_cid = "logo_cid", "image_cid"

    total_emails, email_summaries = 0, []

    # ✅ Use ThreadPoolExecutor for faster multi-threaded execution
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [
            executor.submit(send_email_task, subscriber, selected_template, tracking_server, logo_cid, image_cid)
            for subscriber in subscribers
        ]

        for future in futures:
            email_summary = future.result()
            if email_summary:
                email_summaries.append(email_summary)
            total_emails += 1

    EmailSummery.objects.bulk_create(email_summaries)

    # ✅ Update template count based on successful sends
    total_sent = sum(1 for e in email_summaries if e.status == 'Sent')
    total_failed = sum(1 for e in email_summaries if e.status == 'Failed')
    Template.objects.filter(id=selected_template.id).update(count=F('count') + total_sent)

    # ✅ Summary Output
    print(f"Total Emails Processed: {total_emails}")
    print(f"Emails Sent Successfully: {total_sent}")
    print(f"Emails Failed: {total_failed}")

    return redirect("home:email_sent_summary")
