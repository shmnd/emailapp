import sys, os
from django.shortcuts import render, redirect,get_object_or_404
from home.forms import SubscribeForm,TagForm,TemplateForm
from home.models import Subscriber,Tags,Template,EmailSummery,EmailOpenTracking,Customers
import csv
from django.contrib import messages
from home.subscription_mail import mail_send
from django.db.models import Count
from django.utils.timezone import now
from django.db import IntegrityError
from django.http import HttpResponse
from django.core.paginator import Paginator
from home.serializers import CreateEnquiresSerializer
from rest_framework import generics,status
from emailsender_core.helpers.response import ResponseInfo
from home.schema import EnquiryDetailsSchema
from rest_framework.response import Response
from emailsender_core.helpers.pagination import RestPagination
from rest_framework.permissions import IsAuthenticated

def subscribe_view(request):
    if request.method == 'POST':
        form = SubscribeForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            tag = form.cleaned_data['tags']  

            if not tag:
                messages.error(request, "Please choose a Tag.")
                return redirect('home:subscribe')

            subscriber, created = Subscriber.objects.get_or_create(email=email)

            if subscriber.tags.filter(id=tag.id).exists():
                messages.error(request, "Tag and email already exist.")
            else:
                subscriber.tags.add(tag)
                messages.success(request, "Subscription updated successfully!")

            return redirect('home:subscriber_list')

        else:
            return render(request, 'admin/demo.html', {'form': form})

    form = SubscribeForm()
    tags = Tags.objects.all()
    return render(request, 'admin/demo.html', {'form': form, 'tags': tags})
    

# Tags crud

def tag_list(request):
    tags = Tags.objects.all()
    return render(request,'admin/tags/tag_list.html',{'tags':tags})

def tag_create(request):
    if request.method == 'POST':
        form = TagForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home:tag_list')
    else:
        form = TagForm()

    return render(request,'admin/tags/tag_form.html',{'form':form})


def tag_update(request,tag_id):
    tag = get_object_or_404(Tags,id=tag_id)
    
    if request.method == 'POST':
        form = TagForm(request.POST,instance=tag)
        if form.is_valid():
            form.save()
            return redirect('home:tag_list')
    else:
        form = TagForm(instance=tag)
    return render(request,'admin/tags/tag_form.html',{'form':form})
    
def tag_delete(request,tag_id):
    deleting_tags = get_object_or_404(Tags,id=tag_id)

    if request.method == 'POST':
        deleting_tags.delete()
        return redirect('home:tag_list')
    return render(request,'admin/tags/tag_confirm_delete.html',{'tags':deleting_tags})


# template 

def template_list(request):
    templates = Template.objects.all().order_by('-id')

    # for template in templates:
    #     # Count users who opened this email template
    #     template.opened_count = EmailOpenTracking.objects.filter(template=template).values('email').distinct().count()

    #     # Get a list of distinct emails of users who opened this template's email
    #     template.opened_users = EmailOpenTracking.objects.filter(template=template).values_list('email', flat=True).distinct()

    return render(request, 'admin/templates/templates_list.html', {'templates': templates})


def template_create(request):
    if request.method == "POST":
        form = TemplateForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home:template_list')
    else:
        form = TemplateForm()
    return render(request, 'admin/templates/template_form.html', {'form': form})


def template_update(request, pk):
    template = get_object_or_404(Template, pk=pk)
    if request.method == "POST":
        form = TemplateForm(request.POST, request.FILES, instance=template) 
        if form.is_valid():
            form.save()
            return redirect('home:template_list')
    else:
        form = TemplateForm(instance=template)
    return render(request, 'admin/templates/template_form.html', {'form': form})


def template_delete(request, pk):
    template = get_object_or_404(Template, pk=pk)
    if request.method == "POST":
        template.delete()
        return redirect('home:template_list')
    return render(request, 'admin/templates/template_confirm_delete.html', {'template': template})



#users

def subscriber_list(request):
    tag_filter = request.GET.get('tag')
    page_number = request.GET.get("page", 1)
    if tag_filter:
        subscribers = Subscriber.objects.filter(tags=tag_filter)
    else:
        subscribers = Subscriber.objects.all().order_by('-id')

    tags = Tags.objects.all()
    paginator = Paginator(subscribers, 200)
    page_obj = paginator.get_page(page_number)

    return render(request,'admin/users/users_listing.html',{'subscribers':page_obj,'tags':tags})


# upload csv file

def csv_upload(request):
    if request.method == "POST":
        csv_file = request.FILES.get("csv_file")
        tag_id = request.POST.get("tag")

        if not csv_file or not tag_id:
            messages.error(request, "Please select a tag and upload a valid CSV file.")
            return redirect("home:csv_upload")

        try:
            tag = Tags.objects.get(id=tag_id)
        except Tags.DoesNotExist:
            messages.error(request, "Selected tag does not exist.")
            return redirect("home:csv_upload")

        try:
            decoded_file = csv_file.read().decode("utf-8").splitlines()
            reader = csv.reader(decoded_file)
            next(reader, None)  # Skip header row if present
            
            new_subscribers = []
            for row in reader:
                if not row or len(row) == 0:  # Skip empty rows
                    continue
                
                email = row[0].strip()
                if email and email.endswith('.com'):
                    subscriber, created = Subscriber.objects.get_or_create(email=email)
                    subscriber.tags.add(tag)
                # else:
                #     messages.error(request,'Invalid Email Format')
                #     continue

            messages.success(request, "CSV file uploaded successfully!")
        
        except Exception as e:
            messages.error(request, f"Error processing CSV file: {'Invalid File format'}")

        return redirect("home:subscriber_list")


def export_subscribers(request):
    tag_filter = request.GET.get('tag')
    response = HttpResponse(content_type = 'text/csv')
    response['content-Dispostion'] = 'attachement; filename="subscribers.csv"'

    writer = csv.writer(response)
    writer.writerow(['Email','Tags'])

    if tag_filter:
        subscribers=Subscriber.objects.filter(tags__id=tag_filter).order_by('-id')
    else:
        subscribers=Subscriber.objects.all().order_by('-id')

    for subscriber in subscribers:
        tag_names = ", ".join(tag.name for tag in subscriber.tags.all())
        writer.writerow([subscriber.email,tag_names])

    return response


#selecting template
def send_email_view(request):
    if request.method == 'POST':
        template_id = request.POST.get('template')
        tag_ids = request.POST.getlist('tags')

        if not template_id:
            messages.error(request,"please select a template")
            return redirect('home:send_email')
        
        try:
            template = Template.objects.get(id=template_id)
        except Template.DoesNotExist:
            messages.error(request,'Selected template does not Exists')
            return redirect('home:send_email')
            
        if tag_ids:
            subscribers = Subscriber.objects.filter(tags__id__in=tag_ids).distinct()
        else:
            subscribers = Subscriber.objects.all()

        if not subscribers.exists():
            messages.error(request,'NO subscribers found on selected tags')
            return redirect('home:send_email')
        
        mail_send(request,template,subscribers)
        return redirect("home:email_sent_summary")

    template = Template.objects.all()
    tags = Tags.objects.all()
    return render(request,"admin/email/choose_sending_email_template.html",{"templates":template,"tags":tags})



'''Smaple Template View'''
def template_view(request, template_id):
    selected_template = get_object_or_404(Template, id=template_id)

    subject               = selected_template.email_subject or "Default Subject"
    email_body            = selected_template.email_body or "This is a sample email content."
    button_text           = selected_template.button_text or "Click Here"
    button_color          = selected_template.button_color or "#007BFF"
    button_url            = selected_template.button_url or "#"
    contact_email         = selected_template.contact_email or "support@example.com"
    unsubscribe_url       = selected_template.unsubscribe_url or "#"
    privacy_policy_url    = selected_template.privacy_policy_url or "#"

    logo_url = selected_template.logo.url if selected_template.logo else None
    image_url = selected_template.image.url if selected_template.image else None

    context = {
        "subject": subject,
        "template_name": selected_template.template_name,
        "email_body": email_body,
        "button_text": button_text,
        "button_color": button_color,
        "button_url": button_url,
        "contact_email": contact_email,
        "unsubscribe_url": unsubscribe_url,
        "privacy_policy_url": privacy_policy_url,
        "logo_url": logo_url if logo_url else None,
        "image_url": image_url if image_url else None,
    }


    return render(request, 'email_template/template1.html',context)


'''sended email summery'''
def email_sent_summary(request):
    """
    Displays a summary of successfully sent emails and allows filtering by template.
    """
    selected_template_id = request.GET.get("template", "")
    page_number = request.GET.get("page", 1)

    email_records = EmailSummery.objects.all().order_by('-id')
    
    if selected_template_id:
        email_records = email_records.filter(template_names=selected_template_id).order_by('-id')

    unique_templates = EmailSummery.objects.values_list('template_names', flat=True).distinct()

    paginator = Paginator(email_records, 200)
    page_obj = paginator.get_page(page_number)

    return render(request, "admin/email/email_sent_summary.html", {
        'email_records': page_obj,
        'unique_templates': unique_templates,
        'selected_template_id': selected_template_id,
    })


'''Emailsummery Download'''
def email_sent_summary_download (request):
    template_filter                   = request.GET.get('template')
    response                          = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition']   = 'attachement; filename="email_sent_summary_download.csv"'
    writer                            = csv.writer(response)
    writer.writerow(['Email', 'Template Name'])

    email_records = EmailSummery.objects.all().order_by('-id')

    if template_filter:
        email_records = email_records.filter(template_names=template_filter)

    for record in email_records:
        writer.writerow([record.sended_emails, record.template_names])

    return response




'''Tracking Email,template and count of the persons who opene the Email'''

def track_email_open(request):

    user_agent = request.headers.get('User-Agent', '')
    # print(f"TRACKING REQUEST RECEIVED: {request.GET} | USER AGENT: {user_agent}")

    # ✅ Ignore Gmail's proxy requests (GoogleImageProxy)
    if 'GoogleImageProxy' in user_agent:
        return HttpResponse("Gmail proxy request ignored.", status=200)

    # print(f"TRACKING REQUEST RECEIVED: {request.GET}")
    email           = request.GET.get('email')
    subscriber_id   = request.GET.get('subscriber_id')
    template_id     = request.GET.get('template_id')
    subject         = request.GET.get('subject')
    subscriber_id   = Subscriber.objects.get(id=subscriber_id)
    template_id     = Template.objects.get(id=template_id) 

    if not email or not template_id:
        return HttpResponse("Missing parameters", status=400)

    try:
        EmailOpenTracking.objects.create(
            email         = email,
            template_id   = template_id,
            subscriber_id = subscriber_id,
            opened_at     = now(),
            subject       = subject,
            
        )

    except IntegrityError:
        return HttpResponse("Tracking already recorded.", status=200)

    transparent_pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\xff\x00\xc0\xc0\xc0\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
    return HttpResponse(transparent_pixel, content_type="image/gif")




# api (in restframe work)
class CreateEnquiresApiView(generics.CreateAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(CreateEnquiresApiView,self).__init__(**kwargs)

    serializer_class = CreateEnquiresSerializer

    def post(self,request):
        try:
            serializer = self.serializer_class(data=request.data,context={'request':request})

            if not serializer.is_valid():
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format['status'] = False
                self.response_format['errors'] = serializer.errors
                return Response(self.response_format,status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            self.response_format['status_code'] = status.HTTP_201_CREATED
            self.response_format['status'] = True
            self.response_format['message'] = "Enquiry created successfully"
            self.response_format['data'] = serializer.data
            return Response(self.response_format,status=status.HTTP_201_CREATED)
        
        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format,status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
class EnquriryListApiView(generics.GenericAPIView):
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(EnquriryListApiView,self).__init__( **kwargs)

    serializer_class = EnquiryDetailsSchema
    pagination_class = RestPagination
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        try:
            queryset = Customers.objects.all().order_by('-id')
            page = self.paginate_queryset(queryset)

            if page is not None:
                serializer = self.serializer_class(page,many=True,context={'request':request})
                return self.get_paginated_response(serializer.data)
            
            serializer = self.serializer_class(queryset,many=True,context={'request':request})
            self.response_format['status_code'] = status.HTTP_200_OK
            self.response_format['status'] = True
            self.response_format['data'] = serializer.data
            return Response(self.response_format,status=status.HTTP_200_OK)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = f'Error in {fname}, line {exc_tb.tb_lineno}: {str(e)}'
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

# Unsubscription Email api 

class EmailUnsubscriptionApiView(generics.GenericAPIView):

    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(EmailUnsubscriptionApiView,self).__init__(**kwargs)


    def get(self,request):
        try:

            subscriber_id = request.GET.get('id')
            if not subscriber_id:
                return HttpResponse("Invalid unsubscribe link", status=400)
            try:
                subscriber = Subscriber.objects.filter(id=subscriber_id).first()
                if not subscriber:
                    self.response_format["status"] = False
                    self.response_format["message"] = "Subscriber not found"
                    return Response(self.response_format, status=status.HTTP_404_NOT_FOUND)
                
                subscriber.is_unsubscribed = True
                subscriber.unsubscribed_at = now()
                subscriber.save()

                return HttpResponse("✅ You have successfully unsubscribed. Thank you!", status=200)
            except Exception as e:
                self.response_format['status_code'] = status.HTTP_400_BAD_REQUEST
                self.response_format['status'] = False
                self.response_format['message'] = 'User not found :('
                return Response(self.response_format, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            self.response_format['status_code'] = status.HTTP_500_INTERNAL_SERVER_ERROR
            self.response_format['status'] = False
            self.response_format['message'] = str(e)
            return Response(self.response_format, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
