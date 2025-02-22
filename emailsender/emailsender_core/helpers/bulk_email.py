from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.mail import  get_connection
from emailsender_core import settings

class SendBulkEmailsSend:
    def __init__(self, *args, **kwargs):
        pass

    def send_bulk_email(self, subject, request, context, template_path, sender_email, recipient_emails, email_map):
        """
        Sends bulk email using the given email template.
        
        :param subject: Subject of the email
        :param request: Django request object
        :param context: Context dictionary for rendering the email template
        :param template_path: Path to the email template file
        :param sender_email: Email sender address
        :param recipient_emails: List of recipient email addresses
        :param email_map: Mapping of recipient emails to their encrypted versions
        """

        sending_status = False

        try:
            connection = get_connection()
            connection.open()

            for email in recipient_emails:
                # Render email content using the selected template and provided context
                html_content = render_to_string(template_path, context)
                text_content = strip_tags(html_content)

                # Create email message
                email_message = EmailMultiAlternatives(
                    subject=subject,
                    body=text_content,
                    from_email=sender_email,
                    to=[email],
                    connection=connection,
                )
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()

            connection.close()
            sending_status = True

        except Exception as e:
            print(f"Error sending bulk email: {e}")

        return sending_status

