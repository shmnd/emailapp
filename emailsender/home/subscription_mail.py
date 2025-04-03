from django.contrib import messages
from django.shortcuts import redirect
from home.tasks import send_email_task
from emailsender_core.helpers.utils import get_absolute_url

def mail_send(request, selected_template, subscribers):
    """Optimized mail sending in batches without Celery."""
    if not subscribers.exists():
        messages.error(request, "No subscribers found.")
        return redirect('home:send_email')
    

    request_data = {
        "logo_url": get_absolute_url(request,selected_template.logo.url) if selected_template.logo else None, 
        "image_url": get_absolute_url(request,selected_template.image.url) if selected_template.image else None,

    }

    # print(request_data["logo_url"],'logoooo')
    # print(request_data["image_url"],'imageeeee')


    subscriber_ids = list(subscribers.values_list('id',flat=True))
    
    send_email_task.delay(selected_template.id ,subscriber_ids,request_data)

    messages.success(request,f'Emails are being to sent asynchronously')
    return redirect('home:email_sent_summary')
