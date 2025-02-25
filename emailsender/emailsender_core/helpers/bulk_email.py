from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.core.mail import  get_connection
from emailsender_core import settings
from Crypto.Cipher import AES
import binascii

# -----------------------------------------Encrypt Email -----------------------------------

'''Encryption pad'''

def pad(data, block_size):
    padding_len = block_size - len(data) % block_size
    padding = bytes([padding_len] * padding_len)
    return data + padding

def unpad(data, block_size):
    padding_len = data[-1]
    return data[:-padding_len]

'''Encrypt and Decrypt Emails'''

key = b'B4VK5NGB?m*Y5(#knHAx^9Jas[*=&g;V'

def encrypt_email(email):
    email_bytes = email.encode('utf-8')
    pad_len = 16 - len(email_bytes) % 16
    padded_email = pad(email_bytes, 16)
    cipher = AES.new(key, AES.MODE_CBC)
    encrypted_email = cipher.encrypt(padded_email)
    iv = cipher.iv
    ciphertext = iv + encrypted_email
    hex_ciphertext = binascii.hexlify(ciphertext).decode('utf-8')
    return hex_ciphertext


def decrypt_email(encrypted_email):
    encrypted_email_bytes = binascii.unhexlify(encrypted_email.encode('utf-8'))
    iv = encrypted_email_bytes[:16]  # Extract IV from ciphertext
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_email_bytes = cipher.decrypt(encrypted_email_bytes[16:])
    decrypted_email = unpad(decrypted_email_bytes, AES.block_size).decode('utf-8')
    return decrypted_email


# ----------------------------------------------- SENDING EMAIL -----------------------------------------
'''Sending bulk email'''

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

