from django.contrib import messages
from django.shortcuts import redirect
from home.tasks import send_email_task

def mail_send(request, selected_template, subscribers):
    """Optimized mail sending in batches without Celery."""
    if not subscribers.exists():
        messages.error(request, "No subscribers found.")
        return redirect('home:send_email')

    request_data = {
        "logo_url": request.build_absolute_uri(selected_template.logo.url).replace("http://", "https://"), 
        "image_url": request.build_absolute_uri(selected_template.image.url).replace("http://", "https://"),

    }

    subscriber_ids = list(subscribers.values_list('id',flat=True))
    
    send_email_task.delay(selected_template.id ,subscriber_ids,request_data)

    messages.success(request,f'Emails are being to sent asynchronously')
    return redirect('home:email_sent_summary')
